import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json


class influx_data:
    def __init__(self):
        self.raw_bucket = "raw_data_export"
        self.aggregated_bucket = "aggregated_data_export"
        self.org = "OST"
        self.token = "DkX-6JeCjrHwlmbb6Ts2zxnHwFFNery4_YkufMAr4GSiESF187x-C9UkCciWNhfd8JqWro_9fo6-Sz7f3NuYpw=="
        self.url = "http://localhost:8086/"

        client = influxdb_client.InfluxDBClient(
            url=self.url, token=self.token, org=self.org
        )

        self.query_api = client.query_api()

    def makeprovisionary_aggregate_results(self, api_response):
        results = []
        x = 0
        for table in api_response:
            results.append([])
            for record in table.records:
                results[x].append(
                    {
                        record.get_field(): [
                            record.get_value(),
                            record.values.get("flow_label"),
                        ]
                    }
                )
            x += 1

        return results

    def basic_aggregated_query(self, time):
        query = (
            'from(bucket: "'
            + self.aggregated_bucket
            + '")\
        |> range(start: -'
            + str(time)
            + 'm)\
        |> filter(fn: (r) => r["_measurement"] == "netflow")\
        |> filter(fn: (r) => r["type_5052"] == "0x01")\
        |> group(columns: ["flow_label"])'
        )

        result = self.query_api.query(org=self.org, query=query)
        results = self.makeprovisionary_results(result)
        print(results)
        print("\n")
        print("\n")

        final_results = {}
        for flow in results:
            print(len(flow))
            final_results[list(flow[3].values())[0][1]] = {
                list(flow[0].keys())[0]: list(flow[0].values())[0][0],
                list(flow[1].keys())[0]: list(flow[1].values())[0][0],
                list(flow[2].keys())[0]: list(flow[2].values())[0][0],
                list(flow[3].keys())[0]: list(flow[3].values())[0][0],
            }

        return final_results

    def makeprovisionary_raw_results(self, api_response):
        results = []
        for table in api_response:
            for record in table.records:
                results.append(
                    {
                        record.get_field(): [
                            record.get_value(),
                            record.values.get("flow_label"),
                        ]
                    }
                )
        return results

    def basic_raw_query(self, time):
        query = (
            'from(bucket: "'
            + self.raw_bucket
            + '")\
        |> range(start: -'
            + str(time)
            + 'm)\
        |> filter(fn: (r) => r["_measurement"] == "netflow")'
        )

        result = self.query_api.query(org=self.org, query=query)
        results = self.makeprovisionary_raw_results(result)

        with open("output.json", "w") as f:
            json.dump(results, f)

        return results


data = influx_data()
print(data.basic_raw_query(10))
