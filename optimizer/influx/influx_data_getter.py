from __future__ import annotations
from pprint import pprint
import influxdb_client
import json
from influxdb_client.client.flux_table import FluxStructureEncoder, TableList
from enum import Enum
from typing import Dict, List, TypedDict


class Aggregator(Enum):
    """
    Aggregator type identifier
    """
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

    def convert_json_to_efficiency_data(
        self: InfluxDataGetter, json_data: str
    ) -> dict:
        """
        Deserialize JSON data to python workable data
        """
        #custom type perhaps?
        #   "_value": 13200,
        #   "_field": "aggregate",
        #   "aggregator": "2",
        #   "auxil_data_node_id": "13",
        data = json.loads(json_data)

        efficiency_dict = dict()

        for object in data:
            # print(f'RECORD: {object["records"]}\n')
            for record in object["records"]:
                tmp_dict: dict = dict()
                # print(f'values: {record["values"]}\n')
                values: dict = record["values"]
                source_node: int = values["node_01"]
                destination_node: int = values["node_04"] # Todo: this is statically set for test topology
                path: tuple(int, int, int, int) = (source_node, values["node_02"], values["node_03"], destination_node)
                ioam_data_param: int = values["ioam_data_param"]

                # {'0': {'11': [{('0', '12', '1', '11'): Todo: If ingress is 0 take first non zero value and set as ingress

                tmp_dict[source_node] = {}
                tmp_dict[source_node][destination_node] = []

                efficiency_data = EfficiencyData = {
                    "aggregate_value": int(values["_value"]),
                    "node_id": int(values["auxil_data_node_id"]),
                    "timestamp": 1231412} #todo: unix timestamp converter

                # Append the new data to the list
                tmp_dict[source_node][destination_node].append({
                    path: { # int value
                        ioam_data_param: [{ # int value
                            f'{Aggregator(int(values["aggregator"]))}': efficiency_data
                        }],
                    },
                })

                # Check if source_node exists in tmp_dict
                if source_node not in efficiency_data:
                    tmp_dict[source_node] = {}

                # Check if destination_node exists under the source_node
                if destination_node not in tmp_dict[source_node]:
                    tmp_dict[source_node][destination_node] = []

        # tmp_dict["source"] = "14"
        pprint(tmp_dict)

        # extracted = self.extract_efficiency_data(data)

        # for first_list in data:
            # print(f'{coloum}\n')


        # print(extracted)

    def get_efficiency_data(
        self: InfluxDataGetter, start: int, stop: int
    ) -> EfficiencyDataByIngress:
        """
        Query InfluxDB and return a EfficiencyDataByIngress object

        Args:
            self (InfluxDataGetter): The instance of object used to query the influxDB.
            start (int): The unix time stamp of the start of the time range to include data.
            end (int): The unix time stamp of the end of the time range to include data.

        Returns:
            EfficiencyDataByIngress: The efficiency data grouped by ingress router.
        """

        query: str = f"""from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param"])\n
            """

        tables: TableList = self.query_api.query(org=self.org, query=query)
        json_tables: str = json.dumps(tables, cls=FluxStructureEncoder, indent=2)
        efficiency_data = self.convert_json_to_efficiency_data(
            json_tables
        )
        # print(efficiency_data)
        # print(f'AAAAAAAAAAAAA: {type(efficiency_data)}')
        return efficiency_data
