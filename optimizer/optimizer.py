from influx.influx_data_getter import InfluxDataGetter
from influx.types import Aggregator
from os import environ
from time import time
from pprint import pprint
from rich import print
import yaml

IOAM_DATA_PARAM = 255
RESOURCE_FILE = "config/generator/resources/large_network_temp.yaml"


def is_env_file_loaded():
    return (
        "INFLUXDB_RAW_BUCKET" in environ
        and "INFLUXDB_AGGREGATED_BUCKET" in environ
        and "INFLUXDB_ORG" in environ
        and "INFLUXDB_TOKEN" in environ
        and "INFLUXDB_INIT_URL" in environ
    )


def main():
    if not is_env_file_loaded():
        raise RuntimeError(
            "Unable to intialize InfluxDataGetter because environment variables are unavailable"
        )
    idg = InfluxDataGetter(
        environ.get("INFLUXDB_RAW_BUCKET"),
        environ.get("INFLUXDB_AGGREGATED_BUCKET"),
        environ.get("INFLUXDB_ORG"),
        environ.get("INFLUXDB_TOKEN"),
        environ.get("INFLUXDB_INIT_URL"),
    )
    current_time = int(time())
    path_efficiency_data = idg.get_path_efficiency_by_ingress(
        current_time - 1000, current_time, "last"
    )
    # print(path_efficiency_data)
    sort_path_efficiency_data(path_efficiency_data, IOAM_DATA_PARAM, Aggregator.SUM)
    path_definitions = generate_path_defintion(path_efficiency_data)
    write_paths_to_resource_file(RESOURCE_FILE, path_definitions)

    last_used_paths = idg.get_last_used_paths_by_ingress(current_time - 1000, current_time)
    # pprint(path_efficiency_data)
    path_update_comparison_dict = generate_path_comparison_dict(path_efficiency_data, last_used_paths)
    print_path_comparion_dict(path_update_comparison_dict)


def get_aggregate(item: dict, data_param: int, aggregator: Aggregator):
    """
    Returns the aggregate value of the last entry of the given data param and aggregator

    Args:
        item (dict): The efficiency item to look for
        data_param (int): The identifier of the data param to optimize for
        aggregator (Aggregator): The aggregator to optimize for

    Returns:
        aggregate (int): The aggregate value with given data param and aggregator
    """
    data_param_dict = next(iter(item.values()))
    if data_param not in data_param_dict:
        return float("inf")
    if aggregator not in data_param_dict[data_param]:
        return float("inf")
    return data_param_dict[data_param][aggregator]["aggregate"]


def sort_path_efficiency_data(
    path_efficiency_data: dict, data_param: int, aggregator: Aggregator
):
    """
    Sorts the path list for each ingress and egress according to the given data_param and aggregator

    Args:
        path_efficiency_data (dict): The ingress to egress to path mapping returned by the influx data getter
        data_param (int): The identifier of the data param to optimize for
        aggregator (Aggregator): The aggregator to optimize for

    Returns:
        path_efficiency_data (dict): The sorted ingress to egress to path mapping returned by the influx data getter
    """

    if aggregator != Aggregator.SUM:
        raise ValueError("The provided aggregator is not supported")

    for ingress, egress_dict in path_efficiency_data.items():
        for egress, paths in egress_dict.items():
            paths.sort(key=lambda item: get_aggregate(item, data_param, aggregator))


def generate_path_comparison_dict(sorted_path_efficiency_data: dict, last_used_paths: dict) -> dict:
    path_comparison_dict = {}
    for ingress, egress_dict in sorted_path_efficiency_data.items():
        path_comparison_dict[ingress] = {}
        for egress, paths in egress_dict.items():
            path_comparison_dict[ingress][egress] = {
                "current": None,
                "new": list(paths[0].keys())[0]
            }
            if ingress in last_used_paths and egress in last_used_paths[ingress]:
                path_comparison_dict[ingress][egress]["current"] = last_used_paths[ingress][egress]
    return path_comparison_dict


def print_path_comparion_dict(comparison_dict: dict) -> None:
    for ingress, egress_dict in comparison_dict.items():
        for egress, path_comparison in egress_dict.items():
            if path_comparison["current"] is None:
                print(f"[yellow]s{ingress} -> s{egress}:[/yellow] {path_comparison}")
            elif path_comparison["current"] != path_comparison["new"]:
                print(f"[green]s{ingress} -> s{egress}:[/green] {path_comparison}")


def generate_path_defintion(path_efficiency_data: dict) -> list:
    """
    Generates the path definitions in the format needed for the resource yaml file

    Args:
        path_efficiency_data (dict): The sorted ingress to egress to path mapping returned by the influx data getter

    Returns:
        path_definitions (list): A list of the most efficient path definitions in the format needed for the resource yaml file
    """
    path_definitions = []
    for ingress, egress_dict in path_efficiency_data.items():
        for egress, paths in egress_dict.items():
            most_efficient_path = paths[0]
            nodes = list(most_efficient_path.keys())[0]
            path = {
                "ingress": None,
                "egress": None,
                "via": [],
                "symmetric": False,
            }
            for node_id in nodes:
                if node_id == 0:
                    continue
                node_name: str = f"s{node_id}"
                if path["ingress"] is None:
                    path["ingress"] = node_name
                elif node_id == nodes[-1]:
                    path["egress"] = node_name
                else:
                    path["via"].append(node_name)
            if path["ingress"] is None:
                raise ValueError("All node IDs are set to zero in given path")
            if path["egress"] is None:
                path["egress"] = path["ingress"]
            path_definitions.append(path)
    return path_definitions


def write_paths_to_resource_file(resource_file: str, paths: list):
    """
    Writes the given path definitions to the resource yaml file

    Args:
        resource_file(str): Path to the resource file containing the yaml definitions
        paths (list): A list containing the most efficient paths
    """
    with open(RESOURCE_FILE, "r") as file:
        resources = yaml.safe_load(file)

    resources["paths"] = paths

    with open(RESOURCE_FILE, "w") as file:
        yaml.dump(resources, file)


if __name__ == "__main__":
    main()
