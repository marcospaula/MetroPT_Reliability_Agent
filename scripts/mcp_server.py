#!/usr/bin/env python3
"""MCP server exposing the APU historian, life table and topology as tools.

Four data sources, one tool group each, which is the pattern this project borrows
from ScottDuncanAI/industrial-ai-troubleshooting-agent (see ATTRIBUTION.md). The
fifth group, reliability, is the one that dataset cannot support.

Two conventions run through every tool and are the point of the whole repository:

  Operating time, not calendar. The logging gaps are the machine off, so any rate
  denominated in calendar days is 22 % optimistic. Tools that return a rate say
  which clock they used.

  An event is not an anomaly. `events_life_table` returns the four failures the
  operator reported. Nothing inferred from the signal ever enters it.

Run directly for a self-check, or over stdio from an MCP client:

    .venv/bin/python scripts/mcp_server.py --selftest
    .venv/bin/python scripts/mcp_server.py
"""
import json
import sys
from pathlib import Path

import duckdb
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/metropt.duckdb"
KG = ROOT / "kg/apu_topology.json"
KB = ROOT / "kb"
MAX_ROWS = 3000

mcp = FastMCP("metropt-apu")
_con = None
_kg = None


def con():
    global _con
    if _con is None:
        if not DB.exists():
            raise RuntimeError(f"{DB} missing: run scripts/ingest.py first")
        _con = duckdb.connect(str(DB), read_only=True)
    return _con


def kg():
    global _kg
    if _kg is None:
        _kg = json.loads(KG.read_text())
    return _kg


def rows(sql, params=None):
    cur = con().execute(sql, params or [])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def historian_tags() -> str:
    """List the 15 signals with units, what they measure, and their documented
    thresholds. Start here: tag names are exact and include the origin
    misspelling DV_eletric."""
    return json.dumps(rows("SELECT * FROM tags ORDER BY kind, tag"), indent=2)


@mcp.tool()
def historian_window() -> str:
    """The extent of the data: first and last timestamp, calendar span, operating
    span, and how much of the calendar is missing."""
    r = rows("""SELECT min(timestamp) AS first, max(timestamp) AS last,
                       count(*) AS samples, max(operating_days) AS operating_days
                FROM historian""")[0]
    cal = (r["last"] - r["first"]).total_seconds() / 86400
    r = {k: str(v) for k, v in r.items()}
    r["calendar_days"] = round(cal, 2)
    r["operating_days"] = round(float(r["operating_days"]), 2)
    r["missing_share"] = f'{1 - r["operating_days"]/cal:.1%}'
    r["note"] = ("The missing time is the machine off, not lost telemetry: pressure "
                 "decays monotonically with gap length. Denominate rates in operating "
                 "days.")
    return json.dumps(r, indent=2, default=str)


@mcp.tool()
def historian_get_tag_data(tags: list[str], start: str, end: str,
                           downsample_minutes: int = 0) -> str:
    """Time series for one or more tags between two timestamps ('YYYY-MM-DD HH:MM:SS').

    downsample_minutes averages into buckets; 0 returns raw 10 s samples. Requests
    are capped, so widen the bucket rather than narrowing the window when a long
    period is wanted."""
    known = {r["tag"] for r in rows("SELECT tag FROM tags")}
    bad = [t for t in tags if t not in known]
    if bad:
        return json.dumps({"error": f"unknown tags {bad}", "known": sorted(known)})
    cols = ", ".join(f'"{t}"' for t in tags)
    if downsample_minutes > 0:
        avg = ", ".join(f'avg("{t}") AS "{t}"' for t in tags)
        sql = (f"SELECT time_bucket(INTERVAL '{downsample_minutes} minutes', timestamp)"
               f" AS timestamp, {avg} FROM historian WHERE timestamp BETWEEN ? AND ?"
               f" GROUP BY 1 ORDER BY 1 LIMIT {MAX_ROWS + 1}")
    else:
        sql = (f"SELECT timestamp, {cols} FROM historian WHERE timestamp BETWEEN ? AND ?"
               f" ORDER BY timestamp LIMIT {MAX_ROWS + 1}")
    data = rows(sql, [start, end])
    truncated = len(data) > MAX_ROWS
    out = {"rows": len(data[:MAX_ROWS]), "truncated": truncated, "data": data[:MAX_ROWS]}
    if truncated:
        out["hint"] = "capped: raise downsample_minutes to cover the whole window"
    return json.dumps(out, indent=2, default=str)


