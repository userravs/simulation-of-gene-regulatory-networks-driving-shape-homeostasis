# Project History and Roadmap

This document summarizes the major development milestones of the Gene Regulatory Networks (GRN) shape homeostasis simulation project and tracks the roadmap derived from the original 2017 thesis notes. For detailed release notes, see [`CHANGELOG.md`](../CHANGELOG.md) and [`VERSION`](../VERSION).

---

## Release & Milestone History

### `v0.3.0` — Unified Headless Engine, Thomas ADI Solver, Evolution, Interactive Inspector & CI/Test Suite (2026)
- **Unified Headless Core & Golden Numerical Parity Fixtures**: Decoupled `core/` and `evolution/` from Matplotlib via `core/engine.py` (`SimulationConfig`, `SimulationEngine`, `StepSnapshot`, `SimulationResult`, `run_simulation`), consolidated all four duplicated simulation loops (`core/main.py`, `evolution/main_ga.py`, `evolution/neat_parallel.py`, `visualization/web_app.py`, `analysis/graph_evaluation.py`), replaced $O(M^2)$ cell deletion with $O(M)$ Fisher-Yates shuffling, added deterministic PRNG seeding, and added golden numerical parity fixtures (`tests/fixtures/golden_parity_v0_2.json`).
- **Precomputed $O(N^2)$ Thomas ADI Solver & `(y, x)` Coordinate Standardization**: Replaced per-step $O(N^3)$ `np.linalg.inv` in `LGFDiffEq` with a Numba `@njit` precomputed Thomas tridiagonal factorization (`LGFThomasSolver`, verified within `1e-12` against dense Crank-Nicolson and preserving zero-flux Neumann mass conservation), standardized row-major `(y, x)` coordinates across `core/`, `evolution/`, and `visualization/`, and updated `docs/architecture.md`.
- **GA Offspring Diversity & NEAT `config-ca` Alignment**: Fixed `[-1, 1]` weight initialization (`initialize_population`), single-copy elitism with distinct tournament parents (`select_tournament_parents`, `create_next_generation`), per-gene Gaussian mutation with optional weight bounds, explicit multiprocessing genome passing (`evaluate_genome`, `run_ga`), and aligned `config/config-ca` (`fitness_threshold = 0.95` on `[0, 1]`, `neat-python 2.0` compatibility).
- **Accessible Visualization, Headless Timelapse Export & Web Telemetry**: Added centralized Okabe-Ito colorblind-safe and legacy palettes (`visualization/palettes.py`), headless PNG/GIF `TimelapseExporter` (`visualization/timelapse.py`), deterministic seed controls, 1:1 square heatmaps, instant **Run Full Horizon** batch mode with **Timeline Scrubber**, per-step telemetry curves, and **Shape Homeostasis Summary** ($F$, $S_{T/2}$, $S_T$, $\Delta$) in `visualization/web_app.py`.
- **Interactive GA Evolution, Phase-Space Decision Map, Directed GRN Graph & Vector Overlays**: Wired Tab 2 (`Analysis`) in `visualization/web_app.py` to `tools_ga` operators (`run_evolution_pass`) with a **Load Best Evolved GRN into Simulation** bridge, interactive 2D `(SGF, LGF)` steady-state decision maps (`compute_phase_space_map`, `create_phase_space_plot`), directed excitatory/inhibitory GRN topology graphs (`create_grn_network_plot`), and **Show Cell Polarization Arrows** / **Show LGF Gradient Vectors** ($\nabla \text{LGF}$) overlays (`extract_orientation_grid`, `compute_lgf_gradient`).
- **Modern Python Packaging, Containers & Path-Filtered CI**: Migrated to PEP 621 [`pyproject.toml`](../pyproject.toml) and [`uv`](https://docs.astral.sh/uv/) (`Python 3.11+`) with PEP 420 namespace packages, unified Podman/Docker container scripts (`scripts/run_container.sh`, `scripts/teardown_container.sh`), added `docs/getting-started.md`, and split GitHub Actions into path-filtered `.github/workflows/ci.yml` and `.github/workflows/docker.yml` with Buildx caching and 67 `pytest` unit tests (`tests/`).
- **Scientific Documentation & Topologies**: Consolidated mathematical and architectural documentation in [`docs/architecture.md`](./architecture.md) and added multi-topology graph generation (`erdos-renyi`, `watts-strogatz`, `barabasi-albert`) in `analysis/graph_generator.py`.

### `v0.2.0` — Containerization and Interactive Web Interface (2025)
- **Docker Support**: Added [`Dockerfile`](../Dockerfile) (`python:3.12-slim` + `uv`), [`docker-compose.yml`](../docker-compose.yml), and launcher scripts for reproducible execution.
- **Streamlit & Plotly Web Interface**: Created [`visualization/web_app.py`](../visualization/web_app.py) for interactive parameter exploration and real-time visualization of cell states, SGF, and LGF concentration fields.
- **Modular Codebase**: Separated the flat root scripts into `core/`, `evolution/`, `visualization/`, `analysis/`, and `examples/`.

### `v0.1.0` — Original Master's Thesis Research (2017)
- **Baseline Commit**: [`j0sees/Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis@6c3fae7`](https://github.com/j0sees/Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis/tree/6c3fae7834a2ca502b1a439d7535c4adab1673f3) (*Sept–Dec 2017*, [M.Sc. José Esteban Pérez-Hidalgo](https://orion.tec.ac.cr/en/persons/jos%C3%A9-esteban-p%C3%A9rez-hidalgo/), M.Sc. in Complex Adaptive Systems, supervised by [Ph.D. Philip Gerlee](https://research.chalmers.se/en/person/gerlee), University of Gothenburg & Chalmers University of Technology).
- **Core Model Implementation**:
  - 2D discrete cellular automaton with four cellular actions (`Quiet`, `Move`, `Split`, `Die`) and polarization compass.
  - Non-toroidal boundary enforcement via `flatList` and Crank-Nicolson reaction-diffusion solver (`LGFDiffEq`) with zero-flux Neumann boundary conditions (`GenerateTMatrix`).
  - Generalization of Gerlee et al.'s (2015) two-layer feedforward network into an intracellular Recurrent Neural Network (`RecurrentNeuralNetwork`).
  - Parallel Genetic Algorithm (`evolution/main_ga.py`), `neat-python` neuroevolution integration (`evolution/neat_cell_agent.py`, `evolution/neat_parallel.py`), and `(SGF, LGF)` phase-space mapping (`MapPlot`).
  - Presented at the *9th Swedish Meeting on Mathematical Biology* (Västerås, Sweden, Dec 7–8, 2017).

---

## Completed Roadmap Improvements (Derived from 2017 Thesis Notes)

All planned improvements identified from the original 2017 research notes have been implemented and verified in `v0.3.0`:

- [x] `docs(architecture)`: re-infuse `v0.1.0` (`6c3fae7`) thesis context and multi-topology CLI support
- [x] `refactor(core)`: decouple simulation engine from Matplotlib plotting and consolidate duplicate `sim()` loops (`core/engine.py`)
- [x] `perf(core)`: optimize `LGFDiffEq` Crank-Nicolson solver via $O(N^2)$ Thomas ADI factorization (`LGFThomasSolver`), standardize `(y, x)` coordinates, and add flow diagram
- [x] `feat(visualization)`: adopt Okabe-Ito colorblind-safe palette (`visualization/palettes.py`) and add headless timelapse PNG/GIF export (`visualization/timelapse.py`)
- [x] `feat(evolution)`: improve GA offspring diversity (`evolution/tools_ga.py`, `evolution/main_ga.py`) and align NEAT `config-ca` with `[0, 1]` fitness scale
- [x] `docs(history)`: convert raw 2017 scratch notes in `docs/history-log.md` into structured milestone history
- [x] `feat(visualization)`: add deterministic PRNG seed, batch timeline scrubber, homeostasis telemetry, interactive GA evolution tab, `(SGF, LGF)` phase-space decision map, directed GRN graph, and cell polarization compass / $\nabla \text{LGF}$ gradient vector overlays
