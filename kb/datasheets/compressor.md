---
synthetic: true
title: Compressor and motor
component: compressor
sources: Data Description_Metro.pdf (UCI zip); arXiv:2207.05466
---

> **This is a derived note, not a plant document.** No maintenance manual, datasheet or
> procedure for this unit has been published. Everything below is either quoted from the
> sources named above or measured by this repository, and each statement says which.

## What it is

The air compressor of the Air Production Unit, roof-mounted on a Metro do Porto
vehicle. It draws atmospheric air through the intake valve and delivers it, via the
cyclonic separator and the outlet valve, to the twin-tower air dryer.

**There is no redundancy.** The APU feeds the secondary suspension, which holds vehicle
height regardless of passenger load, and the brakes. Loss of the APU removes the train
from service immediately. The sources report more than 170 trips cancelled for this
reason in 2017.

## Instrumentation (sourced)

| tag | kind | what it reads |
|---|---|---|
| TP2 | analogue, bar | pressure at the compressor |
| Motor_current | analogue, A | current of one phase of the three-phase motor |
| Oil_temperature | analogue, degC | oil temperature |
| Oil_level | digital | active when the oil is below the expected level |

Sensor hardware named by the sources: IFM PT5414 pressure transmitter, LEM AT-B420L AC
current transducer, WIKA TC12-M thermocouple.

## Motor current levels (sourced)

Approximately 0 A off, 4 A running offloaded, 7 A running under load, 9 A starting.

**Measured caveat.** In the published MetroPT-3 file these are nominal labels, not
thresholds. 54.7 % of samples sit below 1 A, 30.1 % between 3 and 5 A, and the running
median is about 5.7 A. The 9 A start level appears in **7 samples out of 1,516,948**,
because a start transient of a few seconds cannot survive the 10:1 decimation of the
published file. Do not test for starts in this data.

## The oil warning that does not reach the driver

The `Oil_level` signal exists in the data, but the sources record that by hardware
design no oil warning reaches the train driver. In the sibling 2022 dataset an oil leak
therefore ran unchecked until it damaged the motor, after which air pressure dropped and
the train had to be removed. A detector built on this signal addresses a real gap.
