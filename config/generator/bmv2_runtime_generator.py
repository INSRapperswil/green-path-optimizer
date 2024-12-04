import logging


def get_next_hop(switch, path):
    complete_path = [path["ingress"]] + path["via"] + [path["egress"]]
    for i, s in enumerate(complete_path):
        if s == switch:
            return complete_path[i + 1]


def get_egress_port(switches, switch_name, host_name, path, is_last_hop):
    neighbor = None

    if is_last_hop:
        neighbor = host_name
    else:
        neighbor = get_next_hop(switch_name, path)

    for port_number, port_details in switches[switch_name]["ports"].items():
        if port_details["neighbor"] == neighbor:
            return port_number


def get_connected_hosts(switch_name, resources):
    connected_hosts = []
    for _, port_details in resources["switches"][switch_name]["ports"].items():
        if port_details["neighbor"].startswith("h"):
            connected_hosts.append(port_details["neighbor"])
    return connected_hosts


def get_ip_table_entry(resources, switch_name, host_name, path, ip_version):
    logging.info(
        "Adding IPv%s configuration for path from %s to %s to switch %s",
        ip_version,
        path["ingress"],
        path["egress"],
        switch_name,
    )

    table_entry = {
        "ip": None,
        "prefix_len": None,
        "port": None,
        "mac": None,
        "route_type": None,
    }
    host_details = resources["hosts"][host_name]
    switch_details = resources["switches"][switch_name]

    # Return in case no configuration is available for specified IP version
    if f"ipv{ip_version}" not in host_details:
        logging.warning(
            "No IPv%s configuration available for destination host %s",
            ip_version,
            host_name,
        )
        return None

    # Check if switch is last hop
    is_last_hop = False
    if switch_name == path["egress"]:
        logging.info(
            "Switch %s is the last hop in path from %s to %s",
            switch_name,
            path["ingress"],
            path["egress"],
        )
        is_last_hop = True

    # Set table entry data
    if is_last_hop:
        table_entry["ip"] = host_details[f"ipv{ip_version}"]["ip"]
        table_entry["prefix_len"] = 32 if ip_version == 4 else 128
        table_entry["mac"] = host_details["mac"]
        table_entry["route_type"] = 0
    else:
        table_entry["ip"] = host_details[f"ipv{ip_version}"]["net"]
        table_entry["prefix_len"] = host_details[f"ipv{ip_version}"]["prefix_len"]
        table_entry["mac"] = resources["switches"][get_next_hop(switch_name, path)][
            "mac"
        ]
        table_entry["route_type"] = 1

    table_entry["port"] = get_egress_port(
        resources["switches"], switch_name, host_name, path, is_last_hop
    )

    # Check if switch already has a an entry for the destination via the specific port
    if host_name in switch_details["tables"][f"ipv{ip_version}_forwarding"]:
        port_existing_entry = switch_details["tables"][f"ipv{ip_version}_forwarding"][
            host_name
        ]["port"]
        if port_existing_entry == table_entry["port"]:
            logging.info(
                "Switch %s already has an IPv%s route to %s and the egress ports match (existing entry port: %s / new entry port: %s) -- no problem ahead",
                switch_name,
                ip_version,
                host_name,
                port_existing_entry,
                table_entry["port"],
            )
        else:
            logging.warning(
                "Switch %s already has an IPv%s route to %s and the egress ports do not match (existing entry port: %s / new entry port: %s) -- ignoring new entry",
                switch_name,
                ip_version,
                host_name,
                port_existing_entry,
                table_entry["port"],
            )
        return None

    return table_entry


def configure_path_on_switch(path, resources, switch_name, ip_version, switch_details):
    for host in get_connected_hosts(path["egress"], resources):
        table_entry = get_ip_table_entry(resources, switch_name, host, path, ip_version)
        if table_entry:
            switch_details["tables"][f"ipv{ip_version}_forwarding"][host] = table_entry


def reverse_path(path):
    reversed_path = {}
    reversed_path["ingress"] = path["egress"]
    reversed_path["egress"] = path["ingress"]
    reversed_path["via"] = list(reversed(path["via"]))
    return reversed_path


def set_ip_forwarding_table_data(resources, switch_name, ip_version):
    logging.info(
        "Setting IPv%s forwarding table data of switch: %s", ip_version, switch_name
    )

    for path in resources["paths"]:
        if (
            path["ingress"] != switch_name
            and path["egress"] != switch_name
            and switch_name not in path["via"]
        ):
            logging.info(
                "Switch %s is not in path from %s to %s",
                switch_name,
                path["ingress"],
                path["egress"],
            )
            continue

        switch_details = resources["switches"][switch_name]

        if "tables" not in switch_details:
            switch_details["tables"] = {}
        if f"ipv{ip_version}_forwarding" not in switch_details["tables"]:
            switch_details["tables"][f"ipv{ip_version}_forwarding"] = {}

        configure_path_on_switch(
            path, resources, switch_name, ip_version, switch_details
        )
        if "symmetric" in path and path["symmetric"]:
            configure_path_on_switch(
                reverse_path(path), resources, switch_name, ip_version, switch_details
            )
            logging.info(
                "Path from %s to %s via %s is symmetric creating table entry for reversed direction",
                path["ingress"],
                path["egress"],
                switch_name,
            )
    return resources


def generate_bmv2_config(resources):
    for switch in resources["switches"]:
        logging.info(
            "Generating control plane table configurations for switch: %s", switch
        )
        resources = set_ip_forwarding_table_data(resources, switch, 4)
        resources = set_ip_forwarding_table_data(resources, switch, 6)
    return resources
