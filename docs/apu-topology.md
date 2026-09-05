# APU topology, item 4 of the pre-code checks

5 September 2026. Built from a published description, not invented, and not taken from
the boiler repository. The machine-readable form is `kg/apu_topology.json`.

> **Revised the same day**, after the CSV was downloaded and the primary source read.
> Three claims below were wrong and are corrected in place: H1's meaning and mounting,
> the existence of a cyclonic separator, and the assertion that three tags were
> undocumented. See `findings-2026-09-05.md` for what went wrong and why.

## Sources

**Primary**: `Data Description_Metro.pdf`, shipped inside the UCI zip for MetroPT-3.
It is not linked from the dataset page, and it is the authority for anything about
*our* dataset.

**Secondary**, for the flow path only: Veloso B, Gama J, Ribeiro RP, Pereira PM.
*A Benchmark dataset for predictive maintenance*. arXiv:2207.05466v3, 2022.

Where the two disagree, the primary source wins. They do disagree, on H1.

That paper documents the **2022** MetroPT dataset, not ours. The topology is the same
physical unit (the APU of a Metro do Porto vehicle) and the sensor definitions carry
over by name, but **nothing numeric from that paper may be carried into our life
table**. Its failure dates belong to a different unit-year. See
`findings-2026-09-05.md`.

## What the APU is

An Air Production Unit mounted on the roof of the vehicle. It compresses, dries and
stores air, then feeds it to onboard clients: the secondary suspension that holds
vehicle height regardless of passenger load, and the brakes. There is **no redundancy**,
so a failure removes the train from service immediately. The paper reports more than
170 cancelled trips from this cause in 2017 alone.

The reliability consequence is worth stating plainly: single unit, no redundancy,
immediate service loss. Availability here is driven by failure rate and repair time
directly, with no capacity to hide a fault.

## Flow path

```
atmosphere
  -> intake valve            (commanded by MPG, state reported by COMP)
  -> compressor              (motor current, oil temperature, oil level, TP2)
  -> cyclonic separator      (H1 reads its discharge)
  -> outlet valve            (DV electric commands it; DV pressure reads the drop)
  -> air dryer, towers 1/2   (TOWERS selects which dries and which drains)
  -> drain pipes             (pilot valve; failure mode of the 2022 air leak #1)
  -> pneumatic panel         (TP3)
  -> reservoirs              (Reservoirs)
  -> clients: suspension, brakes
```

Control is pressure-driven, on a load and unload cycle rather than a modulating loop.
This is the structural difference from the boiler: there is no setpoint being trimmed,
there is a machine cycling between states.

## Documented thresholds

These are the closest thing this dataset has to the boiler's alarm setpoint register,
and unlike that repository's documents they come from a published source.

| signal | threshold | meaning |
|---|---|---|
| MPG | pressure below 8.2 bar | activates the intake valve, starting the compressor under load |
| LPS | pressure below 7 bar | low pressure signal |
| Motor current | ~0 A | compressor off |
| Motor current | ~4 A | compressor running offloaded |
| Motor current | ~7 A | compressor running under load |
| Motor current | ~9 A | starting |
| DV pressure | equal to zero | compressor is working under load |

The 10.2 bar figure that appeared here previously belongs to the 2022 variant, not to
ours, and has been removed. What the primary source fixes is the 8.2 bar load trigger
and the 7 bar floor. An air leak
should show as a shortened cycle: the unit reaching 8.2 bar again sooner, so more
load periods per hour, at higher duty. That is the hypothesis layer 5 has to test,
and it is testable without any label.

## Sensors

Seven analogue and eight digital, matching the 15 columns of MetroPT-3.

| tag | kind | what it measures | described in the source? |
|---|---|---|---|
| TP2 | analogue | pressure at the compressor | yes |
| TP3 | analogue | pressure at the pneumatic panel | yes |
| H1 | analogue | pressure drop when the **cyclonic separator filter** discharges | yes, primary |
| DV_pressure | analogue | pressure drop when the dryer towers discharge water | yes |
| Oil_temperature | analogue | compressor oil temperature | yes |
| Motor_current | analogue | current of one phase of the three-phase motor | yes |
| Reservoirs | analogue | downstream reservoir pressure, should track TP3 | yes, primary |
| COMP | digital | air intake valve electrical signal | yes |
| DV_eletric | digital | commands the compressor outlet valve | yes |
| Towers | digital | which dryer tower is drying, which is draining | yes |
| MPG | digital | activates the intake valve below 8.2 bar | yes |
| LPS | digital | active below 7 bar | yes |
| Oil_level | digital | active when oil is below expected | yes |
| Pressure_switch | digital | detects the discharge in the air-drying towers | yes, primary |
| Caudal_impulses | digital | counts pulses of the air flowing from the APU to the reservoirs | yes, primary |

**All fifteen tags are documented** in the primary source, and no node in the graph is
inferred any more. The earlier claim that Reservoirs, Pressure Switch and Caudal
Impulse were undocumented came from treating the dataset page and the 2022 paper as
the source, when the source was inside the download.

Tag ids in the JSON are the **exact CSV column names**, including the origin
misspelling `DV_eletric`.

The primary source also states that reservoir pressure should sit close to TP3. That
is carried in the graph as a `SHOULD_TRACK` edge: a redundancy check available on 1.5
million rows without any label.

Instrumentation is measured, not assumed: the sensor datasheets are cited in the source
as IFM PT5414 (pressure), LEM AT-B420L (AC current) and WIKA TC12-M (thermocouple).

## Failure modes seen on this unit

From the 2022 maintenance reports, so indicative of what the hardware does, not
evidence about our window:

- **Air leak at the drain pipes**, caused by a pneumatic pilot valve malfunctioning
  and opening the drains while the compressor runs. The train recovered in service.
- **Air leak on the pipe feeding the clients** (brakes, suspension). The train had to
  be moved to the maintenance building.
- **Oil leak at the compressor.** No oil warning reaches the driver by design, so the
  leak ran until it damaged the motor, after which air pressure dropped and the train
  was removed.

The third one is a design observation worth keeping: the `Oil Level` digital signal
exists in the data but does not reach the driver. A detector built on this dataset
therefore has real value on that mode, and that is a defensible claim about the
system, not a modelling flourish.

Our four events are all air leaks, so the oil path is out of scope for the life table
but stays in the graph.
