# data/

Nothing here goes into git. The raw CSV is 208 MB.

```
data/
  raw/            original UCI CSV, as downloaded
  metropt.duckdb  historian built from raw
  events.csv      life table derived from the operator's failure reports
```

## Obtaining the data

Page: https://archive.ics.uci.edu/dataset/791/metropt+3+dataset
CC BY 4.0. Direct download, no registration.

Save the file as `data/raw/MetroPT3(AirCompressor).csv` and **check its hash** before
building anything on top of it.

## The failure reports

The CSV series is **unlabelled**. The failures come from operator reports published
alongside the INESC TEC group's papers, not from inside the CSV. Locating the primary
source of those dates is the project's first task: without it there is no life table,
and without a life table there is no reason for this repository to exist.
