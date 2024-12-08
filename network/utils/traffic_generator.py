import json
from pathlib import Path
from scapy.all import *
import argparse
import time
import logging
import datetime

# Disable scapy promiscuous mode
conf.sniff_promisc = 0

MAX_DELAY_BETWEEN_FLOWS = 30
MAX_NUMBER_PACKETS_PER_FLOW = 100
MAX_FLOW_LABEL_VALUE = 1048575
MAX_FLOW_LABEL_SELECT_RETRY = 10

# Initialize a Set for used FlowLabels
used_flow_labels = set()


def set_ethernet_address(src, dst, packet, config):
    packet.getlayer("Ethernet").src = config["hosts"][src]["src_mac"]
    packet.getlayer("Ethernet").dst = config["hosts"][src]["dst_mac"]


def set_ipv6_address(src, dst, packet, config):
    packet.getlayer("IPv6").src = config["hosts"][src]["ipv6"]
    packet.getlayer("IPv6").dst = config["hosts"][dst]["ipv6"]


def select_ipv6_flow_label():
    for _ in range(0, MAX_FLOW_LABEL_SELECT_RETRY):
        flow_label = random.getrandbits(20)
        if flow_label not in used_flow_labels:
            used_flow_labels.add(flow_label)
            return flow_label
    used_flow_labels.clear()
    flow_label = random.getrandbits(20)
    used_flow_labels.add(flow_label)
    return flow_label


def set_ipv6_flow_label(flow_label, packet):
    packet.getlayer("IPv6").fl = flow_label


def set_ipv6_udp_src_port(port, packet):
    packet.getlayer("UDP").sport = port


def set_dst_host(src_host, dst_host, config):
    if dst_host and dst_host in config["hosts"]:
        return dst_host
    elif dst_host and dst_host not in config["hosts"]:
        exit(
            logging.error(
                "Destination host is invalid, use one of the available hosts: %s",
                ", ".join(config["hosts"]),
            )
        )
    else:
        dst_host = random.choice(config["dst_hosts"][src_host])
        return dst_host


def create_and_send_random_packets(
    src_host, dst_host, flow_label, num_of_packets, pcap, config
):
    # Load pcap file
    ipv6_packets = rdpcap(pcap)

    # Set the specified dst_host or a random host as destination host
    dst = set_dst_host(src_host, dst_host, config)

    # Select the amount of packets
    if not num_of_packets:
        num_of_packets = random.randrange(1, MAX_NUMBER_PACKETS_PER_FLOW)

    # Create unique flow label
    if not flow_label:
        flow_label = select_ipv6_flow_label()
    elif flow_label > MAX_FLOW_LABEL_VALUE:
        exit(
            logging.warning(
                "Flow label is invalid, the flow label must be a valid 20 bit value (Int between 0 - 1048575)"
            )
        )

    # Select random UDP source port from the Ephemeral port range
    src_port = random.randrange(49152, 65535)

    packet_counter = 0

    logging.info(
        "Sending flow 0x%x from src host %s to dst host %s with %s packets",
        flow_label,
        src_host,
        dst,
        num_of_packets,
    )

    while packet_counter < num_of_packets:
        for packet in ipv6_packets:
            if packet_counter >= num_of_packets:
                break
            set_ethernet_address(src_host, dst, packet, config)
            set_ipv6_address(src_host, dst, packet, config)
            set_ipv6_flow_label(flow_label, packet)
            set_ipv6_udp_src_port(src_port, packet)
            sendp(packet, verbose=False)
            packet_counter += 1


def delay_between_new_flow(max_delay):
    seconds = random.randrange(max_delay)
    logging.info("Sleep %i seconds before sending a new flow", seconds)
    time.sleep(seconds)


# send imported IPv6 packets from src to dst
def send_ipv6_packets(
    src_host, dst_host, flow_label, num_of_packets, num_of_flows, infinite, pcap, config
):
    if infinite:
        logging.info(
            "Start the traffic generator on host %s for an infinite amount of time",
            src_host,
        )
        while True:
            create_and_send_random_packets(
                src_host, dst_host, flow_label, num_of_packets, pcap, config
            )
            delay_between_new_flow(MAX_DELAY_BETWEEN_FLOWS)
    elif num_of_flows == 1:
        logging.info(
            "Start the traffic generator on host %s and send one flow to host %s",
            src_host,
            dst_host,
        )
        create_and_send_random_packets(
            src_host, dst_host, flow_label, num_of_packets, pcap, config
        )
    elif num_of_flows > 0:
        if dst_host:
            logging.info(
                "Start the traffic generator on host %s and send %s flows to host %s",
                src_host,
                num_of_flows,
                dst_host,
            )
        else:
            logging.info(
                "Start the traffic generator on host %s and send %s flows to a random destination host",
                src_host,
                num_of_flows,
            )
        for _ in range(num_of_flows):
            create_and_send_random_packets(
                src_host, dst_host, flow_label, num_of_packets, pcap, config
            )
            delay_between_new_flow(MAX_DELAY_BETWEEN_FLOWS)


# Load traffic generator config file
def load_config_file(config):
    try:
        with open(config, "r") as file:
            logging.info("Loading config file: %s", config)
            config = json.load(file)
        return config
    except OSError:
        raise


# initialize argparse
def get_args():
    parser = argparse.ArgumentParser(description="Network Traffic Simulator")
    parser.add_argument(
        "--ipv6",
        help="Send only IPv6 traffic",
        default=True,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--src", help="The source of the traffic", type=str, required=True
    )
    parser.add_argument(
        "--dst", help="The destination of the traffic", type=str, required=False
    )
    parser.add_argument(
        "--flow-label", help="The flow label of the traffic", type=int, required=False
    )
    parser.add_argument(
        "--flow-count", help="Number of flows to be sent", type=int, default=1
    )
    parser.add_argument("--packet-count", help="Number of packets to be sent", type=int)
    parser.add_argument(
        "--infinite",
        help="Traffic generator will run for an infinite amount of time",
        required=False,
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--config",
        help="Path to json configuration file",
        type=str,
        required=True,
    )
    parser.add_argument("--log-dir", type=str, required=False, default=None)
    parser.add_argument(
        "--startup-delay",
        help="Startup delay before starting the traffic generator",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--pcap-file",
        help="Path to pcap file containing packets which can be replicated",
        type=str,
        required=True,
    )
    return parser.parse_args()


def main():
    args = get_args()

    # Configure logging
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"traffic_generator_{args.src}_{current_time}.log"
    if args.log_dir is not None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename=f"{args.log_dir}/{log_filename}",
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )

    # decide which functions to call
    if args.ipv6:
        if args.startup_delay:
            # Startup delay
            logging.info(
                "Startup delay of %i seconds before start sending packets",
                args.startup_delay,
            )
            time.sleep(args.startup_delay)
        send_ipv6_packets(
            args.src,
            args.dst,
            args.flow_label,
            args.packet_count,
            args.flow_count,
            args.infinite,
            args.pcap_file,
            load_config_file(args.config),
        )


if __name__ == "__main__":
    main()
