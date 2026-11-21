"""Headless cellular automata simulation entrypoint and core engine exports."""

from __future__ import annotations

from collections.abc import Callable
import sys
import numpy as np

from core.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationResult,
    StepSnapshot,
    run_simulation,
)
from core.tools import GetrNN

__all__ = [
    "SimulationConfig",
    "SimulationEngine",
    "SimulationResult",
    "StepSnapshot",
    "run_simulation",
    "sim",
]


def sim(
    wMatrix: np.ndarray,
    timeSteps: int,
    nNodes: int,
    nLattice: int,
    mode: bool = True,
    *,
    seed: int | None = None,
    on_step: Callable[[StepSnapshot], None] | None = None,
) -> SimulationResult:
    """
    Run a cellular automata simulation with gene regulatory networks headlessly.

    Parameters
    ----------
    wMatrix : numpy.ndarray
        Weight matrix for the neural network representing the GRN.
    timeSteps : int
        Number of simulation time steps to run.
    nNodes : int
        Number of nodes in the neural network.
    nLattice : int
        Size of the square lattice grid (nLattice x nLattice).
    mode : bool
        True: stop early on extinction or degenerate midpoint occupancy.
        False: run all timeSteps (useful with an external ``on_step`` observer).
    seed : int | None
        Optional deterministic PRNG seed for reproducible execution.
    on_step : Callable[[StepSnapshot], None] | None
        Optional observer callback invoked after each time step.
    """
    return run_simulation(
        wMatrix,
        time_steps=timeSteps,
        n_nodes=nNodes,
        n_lattice=nLattice,
        early_stop=mode,
        seed=seed,
        on_step=on_step,
    )


if __name__ == "__main__":
    print("Headless GRN cellular automata simulation")
    file_name = sys.argv[1]
    n_nodes = int(sys.argv[2])
    individual = int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else None

    w_matrix = GetrNN(file_name, individual)
    result = sim(w_matrix, timeSteps=200, nNodes=n_nodes, nLattice=50, mode=True, seed=seed)
    print(
        f"Steps executed: {result.steps_executed}, "
        f"final living cells: {result.final_cell_count}, "
        f"fitness: {result.fitness:.4f}"
    )
