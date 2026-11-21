"""Parallel NEAT neuroevolution runner for the cellular automata simulation."""

from __future__ import annotations

from functools import partial
import os
import random
import sys
import neat
import numpy as np

# Ensure repository root is on sys.path when invoked directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import SimulationConfig, SimulationEngine
from evolution.neat_cell_agent import cell


def EvaluateIndividual(
    genome,
    config,
    *,
    n_lattice: int = 50,
    time_steps: int = 200,
    seed: int | None = None,
) -> float:
    """Evaluate a NEAT genome using the unified core cellular automata simulation engine."""
    sim_config = SimulationConfig(
        n_lattice=n_lattice,
        time_steps=time_steps,
        early_stop=True,
        seed=seed,
    )
    engine = SimulationEngine(
        lambda y_pos, x_pos: cell(y_pos, x_pos, genome, config),
        config=sim_config,
    )
    return engine.run().fitness


def run(
    config_file: str,
    *,
    max_generations: int | None = 50,
    n_workers: int = 3,
    seed: int | None = None,
    n_lattice: int = 50,
    time_steps: int = 200,
):
    """Load NEAT configuration and run genome evaluation up to max_generations."""
    if n_workers < 1:
        raise ValueError("n_workers must be >= 1.")
    if max_generations is not None and max_generations < 1:
        raise ValueError("max_generations must be >= 1 when specified.")

    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        if hasattr(config, "seed"):
            config.seed = seed

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    if n_workers == 1:
        def _eval_sequential(genomes, cfg) -> None:
            for genome_id, genome in genomes:
                genome_seed = seed + genome_id if seed is not None else None
                genome.fitness = EvaluateIndividual(
                    genome,
                    cfg,
                    n_lattice=n_lattice,
                    time_steps=time_steps,
                    seed=genome_seed,
                )

        winner = population.run(_eval_sequential, n=max_generations)
    else:
        eval_fn = partial(
            EvaluateIndividual,
            n_lattice=n_lattice,
            time_steps=time_steps,
        )
        with neat.ParallelEvaluator(n_workers, eval_fn, seed=seed) as evaluator:
            winner = population.run(evaluator.evaluate, n=max_generations)

    print(f"\nBest genome:\n{winner!s}")
    return winner


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(repo_root, "config", "config-ca")
    run(config_path)
