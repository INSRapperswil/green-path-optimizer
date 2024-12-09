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

    def makeprovisionary_aggregate_results(self, api_response):
        # get all the data out of the InfluxTables and put it into a list to be used later
        results = []
        for i, table in enumerate(api_response):
            results.append([])
            for record in table.records:
                results[i].append(
                    {
                        record.get_field(): [
                            record.get_value(),
                            record.values.get("flow_label"),
                        ]
                    }
                )
        return results

    def basic_aggregated_query(self, time):
        # define the query
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

        # make theAPI query and get the Data in a usable format
        result = self.query_api.query(org=self.org, query=query)
        results = self.makeprovisionary_aggregate_results(result)

        # make a dict in the format we want and input all the data
        final_results = {}
        for flow in results:
            final_results[list(flow[3].values())[0][1]] = {
                list(flow[0].keys())[0]: list(flow[0].values())[0][0],
                list(flow[1].keys())[0]: list(flow[1].values())[0][0],
                list(flow[2].keys())[0]: list(flow[2].values())[0][0],
                list(flow[3].keys())[0]: list(flow[3].values())[0][0],
            }

        # return these results
        return final_results

    def makeprovisionary_raw_results(self, api_response):
        # get all the data from the Influx tables and make it easily usable for later steps
        results = []
        for i, table in enumerate(api_response):
            results.append([])
            results[i].append(
                {
                    "flow_label": table.records[0].values.get("flow_label"),
                    "aggregator": table.records[0].values.get("aggregator"),
                }
            )
            results[i].append(
                {
                    "source_ipv6": table.records[0].values.get("source_ipv6"),
                    "destination_ipv6": table.records[0].values.get("destination_ipv6"),
                    "namespace_id": table.records[0].values.get("namespace_id"),
                    "auxil_data_node_id": table.records[0].values.get(
                        "auxil_data_node_id"
                    ),
                }
            )
            results[i].append(
                {
                    "node1": table.records[0].values.get("node_01"),
                    "node2": table.records[0].values.get("node_02"),
                    "node3": table.records[0].values.get("node_03"),
                    "node4": table.records[0].values.get("node_04"),
                }
            )
            for record in table.records:
                results[i].append({record.get_field(): record.get_value()})

        return results

    def makefinal_raw_results(self, prov_results):
        # make a entry in the dict for each flow
        fin_res = {}
        for flow in prov_results:
            fin_res[flow[0]["flow_label"]] = []

        for flow in prov_results:
            for dict in flow:
                # get each value needed for each flow
                if str(list(dict.keys())[0]) == "aggregate":
                    aggregate = [str(list(dict.keys())[0]), int(list(dict.values())[0])]
                elif str(list(dict.keys())[0]) == "ioam_data_param":
                    ioam_data_param = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_01":
                    hop_limit_node_01 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_02":
                    hop_limit_node_02 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_03":
                    hop_limit_node_03 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_04":
                    hop_limit_node_04 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_count":
                    hop_count = [str(list(dict.keys())[0]), int(list(dict.values())[0])]

            # map the aggregator the the set String
            if int(flow[0]["aggregator"]) == 1:
                sec_lvl_key = "SUM"
            if int(flow[0]["aggregator"]) == 2:
                sec_lvl_key = "MIN"
            if int(flow[0]["aggregator"]) == 4:
                sec_lvl_key = "MAX"

            # fin_res[flow[0]["flow_label"]] = {str(sec_lvl_key):{
            #     "generic":{
            #         str(list(flow[1].keys())[0]):str(ipaddress.ip_address(list(flow[1].values())[0])),
            #         str(list(flow[1].keys())[1]):str(ipaddress.ip_address(list(flow[1].values())[1])),
            #         str(list(flow[1].keys())[2]):str(list(flow[1].values())[2])
            #     },
            #     "ioam_aggr":{
            #         ioam_data_param[0]:ioam_data_param[1],
            #         aggregate[0]:aggregate[1],
            #         str(list(flow[1].keys())[3]):str(list(flow[1].values())[3]),
            #         hop_count[0]:hop_count[1]
            #     },
            #     "ioam_trace":
            #         [
            #             {str(list(flow[2].keys())[0]):[str(list(flow[2].values())[0]),hop_limit_node_01[1]]},
            #             {str(list(flow[2].keys())[1]):[str(list(flow[2].values())[1]),hop_limit_node_02[1]]},
            #             {str(list(flow[2].keys())[2]):[str(list(flow[2].values())[2]),hop_limit_node_03[1]]},
            #             {str(list(flow[2].keys())[3]):[str(list(flow[2].values())[3]),hop_limit_node_04[1]]},
            #         ]
            #     }}

            # input the data into the Table in the Format we want which corresponds to a normal json format
            fin_res[flow[0]["flow_label"]].append(
                {
                    str(sec_lvl_key): {
                        "generic": {
                            str(list(flow[1].keys())[0]): str(
                                ipaddress.ip_address(list(flow[1].values())[0])
                            ),
                            str(list(flow[1].keys())[1]): str(
                                ipaddress.ip_address(list(flow[1].values())[1])
                            ),
                            str(list(flow[1].keys())[2]): str(
                                list(flow[1].values())[2]
                            ),
                        },
                        "ioam_aggr": {
                            ioam_data_param[0]: ioam_data_param[1],
                            aggregate[0]: aggregate[1],
                            str(list(flow[1].keys())[3]): str(
                                list(flow[1].values())[3]
                            ),
                            hop_count[0]: hop_count[1],
                        },
                        "ioam_trace": [
                            {
                                "node_id": str(list(flow[2].values())[0]),
                                "hop_limit": hop_limit_node_01[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[1]),
                                "hop_limit": hop_limit_node_02[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[2]),
                                "hop_limit": hop_limit_node_03[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[3]),
                                "hop_limit": hop_limit_node_04[1],
                            },
                        ],
                    }
                }
            )

        return fin_res

    def basic_raw_query(self, time):
        # define the query
        query = (
            'from(bucket: "'
            + self.raw_bucket
            + '")\
        |> range(start: -'
            + str(time)
            + 'm)\
        |> filter(fn: (r) => r["_measurement"] == "netflow")\
        |> filter(fn: (r) => r["_field"] != "fwd_status" and r["_field"] != "fwd_reason")\
        |> filter(fn: (r) => r["flags"] == "0")\
        |> group(columns: ["flow_label","aggregator"])'
        )

        # make the query, make the provisionary results and then make the final results and return all these results
        result = self.query_api.query(org=self.org, query=query)
        results = self.makeprovisionary_raw_results(result)
        fin_result = self.makefinal_raw_results(results)

        return fin_result

    def makefinal_raw_results_by_query(self, prov_results):
        # make the final table in the format wanted
        fin_res = {}

        for flow in prov_results:
            # make all the empty table in which the data will be input
            for dict in flow:
                if str(list(dict.keys())[0]) == "ioam_data_param":
                    ioam_data_param = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]

            if int(flow[0]["aggregator"]) == 1:
                sec_lvl_key = "SUM"
            if int(flow[0]["aggregator"]) == 2:
                sec_lvl_key = "MIN"
            if int(flow[0]["aggregator"]) == 4:
                sec_lvl_key = "MAX"

            if str(ipaddress.ip_address(list(flow[1].values())[0])) not in list(
                fin_res.keys()
            ):
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))] = {}
            if str(ipaddress.ip_address(list(flow[1].values())[1])) not in list(
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))].keys()
            ):
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                    str(ipaddress.ip_address(list(flow[1].values())[1]))
                ] = {}
            if str(list(flow[0].values())[0]) not in list(
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                    str(ipaddress.ip_address(list(flow[1].values())[1]))
                ].keys()
            ):
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                    str(ipaddress.ip_address(list(flow[1].values())[1]))
                ][list(flow[0].values())[0]] = {}
            if str(ioam_data_param) not in list(
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                    str(ipaddress.ip_address(list(flow[1].values())[1]))
                ][list(flow[0].values())[0]].keys()
            ):
                fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                    str(ipaddress.ip_address(list(flow[1].values())[1]))
                ][list(flow[0].values())[0]][str(ioam_data_param[1])] = []

        for flow in prov_results:
            # get all the data to input into the tables
            for dict in flow:
                if str(list(dict.keys())[0]) == "aggregate":
                    aggregate = [str(list(dict.keys())[0]), int(list(dict.values())[0])]
                elif str(list(dict.keys())[0]) == "ioam_data_param":
                    ioam_data_param = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_01":
                    hop_limit_node_01 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_02":
                    hop_limit_node_02 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_03":
                    hop_limit_node_03 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_limit_node_04":
                    hop_limit_node_04 = [
                        str(list(dict.keys())[0]),
                        int(list(dict.values())[0]),
                    ]
                elif str(list(dict.keys())[0]) == "hop_count":
                    hop_count = [str(list(dict.keys())[0]), int(list(dict.values())[0])]

            # map the aggregator to the string needed
            if int(flow[0]["aggregator"]) == 1:
                sec_lvl_key = "SUM"
            if int(flow[0]["aggregator"]) == 2:
                sec_lvl_key = "MIN"
            if int(flow[0]["aggregator"]) == 4:
                sec_lvl_key = "MAX"

            # input all the data into the empty tables
            fin_res[str(ipaddress.ip_address(list(flow[1].values())[0]))][
                str(ipaddress.ip_address(list(flow[1].values())[1]))
            ][list(flow[0].values())[0]][str(ioam_data_param[1])].append(
                {
                    sec_lvl_key: {
                        "generic": {
                            str(list(flow[1].keys())[2]): str(list(flow[1].values())[2])
                        },
                        "ioam_aggr": {
                            aggregate[0]: aggregate[1],
                            str(list(flow[1].keys())[3]): str(
                                list(flow[1].values())[3]
                            ),
                            hop_count[0]: hop_count[1],
                        },
                        "ioam_trace": [
                            {
                                "node_id": str(list(flow[2].values())[0]),
                                "hop_limit": hop_limit_node_01[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[1]),
                                "hop_limit": hop_limit_node_02[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[2]),
                                "hop_limit": hop_limit_node_03[1],
                            },
                            {
                                "node_id": str(list(flow[2].values())[3]),
                                "hop_limit": hop_limit_node_04[1],
                            },
                        ],
                    }
                }
            )
        return fin_res

    def basic_raw_query_by_src_dst(self, time):
        # define the query to get the data needed
        query = (
            'from(bucket: "'
            + self.raw_bucket
            + '")\
        |> range(start: -'
            + str(time)
            + 'm)\
        |> filter(fn: (r) => r["_measurement"] == "netflow")\
        |> filter(fn: (r) => r["_field"] != "fwd_status" and r["_field"] != "fwd_reason")\
        |> filter(fn: (r) => r["flags"] == "0")\
        |> group(columns: ["source_ipv6","destination_ipv6","flow_label","ioam_data_param","aggregator"])'
        )

        # make the query, make provisionary results and then definite results
        result = self.query_api.query(org=self.org, query=query)
        results = self.makeprovisionary_raw_results(result)
        fin_result = self.makefinal_raw_results_by_query(results)

        return fin_result
