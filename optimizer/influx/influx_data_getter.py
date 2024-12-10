from __future__ import annotations  # needed to make type annotations for own class work

import influxdb_client
import json
from influxdb_client.client.flux_table import FluxStructureEncoder, TableList

# from enum import Enum
from typing import TypedDict


# class Aggregator(Enum):
#     SUM = 1
#     MIN = 2
#     MAX = 4


class EfficiencyData(TypedDict):
    aggregate: int
    auxil_data_node_id: int


class EfficiencyDataByAggregator(TypedDict):
    aggregator: EfficiencyData


class EfficiencyDataByDataParam(TypedDict):
    data_param: EfficiencyDataByAggregator


class EfficiencyDataByPath(TypedDict):
    path: EfficiencyDataByDataParam


class EfficiencyDataByEgress(TypedDict):
    egress: EfficiencyDataByPath


class EfficiencyDataByIngress(TypedDict):
    ingress: EfficiencyDataByEgress


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
    ) -> EfficiencyDataByIngress:
        print(json_data)

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
        efficiency_data: EfficiencyDataByIngress = self.convert_json_to_efficiency_data(
            json_tables
        )
        return efficiency_data
