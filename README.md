# SUMO Signal Timing Optimization

A reproducible signal timing experiment for the simplified Changjiang Middle
Road–Huizhou Avenue intersection in Hefei. The model uses the repository's
SUMO network and demand files. The scripts run independent SUMO simulations
to compare green time allocations at intersection J1.

## Run in SUMO GUI

Tested with SUMO 1.18.0. Run from the repository root with the SUMO binaries on
your PATH:

~~~powershell
sumo-gui -c config/changjiang.sumocfg --start --delay 110
~~~

The default configuration loads the optimized program. To see the equal
split, add `--additional-files config/signal_equal.add.xml` to the command.

## Reproduce the search and comparison

Use Python 3.9+ and SUMO 1.18.0. The two scripts use the Python standard
library. Set `SUMO_HOME` to the installation directory or put `sumo` on PATH.

~~~powershell
python src/ga_optimizer.py
python src/benchmark.py
~~~

The search uses a fixed seed and a fresh simulation for each distinct
candidate. It evaluates 1x demand with seed 42 and writes both signal programs
into `config/`. The benchmark compares them at 1x for 3,600 seconds with
seeds 42 and 43, and at 5x for 1,800 seconds with seed 42. Each pair uses the
same network, demand, seed, and horizon.

Both programs release one approach at a time. They use a 120-second cycle,
with 3 seconds of amber and 1 second of all-red after each approach. Green
times in east, west, north and south approach order are 26/26/26/26 seconds
for the equal split and 26/33/31/14 seconds for the selected split. The search
ranks candidates by collisions and teleports, vehicles waiting to depart,
mean time loss plus mean departure delay, then completed trips.

| Demand and seed | Mean time loss, equal to optimized | Completed trips, equal to optimized |
| --- | --- | --- |
| 1x, seed 42 | 43.535 s to 38.918 s | 2,095 to 2,093 |
| 1x, seed 43 | 43.530 s to 38.883 s | 2,095 to 2,095 |
| 5x, seed 42 | 95.197 s to 92.894 s | 3,610 to 3,685 |

In the 5x run, vehicles still waiting to depart at the cutoff decreased
from 1,426 to 1,349. All six runs recorded zero collisions and teleports.
See the [reference comparison](docs/benchmark_reference.json) for the output.
Means include vehicles already inserted but still on the road at the cutoff.
The report also counts completed trips, vehicles still on the road, and
vehicles waiting to depart, which matters under heavy demand.

The network is a schematic model. Its inherited J1 junction has no
right-of-way conflict matrix. The approach programs and measurements describe
this simulation experiment. The earlier network variants remain available
for reference.

## License

MIT
