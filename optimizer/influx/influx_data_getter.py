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
    timestamp: int # todo: find timestamp type


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

    # def convert_json_to_efficiency_data(
    #     self: InfluxDataGetter, influx_raw_data: list[dict]
    # ) -> dict:
    #     """
    #     Deserialize JSON data to python workable data
    #     """
    #     #custom type perhaps?
    #     #   "_value": 13200,
    #     #   "_field": "aggregate",
    #     #   "aggregator": "2",
    #     #   "auxil_data_node_id": "13",
    #     data = json.loads(json_data)

    #     efficiency_dict = dict()

    #     for object in data:
    #         # print(f'RECORD: {object["records"]}\n')
    #         for record in object["records"]:
    #             tmp_dict: dict = dict()
    #             # print(f'values: {record["values"]}\n')
    #             values: dict = record["values"]
    #             source_node: int = values["node_01"]
    #             destination_node: int = values["node_04"] # Todo: this is statically set for test topology
    #             path: tuple(int, int, int, int) = (source_node, values["node_02"], values["node_03"], destination_node)
    #             ioam_data_param: int = values["ioam_data_param"]

    #             # {'0': {'11': [{('0', '12', '1', '11'): Todo: If ingress is 0 take first non zero value and set as ingress

    #             tmp_dict[source_node] = {}
    #             tmp_dict[source_node][destination_node] = []

    #             # format ISO 8601 to uix time format
    #             datetime_obj = datetime.strptime(values["_time"], "%Y-%m-%dT%H:%M:%S.%f%z")
    #             epoch_time = int(datetime_obj.timestamp())

    #             efficiency_data = EfficiencyData = {
    #                 "aggregate_value": int(values["_value"]),
    #                 "node_id": int(values["auxil_data_node_id"]),
    #                 "timestamp": epoch_time} #todo: unix timestamp converter

    #             # Append the new data to the list
    #             tmp_dict[source_node][destination_node].append({
    #                 path: { # int value
    #                     ioam_data_param: [{ # int value
    #                         f'{Aggregator(int(values["aggregator"]))}': efficiency_data
    #                     }],
    #                 },
    #             })

    #             # pprint(tmp_dict)

    #             # Check if source_node exists in tmp_dict
    #             if source_node not in efficiency_data:
    #                 tmp_dict[source_node] = {}

    #             # Check if destination_node exists under the source_node
    #             if destination_node not in tmp_dict[source_node]:
    #                 tmp_dict[source_node][destination_node] = []



    def get_influx_raw_query_results(self: InfluxDataGetter, start: int, stop: int) -> list[dict]:
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


    def convert_influx_raw_data_to_path_efficiency_entries(self: InfluxDataGetter, influx_data: list[dict]) -> dict:
        # are grouped by data_param and aggregate
        path_efficiency_entries: list = []
        for raw_path_efficiency_entries in influx_data:
            path_efficiency_entries.append([entry["values"] for entry in raw_path_efficiency_entries])
        for path_entries in path_efficiency_entries:
            ingress: str = get_ingress(path_entries[0])
            egress: str = get_egress(path_entries[0])

            if ingress not in self.path_efficiency_dict:
                self.path_efficiency_dict[ingress] = {}
            if egress not in self.path_efficiency_dict[ingress]:
                self.path_efficiency_dict[ingress][egress] = []

            self.insert_path_entries(path_entries, ingress, egress)            

    def insert_path_entries(self: InfluxDataGetter, path_entries: dict, ingress: str, egress: str):
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
                    pprint(path_entry)
                    self.path_efficiency_dict[ingress][egress][path_index][path_key][path_entry["aggregator"]] = {
                        "aggregate": path_entry["_value"]
                    }


# helper functions
def get_ingress(path_entry: dict) -> str:
    nodes = ["node_01", "node_02", "node_03", "node_04"]
    for node in nodes:
        if path_entry[node] != "0":
            return path_entry[node]
    
def get_egress(path_entry: dict) -> str:
    return path_entry["node_04"]

def get_path_tuple(path_entry: dict) -> tuple:
    return (path_entry["node_01"], path_entry["node_02"], path_entry["node_03"], path_entry["node_04"])