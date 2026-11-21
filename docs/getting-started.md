# Getting Started & CLI Guide

This guide covers container and local installation, command-line simulation and evolution runners, repository layout, and local verification checks for the **Simulation of Gene Regulatory Networks Driving Shape Homeostasis** platform.

---

## 1. Prerequisites & Setup

### Option 1: Container — Podman or Docker (Recommended on macOS & Linux)

```bash
git clone https://github.com/j0sees/Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis.git
cd Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis

# Auto-detects Podman or Docker, builds the image, and starts the web app at http://localhost:8501
./scripts/run_container.sh
```

To stop and remove containers, images, and local caches:

```bash
./scripts/teardown_container.sh
```

For Compose mounts, environment variables, and container troubleshooting, see [docker.md](docker.md).

### Option 2: Local Setup with `uv`

Requires **Python 3.11+** and **[uv](https://docs.astral.sh/uv/)**:

```bash
# Install runtime and development dependencies (ruff, pytest)
uv sync --dev

# Launch the interactive Streamlit web interface at http://localhost:8501
./scripts/run_web_app.sh
```

For interactive controls, color palettes, polarization/gradient vector overlays, and timelapse GIF export options, see [web-interface.md](web-interface.md).

---

## 2. Command-Line Execution

```bash
# Run a standalone simulation example (with live Matplotlib observer)
uv run python examples/run_simulation.py

# Run a small-scale Genetic Algorithm example
uv run python examples/run_evolution.py

# Run the headless simulation CLI directly from a saved population CSV
uv run python core/main.py populations/<file_stem>.csv <n_nodes> <individual_idx> [seed]

# Regenerate documentation figures under docs/images/
uv run python examples/generate_documentation_images.py
```

---

## 3. Repository Structure

```text
├── analysis/             # Network topology generation and batch evaluation (ER, WS, BA)
├── config/               # NEAT configuration parameters (config-ca)
├── core/                 # Headless CA/GRN engine (engine.py), cell agent, and O(N^2) PDE solvers
├── docs/                 # Technical documentation and figures
├── evolution/            # Parallel Genetic Algorithm (main_ga.py, tools_ga.py) and NEAT runner
├── examples/             # Runnable simulation, evolution, and figure generation scripts
├── scripts/              # Helper scripts (run_container.sh, run_web_app.sh, teardown_container.sh)
├── tests/                # Pytest suite and golden numerical parity fixtures (tests/fixtures/)
├── visualization/        # Palettes, headless timelapse GIF exporter, Matplotlib, and Streamlit UI
├── CHANGELOG.md          # Versioned release notes
├── CITATION.cff          # Citation metadata for GitHub and academic references
├── CODE_OF_CONDUCT.md    # Contributor Covenant Code of Conduct
├── CONTRIBUTING.md       # Contribution workflow, coding standards, and pre-PR checks
├── Dockerfile            # Container image definition (Python 3.12 + uv)
├── docker-compose.yml    # Docker Compose service configuration
├── LICENSE               # MIT License
├── pyproject.toml        # Project metadata, dependencies, and tool configuration
└── VERSION               # Canonical semantic version file
```

---

## 4. Linting & Verification

Before opening a Pull Request, run the full local verification suite matching `.github/workflows/ci.yml`:

```bash
# 1. Validate shell scripts
bash -n scripts/run_container.sh scripts/run_web_app.sh scripts/teardown_container.sh

# 2. Run Ruff linter
uv run ruff check .

# 3. Verify Python bytecode compilation
uv run python -m compileall -q core evolution visualization analysis examples tests

# 4. Run unit test suite (including golden numerical parity checks)
MPLBACKEND=Agg uv run pytest -v
```
