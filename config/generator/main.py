import argparse
import datetime
import json
import logging
import os
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader

import bmv2_runtime_generator as brg
import mininet_topology_generator as mtg
import traffic_generator_config_generator as tgcg
import grafana_config_generator as gfc


def get_args():
    cwd = os.getcwd()
    default_logs = os.path.join(cwd, "logs")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--template-dir",
        help="Path to template directory",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-m",
        "--mininet-template",
        help="Name of the mininet topology template",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-b",
        "--bmv2-template",
        help="Name of the bmv2 runtime template",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-g",
        "--grafana-template-dir",
        help="Path to Grafana template directory",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-d",
        "--grafana-dashboard-dir",
        help="Path to Grafana dashboard directory",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-r",
        "--resources",
        help="Path to yaml resource definition",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-l", "--log-dir", type=str, required=False, default=default_logs
    )
    parser.add_argument(
        "-o",
        "--out-dir",
        help="Path to template output directory",
        type=str,
        required=False,
        default="out/",
    )
    return parser.parse_args()


def create_bmv2_configuration(resources):
    args = get_args()
    # Configure the jinja2 environment
    env = Environment(loader=FileSystemLoader(args.template_dir), trim_blocks=True)

    template = env.get_template(args.bmv2_template)
    bmv2_resources = brg.generate_bmv2_config(resources)

    for switch in resources["switches"]:
        bmv2_resources["switch_name"] = switch

        # Render the template with the bmv2 dictionary data
        bmv2 = template.render(bmv2_resources)
        json_data = json.loads(bmv2)

        # Write data into switch runtime json FileSystemLoader
        with open(
            os.path.join(args.out_dir, f"{switch}-runtime.json"),
            "w",
        ) as file:
            json.dump(json_data, file, indent=2)


def create_mininet_topology(resources):
    args = get_args()
    # Configure the jinja2 environment
    env = Environment(loader=FileSystemLoader(args.template_dir), trim_blocks=True)

    mininet_template = env.get_template(args.mininet_template)
    mininet = mininet_template.render(
        mtg.generate_mininet_config(resources), out_dir=args.out_dir
    )
    json_data = json.loads(mininet)

    # Write data into switch runtime json files
    with open(
        os.path.join(args.out_dir, "topology.json"),
        "w",
    ) as file:
        json.dump(json_data, file, indent=2)


def create_traffic_generator_configuration(resources):
    args = get_args()
    traffic_generator_config = tgcg.generate_traffic_generator_config(resources)

    # Write data into traffic generator config json files
    with open(
        os.path.join(args.out_dir, "traffic-generator-config.json"),
        "w",
    ) as file:
        json.dump(traffic_generator_config, file, indent=2)


def create_grafana(resources):
    args = get_args()
    # list of all dashboards that need changing with all relevant information
    list = [
        {
            "shortened_ipv6": True,
            "file_name": "flow_statistics.json",
            "id": 4,
            "func": gfc.regex_insert,
            "template": "flow-efficiency-by-receiver.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "flow_statistics.json",
            "id": 3,
            "func": gfc.regex_insert,
            "template": "flow-efficiency-by-receiver.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "flow_statistics.json",
            "id": 7,
            "func": gfc.query_insert,
            "template": "most-inefficient-flow-by-destination.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "flow_statistics.json",
            "id": 6,
            "func": gfc.query_insert,
            "template": "end-to-end-flow-efficiency-matrix.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "simulation_network_statistics.json",
            "id": 2,
            "func": gfc.regex_insert,
            "template": "flow-efficiency-by-receiver.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "simulation_network_statistics.json",
            "id": 10,
            "func": gfc.query_insert,
            "template": "number-of-packets-per-flow-with-usupported-aggregators.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "simulation_network_statistics.json",
            "id": 11,
            "func": gfc.query_insert,
            "template": "number-of-packets-per-flow-with-unsupported-data-parameter.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "simulation_network_statistics.json",
            "id": 9,
            "func": gfc.query_insert,
            "template": "number-of-packets-per-flow-with-unsupported-namespace.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "simulation_network_statistics.json",
            "id": 12,
            "func": gfc.query_insert,
            "template": "number-of-packet-per-flow-with-other-errors.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "hop_statistics.json",
            "id": 2,
            "func": gfc.mapping_insert,
            "template": "efficient-hop-discovery.j2",
        },
        {
            "shortened_ipv6": True,
            "file_name": "hop_statistics.json",
            "id": 3,
            "func": gfc.mapping_insert,
            "template": "efficient-hop-discovery.j2",
        },
        {
            "shortened_ipv6": False,
            "file_name": "path_statistics.json",
            "id": 5,
            "func": gfc.query_insert,
            "template": "current-path-statistics-from-host-to-host.j2",
        },
        {
            "shortened_ipv6": False,
            "file_name": "simulation_network_statistics.json",
            "id": 13,
            "func": gfc.query_insert,
            "template": "flow-error-overview.j2",
        },
        {
            "shortened_ipv6": False,
            "file_name": "hop_statistics.json",
            "id": 7,
            "func": gfc.query_insert,
            "template": "relative-efficient-hop-discovery.j2",
        },
        {
            "shortened_ipv6": False,
            "file_name": "hop_statistics.json",
            "id": 8,
            "func": gfc.query_insert,
            "template": "relative-efficient-hop-discovery.j2",
        },
    ]
    gfc.compile_j2(
        list, resources, args.grafana_template_dir, args.grafana_dashboard_dir
    )


def main():
    args = get_args()
    # Make sure required directories exist
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    Path(args.log_dir).mkdir(parents=True, exist_ok=True)

    # Configure logging
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"config_generator_{current_time}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=f"{args.log_dir}/{log_filename}",
    )

    # Load resources file
    with open(args.resources, "r") as file:
        logging.info("Loading resources file: %s", args.resources)
        resources = yaml.safe_load(file)

    create_bmv2_configuration(resources)
    create_mininet_topology(resources)
    create_traffic_generator_configuration(resources)
    create_grafana(resources)


if __name__ == "__main__":
    main()
