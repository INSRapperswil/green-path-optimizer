#!/bin/bash
set -e

# Create a new bucket using influx CLI
influx bucket create --name aggregated_data_export --org OST --retention 10d
influx bucket create --name raw_data_export --org OST --retention 10d