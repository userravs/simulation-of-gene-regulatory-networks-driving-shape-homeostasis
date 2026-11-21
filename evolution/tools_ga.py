"""Genetic algorithm operators for evolving Gene Regulatory Networks."""

from __future__ import annotations

import numpy as np


def DiracDelta(a: float, b: float) -> int:
    """Return 0 if a == b, otherwise 1 (discrete difference indicator)."""
    return 0 if a == b else 1


def Crossover(
    parent1: np.ndarray,
    parent2: np.ndarray,
    crossoverProb: float,
    *,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Perform single-point length-preserving crossover between two parent chromosomes."""
    offspring1 = np.array(parent1, dtype=np.float64, copy=True)
    offspring2 = np.array(parent2, dtype=np.float64, copy=True)

    rand_val = rng.random() if rng is not None else np.random.random()
    if len(parent1) > 1 and rand_val < crossoverProb:
        crossover_point = (
            int(rng.integers(1, len(parent1)))
            if rng is not None
            else int(np.random.randint(1, len(parent1)))
        )
        offspring1[:crossover_point] = parent2[:crossover_point]
        offspring2[:crossover_point] = parent1[:crossover_point]
    return offspring1, offspring2


def Mutate(
    parent1: np.ndarray,
    parent2: np.ndarray,
    mutationProb: float,
    *,
    gene_mutation_rate: float | None = None,
    sigma: float = float(np.sqrt(0.7)),
    weight_bounds: tuple[float, float] | None = None,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply per-gene Gaussian mutation to two chromosomes with optional weight clamping."""
    if gene_mutation_rate is not None and not (0.0 <= gene_mutation_rate <= 1.0):
        raise ValueError("gene_mutation_rate must be within [0.0, 1.0].")
    if sigma < 0.0:
        raise ValueError("sigma must be non-negative.")
    if weight_bounds is not None and weight_bounds[0] >= weight_bounds[1]:
        raise ValueError("weight_bounds must satisfy low < high.")

    mutated1 = np.array(parent1, dtype=np.float64, copy=True)
    mutated2 = np.array(parent2, dtype=np.float64, copy=True)

    rand_val = rng.random() if rng is not None else np.random.random()
    if rand_val >= mutationProb:
        return mutated1, mutated2

    for chromosome in (mutated1, mutated2):
        n_genes = len(chromosome)
        if n_genes == 0:
            continue

        rate = gene_mutation_rate if gene_mutation_rate is not None else max(1.0 / n_genes, 0.05)
        if rate == 0.0:
            continue

        mask = (
            rng.random(n_genes) < rate
            if rng is not None
            else np.random.random(n_genes) < rate
        )
        if not np.any(mask):
            idx = int(rng.integers(n_genes) if rng is not None else np.random.randint(n_genes))
            mask[idx] = True

        n_mutated = int(np.count_nonzero(mask))
        noise = (
            rng.normal(loc=0.0, scale=sigma, size=n_mutated)
            if rng is not None
            else np.random.normal(loc=0.0, scale=sigma, size=n_mutated)
        )
        chromosome[mask] += noise

        if weight_bounds is not None:
            np.clip(chromosome, weight_bounds[0], weight_bounds[1], out=chromosome)

    return mutated1, mutated2


def DifferentIndex(x1: int, y1: int) -> bool:
    """Return True if indices x1 and y1 are distinct."""
    return x1 != y1


def initialize_population(
    pop_size: int,
    n_genes: int,
    *,
    weight_bounds: tuple[float, float] = (-1.0, 1.0),
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Initialize a population matrix with uniform weights inside weight_bounds."""
    if pop_size < 1:
        raise ValueError("pop_size must be >= 1.")
    if n_genes < 1:
        raise ValueError("n_genes must be >= 1.")
    low, high = weight_bounds
    if low >= high:
        raise ValueError("weight_bounds must satisfy low < high.")

    if rng is not None:
        return rng.uniform(low, high, size=(pop_size, n_genes)).astype(np.float64)
    return np.random.uniform(low, high, size=(pop_size, n_genes)).astype(np.float64)


def select_tournament_parents(
    fitness: np.ndarray,
    tournament_size: int,
    *,
    rng: np.random.Generator | None = None,
) -> tuple[int, int]:
    """Select two distinct parent indices via sequential tournament selection."""
    pop_size = len(fitness)
    if pop_size < 2:
        raise ValueError("At least 2 individuals are required to select two distinct parents.")
    if tournament_size < 2:
        raise ValueError("tournament_size must be >= 2.")

    def _draw_indices(candidates: int | np.ndarray, size: int) -> np.ndarray:
        if rng is not None:
            return rng.choice(candidates, size=size, replace=False)
        return np.random.choice(candidates, size=size, replace=False)

    t1 = _draw_indices(pop_size, min(tournament_size, pop_size))
    parent1_idx = int(t1[int(np.argmax(fitness[t1]))])

    remaining = np.array([idx for idx in range(pop_size) if idx != parent1_idx], dtype=np.intp)
    t2 = _draw_indices(remaining, min(tournament_size, len(remaining)))
    parent2_idx = int(t2[int(np.argmax(fitness[t2]))])

    return parent1_idx, parent2_idx


def create_next_generation(
    population: np.ndarray,
    fitness: np.ndarray,
    *,
    elite_num: int = 2,
    tournament_size: int = 4,
    crossover_prob: float = 0.8,
    mutation_prob: float = 0.9,
    gene_mutation_rate: float | None = None,
    sigma: float = float(np.sqrt(0.7)),
    weight_bounds: tuple[float, float] = (-1.0, 1.0),
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Build the next GA generation via elitism, tournament selection, crossover, and mutation."""
    if population.ndim != 2:
        raise ValueError("population must be a 2D array.")
    pop_size = population.shape[0]
    if pop_size < 2:
        raise ValueError("pop_size must be >= 2.")
    if len(fitness) != pop_size:
        raise ValueError("fitness length must match population size.")
    if not (0 <= elite_num <= pop_size):
        raise ValueError("elite_num must satisfy 0 <= elite_num <= pop_size.")
    if tournament_size < 2:
        raise ValueError("tournament_size must be >= 2.")
    if weight_bounds[0] >= weight_bounds[1]:
        raise ValueError("weight_bounds must satisfy low < high.")

    sorted_desc = np.argsort(fitness)[::-1]
    next_pop = np.empty_like(population, dtype=np.float64)

    for slot in range(elite_num):
        next_pop[slot] = population[sorted_desc[slot]]

    idx = elite_num
    while idx < pop_size:
        p1_idx, p2_idx = select_tournament_parents(fitness, tournament_size, rng=rng)
        child1, child2 = Crossover(
            population[p1_idx], population[p2_idx], crossover_prob, rng=rng
        )
        child1, child2 = Mutate(
            child1,
            child2,
            mutation_prob,
            gene_mutation_rate=gene_mutation_rate,
            sigma=sigma,
            weight_bounds=weight_bounds,
            rng=rng,
        )
        next_pop[idx] = child1
        idx += 1
        if idx < pop_size:
            next_pop[idx] = child2
            idx += 1

    return next_pop
