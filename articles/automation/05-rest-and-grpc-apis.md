# REST and gRPC APIs in Network Automation

Modern network automation does not just talk to network devices. It talks to systems: IPAM systems that allocate IP addresses, CMDB systems that track device inventory, orchestration platforms that trigger workflows, monitoring systems that collect telemetry, and cloud provider APIs that provision infrastructure. All of these systems communicate through APIs, and the two dominant paradigms are REST and gRPC.

Understanding both — how they work, where each is appropriate, and how to use them effectively in Python — is a foundational skill for any senior network engineer building automation at scale.

## REST APIs: The Dominant Standard

**REST (Representational State Transfer)** is an architectural style for distributed systems, not a protocol. RESTful APIs communicate over HTTP, use standard HTTP methods (GET, POST, PUT, PATCH, DELETE), and typically exchange data in JSON format.

The model is simple: resources (devices, interfaces, BGP neighbors, IP addresses) are identified by URLs. HTTP methods define what operation to perform on those resources.

```
GET    /api/devices/leaf-01/interfaces/eth0   → retrieve interface state
POST   /api/devices                           → create a new device record
PUT    /api/devices/leaf-01                   → replace a device's full record
PATCH  /api/devices/leaf-01                   → update specific fields
DELETE /api/devices/leaf-01                   → remove a device record
```

**Python requests library for REST:**

```python
import requests

BASE_URL = "https://netbox.internal/api"
HEADERS = {
    "Authorization": "Token abc123",
    "Content-Type": "application/json"
}

# Get all devices in the spine role
response = requests.get(
    f"{BASE_URL}/dcim/devices/",
    headers=HEADERS,
    params={"role": "spine", "site": "us-east-1a"}
)
response.raise_for_status()  # raises exception on 4xx/5xx
devices = response.json()["results"]

for device in devices:
    print(f"{device['name']}: {device['primary_ip']['address']}")
```

**Error handling matters more than most engineers realize.** Network automation that talks to REST APIs must handle:
- **4xx errors:** Bad request (400), unauthorized (401), not found (404). These indicate a problem with your request — log the response body, which typically contains a descriptive error message.
- **5xx errors:** Server errors. These may be transient — implement retry logic with exponential backoff.
- **Timeouts:** Network issues, overloaded API servers. Set explicit timeouts on every request; never rely on the default (which is often infinite).
- **Rate limiting (429):** Many APIs throttle requests. Respect `Retry-After` headers. In bulk automation, add delays between requests or use batched API calls if supported.

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503])
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

# Now every request through session retries automatically on transient errors
```

## Common Network REST API Integrations

**NetBox / IPAM:** The most common source of truth for network automation. NetBox exposes a full REST API for devices, racks, IP addresses, VLANs, prefixes, cables, and more. Automation reads from NetBox to generate configurations; provisioning tools write back to NetBox to record allocated IPs and device state.

**Arista eAPI:** Arista EOS exposes a JSON-RPC API that accepts CLI commands and returns structured JSON. This is not pure REST but uses HTTP. Useful for Arista-specific operations not covered by NETCONF modules.

```python
import requests

