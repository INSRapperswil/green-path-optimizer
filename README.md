# green-path-optimizer

An application that suggests changes to the forwarding paths of a network to improve energy efficiency developed at [RIPE NCC Green Tech Hackathon](https://labs.ripe.net/author/becha/announcing-the-green-tech-hackathon/).

## Overall Project Achievements

### Before Hackathon

- Dynamic Grafana Dashboards to allow simulations on arbitrary topologies
- Skeleton of green-path-optimizer application
  - Retrieve data from InfluxDB
- Implementation of flooding mechanism for probing packets
  - Loops? / Spanning Tree

### During Hackathon
- Analyse given raw data in InfluxDB
- **Write green-path-optimizer application which suggests path updates to improve efficiency**
- **Connect green-path-optimizer with the configuration-update-utility to acutally deploy the improvements in the PoC**
- In case there is time:
  - Parameter evaluation (Maximum Power Draw)
  - Interpretation of improvements
  - Validation of the suggested improvements also regarding throughput / bottlenecks etc.

### After Hackathon

- Review of fundamental concepts
- Detect data shortages to do the optimizations
- Implementation of a validation component which checks if it acutally makes sense to apply the suggested change

## Background

### Motivation

Over the past year, my colleagues and I have delved into the field of sustainable networking, focusing on the critical challenge of improving energy efficiency in computer networks.
Our initial research revealed a significant gap: optimizing network energy efficiency through traffic engineering methods is extremely difficult due to the lack of visibility into the energy efficiency of network paths.

This realization led us to focus on enhancing visibility into the energy efficiency of network paths and nodes.
After several months of research, we published a paper titled "Towards Sustainable Networking: Unveiling Energy Efficiency Through Hop and Path Efficiency Indicators in Computer Networks", which was presented at IEEE Netsoft 2024 and is now available on [IEEE Xplore](https://ieeexplore.ieee.org/document/10588907).

Currently, we are seeking collaboration partners to expand on this work and are actively exploring its applicability to various network topologies.
Our proof-of-concept (PoC) implementation already includes several key capabilities: the collection of network telemetry data embedded in packet metadata using the IOAM Aggregation Trace Option, standardized export of this data to an arbitrary IPFIX collector, and descriptive dashboards that visualize the collected data.
While this provides a strong foundation, our next goal is to leverage data science techniques and run simulations across different topologies to further analyze and optimize network performance.
This will help us uncover deeper insights, identify critical information gaps, and explore new optimization opportunities.

Participating in the Green Tech Hackathon would be a great opportunity for us to refine our approach, collaborate with experts in the field, and accelerate progress towards more energy-efficient networks.

### Project Proposal

Building on our [previous work](https://ieeexplore.ieee.org/document/10588907) on retrieving network energy efficiency data, we propose developing a simulation-based application that leverages this data to optimize traffic flow and improve overall energy efficiency in computer networks.
The project will focus on creating an algorithm capable of analyzing raw data from our proof-of-concept (PoC) environment, offering real-time suggestions for traffic flow adjustments to reduce energy consumption.

The primary goal is to demonstrate that energy-efficient traffic routing can be achieved using our collected data, while also identifying any gaps in the current dataset that would be crucial for further optimizations.

### Information to share with other participants
To ensure effective collaboration, we recommend reviewing the paper referenced in the project proposal for a deeper understanding of our approach.
It would also be helpful to familiarize yourself with the IOAM protocol, particularly the IOAM Aggregation Trace Option, which is a key element in collecting energy efficiency data in the approach proposed.
You can find the details of this extension in the [Aggregation Trace Option for In-situ Operations, Administration, and Maintenance (IOAM)](https://datatracker.ietf.org/doc/draft-cxx-ippm-ioamaggr/02/) specification.
