def get_destination_mac_address(host, resources):
    for switch_name, switch_details in resources["switches"].items():
        for port_number, port_details in switch_details["ports"].items():
            if port_details["neighbor"] == host:
                return switch_details["mac"]
            else:
                continue


def generate_traffic_generator_config(resources):
    config = {"dst_hosts": {}, "hosts": {}}

    # Get all hosts from resources file
    all_hosts = list(resources["hosts"].keys())

    # For each host, add all possible destination hosts without themselves and the relevant host details
    for host_name, host_details in resources["hosts"].items():
        config["dst_hosts"][host_name] = [h for h in all_hosts if h != host_name]
        config["hosts"][host_name] = {
            "src_mac": host_details["mac"],
            "dst_mac": get_destination_mac_address(host_name, resources),
            "ipv4": host_details["ipv4"]["ip"],
            "ipv6": host_details["ipv6"]["ip"],
        }
    return config
