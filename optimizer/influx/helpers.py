from .types import Aggregator

def get_ingress(path_entry: dict) -> str:
    nodes = ["node_01", "node_02", "node_03", "node_04"]
    for node in nodes:
        if path_entry[node] != "0":
            return int(path_entry[node])


def get_egress(path_entry: dict) -> str:
    return int(path_entry["node_04"])


def get_path_tuple(path_entry: dict) -> tuple:
    return (
        int(path_entry["node_01"]),
        int(path_entry["node_02"]),
        int(path_entry["node_03"]),
        int(path_entry["node_04"]),
    )


def is_empty_node_list(node_list: tuple) -> bool:
    node_id_sum = 0
    for node_id in node_list:
        node_id_sum += node_id
    if node_id_sum == 0:
        return True
    return False


def get_aggregator(path_entry: dict) -> Aggregator:
    match path_entry["aggregator"]:
        case "1":
            return Aggregator.SUM
        case "2":
            return Aggregator.MIN
        case "4":
            return Aggregator.MAX


def extract_path_entries_from_raw_data(influx_data: list) -> list[dict]:
    path_entries: list = []
    for raw_path_entries in influx_data:
        path_entries.append(raw_path_entries[0]["values"])
    return path_entries
