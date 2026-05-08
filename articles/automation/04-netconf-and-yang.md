# NETCONF and YANG: Model-Driven Network Management

Every generation of network automation has been limited by the same problem: network device configuration and state are expressed as human-readable CLI text that was designed for engineers to read, not for software to parse. When you automate against a CLI, you are always one software upgrade away from a broken parser — the vendor changed a column header, added a new line, or reformatted a table, and your regular expression breaks.

NETCONF and YANG solve this problem at its root by separating what the data means (the data model, defined in YANG) from how it is transported (the protocol, defined in NETCONF). The result is structured, machine-readable configuration and state that works consistently across software versions and, with OpenConfig, across vendors.

## YANG: Defining the Data Model

**YANG (Yet Another Next Generation)** is a data modeling language — RFC 6020. It defines the structure, types, constraints, and semantics of configuration and state data for network devices.

Think of a YANG model as a schema for network data. Just as a database schema defines what tables exist, what columns they have, and what types those columns hold, a YANG model defines what configuration exists on a device, what format it takes, and what constraints apply.

A simplified YANG model for a BGP neighbor:

```yang
module bgp {
  container bgp {
    container neighbors {
      list neighbor {
        key "neighbor-address";
        leaf neighbor-address {
          type inet:ip-address;
        }
        leaf remote-as {
          type uint32;
        }
        leaf description {
          type string;
        }
        leaf enabled {
          type boolean;
          default true;
        }
      }
    }
  }
}
```

This model says: there is a `bgp` container, inside which is a `neighbors` container, containing a list of `neighbor` entries keyed by `neighbor-address`. Each neighbor has a `remote-as` (uint32), a `description` (string), and an `enabled` flag (boolean, defaulting to true).

With this model defined, any tool that speaks NETCONF can read and write BGP neighbor configuration in a structured, typed, validated format — regardless of what platform the device is running.

## NETCONF: The Transport Protocol

**NETCONF (Network Configuration Protocol)** — RFC 6241 — is the protocol that uses YANG models to read and write device configuration and state.

NETCONF operates over SSH (port 830) and uses XML as its encoding. It defines a set of operations:

- **`<get-config>`**: Retrieve configuration from a specific datastore (running, candidate, startup)
- **`<edit-config>`**: Modify configuration in a datastore
- **`<get>`**: Retrieve both configuration and operational state
- **`<lock>` / `<unlock>`**: Lock a datastore to prevent concurrent modifications
- **`<commit>`**: Apply changes from the candidate datastore to the running datastore
- **`<validate>`**: Validate a configuration without applying it

The candidate datastore model is particularly important: changes are applied to the candidate (a copy of the running config), validated, and then committed atomically. If validation fails, the running configuration is never touched. This is fundamentally safer than pushing incremental CLI changes where a partial failure leaves the device in an inconsistent state.

A NETCONF `<get-config>` request in Python using ncclient:

```python
from ncclient import manager
from ncclient.xml_ import to_ele

filter_xml = """
<filter>
  <bgp xmlns="urn:ietf:params:xml:ns:yang:ietf-bgp">
    <neighbors/>
  </bgp>
</filter>
"""

with manager.connect(
    host='192.168.1.10',
    port=830,
    username='admin',
    password='secret',
    hostkey_verify=False
) as m:
    result = m.get_config(source='running', filter=to_ele(filter_xml))
    print(result.xml)
```

The response is structured XML conforming to the YANG model — parseable with `lxml` or `xmltodict`, not scraped from terminal output.

## OpenConfig: Vendor-Neutral YANG Models

Vendors ship their own YANG models (Arista's models, Cisco's models, Juniper's models), and they are all different. Writing automation against one vendor's YANG model means rewriting it for another vendor.

**OpenConfig** is a consortium of network operators — Google, Microsoft, AT&T, and others — who defined a set of vendor-neutral YANG models. An OpenConfig BGP model looks the same on Arista, Cisco IOS-XR, and Juniper JunOS. The same automation code, written against OpenConfig models, works on any platform that supports OpenConfig.

OpenConfig models currently cover BGP, OSPF, IS-IS, interfaces, MPLS-TE, QoS, VLAN, and more. Not every platform implements every OpenConfig model fully, and vendor-specific features (things OpenConfig does not model) still require vendor-native YANG. But for standard protocol configuration, OpenConfig is the path to vendor-agnostic automation.

OpenConfig is combined with **gNMI (gRPC Network Management Interface)** as an alternative transport to NETCONF. gNMI uses Protocol Buffers (protobuf) instead of XML — smaller, faster serialization — and gRPC for transport. gNMI is increasingly common for streaming telemetry (subscribe to state and receive updates as they occur) where NETCONF's request-response model is insufficient.

## YANG and NETCONF in Practice

At hyperscale, NETCONF/YANG is most valuable in two scenarios:

**Configuration generation and validation.** Before pushing any configuration change, validate it against the YANG model. Tools like `pyang` can validate YANG instances and detect schema violations before the configuration ever touches a device. Batfish (a network analysis tool) can analyze configurations modeled in YANG and detect policy violations, BGP route leaks, or reachability problems in simulation.

**Source of truth alignment.** When your source of truth (the database of intended network state) is modeled in YANG, you can directly compare the intended state (YANG model instance from the database) against the actual state (YANG model instance retrieved via NETCONF). The diff is structured, unambiguous, and actionable. This is configuration drift detection at scale — running continuously, not as a periodic audit.

## gRPC and gNMI for Streaming Telemetry

The `<get>` operation in NETCONF is a pull model: you request state, the device responds. For monitoring at scale, you need a **push model**: the device streams state continuously to your telemetry collector.

gNMI defines a `Subscribe` RPC that allows a collector to subscribe to specific paths in the YANG model and receive updates whenever the values change. A subscription to `/interfaces/interface/state/counters/in-octets` delivers interface traffic counters continuously — no polling, no periodic SNMP walks, just a stream of structured updates.

At LinkedIn's scale — monitoring thousands of interfaces across hundreds of switches — streaming telemetry via gNMI replaces SNMP polling with a lower-overhead, lower-latency, structured alternative. The data model is the same YANG model used for configuration, making correlation between configuration state and operational state straightforward.

This is the convergence that YANG and NETCONF represent: a single data model that describes configuration, operational state, and the telemetry stream — giving automation, operations, and monitoring a shared, consistent language for talking about network state.
