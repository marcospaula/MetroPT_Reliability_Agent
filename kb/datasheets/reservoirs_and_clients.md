---
synthetic: true
title: Reservoirs and downstream clients
component: reservoirs
sources: Data Description_Metro.pdf (UCI zip)
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## What it is

Air storage downstream of the pneumatic panel, feeding the vehicle's clients: the
secondary suspension and the brakes.

## Instrumentation (sourced)

| tag | kind | what it reads |
|---|---|---|
| Reservoirs | analogue, bar | downstream reservoir pressure, **which should be close to TP3** |
| LPS | digital | active when pressure drops below 7 bar |
| Caudal_impulses | digital | counts pulse outputs from the absolute amount of air flowing from the APU to the reservoirs |

## A free instrumentation check

The source states that `Reservoirs` should track `TP3`. That makes the pair a
redundancy check available on 1.5 million rows with no label: a persistent divergence
between them is either a leak between the panel and the reservoirs, or a drifting
transmitter. Neither has been tested in this repository yet.

## Failure mode (sourced, from the 2022 sibling dataset)

An air leak on the pipe feeding the clients. In that instance the train had to be moved
to the maintenance building rather than recovering in service, so the client-side leak
is the more severe of the two air-leak locations.