payload = {
    "jsonrpc": "2.0",
    "method": "runCmds",
    "params": {"version": 1, "cmds": ["show ip bgp summary"]},
    "id": 1
}
response = requests.post(
    "https://switch-01/command-api",
    json=payload,
    auth=("admin", "secret"),
    verify=False
)
bgp_data = response.json()["result"][0]
```

**AWS APIs / Boto3:** In AWS environments, everything — Lambda invocations, DynamoDB reads, SQS messages, internal service APIs — is accessible via Python's Boto3 SDK, which wraps the AWS REST APIs. A typical Lambda-based deployment orchestration uses Boto3 to read from DynamoDB (source of truth), invoke other Lambda functions (step sequencing), and put messages on SQS queues (event-driven triggers).

## gRPC: When REST Is Not Enough

REST over HTTP/1.1 has known performance limitations: each request is a separate HTTP connection (or reuses a connection pool with HTTP keep-alive), the text-based JSON encoding is verbose, and there is no efficient streaming model.

**gRPC** (Google Remote Procedure Call) addresses these limitations:
- Built on HTTP/2: multiplexed streams over a single connection, binary framing, header compression
- Uses **Protocol Buffers (protobuf)** for encoding: binary format, significantly smaller than JSON, strongly typed
- Supports four communication patterns: unary (like REST), server streaming, client streaming, bidirectional streaming

For network automation, gRPC is most important for two use cases:

**gNMI (gRPC Network Management Interface):** The standard for streaming telemetry from network devices. A gNMI `Subscribe` call establishes a persistent bidirectional stream. The switch sends telemetry updates continuously as values change — no polling. For collecting interface counters, BGP peer state, or CPU/memory metrics from thousands of devices, gNMI streaming is far more efficient than SNMP or REST polling.

**Internal microservices at hyperscale:** At hyperscale, internal systems commonly communicate via gRPC. An automation service that needs to call an internal provisioning service, a topology database API, or a network state cache typically does so via gRPC, not REST — because the performance and schema-enforcement characteristics matter when a single automation operation calls dozens of internal services in sequence.

**Python gRPC client:**

```python
import grpc
from gnmi_pb2_grpc import gNMIStub
from gnmi_pb2 import SubscribeRequest, Subscription, Path

channel = grpc.secure_channel('switch-01:6030',
    grpc.ssl_channel_credentials())
stub = gNMIStub(channel)

subscribe_request = SubscribeRequest(
    subscribe=SubscriptionList(
        subscription=[
            Subscription(
                path=Path(elem=[PathElem(name="interfaces"),
                               PathElem(name="interface",
                                       key={"name": "Ethernet1"}),
                               PathElem(name="state"),
                               PathElem(name="counters")])
            )
        ],
        mode=SubscriptionList.STREAM,
        encoding=SubscriptionList.JSON_IETF
    )
)

for response in stub.Subscribe(iter([subscribe_request])):
    # Process each telemetry update as it arrives
    process_telemetry(response)
```

## Authentication and Security

Every API integration must handle authentication correctly. Common patterns:

**Token-based (Bearer token):** `Authorization: Bearer <token>` in HTTP headers. Most REST APIs use this.
**OAuth 2.0:** For user-delegated access and service-to-service auth. Common in cloud provider APIs.
**Mutual TLS (mTLS):** Both client and server present certificates. Used for service-to-service auth in microservice architectures and gNMI.
**API Keys:** Simple but less secure. Always stored in environment variables or secrets managers — never hardcoded.

In modern cloud environments, internal service credentials are provided via IAM roles to serverless functions — the function never handles static credentials at all. The SDK picks up the credentials automatically from the execution role. This is the right model for production automation: no credentials in code, no credentials on disk, identity managed by the infrastructure.

## Putting It Together: Multi-System Automation

Real production automation orchestrates across multiple APIs in sequence. A DC device provisioning workflow might:

1. Query NetBox REST API → get device parameters (IP, role, rack location)
2. Query internal IPAM API → allocate loopback IPs for the device
3. Generate configuration using Jinja2 templates with the retrieved data
4. Push configuration via NETCONF → structured, validated configuration delivery
5. Write POST to NetBox REST API → record the allocated IPs and device state
6. Call internal monitoring API → register the device in the monitoring system
7. Put message on SQS queue → trigger downstream deployment steps

Each of these is a separate API call, potentially to different systems with different authentication models and error behaviors. Production automation wraps each step in retry logic, handles partial failures gracefully, logs every action for audit, and surfaces meaningful error messages when things go wrong.

This is the architecture behind production deployment orchestration at hyperscale: not a script that does one thing, but an orchestration layer that coordinates multiple systems through their APIs to complete a multi-step deployment safely and repeatably.
