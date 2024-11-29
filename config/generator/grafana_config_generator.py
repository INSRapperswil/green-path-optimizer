import os
import json
import ipaddress
from jinja2 import Environment, FileSystemLoader


def compile_j2(list, resources, grafana_template_dir, grafana_dashboard_dir):
    for element in list:
        # check what type the element has type 1 is with extended ipv6 addresses and type 0 with short ones
        if element["shortened_ipv6"]:
            # get Template and rendere the Template with the apropriate data and then give it to the relevant functon which does what we need it to do.
            template = get_template(element, grafana_template_dir)
            rendered = template.render(resources)
            element["func"](element, rendered, grafana_dashboard_dir)
        elif not element["shortened_ipv6"]:
            # extend ipv6 addresses, get Template and rendere the Template with the apropriate data and then give it to the relevant functon which does what we need it to do.
            new_resources = make_extended_resources(resources)
            template = get_template(element, grafana_template_dir)
            rendered = template.render(new_resources)
            element["func"](element, rendered, grafana_dashboard_dir)


def make_extended_resources(resources):
    # extend the ipv6 addresses for all hosts
    for hosts in resources["hosts"]:
        resources["hosts"][hosts]["ipv6"]["ip"] = ipaddress.ip_address(
            resources["hosts"][hosts]["ipv6"]["ip"]
        ).exploded
    return resources


def get_template(list, grafana_template_dir):
    # make a Jinja Environment and get Template form the Template directory
    env = Environment(loader=FileSystemLoader(grafana_template_dir), trim_blocks=True)
    template = env.get_template(list["template"])
    return template


def get_index_of_dashboard(data, list):
    # get the index of the dashboard since the index in the list is not the same as the index given on the grafana website
    x = 0
    for i in data["panels"]:
        if i["id"] == list["id"]:
            return x
        x += 1


def insert_regex_at_index(data, rendered, index):
    # replace the regex of the dashboard with the give index
    data["panels"][index]["transformations"] = json.loads(rendered)
    return data


def insert_query_at_index(data, rendered, index):
    # replace the query of the dashboard with the give index
    data["panels"][index]["targets"][0]["query"] = rendered
    return data


def insert_mapping_at_index(data, rendered, index):
    # replace the mapping of the dashboard with the give index
    data["panels"][index]["fieldConfig"]["overrides"][0]["properties"][0]["value"][0][
        "options"
    ] = rendered
    return data


def regex_insert(list, rendered, grafana_dashboard_dir):
    # open the appropriate .json document and get data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "r+",
    ) as file:
        data = json.load(file)

    index = get_index_of_dashboard(data, list)
    whole_data = insert_regex_at_index(data, rendered, index)

    # get the apropriate .json document and dump data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "w+",
    ) as file:
        json.dump(whole_data, file, indent=1)


def query_insert(list, rendered, grafana_dashboard_dir):
    # open the appropriate .json document and get data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "r+",
    ) as file:
        data = json.load(file)

    index = get_index_of_dashboard(data, list)
    whole_data = insert_query_at_index(data, rendered, index)

    # get the apropriate .json document and dump data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "w+",
    ) as file:
        json.dump(whole_data, file, indent=1)


def mapping_insert(list, rendered, grafana_dashboard_dir):
    # open the appropriate .json document and get data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "r+",
    ) as file:
        data = json.load(file)

    index = get_index_of_dashboard(data, list)
    whole_data = insert_mapping_at_index(data, rendered, index)

    # get the apropriate .json document and dump data
    with open(
        os.path.join(grafana_dashboard_dir, list["file_name"]),
        "w+",
    ) as file:
        json.dump(whole_data, file, indent=1)
