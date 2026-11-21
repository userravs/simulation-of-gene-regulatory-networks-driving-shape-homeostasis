"""Parallel Genetic Algorithm for evolving Gene Regulatory Networks driving shape homeostasis."""

from __future__ import annotations

from collections.abc import Callable
import csv
import multiprocessing as mp
import os
import sys
import time
import numpy as np

from core.engine import StepSnapshot, run_simulation
from evolution.tools_ga import create_next_generation, initialize_population

population: np.ndarray | None = None
fitness: np.ndarray | None = None


def sim(
    wMatrix: np.ndarray,
    timeSteps: int,
    iGen: int,
    nNodes: int,
    individual: int,
    nLattice: int,
    mode: bool,
    *,
    seed: int | None = None,
    on_step: Callable[[StepSnapshot], None] | None = None,
) -> np.ndarray | None:
    """
    Run a cellular automata simulation via the unified core engine.

    Parameters
    ----------
    wMatrix : numpy.ndarray
        Recurrent neural network weight matrix.
    timeSteps : int
        Number of simulation time steps.
    iGen : int
        Current generation index.
    nNodes : int
        Number of nodes in the neural network.
    individual : int
        Individual index within the population.
    nLattice : int
        Dimension of the square lattice grid.
    mode : bool
        True: evaluate fitness and return the binary structural difference matrix.
        False: run full horizon with optional ``on_step`` observer and return None.
    """
    _ = (iGen, individual)
    result = run_simulation(
        wMatrix,
        time_steps=timeSteps,
        n_nodes=nNodes,
        n_lattice=nLattice,
        early_stop=mode,
        seed=seed,
        on_step=on_step,
    )
    if mode:
        return result.delta_matrix
    return None


def evaluate_genome(
    w_matrix: np.ndarray,
    time_steps: int,
    i_gen: int,
    n_nodes: int,
    individual: int,
    n_lattice: int,
    mode: bool = True,
    seed: int | None = None,
) -> float:
    """Evaluate a single GRN weight matrix and return scalar fitness in [0.0, 1.0]."""
    _ = (i_gen, individual)
    start_time = time.time()
    result = run_simulation(
        w_matrix,
        time_steps=time_steps,
        n_nodes=n_nodes,
        n_lattice=n_lattice,
        early_stop=mode,
        seed=seed,
    )
    secs = time.time() - start_time
    print(f"Proc {os.getpid()}: Time taken to run sim: {secs:.3f} s")
    return result.fitness


def EvaluateIndividual(
    individual: int,
    timeSteps: int,
    iGen: int,
    nNodes: int,
    nLattice: int,
    mode: bool,
) -> np.ndarray:
    """Evaluate a single individual's fitness in the legacy shared population array."""
    if population is None or fitness is None:
        raise RuntimeError("Legacy global population and fitness buffers are not initialized.")

    w_matrix = population[individual, :].reshape(nNodes, nNodes)
    fitness[individual] = evaluate_genome(
        w_matrix, timeSteps, iGen, nNodes, individual, nLattice, mode
    )
    return fitness


def run_ga(
    pop_size: int = 6,
    n_nodes: int = 25,
    n_generations: int = 15,
    time_steps: int = 200,
    n_lattice: int = 50,
    *,
    elite_num: int = 2,
    tournament_size: int = 4,
    crossover_prob: float = 0.8,
    mutation_prob: float = 0.9,
    gene_mutation_rate: float | None = None,
    weight_bounds: tuple[float, float] = (-1.0, 1.0),
    n_procs: int = 2,
    chunk_size: int = 1,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Run the Genetic Algorithm and return (final_population, fitness_history)."""
    if n_procs < 1:
        raise ValueError("n_procs must be >= 1.")
    if n_generations < 1:
        raise ValueError("n_generations must be >= 1.")

    rng = np.random.default_rng(seed)
    n_genes = n_nodes**2
    pop = initialize_population(
        pop_size,
        n_genes,
        weight_bounds=weight_bounds,
        rng=rng,
    )
    fitness_info = np.zeros((n_generations, 2), dtype=np.float64)
    generation_avg = 0.0

    for i_gen in range(n_generations):
        start_time_generation = time.time()
        print(f"\nGeneration #{i_gen + 1}")

        args = [
            (
                pop[idx].reshape(n_nodes, n_nodes),
                time_steps,
                i_gen,
                n_nodes,
                idx,
                n_lattice,
                True,
                (seed + i_gen * pop_size + idx) if seed is not None else None,
            )
            for idx in range(pop_size)
        ]

        if n_procs > 1:
            with mp.Pool(processes=n_procs) as pool:
                scores = np.asarray(
                    pool.starmap(evaluate_genome, args, chunk_size),
                    dtype=np.float64,
                )
        else:
            scores = np.asarray(
                [evaluate_genome(*item) for item in args],
                dtype=np.float64,
            )

        fitness_info[i_gen, 0] = float(np.max(scores))
        fitness_info[i_gen, 1] = float(np.mean(scores))
        print(
            f"Gen: {i_gen + 1}, max fit: {fitness_info[i_gen, 0]:.3f}, "
            f"avg fit: {fitness_info[i_gen, 1]:.3f}"
        )

        if i_gen < n_generations - 1:
            pop = create_next_generation(
                pop,
                scores,
                elite_num=elite_num,
                tournament_size=tournament_size,
                crossover_prob=crossover_prob,
                mutation_prob=mutation_prob,
                gene_mutation_rate=gene_mutation_rate,
                weight_bounds=weight_bounds,
                rng=rng,
            )

        secs = time.time() - start_time_generation
        generation_avg += secs
        minutes = int(secs / 60)
        rem_secs = 60.0 * ((secs / 60.0) - minutes)
        print(f"Time to complete generation: {minutes} m {rem_secs:.3f} s")

    avg_gen_min = int(generation_avg / n_generations / 60)
    avg_gen_sec = 60.0 * ((generation_avg / n_generations / 60.0) - avg_gen_min)
    print(f"Avg time per generation: {avg_gen_min} m {avg_gen_sec:.3f} s")

    return pop, fitness_info


if __name__ == "__main__":
    nProcs = 2
    popSize = 6
    nNodes = 25
    crossoverProb = 0.8
    mutationProb = 0.9
    tournamentSize = 4
    eliteNum = 2
    nOfGenerations = 15
    timeSteps = 200
    nLattice = 50
    fileName = sys.argv[1]
    chunkSize = 1

    print(
        f"Parameters:\nFile name: {fileName}\n"
        f"nProcs = {nProcs}, Population size = {popSize}, nNodes = {nNodes}, "
        f"nLattice = {nLattice}, nGen = {nOfGenerations}, "
        f"Crossover Prob = {crossoverProb}, Mutation prob = {mutationProb}"
    )

    final_pop, _ = run_ga(
        pop_size=popSize,
        n_nodes=nNodes,
        n_generations=nOfGenerations,
        time_steps=timeSteps,
        n_lattice=nLattice,
        elite_num=eliteNum,
        tournament_size=tournamentSize,
        crossover_prob=crossoverProb,
        mutation_prob=mutationProb,
        n_procs=nProcs,
        chunk_size=chunkSize,
    )

    with open(f"{fileName}.csv", "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(final_pop)
