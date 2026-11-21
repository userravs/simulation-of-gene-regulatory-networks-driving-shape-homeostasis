#!/usr/bin/env python3
"""
Basic simulation example.

This script demonstrates how to run a simple cellular automata simulation
with a gene regulatory network.
"""

from __future__ import annotations

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import main
from visualization.plot import make_live_plot_observer


def run_basic_simulation() -> None:
    """Run a basic simulation with default parameters."""
    n_nodes = 25
    time_steps = 50
    n_lattice = 20
    mode = False  # Visualization mode

    rng = np.random.default_rng(42)
    w_matrix = rng.uniform(-1.0, 1.0, size=(n_nodes, n_nodes))

    print("Running simulation with:")
    print(f"  Nodes: {n_nodes}")
    print(f"  Time steps: {time_steps}")
    print(f"  Lattice size: {n_lattice}x{n_lattice}")
    print(f"  Mode: {'Fitness' if mode else 'Visualization'}")

    observer = None
    fig = None
    if not mode:
        observer, fig = make_live_plot_observer(n_lattice, mode=mode)

    result = main.sim(
        w_matrix,
        time_steps,
        n_nodes,
        n_lattice,
        mode,
        seed=42,
        on_step=observer,
    )
    if fig is not None:
        plt.close(fig)

    print(
        f"Simulation completed! Living cells: {result.final_cell_count}, "
        f"Fitness: {result.fitness:.4f}"
    )


if __name__ == "__main__":
    run_basic_simulation()
