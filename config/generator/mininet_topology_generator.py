HOST_PREFIXES = ["h"]


def get_remote_port_number(resources, local_switch, remote_switch):
    for port_number, port_details in resources["switches"][remote_switch][
        "ports"
    ].items():
        if port_details["neighbor"] == local_switch:
            return port_number


def get_switch_number(switch_name):
    return int(switch_name[1:])


def is_switch(switch_name):
    for prefix in HOST_PREFIXES:
        if switch_name.lower().startswith(prefix):
            return False
    return True


def generate_mininet_config(resources):
    if "links" not in resources:
        resources["links"] = {}

    links = []

    for switch_name, switch_details in resources["switches"].items():
        for port_number, port_details in switch_details["ports"].items():
            link = {
                "local": {"name": switch_name, "port": port_number},
                "remote": {"name": port_details["neighbor"], "port": None},
            }

            # Proceed to next port if it connects to a switch with a lower port number
            if is_switch(port_details["neighbor"]) and (
                get_switch_number(switch_name)
                >= get_switch_number(port_details["neighbor"])
            ):
                continue

            # Skip remote link gathering in case the neighbor is a host
            if not is_switch(port_details["neighbor"]):
                links.append(link.copy())
                continue

            link["remote"]["port"] = get_remote_port_number(
                resources, switch_name, port_details["neighbor"]
            )
            links.append(link.copy())
    resources["links"] = links
    return resources
