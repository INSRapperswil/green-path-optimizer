extern void ProcessEfficiencyIndicatorMetadata(
                                        in ioamNodeID_t nodeID,
                                        in flowKey_t flowKey,
                                        in flowLabel_t flowLabel,
                                        in ip6Addr_t srcIPv6,
                                        in ip6Addr_t dstIPv6,
                                        in bit<16> sourceTransportPort,
                                        in bit<16> destinationTransportPort,
                                        in ioamDataParam_t indicatorID,
                                        in ioamAggregate_t indicatorValue,
                                        in bit<8> indicatorAggregator,
                                        in ioamFlag_t indicatorFlags,
                                        in bit<768> raw_ipv6_header
                                    );