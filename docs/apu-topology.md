# APU topology, item 4 of the pre-code checks

6 September 2026. Built from a published description, not invented, and not taken from
the boiler repository. The machine-readable form is `kg/apu_topology.json`.

## Source

Veloso B, Gama J, Ribeiro RP, Pereira PM. *A Benchmark dataset for predictive
maintenance*. arXiv:2207.05466v3, 18 July 2022. Sections "Data Records" and
"Technical Validation".

That paper documents the **2022** MetroPT dataset, not ours. The topology is the same
physical unit (the APU of a Metro do Porto vehicle) and the sensor definitions carry
over by name, but **nothing numeric from that paper may be carried into our life
table**. Its failure dates belong to a different unit-year. See
`findings-2026-09-06.md`.

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
| H1 | pressure above 10.2 bar | valve activated by the command pressure switch |
| LPS | pressure below 7 bar | low pressure signal |
| Motor current | ~0 A | compressor off |
| Motor current | ~4 A | compressor running offloaded |
| Motor current | ~7 A | compressor running under load |
| DV pressure | equal to zero | compressor is working under load |

The 8.2 to 10.2 bar span is the operating band, and 7 bar is the floor. An air leak
should show as a shortened cycle: the unit reaching 8.2 bar again sooner, so more
load periods per hour, at higher duty. That is the hypothesis layer 5 has to test,
and it is testable without any label.

## Sensors

Seven analogue and eight digital, matching the 15 columns of MetroPT-3.

| tag | kind | what it measures | described in the source? |
|---|---|---|---|
| TP2 | analogue | pressure at the compressor | yes |
| TP3 | analogue | pressure at the pneumatic panel | yes |
| H1 | analogue | pressure at the H1 valve | yes |
| DV_pressure | analogue | pressure drop when the dryer towers discharge water | yes |
| Oil_temperature | analogue | compressor oil temperature | yes |
| Motor_current | analogue | motor current | yes |
| Reservoirs | analogue | reservoir pressure | **no** |
| COMP | digital | air intake valve electrical signal | yes |
| DV electric | digital | commands the compressor outlet valve | yes |
| TOWERS | digital | which dryer tower is drying, which is draining | yes |
| MPG | digital | activates the intake valve below 8.2 bar | yes |
| LPS | digital | active below 7 bar | yes |
| Oil Level | digital | active when oil is below expected | yes |
| Pressure Switch | digital | command pressure switch | **no** |
| Caudal Impulse | digital | flow pulse | **no** |

**Three tags of our dataset have no published description**: Reservoirs, Pressure Switch
and Caudal Impulse. Their entries above are inferred from the tag name and from the
flow path, and they are marked as inferred in the JSON. They must not be described to a
user as documented until a source is found. Note that this is exactly the gap count
implied by the source itself, which claims eight analogue and eight digital signals
while naming only six of each.

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
