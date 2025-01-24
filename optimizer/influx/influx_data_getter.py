from __future__ import annotations

from influxdb_client.client.flux_table import FluxStructureEncoder, TableList
from .helpers import (
    get_ingress,
    get_egress,
    get_path_tuple,
    get_aggregator,
    is_empty_node_list,
    extract_path_entries_from_raw_data,
)

import json
import influxdb_client


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
        self.last_used_path_dict: dict = {}
        self.known_path_set: set = set()

    def run_influx_query(self: InfluxDataGetter, query: str) -> list[dict]:
        tables: TableList = self.query_api.query(org=self.org, query=query)
        json_query_results: str = json.dumps(tables, cls=FluxStructureEncoder, indent=2)
        query_results: dict = json.loads(json_query_results)
        return [result["records"] for result in query_results]

    def get_path_efficiency_by_ingress(
        self: InfluxDataGetter, start: int, stop: int, record_aggregator: str
    ) -> dict:
        if record_aggregator == "median":
            query: str = f"""from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param", "aggregator"])\n
            |> median(column: "_value")\n
            |> group()\n
            """
        elif record_aggregator == "last":
            query: str = f"""from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param", "aggregator"])\n
            |> last(column: "_value")\n
            |> group()\n
            """
        elif record_aggregator == "mean":
            query: str = f"""from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param", "aggregator"])\n
            |> mean(column: "_value")\n
            |> group()\n
            """
        else:
            raise ValueError("Unsupported record aggregator")

        influx_raw_data: list[dict] = self.run_influx_query(query)
        path_entries = extract_path_entries_from_raw_data(influx_raw_data)
        self.insert_into_path_efficiency_dict(path_entries)
        return self.path_efficiency_dict

    def get_last_used_paths_by_ingress(
        self: InfluxDataGetter, start: int, stop: int
    ) -> dict:
        query: str = f"""from(bucket: "{self.raw_bucket}")\n
        |> range(start: {start}, stop: {stop})\n
        |> filter(fn: (r) => r["_measurement"] == "netflow")\n
        |> filter(fn: (r) => r["flags"] == "0")\n
        |> filter(fn: (r) => r["_field"] == "aggregate")\n
        |> group(columns: ["node_01", "node_02", "node_03", "node_04"])\n
        |> last(column: "_value")\n
        |> group()\n
        |> sort(columns: ["_time"], desc: true)\n
        """
        influx_raw_data: list[dict] = self.run_influx_query(query)
        path_entries = extract_path_entries_from_raw_data(influx_raw_data)
        self.insert_into_last_path_usage_dict(path_entries)
        return self.last_used_path_dict

    def insert_into_path_efficiency_dict(
        self: InfluxDataGetter, path_entries: list[dict]
    ) -> None:
        for entry in path_entries:
            path_key: tuple = get_path_tuple(entry)

            # skip path entry in case node list is empty
            if is_empty_node_list(path_key):
                continue

            ingress: int = get_ingress(entry)
            egress: int = get_egress(entry)

            # insert ingress/egress nodes if not existing
            if ingress not in self.path_efficiency_dict:
                self.path_efficiency_dict[ingress] = {}
            if egress not in self.path_efficiency_dict[ingress]:
                self.path_efficiency_dict[ingress][egress] = []

            # insert path_dict into provisioned list in ingress egress dict
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

            data_param: int = int(entry["ioam_data_param"])

            path_dict_entry = self.path_efficiency_dict[ingress][egress][path_index][
                path_key
            ]

            if data_param not in path_dict_entry:
                path_dict_entry[data_param] = {}

            path_dict_entry[data_param][get_aggregator(entry)] = {
                "aggregate": entry["_value"],
                "time": entry["_time"],
            }

    def insert_into_last_path_usage_dict(
        self: InfluxDataGetter, path_entries: list[dict]
    ) -> None:
        for entry in path_entries:
            path_key: tuple = get_path_tuple(entry)

            # skip path entry in case node list is empty
            if is_empty_node_list(path_key):
                continue

            ingress: int = get_ingress(entry)
            egress: int = get_egress(entry)

            # insert ingress/egress nodes if not existing
            if ingress not in self.last_used_path_dict:
                self.last_used_path_dict[ingress] = {}

            if egress not in self.last_used_path_dict[ingress]:
                self.last_used_path_dict[ingress][egress] = path_key
