# Ansible for Network Automation

Ansible occupies a specific and important niche in network automation: it is the right tool when you need to manage configuration across many devices using a declarative, human-readable format, without requiring a custom application. Where Python automation requires writing code, Ansible lets you express what you want — and handles the how.

Understanding when Ansible is the right choice, and how it works for network devices specifically (which differ from the server automation Ansible was originally built for), is essential for any senior network engineer doing automation.

## What Ansible Does

Ansible operates on a simple model:

- **Inventory:** A list of devices to manage, grouped by role or location.
- **Playbook:** A YAML file describing what to do to which devices.
- **Modules:** The actual operations — push a configuration, run a command, retrieve state, configure a BGP neighbor.
- **Templates (Jinja2):** Generate device-specific configurations from variables.

A playbook is declarative: you describe the desired state, not the steps to get there. Ansible figures out the steps, connects to the devices, applies the operations, and reports results.

## How Ansible Connects to Network Devices

This is the point that confuses engineers coming from server automation. Ansible normally connects to Linux servers over SSH and runs Python on the remote host. Network devices do not have Python interpreters accessible via SSH (and many do not run Linux at all in the user-accessible shell).

For network devices, Ansible uses two different connection methods:

**`network_cli`:** Connects via SSH, sends CLI commands, and parses the output. This is the Ansible equivalent of Netmiko — it handles the platform-specific SSH quirks, prompt detection, and pagination. The device does not need to support anything beyond SSH CLI access.

**`netconf`:** Connects via the NETCONF protocol, sends XML-encoded operations, and receives structured XML responses. This is the structured-API approach — no text parsing, consistent schema. Requires the device to have NETCONF enabled (most modern platforms support it).

**`httpapi`:** Uses the device's REST API (if available). Arista's eAPI, for example, is a REST/JSON API that Ansible can use via `httpapi`. Returns structured JSON instead of text.

The connection method is specified per inventory group, so you can have some devices using `network_cli` and others using `netconf` in the same playbook run.

## A Real Network Playbook

```yaml
---
- name: Configure BGP neighbors on leaf switches
  hosts: leaf_switches
  gather_facts: no
  connection: network_cli

  vars:
    bgp_asn: 65001
    spine_neighbors:
      - ip: 10.0.0.1
        remote_as: 65000
      - ip: 10.0.0.3
        remote_as: 65000

  tasks:
    - name: Configure BGP process
      arista.eos.eos_bgp_global:
        config:
          as_number: "{{ bgp_asn }}"
          router_id: "{{ ansible_host }}"
        state: merged

    - name: Configure spine neighbors
      arista.eos.eos_bgp_neighbors:
        config:
          - neighbor_address: "{{ item.ip }}"
            remote_as: "{{ item.remote_as }}"
            description: "spine-neighbor"
            send_community: true
        state: merged
      loop: "{{ spine_neighbors }}"
```

Several things to notice:

**`state: merged`** is idempotent — it applies the configuration if it is not already present, does nothing if it is. Run it ten times; the result is the same. This is the declarative model.

**`gather_facts: no`** is required for network devices — the default Ansible fact-gathering connects to the host and runs setup commands intended for Linux servers, which fails on network devices.

**`loop`** applies the same task to multiple items — here, configuring multiple BGP neighbors without duplicating the task.

## Jinja2 Templates for Configuration Generation

For complex configurations where the structured modules are insufficient or where you need to generate a complete device configuration from scratch, Jinja2 templates are the tool.

A template (`leaf_config.j2`):
```
hostname {{ inventory_hostname }}
!
router bgp {{ bgp_asn }}
  router-id {{ loopback_ip }}
  {% for neighbor in spine_neighbors %}
  neighbor {{ neighbor.ip }} remote-as {{ neighbor.remote_as }}
  neighbor {{ neighbor.ip }} description {{ neighbor.description }}
  {% endfor %}
```

Used in a playbook:
```yaml
- name: Generate and push configuration
  arista.eos.eos_config:
    src: leaf_config.j2
```

Ansible renders the template with the variables for each device in the inventory, then pushes the resulting configuration. Every leaf gets its own rendered configuration, but all from the same template — guaranteed consistency.

## Inventory: The Foundation of Scale

The inventory file defines what Ansible manages and how devices are grouped. A well-structured inventory is what makes Ansible scale from managing ten devices to managing ten thousand.

```ini
[spine_switches]
spine-01 ansible_host=10.1.0.1
spine-02 ansible_host=10.1.0.2

[leaf_switches]
leaf-01 ansible_host=10.1.1.1
leaf-02 ansible_host=10.1.1.2

[dc_fabric:children]
spine_switches
leaf_switches

[dc_fabric:vars]
ansible_user=admin
ansible_network_os=arista.eos.eos
ansible_connection=network_cli
```

At hyperscale, static inventory files are replaced by **dynamic inventory** — a script or plugin that queries a CMDB, IPAM system, or cloud provider API and returns the current inventory at runtime. When devices are added or removed from the source of truth, the inventory automatically reflects that change. No manual inventory file maintenance.

## Roles: Reusable Automation Components

For recurring automation patterns — "configure BGP on a leaf switch" or "apply security hardening baseline" — Ansible **roles** package the tasks, templates, and variables into a reusable component.

```
roles/
  leaf_bgp/
    tasks/
      main.yml     # The tasks to run
    templates/
      bgp.j2       # Jinja2 template
    defaults/
      main.yml     # Default variable values
    vars/
      main.yml     # Role-specific variables
```

A playbook then applies the role: `roles: [leaf_bgp]`. Any playbook in any project can reuse the role. When the BGP configuration pattern changes, you update the role in one place and every playbook that uses it picks up the change.

## Ansible vs Python: When to Use Which

| Use Ansible when | Use Python when |
|---|---|
| Declaring desired state across many devices | Complex logic, conditionals, multi-system orchestration |
| Team members who are not developers will run it | Custom data processing, API integration |
| Audit trail and run logs matter | Event-driven or real-time automation |
| Configuration templating and push | Fine-grained error handling and retry logic |
| Reusable roles across projects | One-time data collection/analysis scripts |

In practice, the two complement each other. At AWS, Ansible managed configuration templates and deployment tasks for standardized operations, while Python Lambda functions handled the orchestration logic — deciding what to trigger when, coordinating across systems, and handling complex sequencing that Ansible's linear task model cannot express.
