"""Core mathematical and utility functions for the GRN cellular automata simulation."""

from __future__ import annotations

import numpy as np

try:
    from numba import njit
except ImportError:  # pragma: no cover
    def njit(func=None, **_kwargs):
        if func is None:
            return lambda f: f
        return func


class flatList(list):
    """
    A list subclass that raises IndexError for negative indices.

    Prevents circular wrap-around indexing on cellular automata grid boundaries.
    """

    def __getitem__(self, index: int):
        if index < 0:
            raise IndexError("list index out of range")
        return super().__getitem__(index)


def CheckifOccupied(y_pos: int, x_pos: int, grid) -> bool:
    """
    Check if a grid position is occupied by a cell using row-major (y, x) coordinates.

    Parameters
    ----------
    y_pos : int
        Row coordinate (y axis).
    x_pos : int
        Column coordinate (x axis).
    grid : list or numpy.ndarray
        2D grid indexed as grid[y_pos][x_pos] where values > 0 indicate occupied sites.

    Returns
    -------
    bool
        True if the position is occupied, False otherwise.
    """
    return bool(grid[y_pos][x_pos] > 0)


def CheckifPreferred(y_ori: int, x_ori: int, y_pos: int, x_pos: int) -> bool:
    """
    Check if a candidate (y, x) position matches the preferred (y, x) orientation.

    Parameters
    ----------
    y_ori, x_ori : int
        Preferred orientation coordinates (row, col).
    y_pos, x_pos : int
        Candidate position coordinates (row, col).

    Returns
    -------
    bool
        True if the candidate position matches the preferred direction.
    """
    return y_pos == y_ori and x_pos == x_ori


@njit
def SGFDiffEq(
    s_matrix: np.ndarray, sigma_matrix: np.ndarray, deltaS: float, deltaT: float
) -> np.ndarray:
    """
    Update SGF (Short-range Growth Factor) concentrations using matrix operations.

    Implements the reaction equation for SGF: ds/dt = sigma - delta_s * s
    where sigma is the production rate and delta_s is the decay rate.
    """
    return s_matrix + deltaT * (sigma_matrix - deltaS * s_matrix)


