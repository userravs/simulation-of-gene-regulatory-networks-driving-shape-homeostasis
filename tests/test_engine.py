"""Unit tests for the unified headless simulation engine and Phase 0 golden fixtures."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import neat
import numpy as np
import pytest

from core.engine import (
    SimulationConfig,
    SimulationEngine,
    StepSnapshot,
    run_simulation,
)
from evolution.neat_cell_agent import cell as neat_cell
from visualization.plot import make_live_plot_observer
from visualization.timelapse import TimelapseExporter


def test_core_package_has_zero_matplotlib_or_visualization_imports() -> None:
    """Importing and running core simulation must never import matplotlib or visualization."""
    repo_root = Path(__file__).resolve().parent.parent
    probe_code = (
        "import sys, numpy as np\n"
        "import core.tools, core.cell_agent, core.engine, core.main\n"
        "w = np.random.default_rng(7).uniform(-1.0, 1.0, (8, 8))\n"
        "res = core.main.sim(w, timeSteps=6, nNodes=8, nLattice=8, mode=True, seed=7)\n"
        "assert 'matplotlib' not in sys.modules, 'matplotlib imported by core'\n"
        "assert 'visualization' not in sys.modules, 'visualization imported by core'\n"
        "assert 0.0 <= res.fitness <= 1.0\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", probe_code],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_deterministic_seeding_reproducibility() -> None:
    """Identical (w_matrix, config, seed) inputs should yield bit-for-bit identical outputs."""
    rng = np.random.default_rng(1)
    w_matrix = rng.uniform(-1.0, 1.0, size=(8, 8))

    res_a = run_simulation(w_matrix, time_steps=16, n_nodes=8, n_lattice=12, seed=42)
    res_b = run_simulation(w_matrix, time_steps=16, n_nodes=8, n_lattice=12, seed=42)

    assert res_a.steps_executed == res_b.steps_executed
    assert res_a.final_cell_count == res_b.final_cell_count
    assert res_a.terminated_early == res_b.terminated_early
    assert res_a.fitness == res_b.fitness
    assert np.array_equal(res_a.cell_grid, res_b.cell_grid)
    assert np.array_equal(res_a.sgf_grid, res_b.sgf_grid)
    assert np.array_equal(res_a.lgf_grid, res_b.lgf_grid)
    assert np.array_equal(res_a.delta_matrix, res_b.delta_matrix)


def test_step_callback_and_non_early_stop() -> None:
    """on_step should receive sequential StepSnapshots across the entire horizon."""
    w_matrix = np.random.default_rng(1).uniform(-1.0, 1.0, size=(8, 8))
    snapshots: list[StepSnapshot] = []

    result = run_simulation(
        w_matrix,
        time_steps=10,
        n_nodes=8,
        n_lattice=12,
        early_stop=False,
        seed=1,
        on_step=snapshots.append,
    )

    assert len(snapshots) == 10
    assert [snap.step for snap in snapshots] == list(range(10))
    assert result.steps_executed == 10
    assert np.array_equal(snapshots[-1].cell_grid, result.cell_grid)
    assert np.array_equal(snapshots[-1].sgf_grid, result.sgf_grid)
    assert np.array_equal(snapshots[-1].lgf_grid, result.lgf_grid)


def test_early_termination_extinction_and_sparse_midpoint() -> None:
    """Both cell extinction and <=1% midpoint occupancy should abort early with fitness=0."""
    # Case 1: complete cell extinction before end of horizon
    w_extinct = np.random.default_rng(263).uniform(-2.0, 2.0, size=(8, 8))
    res_extinct = run_simulation(
        w_extinct,
        time_steps=20,
        n_nodes=8,
        n_lattice=10,
        early_stop=True,
        seed=263,
    )
    assert res_extinct.terminated_early is True
    assert res_extinct.final_cell_count == 0
    assert res_extinct.steps_executed < 20
    assert res_extinct.fitness == 0.0

    # Case 2: persistent 2-cell population falls under <= 1% threshold on 15x15 grid
    w_sparse = np.zeros((8, 8), dtype=np.float64)
    w_sparse[2, :] = -1.0
    w_sparse[3, :] = -1.0
    w_sparse[4, :] = 1.5
    res_sparse = run_simulation(
        w_sparse,
        time_steps=12,
        n_nodes=8,
        n_lattice=15,
        early_stop=True,
        seed=7,
    )
    assert res_sparse.terminated_early is True
    assert res_sparse.steps_executed == 6
    assert res_sparse.fitness == 0.0


def test_config_and_engine_validation() -> None:
    """SimulationConfig and SimulationEngine.from_weight_matrix should validate inputs."""
    with pytest.raises(ValueError, match="n_lattice"):
        SimulationConfig(n_lattice=0)
    with pytest.raises(ValueError, match="time_steps"):
        SimulationConfig(time_steps=0)
    with pytest.raises(ValueError, match="delta_r"):
        SimulationConfig(delta_r=0.0)
    with pytest.raises(ValueError, match="delta_s"):
        SimulationConfig(delta_s=-0.1)

    with pytest.raises(ValueError, match="square 2D"):
        SimulationEngine.from_weight_matrix(np.zeros((8, 9)))
    with pytest.raises(ValueError, match="does not match"):
        SimulationEngine.from_weight_matrix(np.zeros((8, 8)), n_nodes=10)
    with pytest.raises(ValueError, match="at least 8 nodes"):
        SimulationEngine.from_weight_matrix(np.zeros((6, 6)))


def test_engine_supports_neat_cell_factory() -> None:
    """SimulationEngine should execute NEAT cell agents via a custom cell_factory."""
    config_path = Path(__file__).resolve().parent.parent / "config" / "config-ca"
    neat_cfg = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path),
    )
    pop = neat.Population(neat_cfg)
    genome = next(iter(pop.population.values()))

    sim_cfg = SimulationConfig(n_lattice=8, time_steps=6, early_stop=True, seed=5)
    result = SimulationEngine(
        lambda y_pos, x_pos: neat_cell(y_pos, x_pos, genome, neat_cfg),
        config=sim_cfg,
    ).run()

    assert result.steps_executed >= 1
    assert 0.0 <= result.fitness <= 1.0


def test_live_plot_observer_integrates_with_engine(tmp_path: Path) -> None:
    """make_live_plot_observer should render headless snapshots through SimulationEngine."""
    w_matrix = np.random.default_rng(1).uniform(-1.0, 1.0, size=(8, 8))
    exporter = TimelapseExporter(tmp_path, interval=2, dpi=72)
    observer, fig = make_live_plot_observer(
        10,
        mode=True,
        timelapse_exporter=exporter,
    )

    result = run_simulation(
        w_matrix,
        time_steps=4,
        n_nodes=8,
        n_lattice=10,
        early_stop=False,
        seed=1,
        on_step=observer,
    )
    assert fig is not None
    assert result.steps_executed == 4
    assert [p.name for p in exporter.saved_frames] == ["frame_00000.png", "frame_00002.png"]


def test_phase0_golden_parity_fixtures() -> None:
    """Golden parity fixtures should reproduce identically within 1e-9 tolerance."""
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "golden_parity_v0_2.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    tol = float(fixture["tolerance"])
    assert tol == pytest.approx(1e-9)
    assert len(fixture["cases"]) >= 3

    for case in fixture["cases"]:
        cfg = case["config"]
        w_matrix = np.asarray(case["w_matrix"], dtype=np.float64)
        expected = case["expected"]

        result = run_simulation(
            w_matrix,
            time_steps=cfg["time_steps"],
            n_nodes=cfg["n_nodes"],
            n_lattice=cfg["n_lattice"],
            early_stop=cfg["early_stop"],
            seed=cfg["seed"],
            delta_t=cfg["delta_t"],
            delta_r=cfg["delta_r"],
            delta_s=cfg["delta_s"],
            delta_l=cfg["delta_l"],
            diff_const=cfg["diff_const"],
        )

        assert result.steps_executed == expected["steps_executed"], case["name"]
        assert result.final_cell_count == expected["final_cell_count"], case["name"]
        assert result.terminated_early is expected["terminated_early"], case["name"]
        assert result.fitness == pytest.approx(expected["fitness"], abs=tol), case["name"]
        assert np.allclose(result.cell_grid, expected["cell_grid"], atol=tol, rtol=0.0)
        assert np.allclose(result.sgf_grid, expected["sgf_grid"], atol=tol, rtol=0.0)
        assert np.allclose(result.lgf_grid, expected["lgf_grid"], atol=tol, rtol=0.0)
        assert np.array_equal(result.halfway_structure, expected["halfway_structure"])
        assert np.array_equal(result.final_structure, expected["final_structure"])
        assert np.array_equal(result.delta_matrix, expected["delta_matrix"])
