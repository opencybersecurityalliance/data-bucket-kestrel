# SQLite data

- `bh22.db`: all data from our Black Hat USA 2022
- `ecs2sqlite.py`: convert ECS [elasticdump](https://github.com/elasticsearch-dump/elasticsearch-dump) exported data to SQlite
    - Usage: provide the db file name, table, and a list of NDJSON .json files to ingest
    - Example: `./ecs2sqlite.py bh22.db events ../elasticsearch/win-111-winlogbeat-bh22-20220727.json ../elasticsearch/win-112-winlogbeat-bh22-20220727.json ../elasticsearch/linux-91-sysflow-bh22-20220727.json`
