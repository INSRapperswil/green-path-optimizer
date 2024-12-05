# green-path-optimizer

An application that suggests changes to the forwarding paths of a network to improve energy efficiency developed at [RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/announcing-the-green-tech-hackathon/).

## Introduction

Over the past year, my colleagues and I have delved into the field of sustainable networking, focusing on the critical challenge of improving energy efficiency in computer networks.
Our initial research revealed a significant gap: optimizing network energy efficiency through traffic engineering methods is extremely difficult due to the **lack of visibility into the energy efficiency of network paths.**

This realization led us to focus on enhancing visibility into the energy efficiency of network paths and nodes.
After several months of research, we published a paper titled *"Towards Sustainable Networking: Unveiling Energy Efficiency Through Hop and Path Efficiency Indicators in Computer Networks"*, which was presented at IEEE Netsoft 2024 and is now available on [IEEE Xplore](https://ieeexplore.ieee.org/document/10588907).

Our proof-of-concept (PoC) implementation already includes several key capabilities:
- The collection of network telemetry data embedded in packet metadata using the [IOAM Aggregation Trace Option](https://datatracker.ietf.org/doc/html/draft-cxx-ippm-ioamaggr-02)
- Standardized export of this data to an [IPFIX](https://www.rfc-editor.org/rfc/rfc7011) collector
- Descriptive Grafana dashboards that visualize the collected data

While this provides a strong foundation, our next goal is to act on the collected data by proposing actual improvements to network configuration. This includes the development of the *green-path-optimizer* application and running simulations across different topologies to verify the applicability in various use cases.

### Overview

![PoC Overview](assets/figures/proof_of_concept_overview.svg)

#### Efficiency Indication

![PoC Overview](assets/figures/path_metrics_visualization.svg)

#### Network Telemetry (IOAM)

#### Export Mechanism (IPFIX)

#### Dashboard

### Related Work

- **IEEE Publication:** [Towards Sustainable Networking: Unveiling Energy Efficiency Through Hop and Path Efficiency Indicators in Computer Networks](https://ieeexplore.ieee.org/document/10588907)
- **Internet - Draft:** [Aggregation Trace Option for In-situ Operations, Administration, and Maintenance IOAM](https://datatracker.ietf.org/doc/html/draft-cxx-ippm-ioamaggr-02)
- **Internet - Draft:** [Challenges and Opportunities in Management for Green Networking](https://datatracker.ietf.org/doc/draft-irtf-nmrg-green-ps/03/)
- **RFC - Proposed Standard:** [Data Fields for In Situ Operations, Administration, and Maintenance (IOAM)](https://datatracker.ietf.org/doc/html/rfc9197)

## Project Objectives During the Hackathon

The primary goal is to demonstrate that energy-efficient traffic routing can be achieved using our collected data, while also identifying any gaps in the current dataset that would be crucial for further optimizations.

This includes the following work items:

- Analysis of given raw data in InfluxDB  
- **Development of green-path-optimizer application which suggests path updates to improve efficiency**
- **Integration of the configuration-update-utility to acutally deploy the improvements in the PoC network environment**
- In case there is time:
  - Parameter evaluation
  - Interpretation of improvements and what is needed to apply it in practice
  - Validation of the suggested improvements also regarding throughput / bottlenecks etc.
  - **Conception of efficiency discovery mechanism of all paths of a given length in an arbitrary topology.**
