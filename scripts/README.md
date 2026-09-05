# scripts/

Run in this order from the repository root, with the venv:

| | |
|---|---|
| `ingest.py` | raw CSV to `data/metropt.duckdb`: the historian, the gaps, the life table and the tag metadata, with the operating-time clock materialised |
| `reliability.py` | writes `data/events.csv` and estimates the rate, the trend and what is not estimable |
| `exposure.py` | shows the logging gaps are the machine off, not lost telemetry |
| `cycles.py` | tests whether the load cycle shortens before a failure |
| `schematic.py` | renders `docs/apu_schematic.svg` from `kg/apu_topology.json` |
| `mcp_server.py` | serves the historian, life table and topology as MCP tools |

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/reliability.py     # writes data/events.csv
.venv/bin/python scripts/ingest.py          # needs data/raw/, see data/README.md
.venv/bin/python scripts/mcp_server.py --selftest
```

`reliability.py` runs before `ingest.py` because the database loads the life table
it writes.

Still to build: the document base under `kb/`, and a `kb_search` tool over it.
