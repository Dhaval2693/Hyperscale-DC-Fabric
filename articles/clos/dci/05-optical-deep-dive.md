# Optical and Layer 1 Deep Dive

Most network engineers stop at Layer 3. For hyperscaler backbone, DCI, and ML training fabric roles, Layer 1 knowledge matters — because that's where capacity, latency, and cost actually live for inter-DC and high-bandwidth links.

This article covers DWDM, coherent optics, transceivers, and the L1 concepts you'll be asked about.

## Why L1 Matters

For DC fabric (within a building), L1 is mostly "plug in a 100G/400G transceiver and it works." For backbone, DCI, and long-haul, L1 is where:

- Capacity is determined (a single fiber can carry 80+ wavelengths)
- Cost is determined (port-hour fees, dark fiber leases)
- Latency is determined (speed of light + amplifier delays)
- Failure modes you've never seen in DC networks emerge (chromatic dispersion, optical signal-to-noise ratio degradation)

## DWDM Basics

**DWDM (Dense Wavelength Division Multiplexing)** lets you carry multiple optical channels on a single fiber, each at a different wavelength of light.

- Standard ITU grid: channels spaced 50 GHz or 100 GHz apart in the C-band (~1530-1565 nm)
- 80-96 channels per fiber typical
- Each channel can carry 100 Gbps, 200 Gbps, 400 Gbps, or higher with modern coherent optics
- **Total fiber capacity:** 80 channels × 400 Gbps = 32 Tbps on a single fiber pair

**The economic implication:** dark fiber is expensive but the per-bit cost drops dramatically as you light more channels. Hyperscalers light tens of channels per fiber pair; service providers may light hundreds.

## Coherent Optics

Modern long-haul transceivers use **coherent detection** — they measure both the amplitude AND phase of the light signal, allowing much higher data rates over much longer distances.

Pre-coherent (NRZ): ~10 Gbps per wavelength, ~80km without amplification.
Coherent (modern): 100-800 Gbps per wavelength, hundreds of km without regeneration.

Coherent uses **modulation formats** like QPSK, 16-QAM, 64-QAM:
- More bits per symbol → higher data rate
- But also more sensitive to noise (lower OSNR tolerance)
- Tradeoff: high-bit-rate modulations require cleaner fiber or shorter distances

**Common coherent line rates:**
- 100G coherent: QPSK, very robust, long reach
- 200G coherent: QPSK or 8-QAM
- 400G coherent: 16-QAM
- 800G coherent: 64-QAM (short reach only)

## Optical Signal-to-Noise Ratio (OSNR)

OSNR is the L1 equivalent of "is my link clean enough?" — the ratio of signal power to noise power in the optical channel.

- Each fiber span adds attenuation (loss); amplifiers (EDFAs) add gain but also noise
- After many spans, OSNR degrades to the point where the receiver can't decode
- Higher-order modulations (16-QAM, 64-QAM) need higher OSNR than QPSK

**The operational metric:** monitor OSNR continuously. Falling OSNR predicts errors before they happen.

## Optical Amplifiers (EDFAs)

Long fiber runs need amplification. **EDFAs (Erbium-Doped Fiber Amplifiers)** amplify all DWDM channels in the C-band simultaneously without converting to electrical.

- Typical spacing: every 60-100 km on a long-haul route
- Each EDFA adds noise (degrading OSNR with each span)
- More amplifiers = more total noise = lower achievable bit rates

## ROADMs (Reconfigurable Optical Add-Drop Multiplexers)

ROADMs let you add/drop specific wavelengths at intermediate sites without converting the whole signal to electrical. Critical for backbone networks where you want to drop some channels at a city while others continue.

- **Colorless** — any port can serve any wavelength
- **Directionless** — any port can route to any direction
- **Contentionless** — any port can be added/dropped without blocking
- **CDC** ROADM = all three. Modern standard.

This matters because reconfiguration without electrical regeneration is much cheaper and faster.