@mcp.tool()
def historian_gaps(min_hours: float = 1.0, limit: int = 50) -> str:
    """Periods with no logging, which are periods with the machine off. Useful for
    reconstructing downtime the maintenance record states only partially."""
    data = rows("SELECT * FROM gaps WHERE gap_hours >= ? ORDER BY gap_hours DESC LIMIT ?",
                [min_hours, limit])
    total = rows("SELECT count(*) AS n, sum(gap_hours)/24 AS days FROM gaps")[0]
    return json.dumps({"gaps_over_60s_total": total["n"],
                       "days_not_operating": round(total["days"], 2),
                       "returned": len(data), "gaps": data}, indent=2, default=str)


@mcp.tool()
def events_life_table() -> str:
    """The life table: four reported air-leak failures and one right-censored
    suspension, with intervals on both the calendar and the operating clock.

    These are the operator's maintenance reports, reproduced with their own defects.
    Nothing detected from the signal belongs in this table."""
    data = rows("SELECT * FROM events ORDER BY operating_days_from_start")
    return json.dumps({
        "events": data,
        "source": "Data Description_Metro.pdf, shipped inside the UCI zip",
        "known_defects_in_the_source": [
            "two reports are numbered #1 and there is no #2",
            "the 29 May failure records maintenance on 30 April, a month earlier",
        ],
        "warning": ("The four reports are not an exhaustive list of anomalies. The "
                    "cleanest unreported episode is 12 March 2020: 11.7 h continuously "
                    "under load at 58 % duty, the highest in the series, on live "
                    "channels. It is an anomalous episode, not a failure, and it does "
                    "not enter this table."),
        "do_not_use": ("23-24 June 2020 looks like the largest excursion in the data "
                       "and is an ACQUISITION FREEZE, not an event: five analogue "
                       "channels hold one value each across 18,515 samples while a "
                       "digital channel toggles on a fixed 40 s / 10 s square wave. Ten "
                       "such blocks exist. Any cycle-based indicator must mask them "
                       "first. See docs/data-quality.md and scripts/freeze.py."),
    }, indent=2, default=str)


@mcp.tool()
def reliability_summary(clock: str = "operating") -> str:
    """Failure rate and trend for the APU. clock is 'operating' or 'calendar'.

    Reports an interval, never a bare point estimate: with four events the interval
    spans a factor of about seven, and that spread is the result."""
    from scipy.stats import chi2, norm
    import numpy as np
    if clock not in ("operating", "calendar"):
        return json.dumps({"error": "clock must be 'operating' or 'calendar'"})
    w = rows("""SELECT min(timestamp) AS a, max(timestamp) AS b,
                       max(operating_days) AS op FROM historian""")[0]
    T = w["op"] if clock == "operating" else (w["b"] - w["a"]).total_seconds() / 86400
    # Order by the failure instant, never by the value being read. Ordering by
    # `calendar_days_since_prev` would sort the intervals by LENGTH, and the
    # cumulative sum would then describe a process that never happened: it flips
    # the apparent trend without changing a single input.
    col = ("operating_days_from_start" if clock == "operating"
           else "calendar_days_since_prev")
    ev = rows(f"SELECT {col} AS t FROM events WHERE censored = 0 "
              f"ORDER BY failure_start")
    ts = np.array([e["t"] for e in ev], dtype=float)
    if clock == "calendar":
        ts = np.cumsum(ts)
    n = len(ts)
    U = float((ts.mean() - T / 2) / (T * np.sqrt(1 / (12 * n))))
    beta = float(n / np.sum(np.log(T / ts)))
    return json.dumps({
        "clock": clock,
        "exposure_days": round(T, 2),
        "failures": n,
        "mtbf_days": round(T / n, 1),
        "mtbf_90pct_interval_days": [round(2 * T / chi2.ppf(0.95, 2 * n + 2), 1),
                                     round(2 * T / chi2.ppf(0.05, 2 * n), 1)],
        "rate_per_year": round(365 * n / T, 1),
        "laplace_U": round(U, 3),
        "laplace_p": round(float(2 * (1 - norm.cdf(abs(U)))), 2),
        "trend": "none detectable at 5 %" if abs(U) < 1.96 else "trend present",
        "crow_amsaa_beta_mle": round(beta, 2),
        "crow_amsaa_beta_bias_corrected": round(beta * (n - 1) / n, 2),
        "crow_amsaa_beta_90pct_interval": [
            round(beta * chi2.ppf(0.05, 2 * n) / (2 * n), 2),
            round(beta * chi2.ppf(0.95, 2 * n) / (2 * n), 2)],
        "not_estimable": ["MTTR", "availability"],
        "why": ("one report has no maintenance record and another's precedes its own "
                "failure, leaving two usable repair times that differ eightfold"),
        "do_not": ("read the Crow-AMSAA point estimate as wear-out: the interval "
                   "contains 1, and four events cannot separate a shape"),
    }, indent=2)


