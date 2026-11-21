"""Headless, deterministic cellular automata and GRN simulation engine."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
import numpy as np

from core.cell_agent import cell
from core.tools import (
    GetStructure,
    LGFThomasSolver,
    SGFDiffEq,
    flatList,
)

CellFactory = Callable[[int, int], Any]


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration parameters for a headless cellular automata simulation."""

    n_lattice: int = 50
    time_steps: int = 200
    delta_t: float = 1.0
    delta_r: float = 1.0
    delta_s: float = 0.5
    delta_l: float = 0.1
    diff_const: float = 1.0
    early_stop: bool = True
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.n_lattice < 1:
            raise ValueError("n_lattice must be >= 1.")
        if self.time_steps < 1:
            raise ValueError("time_steps must be >= 1.")
        if self.delta_r <= 0.0:
            raise ValueError("delta_r must be > 0.")
        if self.delta_t < 0.0:
            raise ValueError("delta_t must be >= 0.")
        if self.delta_s < 0.0:
            raise ValueError("delta_s must be >= 0.")
        if self.delta_l < 0.0:
            raise ValueError("delta_l must be >= 0.")
        if self.diff_const < 0.0:
            raise ValueError("diff_const must be >= 0.")


@dataclass(frozen=True)
class StepSnapshot:
    """Immutable state snapshot emitted after a single simulation tick."""

    step: int
    cell_grid: np.ndarray
    sgf_grid: np.ndarray
    lgf_grid: np.ndarray
    living_cells: int
    orientation_grid: np.ndarray | None = None


def extract_orientation_grid(cell_list: list[Any], n_lattice: int) -> np.ndarray:
    """Extract per-cell polarization compass unit vectors (dy, dx) onto an (N, N, 2) grid."""
    orient = np.zeros((n_lattice, n_lattice, 2), dtype=np.float64)
    for agent in cell_list:
        y = int(agent.yPos)
        x = int(agent.xPos)
        if not (0 <= y < n_lattice and 0 <= x < n_lattice):
            continue
        if not getattr(agent, "compass", True):
            continue

        ori = getattr(agent, "orientation", None)
        if ori is not None and len(ori) >= 2 and (int(ori[0]) != y or int(ori[1]) != x):
            dy = float(np.sign(int(ori[0]) - y))
            dx = float(np.sign(int(ori[1]) - x))
        else:
            v_arr = getattr(agent, "V", None)
            if v_arr is None or len(v_arr) <= 7:
                continue
            arrow = float(v_arr[7])
            if arrow < 0.25:
                dy, dx = -1.0, 0.0
            elif arrow < 0.50:
                dy, dx = 1.0, 0.0
            elif arrow < 0.75:
                dy, dx = 0.0, 1.0
            else:
                dy, dx = 0.0, -1.0

        orient[y, x, 0] = dy
        orient[y, x, 1] = dx

    return orient


@dataclass(frozen=True)
class SimulationResult:
    """Structured final state and homeostasis metrics from a simulation run."""

    cell_grid: np.ndarray
    sgf_grid: np.ndarray
    lgf_grid: np.ndarray
    halfway_structure: np.ndarray
    final_structure: np.ndarray
    delta_matrix: np.ndarray
    fitness: float
    steps_executed: int
    final_cell_count: int
    terminated_early: bool


