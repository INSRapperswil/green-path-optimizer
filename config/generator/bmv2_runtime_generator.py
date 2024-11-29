import logging


def get_next_hop(switch, switch_list):
    for i, s in enumerate(switch_list):
        if s == switch:
            return switch_list[i + 1]


def get_egress_port(switches, switch_name, path, is_last_hop):
    neighbor = None

    if is_last_hop:
        neighbor = path["to"]
    else:
        neighbor = get_next_hop(switch_name, path["via"])

    for port_number, port_details in switches[switch_name]["ports"].items():
        if port_details["neighbor"] == neighbor:
            return port_number


def get_ip_table_entry(resources, switch_name, path, ip_version):
    logging.info(
        "Adding IPv%s configuration for path from %s to %s to switch %s",
        ip_version,
        path["from"],
        path["to"],
        switch_name,
    )

    table_entry = {
        "ip": None,
        "prefix_len": None,
        "port": None,
        "mac": None,
        "route_type": None,
    }
    host_details = resources["hosts"][path["to"]]
    switch_details = resources["switches"][switch_name]

    # Return in case no configuration is available for specified IP version
    if f"ipv{ip_version}" not in host_details:
        logging.warning(
            "No IPv%s configuration available for destination host %s",
            ip_version,
            path["to"],
        )
        return None

    if path["to"] in switch_details["tables"][f"ipv{ip_version}_forwarding"]:
        logging.warning(
            "Switch %s already has an IPv%s route to %s -> not adding an additional route",
            switch_name,
            ip_version,
            path["to"],
        )
        return None

    # Check if switch is last hop
    is_last_hop = False
    if switch_name == path["via"][-1]:
        logging.info(
            "Switch %s is the last hop in path from %s to %s",
            switch_name,
            path["from"],
            path["to"],
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
        table_entry["mac"] = resources["switches"][
            get_next_hop(switch_name, path["via"])
        ]["mac"]
        table_entry["route_type"] = 1

    table_entry["port"] = get_egress_port(
        resources["switches"], switch_name, path, is_last_hop
    )
    return table_entry


def set_ip_forwarding_table_data(resources, switch_name, ip_version):
    logging.info(
        "Setting IPv%s forwarding table data of switch: %s", ip_version, switch_name
    )
    for path in resources["paths"]:
        if switch_name not in path["via"]:
            logging.info(
                "Switch %s is not in path from %s to %s",
                switch_name,
                path["from"],
                path["to"],
            )
            continue

        switch_details = resources["switches"][switch_name]

        if "tables" not in switch_details:
            switch_details["tables"] = {}
        if f"ipv{ip_version}_forwarding" not in switch_details["tables"]:
            switch_details["tables"][f"ipv{ip_version}_forwarding"] = {}

        table_entry = get_ip_table_entry(resources, switch_name, path, ip_version)
        if table_entry:
            switch_details["tables"][f"ipv{ip_version}_forwarding"][
                path["to"]
            ] = table_entry

        if "return_route" in path and path["return_route"]:
            logging.info(
                "Path from %s to %s via %s is symmetric creating table entry for reversed direction",
                path["from"],
                path["to"],
                switch_name,
            )
            reversed_path = {}
            reversed_path["from"] = path["to"]
            reversed_path["to"] = path["from"]
            reversed_path["via"] = path["via"].copy()
            reversed_path["via"].reverse()

            table_entry = get_ip_table_entry(
                resources, switch_name, reversed_path, ip_version
            )
            if table_entry:
                switch_details["tables"][f"ipv{ip_version}_forwarding"][
                    reversed_path["to"]
                ] = table_entry
            else:
                continue
    return resources


def generate_bmv2_config(resources):
    for switch in resources["switches"]:
        logging.info(
            "Generating control plane table configurations for switch: %s", switch
        )
        resources = set_ip_forwarding_table_data(resources, switch, 4)
        resources = set_ip_forwarding_table_data(resources, switch, 6)
    return resources
