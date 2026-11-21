# Changelog

All notable changes to this project are documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-11-21

### Added
- **Unified Headless Core Engine (`core/engine.py`)**: Introduced `SimulationConfig`, `SimulationEngine`, `StepSnapshot`, `SimulationResult`, and `run_simulation()` with explicit deterministic PRNG seeding (`seed`), $O(M)$ Fisher-Yates cell shuffling, and zero imports from `matplotlib` or `visualization/`.
- **Golden Numerical Parity Fixtures (`tests/fixtures/golden_parity_v0_2.json`)**: Added reference JSON fixtures (`tolerance: 1e-9`) and `tests/test_engine.py` verifying headless execution, deterministic reproducibility, early-stop cutoffs, and numerical parity.
- **Colorblind-Safe Palettes & Headless Timelapse Export (`visualization/palettes.py`, `visualization/timelapse.py`)**: Added centralized Okabe-Ito colorblind-safe and legacy palettes, strictly discrete Plotly heatmap colorscales, `TimelapseExporter` for step-numbered PNGs and animated GIFs, and `make_live_plot_observer()` in `visualization/plot.py`.
- **Web App Seed, Batch Timeline Scrubber & Homeostasis Telemetry (`visualization/web_app.py`)**: Added sidebar PRNG seed controls, 1:1 square aspect-ratio heatmaps, instant **Run Full Horizon** batch mode with a **Timeline Scrubber**, per-step cell/chemical telemetry plots, and a **Shape Homeostasis Summary** ($F$, $S_{T/2}$, $S_T$, $\Delta$).
- **Interactive GA Evolution, Phase-Space Decision Map & Directed GRN Graph (`visualization/web_app.py`)**: Wired Tab 2 (`Analysis`) to `run_evolution_pass()` powered by `tools_ga.initialize_population` and `tools_ga.create_next_generation`, added a one-click **Load Best Evolved GRN into Simulation** bridge into Tab 1, and added `compute_phase_space_map()`, `create_phase_space_plot()`, and `create_grn_network_plot()` for interactive `(SGF, LGF)` steady-state decision mapping and functional node/edge inspection.
- **Cell Polarization Compass & $\nabla \text{LGF}$ Chemical Gradient Vector Overlays (`core/engine.py`, `visualization/web_app.py`, `visualization/timelapse.py`)**: Added `extract_orientation_grid()` and `StepSnapshot.orientation_grid` to capture per-cell GRN Node 7 compass unit vectors `(dy, dx)` in row-major `(y, x)` coordinates; extended `create_cell_grid_plot()` with **Show Cell Polarization Arrows** and **Show LGF Gradient Vectors** (`compute_lgf_gradient`) overlays across live execution, batch scrubbing, and headless Matplotlib quiver export (`render_snapshot_figure`, `TimelapseExporter`).
- **Getting Started Guide & Split Docker CI Workflow (`docs/getting-started.md`, `.github/workflows/docker.yml`)**: Extracted detailed setup, CLI runners, and repository tree into `docs/getting-started.md`, and split `Docker Build & Smoke Check` into its own path-filtered workflow with Docker Buildx GitHub Actions layer caching (`cache-from`/`cache-to: type=gha`).
- **Safe Container Teardown Script**: Added `scripts/teardown_container.sh` with interactive confirmation prompt, `-y`/`--force` option, engine auto-detection (Podman/Docker), and container/image/cache cleanup (`2026-11-04`).
- **Hero Header, Mermaid Diagrams & Scientific References**: Added centered hero header and shields.io badges in `README.md`, Mermaid architectural and execution flowcharts across `README.md`, `docs/architecture.md`, `docs/docker.md`, and `docs/web-interface.md`, and a foundational references section (`abaa83e`, `2026-11-04T12:03:07-06:00`).
- **Release Baseline & Community Standards**: Added `VERSION` (`0.3.0`), `CHANGELOG.md`, `CONTRIBUTING.md` (Trunk-Based Development, Conventional Commits, issue guidelines), and `CODE_OF_CONDUCT.md` (`5e8f88e`, `2026-11-04T11:55:56-06:00`).
- **Podman & Docker Container Launcher**: Replaced the Docker-only launcher with `scripts/run_container.sh` supporting both Podman (Podman Desktop / rootless Podman) and Docker on macOS and Linux (`adc3acd`, `2026-11-04T08:27:38-06:00`).
- **Multi-Topology CLI & Thesis Context**: Re-infused `v0.1.0` mathematical and biological context (`flatList` closed boundaries, Neumann zero-flux Laplacian, 2-layer feedforward to RNN generalization, and `MapPlot` phase-space maps) into `docs/architecture.md`, and added CLI/programmatic support for `erdos-renyi`, `watts-strogatz`, and `barabasi-albert` topologies in `analysis/graph_generator.py` (`17ae423`, `2026-11-04T07:48:28-06:00`).
- **Citation & Author Metadata**: Added `CITATION.cff` and standardized author/maintainer attribution across `README.md`, `pyproject.toml`, `LICENSE`, `docs/architecture.md`, and `visualization/web_app.py` (`39bf506`, `2026-11-04T07:24:37-06:00`).
- **GitHub Actions CI & Unit Test Suite**: Added `.github/workflows/ci.yml` (`ruff`, `compileall`, `pytest`, container smoke build) and `pytest` unit tests under `tests/` (`5a59441`, `2026-11-03T23:12:03-06:00`).