@mcp.tool()
def kg_component(name: str) -> str:
    """What a component or tag is, what it connects to, and which sensors watch it.
    Every node carries the source it came from."""
    g = kg()
    node = next((n for n in g["nodes"] if n["id"].lower() == name.lower()), None)
    if node is None:
        return json.dumps({"error": f"unknown node {name!r}",
                           "known": sorted(n["id"] for n in g["nodes"])})
    nid = node["id"]
    return json.dumps({
        "node": node,
        "downstream": [l["target"] for l in g["links"]
                       if l["source"] == nid and l["relationship"] == "FLOW"],
        "upstream": [l["source"] for l in g["links"]
                     if l["target"] == nid and l["relationship"] == "FLOW"],
        "edges": [l for l in g["links"] if nid in (l["source"], l["target"])],
    }, indent=2)


@mcp.tool()
def kb_search(query: str, limit: int = 4) -> str:
    """Search the note base for what a component is, how the control works, what a
    failure looks like in this data, and where the data will mislead you.

    Every note is derived and labelled synthetic: no manual or datasheet for this unit
    has been published. Notes state their sources, and distinguish what is quoted from
    what this repository measured. Ranking is BM25-ish over sections, so ask in the
    words the notes would use ("air leak signature", "why the calendar rate is wrong")."""
    import math
    import re
    docs = []
    for path in sorted(KB.rglob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text()
        head, _, body = text.partition("---\n\n")
        for chunk in re.split(r"\n(?=## )", body):
            if chunk.strip():
                docs.append((str(path.relative_to(ROOT)), chunk.strip()))
    if not docs:
        return json.dumps({"error": f"no notes under {KB}"})

    terms = [t for t in re.findall(r"[a-z_0-9]+", query.lower()) if len(t) > 2]
    tok = [re.findall(r"[a-z_0-9]+", c.lower()) for _, c in docs]
    N, avg = len(docs), sum(len(t) for t in tok) / len(docs)
    df = {t: sum(1 for d in tok if t in d) for t in terms}
    scored = []
    for i, d in enumerate(tok):
        sc = 0.0
        for t in terms:
            if not df.get(t):
                continue
            f = d.count(t)
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            sc += idf * f * 2.5 / (f + 1.5 * (0.25 + 0.75 * len(d) / avg))
        if sc > 0:
            scored.append((sc, i))
    scored.sort(reverse=True)
    if not scored:
        return json.dumps({"query": query, "hits": 0,
                           "notes_available": sorted({p for p, _ in docs})})
    out = [{"source": docs[i][0], "score": round(sc, 2),
            "section": docs[i][1][:1400]} for sc, i in scored[:limit]]
    return json.dumps({"query": query, "hits": len(scored), "results": out,
                       "note": "all sources are derived notes, labelled synthetic"},
                      indent=2)


def selftest():
    print("historian_window:", historian_window()[:120].replace("\n", " "), "...")
    for fn, args in [(historian_tags, ()), (historian_gaps, ()),
                     (events_life_table, ()), (reliability_summary, ()),
                     (kg_component, ("compressor",)),
                     (kb_search, ("air leak signature load cycle",)),
                     (historian_get_tag_data,
                      (["TP3", "Motor_current"], "2020-07-15 14:00",
                       "2020-07-15 20:00", 10))]:
        out = fn(*args)
        assert '"error"' not in out[:200], out[:200]
        print(f"  {fn.__name__:<26} ok  ({len(out):,} chars)")
    print("\nall tools answered")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        mcp.run()
