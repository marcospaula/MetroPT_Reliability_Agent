#!/usr/bin/env python3
"""Build the historian database from the raw CSV.

Creates data/metropt.duckdb with four tables:

  historian   1,516,948 rows, timestamp plus the 15 signals, as published
  gaps        every break longer than 60 s, which exposure.py shows is the
              machine being off rather than lost telemetry
  events      the life table, read from data/events.csv
  tags        one row per signal, joined from kg/apu_topology.json so that
              descriptions and thresholds travel with the data

The operating-time clock is materialised as a column on `historian`, because
every reliability question asked of this dataset needs it and recomputing it
per query is wasteful.

    .venv/bin/python scripts/ingest.py
"""
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data/raw/MetroPT3(AirCompressor).csv"
DB = ROOT / "data/metropt.duckdb"
KG = ROOT / "kg/apu_topology.json"
EVENTS = ROOT / "data/events.csv"
GAP_S = 60


def main():
    if not CSV.exists():
        raise SystemExit(f"missing {CSV}\nsee data/README.md for how to fetch it")
    if DB.exists():
        DB.unlink()
    con = duckdb.connect(str(DB))

    con.execute(f"""
        CREATE TABLE historian AS
        -- column00 is the unnamed index column of the published file: 0 to
        -- 15,169,470 in steps of 10, the trace of the 10:1 decimation. Dropped.
        SELECT * EXCLUDE (column00) FROM read_csv_auto('{CSV}', header=true)
    """)
    n = con.execute("SELECT count(*) FROM historian").fetchone()[0]

    # Operating seconds: every sample carries its own step, a gap carries none.
    con.execute(f"""
        CREATE TABLE hist2 AS
        SELECT *, sum(step_s) OVER (ORDER BY timestamp) / 86400.0 AS operating_days
        FROM (
            SELECT *, CASE
                WHEN d IS NULL OR d > {GAP_S} THEN 0.0 ELSE d
            END AS step_s
            FROM (
                SELECT *, date_diff('second', lag(timestamp) OVER (ORDER BY timestamp),
                                    timestamp) AS d
                FROM historian
            )
        )
    """)
    con.execute("DROP TABLE historian")
    con.execute("ALTER TABLE hist2 RENAME TO historian")

    con.execute(f"""
        CREATE TABLE gaps AS
        SELECT prev AS gap_start, timestamp AS gap_end, d AS gap_seconds,
               d / 3600.0 AS gap_hours
        FROM (
            SELECT timestamp, lag(timestamp) OVER (ORDER BY timestamp) AS prev,
                   date_diff('second', lag(timestamp) OVER (ORDER BY timestamp),
                             timestamp) AS d
            FROM historian
        ) WHERE d > {GAP_S}
        ORDER BY gap_start
    """)

    con.execute(f"CREATE TABLE events AS SELECT * FROM read_csv_auto('{EVENTS}', header=true)")

    kg = json.loads(KG.read_text())
    thr = {}
    for t in kg["nodes"]:
        if t["type"] == "Threshold":
            thr.setdefault(t["signal"], []).append(
                f'{t["sense"]} {t["value"]} {t["units"]}: {t["description"]}')
    rows = [(s["id"], s.get("kind"), s.get("units"), s.get("mounted_on"),
             s["description"], "; ".join(thr.get(s["id"], [])), bool(s.get("sourced")))
            for s in kg["nodes"] if s["type"] == "Sensor"]
    con.execute("""CREATE TABLE tags (tag VARCHAR, kind VARCHAR, units VARCHAR,
                   mounted_on VARCHAR, description VARCHAR, thresholds VARCHAR,
                   sourced BOOLEAN)""")
    con.executemany("INSERT INTO tags VALUES (?,?,?,?,?,?,?)", rows)

    lo, hi, op = con.execute(
        "SELECT min(timestamp), max(timestamp), max(operating_days) FROM historian"
    ).fetchone()
    print(f"historian  {n:,} rows, {lo} to {hi}")
    print(f"           {op:.2f} operating days of "
          f"{(hi-lo).total_seconds()/86400:.2f} calendar")
    for t in ("gaps", "events", "tags"):
        print(f"{t:<11}{con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:>10,} rows")
    con.close()
    print(f"\nwrote {DB} ({DB.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