### Performance
- **Precomputed $O(N^2)$ Thomas ADI Solver (`core/tools.py`)**: Replaced per-step $O(N^3)$ `np.linalg.inv` in `LGFDiffEq` with a Numba `@njit` precomputed Thomas tridiagonal factorization (`LGFThomasSolver`), verified within `1e-12` against dense Crank-Nicolson and preserving zero-flux Neumann mass conservation.

### Changed
- **Standardized Row-Major `(y, x)` Coordinates**: Aligned `CheckifOccupied`, `CheckifPreferred`, cell agent `Move`/`Split`, and initial seeding across `core/`, `evolution/`, and `visualization/`, and updated the execution flow diagram in `docs/architecture.md`.
- **Consolidated Duplicated Simulation Loops**: Eliminated duplicated stepping loops across `core/main.py`, `evolution/main_ga.py`, `evolution/neat_parallel.py`, `visualization/web_app.py`, `analysis/graph_evaluation.py`, and `examples/` in favor of `core/engine.py`.
- **Path-Filtered `ci.yml`**: Added `paths:` filters to `.github/workflows/ci.yml` so documentation-only edits do not trigger redundant Python lint/test runs.
- **Canonical Repository URLs & Citation Alignment**: Updated `CITATION.cff`, `README.md`, and `CONTRIBUTING.md` clone instructions to point to the canonical upstream repository (`j0sees/Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis`) (`2026-11-04`).
- **License Copyright & Upstream CI Compatibility**: Updated `LICENSE` copyright range to `2017-2026` and added `master` branch trigger support to `.github/workflows/ci.yml` (`f054b90`, `2026-11-04T12:28:44-06:00`).
- **Roadmap Tracking**: Converted raw 2017 scratch notes in `docs/history-log.md` into a milestone history and issue tracker (`8d68da2`, `2026-11-04T08:03:03-06:00`).
- **Root Directory Organization & Namespace Packages**: Moved `neat_cell_agent.py` and `neat_parallel.py` to `evolution/`, `web_app.py` and `plots.gp` to `visualization/`, and shell launchers to `scripts/`; removed empty `__init__.py` files in favor of PEP 420 namespace packages and bumped version to `0.3.0` (`dd99a8d`, `2026-11-04T07:11:15-06:00`).
- **PEP 8 Cleanup & Ignore Rules**: Removed commented-out legacy code across all Python modules, enforced PEP 8 formatting (`<= 100` chars/line), and aligned `.gitignore` and `.dockerignore` (`a65cc53`, `2026-11-03T23:02:24-06:00`).
- **Dependency Modernization & `uv` Migration**: Migrated from `pip`/`requirements.txt` to `pyproject.toml` and `uv`, upgraded `Dockerfile` to `python:3.12-slim` + `uv`, updated NetworkX 3.x (`from_numpy_array`, `to_numpy_array`), Numba (`@njit`), and Matplotlib (`draw_idle`) calls, and connected `visualization/web_app.py` and `examples/run_evolution.py` to the live simulation engine (`ed8e9cb`, `2026-11-03T22:49:40-06:00`).
- **Documentation Polish**: Removed decorative emojis across Markdown files, shell scripts, and Streamlit UI, and improved documentation clarity (`62df17d`, `2026-11-03T22:39:14-06:00`).

