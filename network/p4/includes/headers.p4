/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ipv6_t {
    bit<4> version;
    bit<8> trafficClass;
    bit<20> flowLabel;
    bit<16> payloadLen;
    bit<8> nextHeader;
    bit<8> hopLimit;
    ip6Addr_t srcAddr;
    ip6Addr_t dstAddr;
}

// Hop-by-Hop Options Header
header ipv6_ext_hop_by_hop_t {
    bit<8> nextHeader;
    bit<8> hdrLen;
}

// Option Header
header ipv6_option_t {
    bit<8> optionType;
    bit<8> optionDataLen;
}

header option_padn_data_t {
    bit<((IPV6_EXT_HOP_BY_HOP_PADDING - 2) * 8)> padding; // NumOfBytesPadding = N-2
}

// IOAM Header
header ioam_t {
    bit<8> reserved;
    bit<8> ioamOptType;
}

// IOAM Aggreagation Type Option Header
header ioam_aggregation_t {
    bit<16> namespaceID;
    bit<4> flags;
    bit<12> reserved;
    ioamDataParam_t dataParam; // identifies the type of data being aggregated
    ioamAggregator_t aggregator;
    ioamAggregate_t aggregate;
    ioamNodeID_t auxilDataNodeID;
    bit<8> hopCount;
}

// IOAM Aggreagation Type Option Header
header ioam_trace_t {
    bit<16> namespaceID;
    bit<5> nodeLen;
    bit<4> flags;
    bit<7> remainingLen;
    bit<24> ioamTraceType;
    bit<8> reserved;
    bit<(IOAM_TRACE_DATA_LIST_LEN)> dataList;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> legth;
    bit<16> checkSum;
}

struct metadata {
    ioamMeta_t ioamMeta;
    ioamAggrMeta_t ioamAggrMeta;
    forwardingMeta_t forwardingMeta;
}

struct headers {
    // Datalink protocol
    ethernet_t                                      ethernet;
    // Network protocol
    ipv4_t                                          ipv4;
    ipv6_t                                          ipv6;
    // IOAM trace option
    ipv6_ext_hop_by_hop_t                           ipv6_ext_hop_by_hop;
    ipv6_option_t                                   ioam_t_ipv6_option;
    ioam_t                                          ioam_t_ioam;
    ioam_trace_t                                    ioam_t_ioam_trace;
    // IOAM aggregation option
    ipv6_option_t                                   ioam_a_ipv6_option;
    ioam_t                                          ioam_a_ioam;
    ioam_aggregation_t                              ioam_a_ioam_aggregation;
    ipv6_option_t                                   option_padn;
    option_padn_data_t                              option_padn_data;
    // Transport protocol
    udp_t                                           udp;
}
