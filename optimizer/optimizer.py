from influx.influx_data_getter import InfluxDataGetter, Aggregator
from os import environ
from time import time
from pprint import pprint


IOAM_DATA_PARAM = 255

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
    # current_time = int(time())
    # efficiency_data = idg.get_efficiency_data(current_time - 30, current_time)
    efficiency_data = {
        14: {
            11: [
                {
                    (0, 14, 2, 11): {
                        255: [
                            {
                                Aggregator.SUM: {
                                    "aggregate": 15000,
                                    "time": 1733919990
                                }
                            },
                            {
                                Aggregator.SUM: {
                                    "aggregate": 20000,
                                    "time": 1733919995
                                }
                            }
                        ]
                    },
                },
                {
                    (0, 14, 3, 11): {
                        255: [
                            {
                                Aggregator.SUM: {
                                    "aggregate": 9000,
                                    "time": 1733919990
                                }
                            },
                            {
                                Aggregator.SUM: {
                                    "aggregate": 11000,
                                    "time": 1733919995
                                }
                            }
                        ]
                    },
                }
            ]
        }
    }
    sort_efficiency_data(efficiency_data, IOAM_DATA_PARAM, Aggregator.SUM)
    pprint(efficiency_data)


def get_latest_aggregate(item: dict, data_param: int, aggregator: Aggregator):
    _, value = list(item.items())[0] # Unpack the dictionary to access the inner structure
    latest_entry = value[data_param][-1]  # Get the last entry from the list under key data_param
    return latest_entry[aggregator]['aggregate']  # Extract the 'aggregate' value


def sort_efficiency_data(efficiency_data: dict, data_param: int, aggregator: Aggregator):
        """
        Sorts the path list for each ingress and egress according to the given data_param and aggregator

        Args:
            efficiency_data (dict): The ingress to egress to path mapping returned by the influx data getter
            data_param (int): The identifier of the data param to optimize for
            aggregator (Aggregator): The aggregator to optimize for

        Returns:
            efficiency_data (dict): The sorted ingress to egress to path mapping returned by the influx data getter
        """

        if aggregator != Aggregator.SUM:
            raise RuntimeError("The provided aggregator is not supported")

        for ingress, egress_dict in efficiency_data.items():
            for egress, paths in egress_dict.items():
                paths.sort(key=lambda item: get_latest_aggregate(item, data_param, aggregator))



if __name__ == "__main__":
    main()
