import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import ipaddress


class InfluxDataGetter:
    def __init__(self, raw_bucket, aggregated_bucket, org, token, url):
        # making all variables which are needed multiple times
        self.raw_bucket = raw_bucket
        self.aggregated_bucket = aggregated_bucket
        self.org = org
        self.token = token
        self.url = url

        # defining the API Client
        client = influxdb_client.InfluxDBClient(
            url=self.url, token=self.token, org=self.org
        )

        # initializing the API Client
        self.query_api = client.query_api()


    def get_path_metrics(self, start: int, stop: int):
        query = (
            f'''from(bucket: "{self.raw_bucket}")\n
            |> range(start: {start}, stop: {stop})\n
            |> filter(fn: (r) => r["_measurement"] == "netflow")\n
            |> filter(fn: (r) => r["flags"] == "0")\n
            |> filter(fn: (r) => r["_field"] == "aggregate")\n
            |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param"])\n
            '''
        )
        result = self.query_api.query(org=self.org, query=query)
        print(result)