#!/bin/bash
set -e

# Create a new bucket using influx CLI
influx bucket create --name ${INFLUXDB_AGGREGATED_BUCKET} --org ${INFLUXDB_ORG} --retention ${INFLUXDB_RETENTION}
influx bucket create --name ${INFLUXDB_RAW_BUCKET} --org ${INFLUXDB_ORG} --retention ${INFLUXDB_RETENTION}