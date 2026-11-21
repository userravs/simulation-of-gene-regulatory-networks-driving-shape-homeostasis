"""Unit tests for core mathematical utilities and PDE solvers in core/tools.py."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from core.tools import (
    CheckifOccupied,
    CheckifPreferred,
    GenerateIMatrix,
    GenerateTMatrix,
    GetStructure,
    GetrNN,
    LGFDiffEq,
    LGFThomasSolver,
    RecurrentNeuralNetwork,
    SGFDiffEq,
    flatList,
)


def _dense_crank_nicolson_reference(
    i_matrix: np.ndarray,
    t_matrix: np.ndarray,
    l_matrix: np.ndarray,
    lambda_matrix: np.ndarray,
    delta_l: float,
    delta_t: float,
    delta_r: float,
    diff_const: float,
) -> np.ndarray:
    """Dense matrix-inversion Crank-Nicolson reference implementation."""
    alpha = diff_const * delta_t / (delta_r**2)
    g = np.linalg.inv(i_matrix - (alpha / 2.0) * t_matrix)
    h = i_matrix + (alpha / 2.0) * t_matrix
    f_1 = (delta_t / 2.0) * (lambda_matrix - delta_l * l_matrix)
    l_half = g @ (l_matrix @ h + f_1)
    f_2 = (delta_t / 2.0) * (lambda_matrix - delta_l * l_half)
    return ((h @ l_half) + f_2) @ g


def test_flat_list_rejects_negative_indices() -> None:
    """flatList should allow non-negative indices and raise IndexError on negative indices."""
    grid_row = flatList([10, 20, 30])
    assert grid_row[0] == 10
    assert grid_row[2] == 30
    with pytest.raises(IndexError):
        _ = grid_row[-1]


def test_check_if_occupied_and_preferred() -> None:
    """CheckifOccupied and CheckifPreferred should use row-major (y, x) coordinates."""
    grid = [[0, 1], [0, 0]]
    assert not CheckifOccupied(0, 0, grid)
    assert CheckifOccupied(0, 1, grid)
    assert not CheckifOccupied(1, 0, grid)

    assert CheckifPreferred(3, 4, 3, 4)
    assert not CheckifPreferred(3, 4, 4, 3)


def test_generate_matrices() -> None:
    """GenerateIMatrix and GenerateTMatrix should construct valid finite-difference matrices."""
    size = 5
    i_mat = GenerateIMatrix(size)
    t_mat = GenerateTMatrix(size)

    assert i_mat.shape == (size, size)
    assert np.allclose(i_mat, np.eye(size))

    assert t_mat.shape == (size, size)
    assert t_mat[0, 0] == -1.0
    assert t_mat[size - 1, size - 1] == -1.0
    assert t_mat[2, 2] == -2.0
    assert t_mat[2, 3] == 1.0
    assert t_mat[3, 2] == 1.0


def test_sgf_and_lgf_diffusion_equations() -> None:
    """SGFDiffEq and LGFDiffEq should update chemical concentrations without NaNs."""
    size = 6
    s_mat = np.zeros((size, size), dtype=np.float64)
    sigma_mat = np.ones((size, size), dtype=np.float64) * 0.2

    s_next = SGFDiffEq(s_mat, sigma_mat, deltaS=0.5, deltaT=1.0)
    assert s_next.shape == (size, size)
    assert np.allclose(s_next, 0.2)

    i_mat = GenerateIMatrix(size)
    t_mat = GenerateTMatrix(size)
    l_mat = np.zeros((size, size), dtype=np.float64)
    lambda_mat = np.zeros((size, size), dtype=np.float64)
    lambda_mat[size // 2, size // 2] = 1.0

    l_next = LGFDiffEq(
        i_mat, t_mat, l_mat, lambda_mat, deltaL=0.1, deltaT=1.0, deltaR=1.0, D=1.0
    )
    assert l_next.shape == (size, size)
    assert not np.isnan(l_next).any()
    assert l_next[size // 2, size // 2] > 0.0


@pytest.mark.parametrize("size", [2, 5, 16, 32])
@pytest.mark.parametrize(
    ("delta_l", "delta_t", "delta_r", "diff_const"),
    [
        (0.1, 1.0, 1.0, 1.0),
        (0.05, 0.5, 1.0, 1.5),
        (0.0, 0.25, 0.5, 0.8),
    ],
)
def test_lgf_thomas_matches_dense_crank_nicolson_reference(
    size: int,
    delta_l: float,
    delta_t: float,
    delta_r: float,
    diff_const: float,
) -> None:
    """Thomas ADI solver and LGFDiffEq should match dense Crank-Nicolson within 1e-12."""
    rng = np.random.default_rng(1234 + size)
    i_mat = GenerateIMatrix(size)
    t_mat = GenerateTMatrix(size)
    solver = LGFThomasSolver(
        size,
        delta_l=delta_l,
        delta_t=delta_t,
        delta_r=delta_r,
        diff_const=diff_const,
    )

    l_ref = rng.uniform(0.0, 2.0, size=(size, size))
    l_solver = l_ref.copy()
    l_func = l_ref.copy()
    lambda_mat = rng.uniform(0.0, 0.5, size=(size, size))

    for _ in range(5):
        l_ref = _dense_crank_nicolson_reference(
            i_mat, t_mat, l_ref, lambda_mat, delta_l, delta_t, delta_r, diff_const
        )
        l_solver = solver.step(l_solver, lambda_mat)
        l_func = LGFDiffEq(
            i_mat, t_mat, l_func, lambda_mat, delta_l, delta_t, delta_r, diff_const
        )

    assert np.allclose(l_solver, l_ref, atol=1e-12, rtol=1e-12)
    assert np.allclose(l_func, l_ref, atol=1e-12, rtol=1e-12)


def test_lgf_thomas_conserves_mass_under_neumann_boundaries() -> None:
    """Zero-flux Neumann boundaries should conserve total LGF mass when lambda=0 and decay=0."""
    size = 12
    solver = LGFThomasSolver(size, delta_l=0.0, delta_t=1.0, delta_r=1.0, diff_const=1.0)
    l_mat = np.zeros((size, size), dtype=np.float64)
    l_mat[0, 0] = 3.5
    l_mat[4, 9] = 1.5
    lambda_zero = np.zeros((size, size), dtype=np.float64)
    initial_mass = float(np.sum(l_mat))

    for _ in range(20):
        l_mat = solver.step(l_mat, lambda_zero)

    assert np.isclose(float(np.sum(l_mat)), initial_mass, atol=1e-12)


def test_lgf_thomas_solver_validation() -> None:
    """LGFThomasSolver should reject invalid parameters and mismatched array shapes."""
    with pytest.raises(ValueError, match="n_lattice"):
        LGFThomasSolver(0)
    with pytest.raises(ValueError, match="delta_r"):
        LGFThomasSolver(4, delta_r=0.0)
    with pytest.raises(ValueError, match="delta_t"):
        LGFThomasSolver(4, delta_t=-1.0)
    with pytest.raises(ValueError, match="delta_l"):
        LGFThomasSolver(4, delta_l=-0.1)
    with pytest.raises(ValueError, match="diff_const"):
        LGFThomasSolver(4, diff_const=-0.5)

    solver = LGFThomasSolver(4)
    with pytest.raises(ValueError, match="Expected arrays of shape"):
        solver.step(np.zeros((3, 3)), np.zeros((4, 4)))


def test_recurrent_neural_network_bounds() -> None:
    """RecurrentNeuralNetwork activations should remain strictly within (0, 1)."""
    n_nodes = 8
    inputs = np.zeros(n_nodes, dtype=np.float64)
    inputs[0] = 0.5
    inputs[1] = 1.2
    w_matrix = np.ones((n_nodes, n_nodes), dtype=np.float64) * 0.25
    v_state = np.zeros(n_nodes, dtype=np.float64)

    updated_v = RecurrentNeuralNetwork(inputs, w_matrix, v_state)
    assert updated_v.shape == (n_nodes,)
    assert np.all((updated_v > 0.0) & (updated_v < 1.0))


def test_get_structure_and_get_rnn(tmp_path: Path) -> None:
    """GetStructure and GetrNN should convert grids and load saved weight matrices."""
    raw_grid = np.array([[0, 2], [3, 0]])
    binary = GetStructure(raw_grid, 2)
    assert np.array_equal(binary, np.array([[0.0, 1.0], [1.0, 0.0]]))

    csv_path = tmp_path / "pop.csv"
    weights = np.arange(16, dtype=np.float64).reshape(1, 16)
    np.savetxt(csv_path, weights, delimiter=",")

    loaded = GetrNN(str(csv_path), 0)
    assert loaded.shape == (4, 4)
    assert np.allclose(loaded, weights.reshape(4, 4))

