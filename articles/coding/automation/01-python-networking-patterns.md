# Python Networking Patterns for Network Engineers

This article documents the Python patterns that appear repeatedly in real network automation work — not toy examples, but patterns worth knowing because they solve recurring problems in production. These are the code structures you should be able to write and explain in a technical interview.

## Pattern 1: Concurrent Device Access

**The problem:** You need to collect data from 200 switches. Sequential SSH connections take 5 minutes. Parallel connections take 30 seconds.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler
import logging

def get_bgp_summary(host: str, username: str, password: str) -> dict:
    """Returns BGP summary data for a single device."""
    device = {
        "device_type": "arista_eos",
        "host": host,
        "username": username,
        "password": password,
        "timeout": 30,
    }
    try:
        with ConnectHandler(**device) as conn:
            output = conn.send_command("show bgp summary", use_textfsm=True)
            return {"host": host, "data": output, "error": None}
    except Exception as e:
        logging.error(f"Failed to connect to {host}: {e}")
        return {"host": host, "data": None, "error": str(e)}

def collect_bgp_from_fleet(hosts: list[str], username: str, password: str, max_workers: int = 20) -> list[dict]:
    """Collects BGP summary from all hosts in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(get_bgp_summary, host, username, password): host
            for host in hosts
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result["error"]:
                logging.warning(f"Error on {result['host']}: {result['error']}")
    return results

# Usage
hosts = ["spine-01", "spine-02", "leaf-01", "leaf-02"]
results = collect_bgp_from_fleet(hosts, username="admin", password="secret")
successful = [r for r in results if r["error"] is None]
failed = [r for r in results if r["error"] is not None]
print(f"Collected from {len(successful)}/{len(hosts)} devices")
```

**Key points:**
- `ThreadPoolExecutor` is appropriate here — Netmiko connections are I/O-bound (waiting for SSH responses), so threading works despite Python's GIL
- Each device call is wrapped in try/except — a failure on one device does not abort the entire run
- Results track both successes and failures — never silently drop errors
- `max_workers=20` is a reasonable starting point; too high and you hit SSH rate limits or overwhelm devices

## Pattern 2: Configuration Validation Before Push

**The problem:** Before pushing config to a device, validate it against expected values.

```python
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class BGPNeighborState:
    neighbor: str
    remote_as: int
    state: str
    prefixes_received: int

def parse_bgp_neighbors(raw_output: str) -> list[BGPNeighborState]:
    """Parse 'show bgp summary' text output into structured objects."""
    neighbors = []
    # Skip header lines
    lines = raw_output.strip().split('\n')
    for line in lines:
        # Match lines like: 192.168.1.1    4 65000    100    100    0    0    1d Estab  1
        match = re.match(
            r'(\d+\.\d+\.\d+\.\d+)\s+\d+\s+(\d+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\w+)\s+(\d+)',
            line.strip()
        )
        if match:
            neighbors.append(BGPNeighborState(
                neighbor=match.group(1),
                remote_as=int(match.group(2)),
                state=match.group(3),
                prefixes_received=int(match.group(4)),
            ))
    return neighbors

def validate_bgp_state(neighbors: list[BGPNeighborState], expected_count: int) -> tuple[bool, list[str]]:
    """Validate BGP state against expectations. Returns (is_valid, list_of_issues)."""
    issues = []

    # Check all sessions are established
    down_neighbors = [n for n in neighbors if n.state != "Estab"]
    if down_neighbors:
        issues.append(f"BGP sessions not established: {[n.neighbor for n in down_neighbors]}")

    # Check expected peer count
    if len(neighbors) != expected_count:
        issues.append(f"Expected {expected_count} BGP peers, found {len(neighbors)}")

    # Check no peer has zero prefixes received (leaf should always have routes from spines)
    zero_prefix_peers = [n for n in neighbors if n.prefixes_received == 0]
    if zero_prefix_peers:
        issues.append(f"BGP peers with no prefixes: {[n.neighbor for n in zero_prefix_peers]}")

    return len(issues) == 0, issues
```

**Key points:**
- Parse unstructured output into typed data structures before validating — makes the validation logic clean
- Return structured results from validation, not just pass/fail — the caller needs to know *what* failed
- This pattern is the foundation of automated health checks post-deployment

## Pattern 3: Idempotent Configuration Push

**The problem:** Push a configuration change only if the current state differs from the desired state.

```python
def ensure_bgp_community(conn, prefix: str, community: str) -> bool:
    """
    Ensure a BGP route-map sets a community on a given prefix.
    Returns True if a change was made, False if already correct.
    """
    # Check current state
    current = conn.send_command(f"show route-map SET-COMMUNITY permit 10", use_textfsm=True)
    
    # Determine if change is needed
    community_already_set = any(
        entry.get("match_prefix") == prefix and community in entry.get("set_community", "")
        for entry in (current if isinstance(current, list) else [])
    )
    
    if community_already_set:
        return False  # No change needed
    
    # Apply the change
    config_commands = [
        f"route-map SET-COMMUNITY permit 10",
        f" match ip address prefix-list MATCH-{prefix.replace('/', '-')}",
        f" set community {community}",
    ]
    conn.send_config_set(config_commands)
    return True  # Change was made
```

**Key points:**
- Check before changing — idempotent operations are safe to re-run
- Return whether a change was made — callers can track what actually changed vs. what was already correct
- This pattern prevents "ghost changes" in change audits where re-running automation looks like it modified devices it did not actually change

## Pattern 4: Source-of-Truth-Driven Configuration Generation

**The problem:** Generate device-specific configurations from structured data.

```python
from jinja2 import Environment, FileSystemLoader
import yaml

def generate_leaf_config(device_data: dict, template_dir: str) -> str:
    """Generate a complete leaf switch configuration from structured data."""
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("leaf.j2")
    return template.render(**device_data)

# Device data comes from source of truth (CMDB/IPAM)
device = {
    "hostname": "leaf-01-dc1",
    "loopback_ip": "10.0.0.1",
    "bgp_asn": 65001,
    "spine_neighbors": [
        {"ip": "10.1.0.1", "remote_as": 65000, "description": "spine-01"},
        {"ip": "10.1.0.3", "remote_as": 65000, "description": "spine-02"},
    ],
    "vlans": [
        {"id": 100, "name": "tenant-a-web", "vni": 10100},
        {"id": 200, "name": "tenant-b-app", "vni": 10200},
    ],
}

config = generate_leaf_config(device, template_dir="./templates")
```

**The Jinja2 template (`templates/leaf.j2`):**
```jinja2
hostname {{ hostname }}
!
interface Loopback0
   ip address {{ loopback_ip }}/32
!
router bgp {{ bgp_asn }}
   router-id {{ loopback_ip }}
   {% for neighbor in spine_neighbors %}
   neighbor {{ neighbor.ip }} remote-as {{ neighbor.remote_as }}
   neighbor {{ neighbor.ip }} description {{ neighbor.description }}
   {% endfor %}
   !
   address-family ipv4
      {% for neighbor in spine_neighbors %}
      neighbor {{ neighbor.ip }} activate
      {% endfor %}
!
{% for vlan in vlans %}
vlan {{ vlan.id }}
   name {{ vlan.name }}
vxlan vni {{ vlan.vni }} vlan {{ vlan.id }}
{% endfor %}
```

## Pattern 5: Structured Logging for Audit Trails

**The problem:** Production automation must be auditable — what ran, when, on which device, with what result.

```python
import logging
import json
from datetime import datetime, timezone

def setup_audit_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("network.audit")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(message)s'))  # Raw JSON
    logger.addHandler(handler)
    return logger

def log_device_action(logger, device: str, action: str, result: str, details: dict = None):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "device": device,
        "action": action,
        "result": result,  # "success" | "failure" | "no_change"
        "details": details or {},
    }
    logger.info(json.dumps(record))

# Usage
audit = setup_audit_logger("/var/log/netauto/audit.json")
log_device_action(audit, "leaf-01", "bgp_community_push", "success",
                  {"prefix": "10.1.0.0/24", "community": "65000:100"})
log_device_action(audit, "leaf-02", "bgp_community_push", "failure",
                  {"error": "SSH connection timeout"})
```

**Key points:**
- JSON-structured logs are machine-parseable — you can query them with `jq`, import into logging systems, and build dashboards on them
- Always include timestamp in UTC ISO format
- `result` as an enum-like field ("success" / "failure" / "no_change") makes it easy to filter for failures in bulk runs
