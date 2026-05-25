# SUMO Signal Timing Optimization (Genetic Algorithm)

## Project Overview

Urban intersection signal timing optimization using Genetic Algorithm (GA) combined with SUMO microscopic traffic simulation. Case study: Changjiang Middle Road, Hefei.

## Tech Stack

- **Simulation**: SUMO 1.18.0 + TraCI
- **Language**: Python 3.8+
- **Optimization**: Custom Genetic Algorithm
- **Visualization**: matplotlib, pandas
- **AI Integration**: ZhipuAI scene generation

## Project Structure

```
sumo-signal-optimization-ga/
+-- src/                    # Source code
|   +-- ga_optimizer.py     # GA optimization main program
|   +-- benchmark.py        # Benchmark comparison script
|   +-- analyze_tripinfo.py # Trip information analysis
+-- config/                 # SUMO configuration
|   +-- changjiang.net.xml  # Road network (6360 lines)
|   +-- changjiang.sumocfg  # SUMO config file
|   +-- changjiang_official.net.xml  # Official signal timing
|   +-- changjiang_optimized.net.xml # GA optimized timing
|   +-- routes_final.rou.xml         # Original traffic flow
|   +-- routes_5x.rou.xml            # 5x traffic flow
+-- tests/                  # Unit tests
|   +-- test_sumo_connection.py
+-- docs/                   # Documentation & charts
|   +-- convergence_curve.png
|   +-- flow_capacity.png
|   +-- gaode_validation.png
|   +-- signal_timing.png
+-- results/                # Runtime output (gitignored)
```

## Quick Start

### Prerequisites

- SUMO 1.18.0
- Python 3.8+
- SUMO tools in PATH

### Setup

```bash
pip install -r requirements.txt
```

### Run GA Optimization

```bash
cd src
python ga_optimizer.py
```

### Run Benchmark Comparison

```bash
cd src
python benchmark.py
```

## Core Features

### Genetic Algorithm
- **Encoding**: Phase timing parameters
- **Fitness**: Average delay + queue length
- **Selection**: Tournament selection
- **Crossover**: Single-point crossover
- **Mutation**: Gaussian mutation

### Road Network
- **Location**: Changjiang Middle Road, Hefei
- **Size**: 6360 lines of NET XML
- **Signal**: 4-phase control plan
- **Lanes**: Multi-lane arterial road

### Results
- **Optimization**: +5s north-south through phase
- **Capacity**: >= 50000 pcu/h
- **Test scenarios**: 1x - 6x traffic flow multipliers

## Documentation

- [Convergence Curve](docs/convergence_curve.png)
- [Flow Capacity](docs/flow_capacity.png)
- [GAODE Validation](docs/gaode_validation.png)
- [Signal Timing](docs/signal_timing.png)

## TODO

- [ ] Add more intersection case studies
- [ ] Implement adaptive signal control
- [ ] Add reinforcement learning baseline
- [ ] Add CI/CD pipeline
- [ ] Document GA parameter tuning methodology

## License

MIT License
