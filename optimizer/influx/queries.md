# InfluxDB Queries

1. Get efficiency data grouped by path.

```
from(bucket: "raw_data_export")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "netflow")
  |> filter(fn: (r) => r["flags"] == "0")
  |> filter(fn: (r) => r["_field"] == "aggregate")
  |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param"])
```

```
from(bucket: "raw_data_export")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r["_measurement"] == "netflow")
  |> filter(fn: (r) => r["flags"] == "0")
  |> filter(fn: (r) => r["_field"] == "aggregate")
  |> group(columns: ["node_01", "node_02", "node_03", "node_04", "ioam_data_param", "aggregator"])
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  ```