@njit
def _factor_thomas_tridiagonal(
    t_matrix: np.ndarray, alpha: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Precompute tridiagonal bands of H = I+(alpha/2)T and Thomas factors of A = I-(alpha/2)T."""
    n = t_matrix.shape[0]
    half_alpha = 0.5 * alpha

    h_sub = np.zeros(n, dtype=np.float64)
    h_diag = np.zeros(n, dtype=np.float64)
    h_sup = np.zeros(n, dtype=np.float64)
    a_sub = np.zeros(n, dtype=np.float64)
    c_prime = np.zeros(n, dtype=np.float64)
    inv_denom = np.zeros(n, dtype=np.float64)

    for i in range(n):
        h_diag[i] = 1.0 + half_alpha * t_matrix[i, i]
        if i > 0:
            h_sub[i] = half_alpha * t_matrix[i, i - 1]
        if i < n - 1:
            h_sup[i] = half_alpha * t_matrix[i, i + 1]

    a_diag_0 = 1.0 - half_alpha * t_matrix[0, 0]
    inv_denom[0] = 1.0 / a_diag_0
    if n > 1:
        c_prime[0] = (-half_alpha * t_matrix[0, 1]) * inv_denom[0]

    for i in range(1, n):
        a_sub_i = -half_alpha * t_matrix[i, i - 1]
        a_sub[i] = a_sub_i
        a_diag_i = 1.0 - half_alpha * t_matrix[i, i]
        inv_d = 1.0 / (a_diag_i - a_sub_i * c_prime[i - 1])
        inv_denom[i] = inv_d
        if i < n - 1:
            c_prime[i] = (-half_alpha * t_matrix[i, i + 1]) * inv_d

    return h_sub, h_diag, h_sup, a_sub, c_prime, inv_denom


@njit
def _lgf_adi_thomas_step(
    l_matrix: np.ndarray,
    lambda_matrix: np.ndarray,
    h_sub: np.ndarray,
    h_diag: np.ndarray,
    h_sup: np.ndarray,
    a_sub: np.ndarray,
    c_prime: np.ndarray,
    inv_denom: np.ndarray,
    delta_l: float,
    delta_t: float,
) -> np.ndarray:
    """Solve one Crank-Nicolson ADI step for LGF via Thomas elimination in O(N^2)."""
    n = l_matrix.shape[0]
    half_dt = 0.5 * delta_t
    l_half = np.empty((n, n), dtype=np.float64)
    l_next = np.empty((n, n), dtype=np.float64)

    if n == 1:
        lh = l_matrix[0, 0] * h_diag[0]
        r1 = lh + half_dt * (lambda_matrix[0, 0] - delta_l * l_matrix[0, 0])
        l_half_0 = r1 * inv_denom[0]
        hl = h_diag[0] * l_half_0
        r2 = hl + half_dt * (lambda_matrix[0, 0] - delta_l * l_half_0)
        l_next[0, 0] = r2 * inv_denom[0]
        return l_next

    # Half-step 1: solve A * l_half = l_matrix @ H + (dt/2) * (lambda - delta_l * l_matrix)
    inv_d_0 = inv_denom[0]
    for j in range(n):
        if j == 0:
            lh = l_matrix[0, 0] * h_diag[0] + l_matrix[0, 1] * h_sub[1]
        elif j == n - 1:
            lh = l_matrix[0, n - 2] * h_sup[n - 2] + l_matrix[0, n - 1] * h_diag[n - 1]
        else:
            lh = (
                l_matrix[0, j - 1] * h_sup[j - 1]
                + l_matrix[0, j] * h_diag[j]
                + l_matrix[0, j + 1] * h_sub[j + 1]
            )
        r1 = lh + half_dt * (lambda_matrix[0, j] - delta_l * l_matrix[0, j])
        l_half[0, j] = r1 * inv_d_0

    for i in range(1, n):
        a_sub_i = a_sub[i]
        inv_d_i = inv_denom[i]

        lh_0 = l_matrix[i, 0] * h_diag[0] + l_matrix[i, 1] * h_sub[1]
        r1_0 = lh_0 + half_dt * (lambda_matrix[i, 0] - delta_l * l_matrix[i, 0])
        l_half[i, 0] = (r1_0 - a_sub_i * l_half[i - 1, 0]) * inv_d_i

        for j in range(1, n - 1):
            lh = (
                l_matrix[i, j - 1] * h_sup[j - 1]
                + l_matrix[i, j] * h_diag[j]
                + l_matrix[i, j + 1] * h_sub[j + 1]
            )
            r1 = lh + half_dt * (lambda_matrix[i, j] - delta_l * l_matrix[i, j])
            l_half[i, j] = (r1 - a_sub_i * l_half[i - 1, j]) * inv_d_i

        lh_last = l_matrix[i, n - 2] * h_sup[n - 2] + l_matrix[i, n - 1] * h_diag[n - 1]
        r1_last = lh_last + half_dt * (lambda_matrix[i, n - 1] - delta_l * l_matrix[i, n - 1])
        l_half[i, n - 1] = (r1_last - a_sub_i * l_half[i - 1, n - 1]) * inv_d_i

    for i in range(n - 2, -1, -1):
        cp_i = c_prime[i]
        for j in range(n):
            l_half[i, j] = l_half[i, j] - cp_i * l_half[i + 1, j]

    # Half-step 2: solve l_next @ A = H @ l_half + (dt/2) * (lambda - delta_l * l_half)
    for i in range(n):
        hd_i = h_diag[i]
        w_prev = h_sub[i] if i > 0 else 0.0
        w_next = h_sup[i] if i < n - 1 else 0.0
        prev_row = i - 1 if i > 0 else 0
        next_row = i + 1 if i < n - 1 else n - 1

        hl_0 = (
            w_prev * l_half[prev_row, 0]
            + hd_i * l_half[i, 0]
            + w_next * l_half[next_row, 0]
        )
        r2_0 = hl_0 + half_dt * (lambda_matrix[i, 0] - delta_l * l_half[i, 0])
        l_next[i, 0] = r2_0 * inv_denom[0]

        for j in range(1, n):
            hl = (
                w_prev * l_half[prev_row, j]
                + hd_i * l_half[i, j]
                + w_next * l_half[next_row, j]
            )
            r2 = hl + half_dt * (lambda_matrix[i, j] - delta_l * l_half[i, j])
            l_next[i, j] = (r2 - a_sub[j] * l_next[i, j - 1]) * inv_denom[j]

        for j in range(n - 2, -1, -1):
            l_next[i, j] = l_next[i, j] - c_prime[j] * l_next[i, j + 1]

    return l_next


class LGFThomasSolver:
    """Precomputed O(N^2) Crank-Nicolson ADI solver for LGF using the Thomas algorithm."""

    def __init__(
        self,
        n_lattice: int,
        delta_l: float = 0.1,
        delta_t: float = 1.0,
        delta_r: float = 1.0,
        diff_const: float = 1.0,
    ) -> None:
        """Precompute constant tridiagonal Neumann factors for a square n_lattice grid."""
        if n_lattice < 1:
            raise ValueError("n_lattice must be >= 1.")
        if delta_r <= 0.0:
            raise ValueError("delta_r must be > 0.")
        if delta_t < 0.0:
            raise ValueError("delta_t must be >= 0.")
        if delta_l < 0.0:
            raise ValueError("delta_l must be >= 0.")
        if diff_const < 0.0:
            raise ValueError("diff_const must be >= 0.")

        self.n_lattice = n_lattice
        self.delta_l = delta_l
        self.delta_t = delta_t
        self.delta_r = delta_r
        self.diff_const = diff_const

        t_matrix = GenerateTMatrix(n_lattice)
        alpha = diff_const * delta_t / (delta_r**2)
        (
            self._h_sub,
            self._h_diag,
            self._h_sup,
            self._a_sub,
            self._c_prime,
            self._inv_denom,
        ) = _factor_thomas_tridiagonal(t_matrix, alpha)

    def step(self, l_matrix: np.ndarray, lambda_matrix: np.ndarray) -> np.ndarray:
        """Advance the LGF concentration field by one Crank-Nicolson ADI step."""
        expected = (self.n_lattice, self.n_lattice)
        if l_matrix.shape != expected or lambda_matrix.shape != expected:
            raise ValueError(
                f"Expected arrays of shape {expected}, got "
                f"l_matrix={l_matrix.shape} and lambda_matrix={lambda_matrix.shape}."
            )
        return _lgf_adi_thomas_step(
            l_matrix,
            lambda_matrix,
            self._h_sub,
            self._h_diag,
            self._h_sup,
            self._a_sub,
            self._c_prime,
            self._inv_denom,
            self.delta_l,
            self.delta_t,
        )


@njit
def LGFDiffEq(
    i_matrix: np.ndarray,
    t_matrix: np.ndarray,
    l_matrix: np.ndarray,
    lambda_matrix: np.ndarray,
    deltaL: float,
    deltaT: float,
    deltaR: float,
    D: float,
) -> np.ndarray:
    """
    Update LGF (Long-range Growth Factor) concentrations using a Crank-Nicolson scheme.

    Implements the reaction-diffusion PDE via Thomas tridiagonal ADI sweeps in O(N^2):
    dl/dt = D * nabla^2(l) + lambda - delta_l * l
    """
    _ = i_matrix
    alpha = D * deltaT / (deltaR**2)
    h_sub, h_diag, h_sup, a_sub, c_prime, inv_denom = _factor_thomas_tridiagonal(
        t_matrix, alpha
    )
    return _lgf_adi_thomas_step(
        l_matrix,
        lambda_matrix,
        h_sub,
        h_diag,
        h_sup,
        a_sub,
        c_prime,
        inv_denom,
        deltaL,
        deltaT,
    )


def GenerateTMatrix(size: int) -> np.ndarray:
    """Generate the discrete 1D Laplacian T-matrix for LGF spatial discretization."""
    t_matrix = np.zeros((size, size), dtype=np.float64)
    for ix in range(size - 1):
        t_matrix[ix, ix] = -2.0
        t_matrix[ix, ix + 1] = 1.0
        t_matrix[ix + 1, ix] = 1.0
    t_matrix[0, 0] = -1.0
    t_matrix[size - 1, size - 1] = -1.0
    return t_matrix


def GenerateIMatrix(size: int) -> np.ndarray:
    """Generate an identity matrix of size x size."""
    return np.eye(size, dtype=np.float64)


@njit
def RecurrentNeuralNetwork(
    inputs: np.ndarray, wMatrix: np.ndarray, V: np.ndarray
) -> np.ndarray:
    """Update Recurrent Neural Network activation values using a sigmoid transfer function."""
    bj = np.dot(wMatrix, V) - inputs
    for ix in range(len(bj)):
        V[ix] = 1.0 / (1.0 + np.exp(-2.0 * bj[ix]))
    return V


def GetStructure(cell_array, nLattice: int) -> np.ndarray:
    """Return a binary occupancy matrix (1 where cell_array != 0, else 0)."""
    return (np.asarray(cell_array) != 0).astype(np.float64)


def GetrNN(csvFile: str, ind: int) -> np.ndarray:
    """Load an individual's recurrent neural network weight matrix from a CSV file."""
    with open(csvFile, "r", encoding="utf-8") as csvfile:
        best_individuals = np.loadtxt(csvfile, delimiter=",")
    row = best_individuals if best_individuals.ndim == 1 else best_individuals[ind, :]
    n_nodes = int(np.sqrt(len(row)))
    return np.array(row.reshape(n_nodes, n_nodes), dtype=np.float64)