### Fixed
- **GA Offspring Diversity & Multiprocessing Propagation (`evolution/tools_ga.py`, `evolution/main_ga.py`)**: Fixed `[-1, 1]` weight initialization (`initialize_population`), single-copy elitism with distinct tournament parents (`select_tournament_parents`, `create_next_generation`), per-gene Gaussian mutation with optional weight bounds, and explicit genome passing (`evaluate_genome`, `run_ga`) eliminating stale `mp.Array` buffers.
- **NEAT Configuration & `neat-python 2.0` Alignment (`config/config-ca`, `evolution/neat_parallel.py`)**: Aligned `fitness_threshold` from `8.0` to `0.95` on the `[0, 1]` homeostasis scale, added required `no_fitness_termination = False` and `min_species_size = 1`, added `max_generations`/`seed` controls, and removed unused XOR benchmark helpers.
- **Web UI Layout, Colorbar Spacing & GRN Node Labels (`visualization/web_app.py`)**: Resolved overlapping SGF/LGF colorbars via dedicated per-subplot positioning, constrained cell/chemical heatmap axes to `[-0.5, N - 0.5]` to prevent vector overlay auto-range gaps, and repositioned directed GRN graph node labels outside circles for readability.

---

## [0.2.0] - 2025-09-03

### Added
- **MIT License**: Added repository `LICENSE` (`0f78f98`, `2025-09-03T11:24:01-06:00`).
- **Interactive Web Interface & Containerization**: Added Streamlit and Plotly web interface (`web_app.py`), `Dockerfile`, `docker-compose.yml`, launcher scripts, and documentation figures (`5fde409`, `2025-09-03T11:07:55-06:00`; `2e6a67f`, `2025-08-31T21:18:02-06:00`; `a7591ad`, `2025-08-31T22:00:49-06:00`).

### Changed
- **Modular Directory Structure**: Reorganized flat root scripts into `core/`, `evolution/`, `visualization/`, `analysis/`, and `examples/` and fixed `tools_ga` imports (`dd0a2b0`, `2025-08-31T20:40:08-06:00`; `2084c7b`, `2025-08-31T21:35:17-06:00`).

---

## [0.1.0] - 2017-12-15 (Thesis Baseline Updated 2025-08-06)

### Added
- **Thesis Overview & Documentation Baseline**: Documented master's thesis objectives and model summary in `README.md` and `log` (`6c3fae7`, `2025-08-06T11:54:17-06:00`; `615f383`, `2017-12-15T17:31:18+01:00`).
- **Graph Topology Generation & Evaluation**: Added `graph_generator.py` and `graph_evaluation.py` for GRN topology analysis (`5aee700`, `2017-12-12T16:50:58+01:00`).
- **NEAT Neuroevolution**: Added `neat-python` cell agent (`neat_cell_agent.py`), parallel runner (`neat_parallel.py`), and `config-ca` (`77e4595`, `2017-12-12T16:50:09+01:00`).
- **Closed Lattice Boundaries (`flatList`) & Compass Fix**: Separated `cellgrid` and `chemgrid` using `flatList` to prevent negative-index toroidal wrapping and corrected compass neighbor selection (`4073a36`, `2017-11-17T16:54:08+01:00`; `d42c147`, `2017-11-14T18:14:26+01:00`).
- **Parallel Genetic Algorithm & Numba JIT**: Implemented `multiprocessing.Pool` evolution (`main_GA.py`, `tools_GA.py`), shape-homeostasis fitness function, and Numba `@jit` acceleration (`3c879b4`, `2017-11-01T16:29:56+01:00`; `1422e07`, `2017-10-08T21:05:25+02:00`; `697d2bc`, `2017-10-06T02:59:41+02:00`; `dc206d5`, `2017-10-04T17:53:05+02:00`).
- **Recurrent Neural Network & SGF/LGF Reaction-Diffusion**: Implemented intracellular `RecurrentNeuralNetwork`, explicit Euler `SGFDiffEq`, and Crank-Nicolson `LGFDiffEq` with Neumann boundary matrix `GenerateTMatrix` (`466a79a`, `2017-10-02T01:29:59+02:00`; `d349fce`, `2017-09-25T15:41:21+02:00`).
- **2D Cellular Automaton Core**: Implemented initial cell agent states (`Quiet`, `Move`, `Split`, `Die`), polarization compass, and Matplotlib environment plotting (`0657f64`, `2017-09-14T18:00:45+02:00`; `c3ec607`, `2017-09-04T17:26:01+02:00`; `1f1ebe2`, `2017-08-31T00:37:55+02:00`).
