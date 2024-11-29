/*************************************************************************
*********************** TYPE ALIAS  **************************************
*************************************************************************/

typedef bit<9>  egressSpec_t;

// Ethernet Types
typedef bit<48> macAddr_t;

// IP Types
typedef bit<32> ip4Addr_t;
typedef bit<128> ip6Addr_t;

// IOAM Types
typedef bit<24> ioamNodeID_t;
typedef bit<24> ioamDataParam_t;
typedef bit<4> ioamFlag_t;
typedef bit<8> ioamAggregator_t;
typedef bit<32> ioamAggregate_t;
typedef bit<16> ioamNamespace_t;

struct ioamAggrMeta_t {
    ioamAggregate_t aggregate;
    ioamDataParam_t dataParam;
    bit<2> aggregator_selector;
    bit<1> dataParamError;
    bit<1> otherError;
}

struct ioamMeta_t {
    ioamNamespace_t namespaceID;
    ioamNodeID_t nodeID;
}

struct forwardingMeta_t {
    bit<8> routeType;
    bit<8> reverseRouteType;
}

// UDP Types
typedef bit<16> udpAddr_t;

// IPFIX Types
typedef bit<148> flowKey_t;
typedef bit<20> flowLabel_t;
