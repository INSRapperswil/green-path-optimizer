from influx.influx_data_getter import InfluxDataGetter
from os import environ
from pprint import pprint


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
    idg.get_path_metrics(1733846800, 1733846920)
    # pprint(result)


if __name__ == "__main__":
    main()