class SimulationEngine:
    """Unified, plotting-free simulation stepper with deterministic PRNG seeding."""

    def __init__(
        self,
        cell_factory: CellFactory,
        config: SimulationConfig | None = None,
    ) -> None:
        """Initialize lattice grids, Thomas LGF solver, and central mother cell."""
        self.config = config if config is not None else SimulationConfig()
        self._rng = np.random.default_rng(self.config.seed)

        n = self.config.n_lattice
        np_cell_grid = np.zeros((n, n), dtype=np.float64)
        self.cell_grid = flatList([flatList(np_cell_grid[r, :]) for r in range(n)])
        self.chem_grid = np.zeros((n, n, 2), dtype=np.float64)

        init_y = n // 2
        init_x = n // 2
        self.cell_list: list[Any] = [cell_factory(init_y, init_x)]
        self.cell_grid[init_y][init_x] = 1

        self.lgf_solver = LGFThomasSolver(
            n,
            delta_l=self.config.delta_l,
            delta_t=self.config.delta_t,
            delta_r=self.config.delta_r,
            diff_const=self.config.diff_const,
        )

        self._halfway_raw = np.zeros((n, n), dtype=np.float64)
        self._final_raw = np.ones((n, n), dtype=np.float64)
        self.current_step = 0
        self.terminated_early = False

    @classmethod
    def from_weight_matrix(
        cls,
        w_matrix: np.ndarray,
        n_nodes: int | None = None,
        config: SimulationConfig | None = None,
    ) -> SimulationEngine:
        """Build an engine driven by core.cell_agent.cell and an RNN weight matrix."""
        weights = np.asarray(w_matrix, dtype=np.float64)
        if weights.ndim != 2 or weights.shape[0] != weights.shape[1]:
            raise ValueError("w_matrix must be a square 2D array.")

        inferred_nodes = weights.shape[0]
        if n_nodes is not None and n_nodes != inferred_nodes:
            raise ValueError(
                f"n_nodes ({n_nodes}) does not match w_matrix shape {weights.shape}."
            )
        if inferred_nodes < 8:
            raise ValueError("w_matrix must have at least 8 nodes for GRN signaling outputs.")

        return cls(
            lambda y_pos, x_pos: cell(y_pos, x_pos, weights, inferred_nodes),
            config=config,
        )

    def step(self) -> StepSnapshot:
        """Advance cellular automata, chemical secretions, and PDE diffusion by one step."""
        n = self.config.n_lattice
        sigma_m = np.zeros((n, n), dtype=np.float64)
        lambda_m = np.zeros((n, n), dtype=np.float64)

        # O(M) Fisher-Yates shuffle over the living cells at the start of the tick.
        snapshot_cells = list(self.cell_list)
        order = np.arange(len(snapshot_cells), dtype=np.intp)
        self._rng.shuffle(order)

        for idx in order:
            current_cell = snapshot_cells[int(idx)]
            sgf_reading, lgf_reading = current_cell.Sense(self.chem_grid)
            current_cell.GenerateStatus(sgf_reading, lgf_reading)

            sigma_m[current_cell.yPos, current_cell.xPos] = current_cell.sgfAmount
            lambda_m[current_cell.yPos, current_cell.xPos] = current_cell.lgfAmount

            if current_cell.state == "Quiet":
                current_cell.Quiet(self.cell_grid)
            elif current_cell.state == "Split":
                current_cell.Split(self.cell_grid, self.cell_list, rng=self._rng)
            elif current_cell.state == "Move":
                current_cell.Move(self.cell_grid, rng=self._rng)
            else:
                current_cell.Die(self.cell_grid)

        self.cell_list = [agent for agent in self.cell_list if not agent.amidead]

        self.chem_grid[:, :, 0] = SGFDiffEq(
            self.chem_grid[:, :, 0],
            sigma_m,
            self.config.delta_s,
            self.config.delta_t,
        )
        self.chem_grid[:, :, 1] = self.lgf_solver.step(
            self.chem_grid[:, :, 1],
            lambda_m,
        )

        step_idx = self.current_step
        midpoint_step = max(0, (self.config.time_steps // 2) - 1)
        final_step = self.config.time_steps - 1

        if len(self.cell_list) == 0:
            self._halfway_raw = np.zeros((n, n), dtype=np.float64)
            self._final_raw = np.ones((n, n), dtype=np.float64)
            self.terminated_early = True
        else:
            if step_idx == midpoint_step:
                if len(self.cell_list) <= int((n**2) * 0.01):
                    self._halfway_raw = np.zeros((n, n), dtype=np.float64)
                    self._final_raw = np.ones((n, n), dtype=np.float64)
                    self.terminated_early = True
                else:
                    self._halfway_raw = np.array(self.cell_grid, dtype=np.float64)

            if step_idx == final_step and not self.terminated_early:
                if len(self.cell_list) == n**2:
                    self._halfway_raw = np.zeros((n, n), dtype=np.float64)
                    self._final_raw = np.ones((n, n), dtype=np.float64)
                else:
                    self._final_raw = np.array(self.cell_grid, dtype=np.float64)

        snapshot = StepSnapshot(
            step=step_idx,
            cell_grid=np.asarray(self.cell_grid, dtype=np.float64).copy(),
            sgf_grid=self.chem_grid[:, :, 0].copy(),
            lgf_grid=self.chem_grid[:, :, 1].copy(),
            living_cells=len(self.cell_list),
            orientation_grid=extract_orientation_grid(self.cell_list, n),
        )
        self.current_step += 1
        return snapshot

    def run(
        self,
        *,
        on_step: Callable[[StepSnapshot], None] | None = None,
    ) -> SimulationResult:
        """Run up to config.time_steps ticks and compute homeostasis metrics."""
        while self.current_step < self.config.time_steps:
            snapshot = self.step()
            if on_step is not None:
                on_step(snapshot)
            if self.config.early_stop and self.terminated_early:
                break

        n = self.config.n_lattice
        halfway_structure = GetStructure(self._halfway_raw, n)
        final_structure = GetStructure(self._final_raw, n)
        delta_matrix = (halfway_structure != final_structure).astype(np.float64)
        fitness = 1.0 - (float(np.sum(delta_matrix)) / (n**2))

        return SimulationResult(
            cell_grid=np.asarray(self.cell_grid, dtype=np.float64).copy(),
            sgf_grid=self.chem_grid[:, :, 0].copy(),
            lgf_grid=self.chem_grid[:, :, 1].copy(),
            halfway_structure=halfway_structure,
            final_structure=final_structure,
            delta_matrix=delta_matrix,
            fitness=fitness,
            steps_executed=self.current_step,
            final_cell_count=len(self.cell_list),
            terminated_early=self.terminated_early,
        )


def run_simulation(
    w_matrix: np.ndarray,
    *,
    time_steps: int = 200,
    n_nodes: int | None = None,
    n_lattice: int = 50,
    seed: int | None = None,
    early_stop: bool = True,
    on_step: Callable[[StepSnapshot], None] | None = None,
    delta_t: float = 1.0,
    delta_r: float = 1.0,
    delta_s: float = 0.5,
    delta_l: float = 0.1,
    diff_const: float = 1.0,
) -> SimulationResult:
    """Convenience wrapper to execute a full RNN simulation headlessly."""
    config = SimulationConfig(
        n_lattice=n_lattice,
        time_steps=time_steps,
        delta_t=delta_t,
        delta_r=delta_r,
        delta_s=delta_s,
        delta_l=delta_l,
        diff_const=diff_const,
        early_stop=early_stop,
        seed=seed,
    )
    engine = SimulationEngine.from_weight_matrix(
        w_matrix,
        n_nodes=n_nodes,
        config=config,
    )
    return engine.run(on_step=on_step)
