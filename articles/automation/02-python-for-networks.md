# Python for Network Engineers

Python became the dominant language for network automation not because network engineers chose it deliberately, but because it chose them. The language's readability, its vast ecosystem of libraries, and the low barrier to entry for engineers who learned programming on the side of a primary networking career made it the natural fit. Today, "network automation" and "Python" are nearly synonymous in the industry.

But there is a difference between writing Python scripts and writing production-quality network automation. This article covers the libraries, patterns, and practices that matter in a hyperscale environment.

## The Core Libraries

**Netmiko** is the most widely used library for SSH-based device access. It abstracts the connection and command-sending to dozens of different network device platforms — Cisco IOS, NX-OS, Arista EOS, Juniper JunOS, and many more — behind a consistent API.

```python
from netmiko import ConnectHandler

device = {
    'device_type': 'arista_eos',
    'host': '192.168.1.10',
    'username': 'admin',
    'password': 'secret',
}

with ConnectHandler(**device) as conn:
    output = conn.send_command('show ip bgp summary')
    print(output)
```

The key advantage: Netmiko handles the SSH session lifecycle, the platform-specific prompt detection, and the timing issues of interactive CLI sessions. You write device-agnostic code; Netmiko handles the platform differences.

The key limitation: you are still dealing with unstructured text output. `show ip bgp summary` returns a wall of text that you must parse with string operations or regular expressions. This is fragile. It is fine for quick scripts; it is not the right foundation for production automation.

**NAPALM (Network Automation and Programmability Abstraction Layer with Multivendor support)** goes further. It provides structured output for common network operations across multiple platforms.

```python
from napalm import get_network_driver

driver = get_network_driver('eos')
device = driver('192.168.1.10', 'admin', 'secret')
device.open()

bgp_neighbors = device.get_bgp_neighbors()
# Returns a structured dictionary, not raw text
for neighbor, data in bgp_neighbors['global']['peers'].items():
    print(f"{neighbor}: {data['description']} - {data['is_up']}")

device.close()
```

NAPALM's `get_bgp_neighbors()` returns a Python dictionary with a consistent schema regardless of whether the device is Arista or Cisco. This is structured automation — your code works across vendors without parsing platform-specific text.

NAPALM also has a crucial feature: **configuration comparison and atomic deployment**. You can load a desired configuration, compare it to the running configuration to see what would change, and commit or discard. This candidate configuration model is much safer than pushing incremental config changes directly.

**Paramiko** is the underlying SSH library that Netmiko is built on. You rarely need to use it directly for network automation, but understanding it matters — when Netmiko does not support a device type or when you need fine-grained control over SSH sessions, Paramiko is what you reach for.

**ncclient** is the Python library for NETCONF. When devices support NETCONF (most modern platforms do), ncclient gives you structured XML-based configuration access:

```python
from ncclient import manager

with manager.connect(host='192.168.1.10', port=830,
                     username='admin', password='secret',
                     hostkey_verify=False) as m:
    config = m.get_config(source='running')
    print(config)
```

NETCONF with ncclient returns structured XML that maps to YANG models — no text parsing, no fragility. This is the right approach for production automation systems.

## Patterns That Matter at Scale

**Concurrency for bulk operations.** When you need to connect to hundreds of devices and run commands, doing it sequentially is too slow. Python's `concurrent.futures.ThreadPoolExecutor` is the practical tool for this — Netmiko connections are I/O-bound (waiting for SSH responses), so threading works well even in Python's GIL model.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_device(host):
    with ConnectHandler(device_type='arista_eos', host=host,
                        username='admin', password='secret') as conn:
        return host, conn.send_command('show version')

hosts = ['192.168.1.10', '192.168.1.11', '192.168.1.12']

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(check_device, h): h for h in hosts}
    for future in as_completed(futures):
        host, output = future.result()
        print(f"{host}: done")
```

This pattern — submitting all tasks to a thread pool and processing results as they complete — is how automation runs checks and configuration pushes across hundreds of devices at hyperscale. A sequential loop that takes 5 minutes per device becomes a parallel operation that takes 30 seconds.

**Idempotency.** Production automation should be safe to run multiple times. If you run a script to configure a BGP neighbor and the BGP neighbor is already correctly configured, the script should do nothing — not error, not re-apply the configuration, not create a duplicate. Design every automation operation to first check the current state before applying changes.

**Error handling and logging.** At scale, some devices will fail to respond, some will have authentication errors, some will be in maintenance mode. Automation that crashes on the first error leaves you with a partial deployment. Wrap every device operation in exception handling, log the error with the device identity, and continue to the next device. At the end, report which devices succeeded and which failed — never silently swallow errors.

**Source of truth integration.** The most powerful automation is driven by a source of truth — a database or structured data store that contains the intended state of the network. At hyperscale, the source of truth for device roles, rack assignments, IP addresses, and network topology drives configuration generation. Changes to the source of truth automatically trigger re-generation and deployment. The configuration on devices is always derived from the source of truth, never manually edited in isolation.

That is the difference between writing Python scripts and building production automation: the latter is a system with state, safety checks, observability, and defined failure modes.
