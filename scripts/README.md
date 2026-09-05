# scripts/

Deliberately empty. The design lives in `docs/design-sketch-2026-09-05.md`; nothing is
written before the checks under "Before writing code" have passed.

Planned order:

1. `ingest.py`      raw CSV to DuckDB, with continuity and gap checks
2. `events.py`      failure reports to a life table with censoring
3. `reliability.py` life fitting, ranges, Weibayes where events are scarce
4. `kg.py`          loads kg/apu_topology.json and answers topology queries
                    (the graph itself is already written, by hand, from a cited source)
5. `mcp_server.py`  exposes historian, events, graph and documents as tools

Already written, because the checks they belong to are closed:
`exposure.py`, `cycles.py`, `reliability.py`, `schematic.py`.
