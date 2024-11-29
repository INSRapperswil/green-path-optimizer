# Green Networking

**Visibility, a first step towards sustainable networking.**

In today's digital age, the vast network infrastructure supporting our internet and communication systems is a significant consumer of energy.
Despite the critical role of networks, there is currently no effective method for retrieving information about the carbon intensity and energy efficiency of network paths and devices. This lack of visibility hampers efforts to identify and mitigate inefficiencies, making it challenging to reduce the overall environmental impact of these systems. This project addresses this gap by proposing a method to export and visualize network telemetry data, which will provide insights into the carbon footprint of networks at both the path and flow levels. The ultimate goal is to lay the groundwork for future improvements in network sustainability.

## Project Overview
As already mentioned in the introduction and in the term paper [Green Networking - Visibility, a first step towards sustainable networking](https://gitlab.ost.ch/green-networking/about/-/blob/main/README.md?ref_type=heads), the networking industry will increasingly need to focus on becoming more sustainable and reducing their carbon footprint.
The goal of the bachelor thesis is to improve the previous work and extend the network virtualization system and the existing efficiency indicators HEI and PEI with the flow efficiency indicator (FEI) and the link efficiency indicator (LEI).
A comprehensive monitoring system with several dashboards should be implemented to visualize the efficiency of the network.
To be able to adjust and adapt the network virtualization system to a realistic real world network scenario a configuration update system and a traffic generator will be implemented to generate realistic network traffic.
With the same external partner as in the previous term paper, we have a very great and productive collaboration with Alexander Clemm.

### Members
This research project is currently being carried out as a bachelor thesis at the Eastern Switzerland University of Applied Sciences (OST).
The people involved are:
- **Bachelor Students:**
  - Ramon Bister
  - Reto Furrer
- **Advisor:** Prof. Laurent Metzger (OST)
- **Co-Advisor:** Severin Dellsperger (OST)
- **Proofreader:** Prof. Dr. Daniel Patrick Politze (OST)
- **External Partner:** Dr. Alexander Clemm (Sympotech)

## Repositories

1. [**About**](https://gitlab.ost.ch/green-networking-ba/about)  
The _About_ repository provides a brief introduction to the Green Networking project.

1. [**Documentation**](https://gitlab.ost.ch/green-networking-ba/documentation)  
The _Documentation_ repository gives you some insights about the most important concepts and challenges in this project.
The terms **Green Networking** and **Sustainable Networking** are used interchangeably in this project.

1. [**Efficiency Indicator P4**](https://gitlab.ost.ch/green-networking-ba/efficiency-indicator-p4)  
The _Efficiency Indicator P4_ repository contains the virtual network environment with the BMv2 software switches.
It also includes the P4 code for programming the data plane and the traffic generator.

1. [**Efficiency Indicator Monitoring**](https://gitlab.ost.ch/green-networking-ba/efficiency-indicator-monitoring)  
The _Efficiency Indicator Monitoring_ repository provides a monitoring solution using a TIG (Telegraf, InfluxDB and Grafana) stack.

1. [**Efficiency Indicator Configuration Update**](https://gitlab.ost.ch/green-networking-ba/efficiency-indicator-configuration-update)  
The _Efficiency Indicator Configuration Update_ repository is used to update the control plane table definitions of the BMv2 software switches at runtime.

1. [**Behavioral-Model**](https://github.com/ramobis/behavioral-model)  
The _Behavioral-Model_ repository is a fork from [p4lang behavioral-model](https://github.com/p4lang/behavioral-model) which contains the code for the P4 software switch (bmv2 switch) used in the Mininet and our BMv2 IPFIX extension as a BMv2 plugin.

1. [**Wireshark**](https://github.com/ramobis/wireshark)  
The _Wireshark_ repository is a fork from [wireshark](https://github.com/wireshark/wireshark) where we implemented the Wireshark dissector for the IOAM aggregation option as part of the IPv6 dissector.
