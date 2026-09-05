#!/usr/bin/env python3
"""Render the APU process schematic as SVG from kg/apu_topology.json.

This is NOT a P&ID. The boiler repository we modelled the project on cites P&ID
document numbers (P&ID-8300-006 and so on) inside synthetic datasheets, pointing at
drawings that do not exist. Copying that would copy the defect: a drawing number is
the one thing an engineer assumes is traceable.

So: no document number, no title block pretending to be a plant deliverable. Every
symbol here traces to a node in the topology JSON, which in turn cites its source.
Tag names are the exact CSV column names, origin misspelling included.

Layout is editorial and lives here; content is read from the JSON, so a change to the
topology shows up in the drawing.

    python3 scripts/schematic.py        -> docs/apu_schematic.svg
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KG = ROOT / "kg/apu_topology.json"
OUT = ROOT / "docs/apu_schematic.svg"

W, H = 1600, 770
BOX_W, BOX_H, PITCH = 140, 70, 170
ROW_Y = 235
PILL_W, PILL_H, PILL_PITCH = 118, 28, 34

INK, INK2, INK3 = "#1a1d21", "#5b6470", "#8b949e"
SURF, PANEL, RULE = "#ffffff", "#f4f6f8", "#c9d1d9"
ANALOGUE, DIGITAL, FAULT = "#1f6feb", "#bf5b04", "#b3261e"

# Editorial: the order of the flow path. Content comes from the JSON.
FLOW = ["atmosphere", "intake_valve", "compressor", "cyclonic_separator",
        "outlet_valve", "air_dryer", "pneumatic_panel", "reservoirs", "clients"]
# name, then an optional subtitle. A wrapped name is NOT a subtitle: long names
# shrink to one line instead, so the second line always means something.
SHORT = {"atmosphere": ("Atmosphere", None), "intake_valve": ("Intake valve", None),
         "compressor": ("Compressor", None),
         "cyclonic_separator": ("Cyclonic separator", None),
         "outlet_valve": ("Outlet valve", None),
         "air_dryer": ("Air dryer", "towers 1 / 2"),
         "pneumatic_panel": ("Pneumatic panel", None),
         "reservoirs": ("Reservoirs", None),
         "clients": ("Clients", "suspension, brakes")}

# Which drawn box carries each documented failure mode.
FM_ANCHOR = {"fm_air_leak_drains": "pilot_valve", "fm_air_leak_clients": "clients",
             "fm_oil_leak": "compressor"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    g = json.loads(KG.read_text())
    N = {n["id"]: n for n in g["nodes"]}
    sensors = [n for n in g["nodes"] if n["type"] == "Sensor"]
    thresholds = [n for n in g["nodes"] if n["type"] == "Threshold"]
    modes = [n for n in g["nodes"] if n["type"] == "FailureMode"]

    mounted = {}
    for s in sensors:
        mounted.setdefault(s.get("mounted_on"), []).append(s)

    x = {e: 40 + i * PITCH for i, e in enumerate(FLOW)}
    o = []
    add = o.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" font-family="Inter, Helvetica, Arial, sans-serif">')
    add(f'<rect width="{W}" height="{H}" fill="{SURF}"/>')
    add('<defs><marker id="a" markerWidth="9" markerHeight="7" refX="8.5" refY="3.5" '
        f'orient="auto"><path d="M0,0 L9,3.5 L0,7 z" fill="{INK}"/></marker></defs>')

    # --- header
    add(f'<text x="40" y="42" font-size="21" font-weight="700" fill="{INK}">'
        'Air Production Unit, Metro do Porto — process schematic</text>')
    add(f'<text x="40" y="66" font-size="13" fill="{INK2}">'
        'Derived from kg/apu_topology.json. Not a P&amp;ID and not a plant document: '
        'it carries no drawing number because no drawing exists.</text>')
    add(f'<text x="40" y="86" font-size="13" fill="{INK2}">'
        'Tags are the exact MetroPT-3 CSV column names, including the origin '
        'misspelling DV_eletric.</text>')

    # --- flow line and equipment
    add(f'<line x1="{x[FLOW[0]]+BOX_W}" y1="{ROW_Y+BOX_H/2}" '
        f'x2="{x[FLOW[-1]]}" y2="{ROW_Y+BOX_H/2}" stroke="{INK}" stroke-width="2"/>')
    for a, b in zip(FLOW[:-1], FLOW[1:]):
        mx = (x[a] + BOX_W + x[b]) / 2
        add(f'<line x1="{mx-14}" y1="{ROW_Y+BOX_H/2}" x2="{mx+6}" y2="{ROW_Y+BOX_H/2}" '
            f'stroke="{INK}" stroke-width="2" marker-end="url(#a)"/>')

    for e in FLOW:
        boundary = N[e]["type"] == "Boundary"
        fill = PANEL if boundary else SURF
        dash = ' stroke-dasharray="5 3"' if boundary else ""
        add(f'<rect x="{x[e]}" y="{ROW_Y}" width="{BOX_W}" height="{BOX_H}" rx="6" '
            f'fill="{fill}" stroke="{INK}" stroke-width="2"{dash}/>')
        name, sub = SHORT[e]
        fs = 13 if len(name) <= 12 else 11.5
        y0 = ROW_Y + BOX_H / 2 + (0 if sub is None else -3) + 5
        add(f'<text x="{x[e]+BOX_W/2}" y="{y0}" font-size="{fs}" font-weight="600" '
            f'fill="{INK}" text-anchor="middle">{esc(name)}</text>')
        if sub:
            add(f'<text x="{x[e]+BOX_W/2}" y="{y0+16}" font-size="10.5" fill="{INK2}" '
                f'text-anchor="middle">{esc(sub)}</text>')

    # --- sensor pills: analogue above (rounded), digital below (square corners)
    for eq, group in mounted.items():
        if eq not in x:
            continue
        cx = x[eq] + BOX_W / 2
        for kind, sense in (("analogue", -1), ("digital", +1)):
            grp = [s for s in group if s.get("kind") == kind]
            col = ANALOGUE if kind == "analogue" else DIGITAL
            rx = 14 if kind == "analogue" else 2
            for i, s in enumerate(grp):
                if sense < 0:
                    py = ROW_Y - 26 - (len(grp) - i) * PILL_PITCH
                    ly1, ly2 = py + PILL_H, ROW_Y
                else:
                    py = ROW_Y + BOX_H + 26 + i * PILL_PITCH
                    ly1, ly2 = ROW_Y + BOX_H, py
                add(f'<line x1="{cx}" y1="{ly1}" x2="{cx}" y2="{ly2}" stroke="{col}" '
                    f'stroke-width="1.2" stroke-dasharray="3 3"/>')
                add(f'<rect x="{cx-PILL_W/2}" y="{py}" width="{PILL_W}" height="{PILL_H}" '
                    f'rx="{rx}" fill="{SURF}" stroke="{col}" stroke-width="1.8"/>')
                add(f'<text x="{cx}" y="{py+18}" font-size="11.5" font-weight="600" '
                    f'fill="{col}" text-anchor="middle">{esc(s["id"])}</text>')

    # --- the drain branch, routed clear of the pill columns
    by = 465
    dx_pilot, dx_drain = 950, 1220
    add(f'<path d="M{x["air_dryer"]+BOX_W},290 H1045 V{by-24} H{dx_drain+60} V{by}" '
        f'fill="none" stroke="{INK}" stroke-width="1.6" marker-end="url(#a)"/>')
    for label, px, sub in (("Drain pipes", dx_drain, "water discharge"),
                           ("Pilot valve", dx_pilot, "opens the drains")):
        add(f'<rect x="{px}" y="{by}" width="120" height="52" rx="6" fill="{SURF}" '
            f'stroke="{INK}" stroke-width="1.6"/>')
        add(f'<text x="{px+60}" y="{by+22}" font-size="12" font-weight="600" fill="{INK}" '
            f'text-anchor="middle">{label}</text>')
        add(f'<text x="{px+60}" y="{by+38}" font-size="10" fill="{INK2}" '
            f'text-anchor="middle">{sub}</text>')
    add(f'<line x1="{dx_pilot+120}" y1="{by+26}" x2="{dx_drain-6}" y2="{by+26}" '
        f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3" marker-end="url(#a)"/>')
    add(f'<text x="{(dx_pilot+120+dx_drain)/2}" y="{by+18}" font-size="10" fill="{INK2}" '
        f'text-anchor="middle">actuates</text>')

    # --- failure mode markers: every documented mode, numbered, keyed to the legend
    anchors = {e: (x[e] + BOX_W - 13, ROW_Y + 13) for e in FLOW}
    anchors["pilot_valve"] = (dx_pilot + 13, by + 13)
    fm_num = {}
    for i, m in enumerate(modes, 1):
        fm_num[m["id"]] = i
        cx, cy = anchors[FM_ANCHOR[m["id"]]]
        add(f'<path d="M{cx},{cy-9} l9,9 l-9,9 l-9,-9 z" fill="{FAULT}"/>')
        add(f'<text x="{cx}" y="{cy+4}" font-size="10" font-weight="700" fill="{SURF}" '
            f'text-anchor="middle">{i}</text>')

    # --- legend: thresholds, symbols, failure modes
    lx, ly = 40, 560
    add(f'<rect x="{lx}" y="{ly}" width="1520" height="185" rx="8" fill="{PANEL}" '
        f'stroke="{RULE}"/>')

    add(f'<text x="{lx+22}" y="{ly+28}" font-size="13" font-weight="700" fill="{INK}">'
        'Documented thresholds</text>')
    ty = ly + 50
    for t in sorted(thresholds, key=lambda z: (str(z["signal"]), z["value"])):
        sign = {"below": "&lt;", "above": "&gt;", "about": "≈"}[t["sense"]]
        add(f'<text x="{lx+22}" y="{ty}" font-size="11.5" fill="{INK2}">'
            f'<tspan font-weight="600" fill="{INK}">{esc(str(t["signal"]))}</tspan>'
            f'  {sign} {t["value"]} {t["units"]}  —  {esc(t["description"])}</text>')
        ty += 19

    sx = lx + 500
    add(f'<text x="{sx}" y="{ly+28}" font-size="13" font-weight="700" fill="{INK}">'
        'Symbols</text>')
    add(f'<rect x="{sx}" y="{ly+40}" width="66" height="22" rx="11" fill="{SURF}" '
        f'stroke="{ANALOGUE}" stroke-width="1.8"/>')
    add(f'<text x="{sx+78}" y="{ly+55}" font-size="11.5" fill="{INK2}">'
        'analogue tag (rounded)</text>')
    add(f'<rect x="{sx}" y="{ly+72}" width="66" height="22" rx="2" fill="{SURF}" '
        f'stroke="{DIGITAL}" stroke-width="1.8"/>')
    add(f'<text x="{sx+78}" y="{ly+87}" font-size="11.5" fill="{INK2}">'
        'digital tag (square)</text>')
    add(f'<rect x="{sx}" y="{ly+104}" width="66" height="22" rx="4" fill="{PANEL}" '
        f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 3"/>')
    add(f'<text x="{sx+78}" y="{ly+119}" font-size="11.5" fill="{INK2}">'
        'system boundary</text>')
    add(f'<path d="M{sx+33},{ly+136} l9,9 l-9,9 l-9,-9 z" fill="{FAULT}"/>')
    add(f'<text x="{sx+78}" y="{ly+151}" font-size="11.5" fill="{INK2}">'
        'documented failure mode</text>')

    fx = lx + 800
    add(f'<text x="{fx}" y="{ly+28}" font-size="13" font-weight="700" fill="{INK}">'
        'Documented failure modes</text>')
    fy = ly + 50
    for m in modes:
        cx = fx + 9
        add(f'<path d="M{cx},{fy-13} l9,9 l-9,9 l-9,-9 z" fill="{FAULT}"/>')
        add(f'<text x="{cx}" y="{fy-0.5}" font-size="10" font-weight="700" fill="{SURF}" '
            f'text-anchor="middle">{fm_num[m["id"]]}</text>')
        txt = m["description"]
        if len(txt) > 88:
            txt = txt[:86].rsplit(" ", 1)[0] + "…"
        add(f'<text x="{fx+26}" y="{fy}" font-size="11.5" fill="{INK2}">'
            f'<tspan font-weight="600" fill="{INK}">{esc(m["component"])}</tspan>  '
            f'{esc(txt)}</text>')
        fy += 22
    add(f'<text x="{fx}" y="{ly+128}" font-size="10.5" fill="{INK3}">'
        'All three come from the 2022 sibling dataset. They are what this hardware '
        'does,</text>')
    add(f'<text x="{fx}" y="{ly+144}" font-size="10.5" fill="{INK3}">'
        'not events in our window: the four MetroPT-3 reports are all mode 1 or 2.'
        '</text>')

    add(f'<text x="{lx+22}" y="{ly+172}" font-size="10.5" fill="{INK3}">'
        f'{len(sensors)} tags, {len(thresholds)} thresholds, {len(modes)} failure modes. '
        'Source: Data Description_Metro.pdf (UCI zip), primary; flow path from '
        'arXiv:2207.05466.</text>')

    add("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}  ({len(sensors)} tags, {len(thresholds)} thresholds)")


if __name__ == "__main__":
    main()
