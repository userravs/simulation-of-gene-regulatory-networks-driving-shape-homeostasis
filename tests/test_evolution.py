"""Unit tests for evolutionary operators, GA diversity, NEAT config, and headless evaluation."""

from __future__ import annotations

from pathlib import Path
import neat
import numpy as np
import pytest

from evolution import main_ga, neat_parallel, tools_ga


def test_dirac_delta_and_different_index() -> None:
    """DiracDelta and DifferentIndex should return expected boolean/integer indicators."""
    assert tools_ga.DiracDelta(1.0, 1.0) == 0
    assert tools_ga.DiracDelta(1.0, 0.0) == 1
    assert not tools_ga.DifferentIndex(4, 4)
    assert tools_ga.DifferentIndex(4, 5)


def test_crossover_and_mutate_preserve_shape() -> None:
    """Crossover and Mutate should return non-aliased copies, apply per-gene mutation, and clip."""
    parent1 = np.zeros(64, dtype=np.float64)
    parent2 = np.ones(64, dtype=np.float64)

    # With probability 0, copies are equal to parents without aliasing
    c1_no, c2_no = tools_ga.Crossover(parent1, parent2, crossoverProb=0.0)
    assert np.array_equal(c1_no, parent1)
    assert np.array_equal(c2_no, parent2)
    assert c1_no is not parent1
    assert c2_no is not parent2

    # With probability 1, single-point crossover exchanges a non-empty prefix
    rng = np.random.default_rng(123)
    c1, c2 = tools_ga.Crossover(parent1, parent2, crossoverProb=1.0, rng=rng)
    assert c1.shape == (64,)
    assert c2.shape == (64,)
    assert np.allclose(c1 + c2, np.ones(64))

    # Per-gene mutation with probability 1 alters multiple genes and obeys weight bounds
    m1, m2 = tools_ga.Mutate(
        parent1,
        parent2,
        mutationProb=1.0,
        gene_mutation_rate=0.5,
        weight_bounds=(-1.0, 1.0),
        rng=rng,
    )
    assert m1.shape == (64,)
    assert m2.shape == (64,)
    assert np.count_nonzero(m1 != parent1) > 1
    assert np.count_nonzero(m2 != parent2) > 1
    assert np.all((m1 >= -1.0) & (m1 <= 1.0))
    assert np.all((m2 >= -1.0) & (m2 <= 1.0))


def test_initialize_population_bounds_and_validation() -> None:
    """initialize_population should sample excitatory and inhibitory weights in [-1, 1]."""
    rng = np.random.default_rng(99)
    pop = tools_ga.initialize_population(20, 64, rng=rng)
    assert pop.shape == (20, 64)
    assert np.all((pop >= -1.0) & (pop <= 1.0))
    assert np.any(pop < 0.0)
    assert np.any(pop > 0.0)

    with pytest.raises(ValueError, match="pop_size"):
        tools_ga.initialize_population(0, 16)
    with pytest.raises(ValueError, match="n_genes"):
        tools_ga.initialize_population(4, 0)
    with pytest.raises(ValueError, match="weight_bounds"):
        tools_ga.initialize_population(4, 16, weight_bounds=(1.0, -1.0))


@pytest.mark.parametrize(
    ("pop_size", "elite_num", "tournament_size"),
    [
        (6, 2, 4),
        (8, 2, 4),
        (5, 1, 3),
        (7, 3, 2),
        (10, 0, 3),
    ],
)
def test_create_next_generation_invariants(
    pop_size: int,
    elite_num: int,
    tournament_size: int,
) -> None:
    """create_next_generation should preserve elites once and fill all offspring slots cleanly."""
    rng = np.random.default_rng(42 + pop_size)
    n_genes = 64
    pop = tools_ga.initialize_population(pop_size, n_genes, rng=rng)
    fitness_scores = np.linspace(0.1, 0.9, pop_size)

    next_pop = tools_ga.create_next_generation(
        pop,
        fitness_scores,
        elite_num=elite_num,
        tournament_size=tournament_size,
        crossover_prob=0.8,
        mutation_prob=1.0,
        gene_mutation_rate=0.25,
        weight_bounds=(-1.0, 1.0),
        rng=rng,
    )

    assert next_pop.shape == (pop_size, n_genes)
    assert np.all((next_pop >= -1.0) & (next_pop <= 1.0))
    assert not np.any(np.all(next_pop == 0.0, axis=1))

    sorted_desc = np.argsort(fitness_scores)[::-1]
    for slot in range(elite_num):
        assert np.array_equal(next_pop[slot], pop[sorted_desc[slot]])

    for idx in range(elite_num, pop_size):
        assert not any(np.array_equal(next_pop[idx], pop[p]) for p in range(pop_size))


def test_headless_simulation_returns_delta_matrix() -> None:
    """main_ga.sim in fitness mode (mode=True) should return a binary delta matrix."""
    np.random.seed(42)
    n_nodes = 8
    n_lattice = 10
    time_steps = 10
    w_matrix = np.random.uniform(-1.0, 1.0, size=(n_nodes, n_nodes))

    delta_matrix = main_ga.sim(
        w_matrix,
        timeSteps=time_steps,
        iGen=0,
        nNodes=n_nodes,
        individual=0,
        nLattice=n_lattice,
        mode=True,
    )
    assert delta_matrix is not None
    assert delta_matrix.shape == (n_lattice, n_lattice)
    assert set(np.unique(delta_matrix)).issubset({0.0, 1.0})


@pytest.mark.parametrize("n_procs", [1, 2])
def test_run_ga_propagates_generations_sequential_and_parallel(n_procs: int) -> None:
    """run_ga should evaluate and evolve valid populations sequentially and with mp.Pool."""
    rng_init = np.random.default_rng(42)
    initial_pop = tools_ga.initialize_population(4, 64, rng=rng_init)

    final_pop, fitness_info = main_ga.run_ga(
        pop_size=4,
        n_nodes=8,
        n_generations=3,
        time_steps=6,
        n_lattice=8,
        elite_num=1,
        tournament_size=2,
        crossover_prob=0.8,
        mutation_prob=1.0,
        gene_mutation_rate=0.25,
        n_procs=n_procs,
        seed=42,
    )

    assert final_pop.shape == (4, 64)
    assert np.all((final_pop >= -1.0) & (final_pop <= 1.0))
    assert not np.array_equal(final_pop, initial_pop)
    assert fitness_info.shape == (3, 2)
    assert np.all((fitness_info >= 0.0) & (fitness_info <= 1.0))


def test_neat_config_and_runner_alignment() -> None:
    """config/config-ca and neat_parallel should align with [0, 1] homeostasis fitness."""
    config_path = Path(__file__).resolve().parent.parent / "config" / "config-ca"
    cfg = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        str(config_path),
    )

    assert 0.0 < cfg.fitness_threshold <= 1.0
    assert cfg.no_fitness_termination is False
    assert cfg.genome_config.num_inputs == 2
    assert cfg.genome_config.num_outputs == 6

    assert not hasattr(neat_parallel, "eval_genome")
    assert not hasattr(neat_parallel, "xor_inputs")
    assert not hasattr(neat_parallel, "xor_outputs")

    winner = neat_parallel.run(
        str(config_path),
        max_generations=1,
        n_workers=1,
        seed=7,
        n_lattice=8,
        time_steps=6,
    )
    assert winner is not None
    assert winner.fitness is not None
    assert 0.0 <= winner.fitness <= 1.0