## Transceiver Form Factors

For DC fabric and short reach:

| Form factor | Typical speeds | Reach |
|---|---|---|
| **SFP** | 1G, 10G | Short |
| **SFP+** | 10G | Short |
| **SFP28** | 25G | Short |
| **QSFP+** | 40G | Short |
| **QSFP28** | 100G | Short to medium |
| **QSFP56** | 200G | Short |
| **QSFP-DD** | 400G, 800G | Short to medium |
| **OSFP** | 400G, 800G, 1.6T | Short to medium |

For long-haul / coherent:
- **CFP / CFP2 / CFP4** — older coherent
- **QSFP-DD ZR / ZR+** — pluggable coherent, 400G over 80-120km with no external transponder

**The "pluggable coherent" revolution (ZR/ZR+):** modern coherent optics fit in a QSFP-DD slot. This means a router can talk directly to DWDM without a separate transponder shelf. Massively simplifies backbone architecture.

## LAGs (Link Aggregation Groups)

When a single link's capacity isn't enough, bundle multiple links into a LAG.

- LACP (802.3ad) is the standard protocol
- Hash function distributes flows across member links (typically per-flow, not per-packet, to avoid reordering)
- **The trap:** elephant flows can bottleneck on a single LAG member even when the bundle has spare capacity (the "hash polarization" problem)

For ML training, where flows are large and few, LAG hash limitations matter — sometimes single-flow throughput is the bottleneck, not aggregate bandwidth.

## How to Talk About It

> "L1 matters at the backbone — DWDM lets you carry 80+ channels on one fiber pair, coherent optics push each channel to 400G+ over long reach. Pluggable coherent (ZR/ZR+) is changing backbone architecture by eliminating separate transponder shelves. OSNR is the metric to watch — degraded OSNR predicts errors. ROADMs (specifically CDC ROADMs) let you flexibly add/drop wavelengths without electrical regeneration."

For a DCI design question:
> "For metro DCI under 80km, I'd use ZR pluggables in routers, single fiber pair with DWDM if I need multiple channels. For long-haul, coherent transponders with EDFA amplification at 80km intervals, OSNR-monitored. Capacity is determined by channel count × per-channel rate, both controllable independently. Cost is dominated by the fiber lease and the optical hardware, not the IP layer."

## What to Memorize

| Concept | Key idea |
|---|---|
| **DWDM** | Multiple wavelengths on one fiber (80+ channels) |
| **Coherent optics** | High bit rates per wavelength using amplitude + phase |
| **OSNR** | Signal-to-noise ratio; key operational metric |
| **EDFAs** | Optical amplifiers, every 60-100 km on long-haul |
| **ROADMs** | Add/drop wavelengths at intermediate sites |
| **ZR / ZR+** | Pluggable coherent — router talks DWDM directly |
| **LAG / LACP** | Bundle links; per-flow hash, watch elephants |
| **Form factors** | QSFP28 (100G), QSFP-DD (400G), OSFP (800G) |

## Connection to Other Topics

- **Builds on:** [01-what-is-dci.md](01-what-is-dci.md), [02-dci-transport-options.md](02-dci-transport-options.md)
- **Bridges to:** capacity planning, cost modeling (optical leases), failure scenarios
- **Relevant for:** backbone roles, DCI design, AI training fabric L1 capacity

## Anthropic-Specific Framing

The JD calls out "L1/optical basics (DWDM, coherent, LAGs)" explicitly. Be ready to discuss:

1. How a backbone capacity decision works (channels × per-channel rate × number of fiber pairs)
2. When to use ZR pluggable vs traditional transponder shelf (cost, operational complexity)
3. How OSNR monitoring fits into telemetry (gauge metric, alerting before failure)
4. Why LAG hash polarization matters for ML training (single elephant flow can starve a member link)

You don't need to be an optical engineer. You need to know enough to participate in architecture conversations with the optical team and reason about capacity and cost.
