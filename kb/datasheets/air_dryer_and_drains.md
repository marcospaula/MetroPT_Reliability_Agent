---
synthetic: true
title: Air dryer, towers and drain circuit
component: air_dryer
sources: Data Description_Metro.pdf (UCI zip); arXiv:2207.05466
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## What it is

A twin-tower desiccant dryer downstream of the compressor outlet valve. One tower dries
the air while the other drains the humidity it removed. A pneumatic pilot valve opens
the drain pipes to discharge that water.

## Instrumentation (sourced)

| tag | kind | what it reads |
|---|---|---|
| DV_pressure | analogue, bar | the pressure drop generated when the towers discharge. **A zero reading means the compressor is working under load** |
| Towers | digital | inactive means tower one is working, active means tower two |
| Pressure_switch | digital | detects the discharge in the air-drying towers |

## Failure mode on this circuit (sourced, from the 2022 sibling dataset)

An air leak caused by the pneumatic pilot valve malfunctioning and opening the drain
pipes while the compressor is running. In that instance the train recovered in service
rather than being withdrawn.

This is the mode most likely to be behind the MetroPT-3 reports, all four of which are
recorded only as "air leak, high stress" with no component named.
