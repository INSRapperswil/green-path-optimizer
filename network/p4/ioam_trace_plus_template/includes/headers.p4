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
header ipv6_hop_opt_t {
    bit<8> nextHeader;
    bit<8> hdrLen;
}

// Option Header
header ipv6_option_t {
    bit<8> optionType;
    bit<8> optionDataLen;
}

// IOAM Header
header ioam_option_t {
    bit<8> reserved;
    bit<8> ioamOptType;
}

// IOAM Aggreagation Type Option Header
header ioam_pto_t {
    bit<16> namespaceID;
    bit<5> nodeLen;
    bit<4> flags;
    bit<7> remainingLen;
    bit<24> ioamTraceType;
    bit<8> templateID;
}

header ioam_pto_ndl_t {
    bit<(IOAM_PTO_DATA_LIST_LEN)> dataList;
}

// IOAM Aggreagation Template
header ioam_aggregation_t {
    ioamDataParam_t dataParam; // identifies the type of data being aggregated
    ioamAggregateFunc_t aggregator;
    ioamFlag_t flags;
    ioamAggregate_t aggregate;
    ioamNodeID_t auxilDataNodeID;
    bit<8> hopCount;
}

// PadN Option padding field with the required length for 8 octet alignment of the Hop by Hop Option header
// when the IOAM PTO is present in combination with the IOAM Template Option carrying the Aggregation Template
header option_padn_data_t {
    bit<32> padding;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> legth;
    bit<16> checkSum;
}

struct metadata {
    ioamMeta_t ioamMeta;
    ioamTemplateMeta_t ioamTemplateMeta;
    ioamAggregationMeta_t ioamAggregationMeta;
    forwardingMeta_t forwardingMeta;
}

struct headers {
    ethernet_t                                      ethernet;
    ipv4_t                                          ipv4;
    ipv6_t                                          ipv6;
    // IOAM Preallocated Trace Option
    ipv6_hop_opt_t                                  ipv6_hop_opt;
    ipv6_option_t                                   ipv6_option_pto;
    ioam_option_t                                   ioam_option_pto;
    ioam_pto_t                                      ioam_pto;
    ioam_aggregation_t                              ioam_aggregation;
    ioam_pto_ndl_t                                  ioam_pto_ndl;
    // Hop By Hop Option PadN for 8 octett alignment of option data
    ipv6_option_t                                   ipv6_option_padn;
    option_padn_data_t                              padn;
    udp_t                                           udp;
}
