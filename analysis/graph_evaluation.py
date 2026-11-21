"""Evaluate fitness across a population of saved Gene Regulatory Network topologies."""

from __future__ import annotations

from contextlib import contextmanager
import multiprocessing as mp
import sys
import matplotlib.pyplot as plt
import numpy as np

from core.engine import run_simulation


def partialEval(ind: int) -> float:
    """Evaluate a single network index using default simulation parameters."""
    time_steps = 200
    n_nodes = 25
    n_lattice = 50
    return EvaluateIndividual(time_steps, n_nodes, n_lattice, ind)


def EvaluateIndividual(
    timeSteps: int,
    nNodes: int,
    nLattice: int,
    ind: int,
    *,
    seed: int | None = None,
) -> float:
    """Run the cellular automata simulation and compute the shape homeostasis fitness."""
    w_matrix = networkArrays[ind]
    result = run_simulation(
        w_matrix,
        time_steps=timeSteps,
        n_nodes=nNodes,
        n_lattice=nLattice,
        early_stop=True,
        seed=seed,
    )
    return result.fitness


@contextmanager
def poolcontext(*args, **kwargs):
    """Context manager that terminates a multiprocessing pool on exit."""
    pool = mp.Pool(*args, **kwargs)
    try:
        yield pool
    finally:
        pool.terminate()


if __name__ == "__main__":
    file_name = sys.argv[1]
    csv_file = f"populations/{file_name}.csv"
    n_procs = 20

    with open(csv_file, "r", encoding="utf-8") as csvfile:
        network_container = np.loadtxt(csvfile, delimiter=",")
    n_nets, n_genes = network_container.shape
    side = int(np.sqrt(n_genes))
    networkArrays = network_container.reshape(n_nets, side, side)

    index_list = list(range(n_nets))
    with poolcontext(processes=n_procs) as pool:
        fitness_array = pool.map(partialEval, index_list)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_ylabel("fitness")
    ax.set_title("histogram")
    ax.hist(fitness_array)
    plt.savefig("test.png")
