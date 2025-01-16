from __future__ import annotations
from datetime import datetime
from pprint import pprint
from influxdb_client.client.flux_table import FluxStructureEncoder, TableList
from enum import Enum
from typing import TypedDict

import json
import influxdb_client

# import pytz


class Aggregator(Enum):
    SUM = 1
    MIN = 2
    MAX = 4


class EfficiencyData(TypedDict):
    """
    Inside aggregator type
    """

    aggregate_value: int
    node_id: int
    timestamp: int  # todo: find timestamp type


class InfluxDataGetter:
    def __init__(
        self: InfluxDataGetter,
        raw_bucket: str,
        aggregated_bucket: str,
        org: str,
        token: str,
        url: str,
    ) -> InfluxDataGetter:
        # making all variables which are needed multiple times
        self.raw_bucket = raw_bucket
        self.aggregated_bucket = aggregated_bucket
        self.org = org
        self.token = token
        self.url = url

        # defining the API Client
        client: influxdb_client.InfluxDBClient = influxdb_client.InfluxDBClient(
            url=self.url, token=self.token, org=self.org
        )

        # initializing the API Client
        self.query_api: influxdb_client.QueryAPI = client.query_api()

        self.path_efficiency_dict: dict = {}

        self.known_path_set: set = set()

    def get_influx_raw_query_results(
        self: InfluxDataGetter, start: int, stop: int
    ) -> list[dict]:
        query: str = f"""from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param", "aggregator"])\n
            |> median(column: "_value")\n
            """

        tables: TableList = self.query_api.query(org=self.org, query=query)
        json_query_results: str = json.dumps(tables, cls=FluxStructureEncoder, indent=2)
        query_results: dict = json.loads(json_query_results)
        return [result["records"] for result in query_results]

    def get_path_efficiency_by_ingress(
        self: InfluxDataGetter, start: int, stop: int
    ) -> dict:
        influx_raw_data: list[dict] = self.get_influx_raw_query_results(start, stop)
        self.convert_influx_raw_data_to_path_efficiency_entries(influx_raw_data)
        return self.path_efficiency_dict

    def convert_influx_raw_data_to_path_efficiency_entries(
        self: InfluxDataGetter, influx_data: list[dict]
    ) -> dict:
        # are grouped by data_param and aggregate
        path_efficiency_entries: list = []
        for raw_path_efficiency_entries in influx_data:
            path_efficiency_entries.append(
                [entry["values"] for entry in raw_path_efficiency_entries]
            )
        for path_entries in path_efficiency_entries:
            ingress: int = get_ingress(path_entries[0])
            egress: int = get_egress(path_entries[0])

            if ingress not in self.path_efficiency_dict:
                self.path_efficiency_dict[ingress] = {}
            if egress not in self.path_efficiency_dict[ingress]:
                self.path_efficiency_dict[ingress][egress] = []

            self.insert_path_entries(path_entries, ingress, egress)

    def insert_path_entries(
        self: InfluxDataGetter, path_entries: dict, ingress: str, egress: str
    ):
        path_key: tuple = get_path_tuple(path_entries[0])
        path_index = 0

        if path_key not in self.known_path_set:
            self.path_efficiency_dict[ingress][egress].append({path_key: {}})
            self.known_path_set.add(path_key)
            path_index = -1
        else:
            for i, path in enumerate(self.path_efficiency_dict[ingress][egress]):
                if path_key in path:
                    path_index = i
                    break

        for path_entry in path_entries:
            data_param: int = int(path_entry["ioam_data_param"])
            if (
                data_param
                not in self.path_efficiency_dict[ingress][egress][path_index][path_key]
            ):
                self.path_efficiency_dict[ingress][egress][path_index][path_key][
                    data_param
                ] = {}
            self.path_efficiency_dict[ingress][egress][path_index][path_key][
                data_param
            ][get_aggregator(path_entry)] = {"aggregate": path_entry["_value"]}


# helper functions
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


def get_aggregator(path_entry: dict) -> Aggregator:
    match path_entry["aggregator"]:
        case "1":
            return Aggregator.SUM
        case "2":
            return Aggregator.MIN
        case "4":
            return Aggregator.MAX
