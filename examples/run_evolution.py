#!/usr/bin/env python3
"""
Genetic algorithm example.

This script demonstrates how to run the genetic algorithm to evolve
gene regulatory networks.
"""

from __future__ import annotations

import os
import sys
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import run_simulation
from evolution import tools_ga


def run_evolution_example() -> None:
    """Run a simple genetic algorithm example."""
    pop_size = 4
    n_nodes = 10
    n_genes = n_nodes**2
    n_generations = 5
    time_steps = 30
    n_lattice = 15
    seed = 42

    print("Running genetic algorithm with:")
    print(f"  Population size: {pop_size}")
    print(f"  Nodes: {n_nodes}")
    print(f"  Generations: {n_generations}")
    print(f"  Lattice size: {n_lattice}x{n_lattice}")

    rng = np.random.default_rng(seed)
    population = tools_ga.initialize_population(pop_size, n_genes, rng=rng)

    for gen in range(n_generations):
        print(f"\nGeneration {gen + 1}/{n_generations}")

        fitness = np.zeros(pop_size)
        for idx in range(pop_size):
            w_matrix = population[idx].reshape(n_nodes, n_nodes)
            result = run_simulation(
                w_matrix,
                time_steps=time_steps,
                n_nodes=n_nodes,
                n_lattice=n_lattice,
                early_stop=True,
                seed=seed + gen * pop_size + idx,
            )
            fitness[idx] = result.fitness

        print(f"  Best fitness: {np.max(fitness):.3f}")
        print(f"  Average fitness: {np.mean(fitness):.3f}")

        if gen < n_generations - 1:
            population = tools_ga.create_next_generation(
                population,
                fitness,
                elite_num=2,
                tournament_size=2,
                crossover_prob=0.8,
                mutation_prob=0.5,
                rng=rng,
            )

    print("\nEvolution completed!")


if __name__ == "__main__":
    run_evolution_example()
