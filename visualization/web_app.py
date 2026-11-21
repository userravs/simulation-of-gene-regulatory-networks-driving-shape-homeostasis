#!/usr/bin/env python3
"""
Streamlit Web Application for Gene Regulatory Network Simulation.

This web application provides an interactive interface for running cellular
automata simulations driven by recurrent gene regulatory networks and
visualizing cell states and chemical signaling fields in real time.
"""

from __future__ import annotations

import os
import sys
import time
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cell_agent import cell
from core.engine import (
    SimulationConfig,
    SimulationEngine,
    SimulationResult,
    StepSnapshot,
    extract_orientation_grid,
    run_simulation,
)
from evolution import tools_ga
from visualization.palettes import (
    CELL_STATE_LABELS,
    DEFAULT_PALETTE,
    build_discrete_plotly_colorscale,
    get_cell_state_colors,
)
from visualization.timelapse import build_gif_bytes, render_snapshot_png_bytes

# Page configuration
st.set_page_config(
    page_title="Gene Regulatory Network Simulation",
    layout="wide",
    initial_sidebar_state="expanded",
)


def generate_weight_matrix(
    n_nodes: int,
    network_type: str,
    seed: int | None = None,
) -> np.ndarray:
    """Generate a GRN weight matrix for the requested network topology."""
    rng = np.random.default_rng(seed)
    weights = rng.uniform(-1.0, 1.0, size=(n_nodes, n_nodes))

    if network_type == "Erdős-Rényi":
        graph = nx.erdos_renyi_graph(n_nodes, p=0.3, seed=seed, directed=True)
        adj = nx.to_numpy_array(graph, dtype=np.float64)
        return adj * weights
    if network_type == "Watts-Strogatz":
        k = max(2, min(n_nodes - 1, 4))
        graph = nx.watts_strogatz_graph(n_nodes, k=k, p=0.2, seed=seed)
        adj = nx.to_numpy_array(graph, dtype=np.float64)
        return adj * weights
    if network_type == "Barabási-Albert":
        m = max(1, min(n_nodes - 1, 2))
        graph = nx.barabasi_albert_graph(n_nodes, m=m, seed=seed)
        adj = nx.to_numpy_array(graph, dtype=np.float64)
        return adj * weights
    return weights


def compute_step_telemetry(snapshot: StepSnapshot) -> dict[str, float | int]:
    """Extract cell-state counts and chemical summary statistics from a StepSnapshot."""
    grid = snapshot.cell_grid
    return {
        "step": snapshot.step + 1,
        "quiet_cells": int(np.count_nonzero(grid == 1)),
        "moving_cells": int(np.count_nonzero(grid == 2)),
        "divided_cells": int(np.count_nonzero(grid == 3)),
        "living_cells": int(snapshot.living_cells),
        "sgf_mean": float(np.mean(snapshot.sgf_grid)),
        "sgf_max": float(np.max(snapshot.sgf_grid)),
        "lgf_mean": float(np.mean(snapshot.lgf_grid)),
        "lgf_max": float(np.max(snapshot.lgf_grid)),
    }


def run_batch_simulation(
    w_matrix: np.ndarray,
    *,
    time_steps: int,
    n_nodes: int,
    n_lattice: int,
    seed: int | None = None,
    early_stop: bool = False,
) -> tuple[SimulationResult, list[StepSnapshot], list[dict[str, float | int]]]:
    """Run a full simulation horizon in one pass and collect snapshots and telemetry."""
    snapshots: list[StepSnapshot] = []
    telemetry: list[dict[str, float | int]] = []

    def _record(snapshot: StepSnapshot) -> None:
        snapshots.append(snapshot)
        telemetry.append(compute_step_telemetry(snapshot))

    result = run_simulation(
        w_matrix,
        time_steps=time_steps,
        n_nodes=n_nodes,
        n_lattice=n_lattice,
        early_stop=early_stop,
        seed=seed,
        on_step=_record,
    )
    return result, snapshots, telemetry


def init_simulation_state(
    n_nodes: int,
    n_lattice: int,
    network_type: str,
    seed: int | None = None,
    time_steps: int = 100,
) -> None:
    """Initialize a unified SimulationEngine and expose its state in session_state."""
    w_matrix = generate_weight_matrix(n_nodes, network_type, seed=seed)
    engine = SimulationEngine.from_weight_matrix(
        w_matrix,
        n_nodes=n_nodes,
        config=SimulationConfig(
            n_lattice=n_lattice,
            time_steps=time_steps,
            early_stop=False,
            seed=seed,
        ),
    )

    st.session_state.engine = engine
    st.session_state.w_matrix = w_matrix
    st.session_state.cell_grid = engine.cell_grid
    st.session_state.chem_grid = engine.chem_grid
    st.session_state.cell_list = engine.cell_list
    st.session_state.snapshots = []
    st.session_state.telemetry = []
    st.session_state.sim_result = None
    st.session_state.sim_config = (n_nodes, n_lattice, network_type, time_steps, seed)


def run_simulation_step(n_lattice: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Advance the unified core simulation engine by one time step."""
    _ = n_lattice
    engine: SimulationEngine = st.session_state.engine
    snapshot = engine.step()
    st.session_state.cell_grid = engine.cell_grid
    st.session_state.chem_grid = engine.chem_grid
    st.session_state.cell_list = engine.cell_list
    st.session_state.snapshots.append(snapshot)
    st.session_state.telemetry.append(compute_step_telemetry(snapshot))
    return snapshot.cell_grid, snapshot.sgf_grid, snapshot.lgf_grid


def compute_lgf_gradient(lgf_grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute finite-difference (grad_y, grad_x) chemical gradient fields for LGF."""
    lgf_data = np.asarray(lgf_grid, dtype=np.float64)
    if lgf_data.ndim != 2 or lgf_data.shape[0] < 2 or lgf_data.shape[1] < 2:
        zeros = np.zeros_like(lgf_data, dtype=np.float64)
        return zeros, zeros
    grad_y, grad_x = np.gradient(lgf_data)
    return np.asarray(grad_y, dtype=np.float64), np.asarray(grad_x, dtype=np.float64)


def create_cell_grid_plot(
    cell_grid: np.ndarray,
    sgf_grid: np.ndarray,
    lgf_grid: np.ndarray,
    palette: str = DEFAULT_PALETTE,
    *,
    step: int | None = None,
    orientation_grid: np.ndarray | None = None,
    show_compass: bool = False,
    show_lgf_gradient: bool = False,
) -> go.Figure:
    """Create an interactive Plotly visualization of the cell system with 1:1 square axes."""
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=("Cells", "SGF Concentration", "LGF Concentration"),
        specs=[[{"type": "xy"}, {"type": "xy"}, {"type": "xy"}]],
        horizontal_spacing=0.07,
    )

    colorscale = build_discrete_plotly_colorscale(get_cell_state_colors(palette))

    fig.add_trace(
        go.Heatmap(
            z=cell_grid,
            colorscale=colorscale,
            zmin=-0.5,
            zmax=3.5,
            showscale=True,
            colorbar=dict(
                title=dict(text="Cell States", side="top"),
                orientation="h",
                x=0.145,
                xanchor="center",
                y=-0.22,
                yanchor="top",
                len=0.28,
                thickness=14,
                ticktext=list(CELL_STATE_LABELS),
                tickvals=[0, 1, 2, 3],
            ),
            name="Cells",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Heatmap(
            z=sgf_grid,
            colorscale="Reds",
            showscale=True,
            colorbar=dict(
                title=dict(text="SGF Level", side="top"),
                orientation="h",
                x=0.50,
                xanchor="center",
                y=-0.22,
                yanchor="top",
                len=0.28,
                thickness=14,
            ),
            name="SGF",
        ),
        row=1,
        col=2,
    )

    fig.add_trace(
        go.Heatmap(
            z=lgf_grid,
            colorscale="Blues",
            showscale=True,
            colorbar=dict(
                title=dict(text="LGF Level", side="top"),
                orientation="h",
                x=0.855,
                xanchor="center",
                y=-0.22,
                yanchor="top",
                len=0.28,
                thickness=14,
            ),
            name="LGF",
        ),
        row=1,
        col=3,
    )

    cell_data = np.asarray(cell_grid, dtype=np.float64)
    if show_compass and orientation_grid is not None:
        orient = np.asarray(orientation_grid, dtype=np.float64)
        if orient.ndim == 3 and orient.shape[:2] == cell_data.shape and orient.shape[2] >= 2:
            dy = orient[:, :, 0]
            dx = orient[:, :, 1]
            mask = (cell_data > 0) & ((dy != 0.0) | (dx != 0.0))
            if np.any(mask):
                ys, xs = np.nonzero(mask)
                symbols: list[str] = []
                labels: list[str] = []
                for y_idx, x_idx in zip(ys, xs, strict=False):
                    vy = float(dy[y_idx, x_idx])
                    vx = float(dx[y_idx, x_idx])
                    if vy < 0.0:
                        symbols.append("triangle-down")
                        labels.append(f"({int(y_idx)}, {int(x_idx)}): North (dy=-1, dx=0)")
                    elif vy > 0.0:
                        symbols.append("triangle-up")
                        labels.append(f"({int(y_idx)}, {int(x_idx)}): South (dy=+1, dx=0)")
                    elif vx > 0.0:
                        symbols.append("triangle-right")
                        labels.append(f"({int(y_idx)}, {int(x_idx)}): East (dy=0, dx=+1)")
                    else:
                        symbols.append("triangle-left")
                        labels.append(f"({int(y_idx)}, {int(x_idx)}): West (dy=0, dx=-1)")
                fig.add_trace(
                    go.Scatter(
                        x=xs,
                        y=ys,
                        mode="markers",
                        marker=dict(
                            symbol=symbols,
                            size=9,
                            color="#111111",
                            line=dict(width=1, color="#FFFFFF"),
                        ),
                        hovertext=labels,
                        hoverinfo="text",
                        name="Polarization Compass",
                    ),
                    row=1,
                    col=1,
                )

    if show_lgf_gradient:
        grad_y, grad_x = compute_lgf_gradient(lgf_grid)
        mag = np.hypot(grad_y, grad_x)
        max_mag = float(np.max(mag)) if mag.size > 0 else 0.0
        if max_mag > 1e-9:
            n_rows, n_cols = grad_y.shape
            stride = max(1, min(n_rows, n_cols) // 15)
            line_xs: list[float | None] = []
            line_ys: list[float | None] = []
            scale = 0.85 * stride / max_mag
            for y_idx in range(0, n_rows, stride):
                for x_idx in range(0, n_cols, stride):
                    if mag[y_idx, x_idx] <= 1e-9:
                        continue
                    vy = float(grad_y[y_idx, x_idx]) * scale
                    vx = float(grad_x[y_idx, x_idx]) * scale
                    line_xs.extend([float(x_idx), float(x_idx) + vx, None])
                    line_ys.extend([float(y_idx), float(y_idx) + vy, None])
            if line_xs:
                fig.add_trace(
                    go.Scatter(
                        x=line_xs,
                        y=line_ys,
                        mode="lines",
                        line=dict(color="#E69F00", width=1.8),
                        hoverinfo="skip",
                        name="LGF Gradient",
                    ),
                    row=1,
                    col=3,
                )

    title = (
        f"Gene Regulatory Network Simulation — Step {step}"
        if step is not None
        else "Gene Regulatory Network Simulation"
    )
    fig.update_layout(
        title=dict(text=title, y=0.97),
        height=520,
        margin=dict(l=45, r=30, t=70, b=115),
        showlegend=False,
    )

    n_rows, n_cols = cell_data.shape
    for i in range(1, 4):
        anchor = "x" if i == 1 else f"x{i}"
        fig.update_xaxes(
            title_text="X Position",
            range=[-0.5, n_cols - 0.5],
            constrain="domain",
            showgrid=False,
            zeroline=False,
            row=1,
            col=i,
        )
        fig.update_yaxes(
            title_text="Y Position" if i == 1 else None,
            range=[-0.5, n_rows - 0.5],
            scaleanchor=anchor,
            scaleratio=1,
            constrain="domain",
            showgrid=False,
            zeroline=False,
            row=1,
            col=i,
        )

    return fig


def create_telemetry_plot(telemetry: list[dict[str, float | int]]) -> go.Figure:
    """Create a 2-panel Plotly time-series chart of cell state counts and chemical levels."""
    steps = [entry["step"] for entry in telemetry]
    colors = get_cell_state_colors("colorblind_safe")

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Cell State Dynamics", "Chemical Signaling (SGF & LGF)"),
        horizontal_spacing=0.10,
    )

    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["living_cells"] for entry in telemetry],
            mode="lines",
            name="Total Living",
            line=dict(color="#333333", width=2.5),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["quiet_cells"] for entry in telemetry],
            mode="lines",
            name="Quiet",
            line=dict(color=colors[1], width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["moving_cells"] for entry in telemetry],
            mode="lines",
            name="Moving",
            line=dict(color=colors[2], width=2),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["divided_cells"] for entry in telemetry],
            mode="lines",
            name="Divided",
            line=dict(color=colors[3], width=2),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["sgf_mean"] for entry in telemetry],
            mode="lines",
            name="SGF Mean",
            line=dict(color="#D55E00", width=2),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["sgf_max"] for entry in telemetry],
            mode="lines",
            name="SGF Max",
            line=dict(color="#D55E00", width=1.5, dash="dash"),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["lgf_mean"] for entry in telemetry],
            mode="lines",
            name="LGF Mean",
            line=dict(color="#0072B2", width=2),
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=[entry["lgf_max"] for entry in telemetry],
            mode="lines",
            name="LGF Max",
            line=dict(color="#0072B2", width=1.5, dash="dash"),
        ),
        row=1,
        col=2,
    )

    fig.update_xaxes(title_text="Step", row=1, col=1)
    fig.update_yaxes(title_text="Cell Count", row=1, col=1)
    fig.update_xaxes(title_text="Step", row=1, col=2)
    fig.update_yaxes(title_text="Concentration", row=1, col=2)
    fig.update_layout(
        height=410,
        title=dict(text="Simulation Telemetry", y=0.96),
        margin=dict(l=55, r=30, t=75, b=85),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.24,
            yanchor="top",
        ),
    )
    return fig


def create_homeostasis_summary_plot(result: SimulationResult) -> go.Figure:
    """Create a 3-panel 1:1 square Plotly comparison of S_{T/2}, S_T, and structural delta."""
    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Midpoint Occupancy (S<sub>T/2</sub>)",
            "Final Occupancy (S<sub>T</sub>)",
            "Structural Delta (|S<sub>T/2</sub> − S<sub>T</sub>|)",
        ),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}, {"type": "heatmap"}]],
        horizontal_spacing=0.07,
    )

    binary_scale = build_discrete_plotly_colorscale(["#F8F9FA", "#0072B2"])
    delta_scale = build_discrete_plotly_colorscale(["#F8F9FA", "#D55E00"])

    fig.add_trace(
        go.Heatmap(
            z=result.halfway_structure,
            colorscale=binary_scale,
            zmin=-0.5,
            zmax=1.5,
            showscale=False,
            name="Midpoint",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Heatmap(
            z=result.final_structure,
            colorscale=binary_scale,
            zmin=-0.5,
            zmax=1.5,
            showscale=False,
            name="Final",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Heatmap(
            z=result.delta_matrix,
            colorscale=delta_scale,
            zmin=-0.5,
            zmax=1.5,
            showscale=False,
            name="Delta",
        ),
        row=1,
        col=3,
    )

    fig.update_layout(
        title=dict(
            text=f"Shape Homeostasis Comparison (Fitness F = {result.fitness:.4f})",
            y=0.96,
        ),
        height=400,
        margin=dict(l=45, r=30, t=70, b=50),
        showlegend=False,
    )

    n_rows, n_cols = np.asarray(result.halfway_structure).shape
    for i in range(1, 4):
        anchor = "x" if i == 1 else f"x{i}"
        fig.update_xaxes(
            title_text="X Position",
            range=[-0.5, n_cols - 0.5],
            constrain="domain",
            showgrid=False,
            zeroline=False,
            row=1,
            col=i,
        )
        fig.update_yaxes(
            title_text="Y Position" if i == 1 else None,
            range=[-0.5, n_rows - 0.5],
            scaleanchor=anchor,
            scaleratio=1,
            constrain="domain",
            showgrid=False,
            zeroline=False,
            row=1,
            col=i,
        )

    return fig


_STATE_TO_CODE: dict[str, float] = {
    "Die": 0.0,
    "Quiet": 1.0,
    "Move": 2.0,
    "Split": 3.0,
}

_FUNCTIONAL_NODE_LABELS: dict[int, str] = {
    0: "0: SGF_in",
    1: "1: LGF_in",
    2: "2: Split",
    3: "3: Move",
    4: "4: Die",
    5: "5: SGF_out",
    6: "6: LGF_out",
    7: "7: Compass",
}


def compute_phase_space_map(
    w_matrix: np.ndarray,
    *,
    resolution: int = 25,
    sgf_max: float = 1.0,
    lgf_max: float = 3.0,
    settle_steps: int = 10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Probe an RNN GRN across a 2D (SGF, LGF) grid and return decision codes 0..3."""
    weights = np.asarray(w_matrix, dtype=np.float64)
    if weights.ndim != 2 or weights.shape[0] != weights.shape[1] or weights.shape[0] < 8:
        raise ValueError("w_matrix must be a square 2D array with at least 8 nodes.")
    if resolution < 2:
        raise ValueError("resolution must be >= 2.")
    if sgf_max <= 0.0 or lgf_max <= 0.0:
        raise ValueError("sgf_max and lgf_max must be > 0.")
    if settle_steps < 1:
        raise ValueError("settle_steps must be >= 1.")

    n_nodes = weights.shape[0]
    sgf_vals = np.linspace(0.0, sgf_max, resolution)
    lgf_vals = np.linspace(0.0, lgf_max, resolution)
    decision_map = np.zeros((resolution, resolution), dtype=np.float64)

    for row_idx, lgf_val in enumerate(lgf_vals):
        for col_idx, sgf_val in enumerate(sgf_vals):
            probe_cell = cell(0, 0, weights, n_nodes)
            for _ in range(settle_steps):
                probe_cell.GenerateStatus(float(sgf_val), float(lgf_val))
            decision_map[row_idx, col_idx] = _STATE_TO_CODE.get(probe_cell.state, 0.0)

    return decision_map, sgf_vals, lgf_vals


def create_phase_space_plot(
    w_matrix: np.ndarray,
    *,
    resolution: int = 25,
    sgf_max: float = 1.0,
    lgf_max: float = 3.0,
    settle_steps: int = 10,
    palette: str = DEFAULT_PALETTE,
) -> go.Figure:
    """Create an interactive Plotly heatmap of steady-state GRN decisions over (SGF, LGF)."""
    decision_map, sgf_vals, lgf_vals = compute_phase_space_map(
        w_matrix,
        resolution=resolution,
        sgf_max=sgf_max,
        lgf_max=lgf_max,
        settle_steps=settle_steps,
    )
    colorscale = build_discrete_plotly_colorscale(get_cell_state_colors(palette))

    fig = go.Figure(
        data=go.Heatmap(
            x=sgf_vals,
            y=lgf_vals,
            z=decision_map,
            colorscale=colorscale,
            zmin=-0.5,
            zmax=3.5,
            colorbar=dict(
                title="Decision",
                tickvals=[0, 1, 2, 3],
                ticktext=["Die (0)", "Quiet (1)", "Move (2)", "Split (3)"],
            ),
            name="PhaseSpace",
        )
    )
    fig.update_layout(
        title=dict(text="Intracellular GRN (SGF, LGF) Phase-Space Decision Map", y=0.96),
        xaxis_title="SGF Concentration",
        yaxis_title="LGF Concentration",
        height=480,
        margin=dict(l=55, r=40, t=65, b=65),
    )
    return fig


def create_grn_network_plot(
    w_matrix: np.ndarray,
    *,
    weight_threshold: float = 0.05,
) -> go.Figure:
    """Create an interactive directed Plotly graph of a GRN weight matrix."""
    weights = np.asarray(w_matrix, dtype=np.float64)
    if weights.ndim != 2 or weights.shape[0] != weights.shape[1] or weights.shape[0] < 8:
        raise ValueError("w_matrix must be a square 2D array with at least 8 nodes.")

    n_nodes = weights.shape[0]
    angles = (np.pi / 4.0) - np.linspace(0.0, 2.0 * np.pi, n_nodes, endpoint=False)
    xs = np.cos(angles)
    ys = np.sin(angles)

    exc_x: list[float | None] = []
    exc_y: list[float | None] = []
    inh_x: list[float | None] = []
    inh_y: list[float | None] = []

    for dst in range(n_nodes):
        for src in range(n_nodes):
            if src == dst:
                continue
            weight = float(weights[dst, src])
            if weight >= weight_threshold:
                exc_x.extend([float(xs[src]), float(xs[dst]), None])
                exc_y.extend([float(ys[src]), float(ys[dst]), None])
            elif weight <= -weight_threshold:
                inh_x.extend([float(xs[src]), float(xs[dst]), None])
                inh_y.extend([float(ys[src]), float(ys[dst]), None])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=exc_x,
            y=exc_y,
            mode="lines",
            line=dict(color="#0072B2", width=1.4),
            hoverinfo="skip",
            name="Excitatory (w > 0)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=inh_x,
            y=inh_y,
            mode="lines",
            line=dict(color="#D55E00", width=1.4, dash="dot"),
            hoverinfo="skip",
            name="Inhibitory (w < 0)",
        )
    )

    node_labels = [
        _FUNCTIONAL_NODE_LABELS.get(idx, f"{idx}: G{idx}") for idx in range(n_nodes)
    ]
    display_labels = [
        node_labels[idx] if (n_nodes <= 12 or idx < 8) else str(idx)
        for idx in range(n_nodes)
    ]
    text_positions = []
    for idx in range(n_nodes):
        x_val = float(xs[idx])
        y_val = float(ys[idx])
        if abs(x_val) < 0.22 and y_val >= 0.0:
            text_positions.append("top center")
        elif abs(x_val) < 0.22 and y_val < 0.0:
            text_positions.append("bottom center")
        elif x_val >= 0.0:
            text_positions.append("middle right")
        else:
            text_positions.append("middle left")

    node_colors = [
        "#009E73"
        if idx in (0, 1)
        else "#E69F00"
        if idx in (2, 3, 4)
        else "#56B4E9"
        if idx in (5, 6)
        else "#CC79A7"
        if idx == 7
        else "#0072B2"
        for idx in range(n_nodes)
    ]
    hover_texts = [
        f"{node_labels[idx]} | self-weight={weights[idx, idx]:.2f}"
        for idx in range(n_nodes)
    ]

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            text=display_labels,
            textposition=text_positions,
            textfont=dict(size=11),
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(size=14, color=node_colors, line=dict(width=1.5, color="#222222")),
            name="GRN Nodes",
        )
    )

    fig.update_layout(
        title=dict(text="Directed Gene Regulatory Network Topology", y=0.96),
        height=480,
        margin=dict(l=30, r=30, t=65, b=80),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
        ),
        xaxis=dict(visible=False, range=[-1.75, 1.75]),
        yaxis=dict(visible=False, range=[-1.75, 1.75], scaleanchor="x", scaleratio=1),
    )
    return fig


def run_evolution_pass(
    n_nodes: int,
    *,
    pop_size: int = 6,
    n_generations: int = 8,
    time_steps: int = 20,
    n_lattice: int = 15,
    elite_num: int = 2,
    tournament_size: int = 3,
    crossover_prob: float = 0.8,
    mutation_prob: float = 0.9,
    gene_mutation_rate: float = 0.1,
    seed: int | None = 42,
    on_generation=None,
) -> tuple[np.ndarray, float, list[float], list[float]]:
    """Run an in-process GA optimization pass using tools_ga operators."""
    rng = np.random.default_rng(seed)
    n_genes = n_nodes**2
    population = tools_ga.initialize_population(pop_size, n_genes, rng=rng)

    best_history: list[float] = []
    avg_history: list[float] = []
    best_score = -1.0
    best_matrix = population[0].reshape(n_nodes, n_nodes).copy()

    for gen_idx in range(n_generations):
        scores = np.zeros(pop_size, dtype=np.float64)
        for ind_idx in range(pop_size):
            w_mat = population[ind_idx].reshape(n_nodes, n_nodes)
            eval_seed = (
                (seed + gen_idx * pop_size + ind_idx) if seed is not None else None
            )
            result = run_simulation(
                w_mat,
                time_steps=time_steps,
                n_nodes=n_nodes,
                n_lattice=n_lattice,
                early_stop=True,
                seed=eval_seed,
            )
            scores[ind_idx] = result.fitness

        gen_best_idx = int(np.argmax(scores))
        gen_best = float(scores[gen_best_idx])
        best_history.append(gen_best)
        avg_history.append(float(np.mean(scores)))

        if gen_best > best_score:
            best_score = gen_best
            best_matrix = population[gen_best_idx].reshape(n_nodes, n_nodes).copy()

        if on_generation is not None:
            on_generation(gen_idx + 1, n_generations)

        if gen_idx < n_generations - 1:
            population = tools_ga.create_next_generation(
                population,
                scores,
                elite_num=min(elite_num, pop_size),
                tournament_size=min(tournament_size, pop_size),
                crossover_prob=crossover_prob,
                mutation_prob=mutation_prob,
                gene_mutation_rate=gene_mutation_rate,
                rng=rng,
            )

    return best_matrix, best_score, best_history, avg_history


def main() -> None:
    """Main Streamlit application."""
    st.title("Gene Regulatory Network Simulation")
    st.markdown("Interactive simulation of cellular automata with gene regulatory networks")

    st.sidebar.header("Simulation Parameters")

    n_nodes = st.sidebar.slider("Number of Nodes", 8, 50, 25, help="Size of the neural network")
    n_lattice = st.sidebar.slider("Lattice Size", 10, 100, 50, help="Size of the simulation grid")
    time_steps = st.sidebar.slider("Time Steps", 10, 500, 100, help="Number of simulation steps")

    network_type = st.sidebar.selectbox(
        "Network Type",
        ["Random", "Erdős-Rényi", "Watts-Strogatz", "Barabási-Albert"],
        help="Type of network architecture",
    )

    use_seed = st.sidebar.checkbox(
        "Use Deterministic Seed",
        value=True,
        help="Reproduce identical initial GRN topology and simulation trajectories",
    )
    seed_input = st.sidebar.number_input(
        "PRNG Seed",
        min_value=0,
        max_value=2**31 - 1,
        value=42,
        step=1,
        disabled=not use_seed,
        help="Explicit seed passed to topology generation and SimulationEngine",
    )
    active_seed = int(seed_input) if use_seed else None

    palette_options = {
        "Colorblind-Safe (Okabe-Ito)": "colorblind_safe",
        "Legacy (RGB)": "legacy",
    }
    palette_label = st.sidebar.selectbox(
        "Color Palette",
        list(palette_options.keys()),
        help="Color palette used for cellular state heatmaps and snapshots",
    )
    palette_key = palette_options[palette_label]

    show_compass = st.sidebar.checkbox(
        "Show Cell Polarization Arrows",
        value=False,
        help="Overlay GRN Node 7 compass polarization arrows on living cells",
    )
    show_lgf_gradient = st.sidebar.checkbox(
        "Show LGF Gradient Vectors",
        value=False,
        help="Overlay chemical gradient vectors on the LGF concentration panel",
    )

    record_timelapse = st.sidebar.checkbox(
        "Record Timelapse",
        value=False,
        help="Capture periodic snapshots during the run for GIF export",
    )
    snapshot_interval = st.sidebar.slider(
        "Snapshot Interval (steps)",
        1,
        25,
        5,
        disabled=not record_timelapse,
        help="Capture one timelapse frame every N simulation steps",
    )

    if "running" not in st.session_state:
        st.session_state.running = False
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "timelapse_frames" not in st.session_state:
        st.session_state.timelapse_frames = []
    if "snapshots" not in st.session_state:
        st.session_state.snapshots = []
    if "telemetry" not in st.session_state:
        st.session_state.telemetry = []
    if "sim_result" not in st.session_state:
        st.session_state.sim_result = None

    desired_config = (n_nodes, n_lattice, network_type, time_steps, active_seed)
    if "sim_config" not in st.session_state or st.session_state.sim_config != desired_config:
        init_simulation_state(
            n_nodes,
            n_lattice,
            network_type,
            seed=active_seed,
            time_steps=time_steps,
        )
        st.session_state.current_step = 0
        st.session_state.running = False
        st.session_state.timelapse_frames = []

    tab1, tab2, tab3 = st.tabs(["Simulation", "Analysis", "About"])

    with tab1:
        st.header("Live Simulation & Timeline Scrubber")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("Start Live", type="primary"):
                at_end = st.session_state.current_step >= time_steps
                if st.session_state.current_step == 0 or at_end:
                    init_simulation_state(
                        n_nodes,
                        n_lattice,
                        network_type,
                        seed=active_seed,
                        time_steps=time_steps,
                    )
                    st.session_state.current_step = 0
                    st.session_state.timelapse_frames = []
                st.session_state.running = True

        with col2:
            if st.button("Run Full Horizon"):
                init_simulation_state(
                    n_nodes,
                    n_lattice,
                    network_type,
                    seed=active_seed,
                    time_steps=time_steps,
                )
                result, snapshots, telemetry = run_batch_simulation(
                    st.session_state.w_matrix,
                    time_steps=time_steps,
                    n_nodes=n_nodes,
                    n_lattice=n_lattice,
                    seed=active_seed,
                    early_stop=False,
                )
                st.session_state.running = False
                st.session_state.snapshots = snapshots
                st.session_state.telemetry = telemetry
                st.session_state.sim_result = result
                st.session_state.current_step = result.steps_executed
                st.session_state.timelapse_frames = []
                if record_timelapse:
                    for snap in snapshots:
                        if (snap.step + 1) % snapshot_interval == 0:
                            st.session_state.timelapse_frames.append(
                                render_snapshot_png_bytes(
                                    snap.cell_grid,
                                    snap.sgf_grid,
                                    snap.lgf_grid,
                                    step=snap.step + 1,
                                    palette=palette_key,
                                    dpi=100,
                                    orientation_grid=snap.orientation_grid,
                                    show_compass=show_compass,
                                )
                            )

        with col3:
            if st.button("Pause"):
                st.session_state.running = False

        with col4:
            if st.button("Reset"):
                st.session_state.running = False
                st.session_state.current_step = 0
                st.session_state.timelapse_frames = []
                init_simulation_state(
                    n_nodes,
                    n_lattice,
                    network_type,
                    seed=active_seed,
                    time_steps=time_steps,
                )

        plot_placeholder = st.empty()

        if st.session_state.running and st.session_state.current_step < time_steps:
            cell_grid, sgf_grid, lgf_grid = run_simulation_step(n_lattice)
            st.session_state.current_step += 1
            latest_orient = (
                st.session_state.snapshots[-1].orientation_grid
                if st.session_state.snapshots
                else extract_orientation_grid(st.session_state.cell_list, n_lattice)
            )
            fig = create_cell_grid_plot(
                cell_grid,
                sgf_grid,
                lgf_grid,
                palette=palette_key,
                step=st.session_state.current_step,
                orientation_grid=latest_orient,
                show_compass=show_compass,
                show_lgf_gradient=show_lgf_gradient,
            )
            plot_placeholder.plotly_chart(fig, width="stretch")

            if record_timelapse and st.session_state.current_step % snapshot_interval == 0:
                frame_bytes = render_snapshot_png_bytes(
                    cell_grid,
                    sgf_grid,
                    lgf_grid,
                    step=st.session_state.current_step,
                    palette=palette_key,
                    dpi=100,
                    orientation_grid=latest_orient,
                    show_compass=show_compass,
                )
                st.session_state.timelapse_frames.append(frame_bytes)

            if st.session_state.current_step >= time_steps:
                st.session_state.sim_result = st.session_state.engine.run()
                st.session_state.running = False

            st.progress(st.session_state.current_step / time_steps)
            st.write(
                f"Step {st.session_state.current_step} of {time_steps} "
                f"(Living cells: {len(st.session_state.cell_list)})"
            )

            time.sleep(0.05)
            st.rerun()
        else:
            snapshots: list[StepSnapshot] = st.session_state.snapshots
            if snapshots:
                if len(snapshots) > 1:
                    scrub_idx = st.slider(
                        "Timeline Scrubber (Step)",
                        min_value=1,
                        max_value=len(snapshots),
                        value=len(snapshots),
                        help="Scrub across any recorded simulation step",
                    ) - 1
                else:
                    scrub_idx = 0
                active_snap = snapshots[scrub_idx]
                fig = create_cell_grid_plot(
                    active_snap.cell_grid,
                    active_snap.sgf_grid,
                    active_snap.lgf_grid,
                    palette=palette_key,
                    step=active_snap.step + 1,
                    orientation_grid=active_snap.orientation_grid,
                    show_compass=show_compass,
                    show_lgf_gradient=show_lgf_gradient,
                )
            else:
                cell_grid = np.asarray(st.session_state.cell_grid, dtype=np.float64)
                sgf_grid = st.session_state.chem_grid[:, :, 0]
                lgf_grid = st.session_state.chem_grid[:, :, 1]
                init_orient = extract_orientation_grid(st.session_state.cell_list, n_lattice)
                fig = create_cell_grid_plot(
                    cell_grid,
                    sgf_grid,
                    lgf_grid,
                    palette=palette_key,
                    orientation_grid=init_orient,
                    show_compass=show_compass,
                    show_lgf_gradient=show_lgf_gradient,
                )

            plot_placeholder.plotly_chart(fig, width="stretch")

            if st.session_state.current_step >= time_steps:
                st.success("Simulation completed!")
                st.session_state.running = False

            if st.session_state.timelapse_frames:
                st.caption(
                    f"Recorded {len(st.session_state.timelapse_frames)} timelapse frame(s)."
                )
                st.download_button(
                    "Download Timelapse GIF",
                    data=build_gif_bytes(st.session_state.timelapse_frames),
                    file_name="grn_timelapse.gif",
                    mime="image/gif",
                )

            if st.session_state.telemetry:
                st.plotly_chart(
                    create_telemetry_plot(st.session_state.telemetry),
                    width="stretch",
                )

            if st.session_state.sim_result is not None:
                res: SimulationResult = st.session_state.sim_result
                st.subheader("Shape Homeostasis Summary")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Homeostasis Fitness (F)", f"{res.fitness:.4f}")
                m2.metric("Steps Executed", f"{res.steps_executed}")
                m3.metric("Final Living Cells", f"{res.final_cell_count}")
                m4.metric("Early Termination", "Yes" if res.terminated_early else "No")
                if res.terminated_early:
                    st.warning(
                        "Colony below 1% lattice occupancy at midpoint (T/2): "
                        "the homeostasis fitness evaluator assigns S(T/2) = 0 and S(T) = 1 "
                        "(penalty F = 0.0000)."
                    )
                st.plotly_chart(
                    create_homeostasis_summary_plot(res),
                    width="stretch",
                )

    with tab2:
        st.header("Evolutionary Optimization & GRN Inspector")
        st.subheader("1. Genetic Algorithm Evolution")

        ga_c1, ga_c2, ga_c3, ga_c4 = st.columns(4)
        with ga_c1:
            ga_pop_size = st.number_input("Population Size", min_value=4, max_value=20, value=6)
        with ga_c2:
            ga_generations = st.number_input("Generations", min_value=2, max_value=25, value=8)
        with ga_c3:
            ga_elite = st.number_input("Elite Count", min_value=1, max_value=4, value=2)
        with ga_c4:
            ga_mut_rate = st.slider("Gene Mutation Rate", 0.01, 0.50, 0.10, step=0.01)

        if "evolved_w_matrix" not in st.session_state:
            st.session_state.evolved_w_matrix = None
        if "evolved_fitness" not in st.session_state:
            st.session_state.evolved_fitness = None
        if "evolved_history" not in st.session_state:
            st.session_state.evolved_history = None

        if st.button("Run Evolutionary Optimization", type="primary"):
            progress_bar = st.progress(0.0)
            best_mat, best_score, best_fitness, avg_fitness = run_evolution_pass(
                n_nodes,
                pop_size=int(ga_pop_size),
                n_generations=int(ga_generations),
                time_steps=20,
                n_lattice=min(n_lattice, 20),
                elite_num=min(int(ga_elite), int(ga_pop_size) - 1),
                tournament_size=min(3, int(ga_pop_size)),
                gene_mutation_rate=float(ga_mut_rate),
                seed=active_seed,
                on_generation=lambda done, total: progress_bar.progress(done / total),
            )
            st.session_state.evolved_w_matrix = best_mat
            st.session_state.evolved_fitness = best_score
            st.session_state.evolved_history = (best_fitness, avg_fitness)

        if st.session_state.evolved_history is not None:
            best_fitness, avg_fitness = st.session_state.evolved_history
            generations = list(range(1, len(best_fitness) + 1))
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=generations, y=best_fitness, mode="lines+markers", name="Best Fitness")
            )
            fig.add_trace(
                go.Scatter(
                    x=generations, y=avg_fitness, mode="lines+markers", name="Average Fitness"
                )
            )
            fig.update_layout(
                title="Fitness Evolution Over Generations",
                xaxis_title="Generation",
                yaxis_title="Fitness",
                height=380,
            )
            st.plotly_chart(fig, width="stretch")

        if (
            st.session_state.evolved_w_matrix is not None
            and st.session_state.evolved_w_matrix.shape == (n_nodes, n_nodes)
        ):
            st.info(f"Best Evolved Homeostasis Fitness: {st.session_state.evolved_fitness:.4f}")
            if st.button("Load Best Evolved GRN into Simulation"):
                engine = SimulationEngine.from_weight_matrix(
                    st.session_state.evolved_w_matrix,
                    n_nodes=n_nodes,
                    config=SimulationConfig(
                        n_lattice=n_lattice,
                        time_steps=time_steps,
                        early_stop=False,
                        seed=active_seed,
                    ),
                )
                st.session_state.engine = engine
                st.session_state.w_matrix = st.session_state.evolved_w_matrix.copy()
                st.session_state.cell_grid = engine.cell_grid
                st.session_state.chem_grid = engine.chem_grid
                st.session_state.cell_list = engine.cell_list
                st.session_state.snapshots = []
                st.session_state.telemetry = []
                st.session_state.sim_result = None
                st.session_state.current_step = 0
                st.session_state.running = False
                st.session_state.timelapse_frames = []
                st.success("Loaded best evolved GRN into the Simulation tab!")

        st.divider()
        st.subheader("2. Interactive (SGF, LGF) Phase-Space & Directed GRN Graph")

        ps_c1, ps_c2 = st.columns(2)
        with ps_c1:
            ps_resolution = st.slider(
                "Phase-Space Grid Resolution",
                10,
                40,
                20,
                help="Number of SGF and LGF sample points along each axis",
            )
        with ps_c2:
            weight_thresh = st.slider(
                "GRN Edge Weight Threshold (|w|)",
                0.01,
                0.75,
                0.15,
                step=0.01,
                help="Filter weak regulatory edges to keep the directed GRN topology clear",
            )
        insp_col1, insp_col2 = st.columns(2)
        with insp_col1:
            st.plotly_chart(
                create_phase_space_plot(
                    st.session_state.w_matrix,
                    resolution=ps_resolution,
                    palette=palette_key,
                ),
                width="stretch",
            )
        with insp_col2:
            st.plotly_chart(
                create_grn_network_plot(
                    st.session_state.w_matrix,
                    weight_threshold=float(weight_thresh),
                ),
                width="stretch",
            )

    with tab3:
        st.header("About This Simulation")

        st.markdown(
            """
        ### Gene Regulatory Networks Driving Shape Homeostasis

        This simulation explores how gene regulatory networks (GRNs) drive shape homeostasis
        in multicellular systems. The model combines:

        - **Cellular Automata**: Spatial modeling of cell dynamics
        - **Neural Networks**: Gene regulatory networks within each cell
        - **Evolutionary Algorithms**: Optimization of network parameters

        ### Key Components

        1. **Cell States**: Empty, Quiet, Moving, Divided
        2. **Chemical Signaling**: SGF (Short-range) and LGF (Long-range) Growth Factors
        3. **Neural Networks**: Control cell behavior based on local conditions

        ### Research Applications

        - Developmental biology
        - Artificial life
        - Emergent behavior studies
        - Homeostasis mechanisms

        ### Technical Details

        - **Language**: Python 3.11+
        - **Package Manager**: uv
        - **Dependencies**: NumPy, SciPy, Matplotlib, NetworkX, Numba, NEAT-Python
        - **Web Interface**: Streamlit + Plotly
        - **Containerization**: Docker for reproducible environments
        """
        )

        st.info(
            """
        **Interactive Web Interface**: This web application provides real-time browser-based
        simulation controls and visualization for the cellular automata and GRN model.
        """
        )

        baseline_url = (
            "https://github.com/j0sees/"
            "Simulation-of-Gene-Regulatory-Networks-Driving-Shape-Homeostasis/"
            "tree/6c3fae7834a2ca502b1a439d7535c4adab1673f3"
        )
        esteban_url = "https://orion.tec.ac.cr/en/persons/jos%C3%A9-esteban-p%C3%A9rez-hidalgo/"
        gerlee_url = "https://research.chalmers.se/en/person/gerlee"
        reymer_orcid = "https://orcid.org/0009-0002-9091-8431"
        st.markdown(
            f"""
        ### Research Project Information

        This software is based on the master's thesis
        *"Classification of Gene Regulatory Networks Driving Shape Homeostasis"*.

        - **Original Research & Model (`v0.1.0`)**:
          [M.Sc. José Esteban Pérez-Hidalgo]({esteban_url})
          ([@j0sees](https://github.com/j0sees),
          School of Physics, Costa Rica Institute of Technology),
          supervised by [Ph.D. Philip Gerlee]({gerlee_url})
          (University of Gothenburg & Chalmers University of Technology)
          — [Baseline (`6c3fae7`)]({baseline_url})
        - **Software Architecture, Core Engine & Lead Maintainer (`v0.2.0`–`v0.3.0`)**:
          Reymer Vargas ([@userravs](https://github.com/userravs),
          [ORCID `0009-0002-9091-8431`]({reymer_orcid}),
          Independent Research Software Engineer) — Unified headless engine,
          $O(N^2)$ Thomas ADI solver, evolutionary diversity & NEAT upgrades,
          interactive phase-space/GRN inspector & vector overlays, accessible
          visualization & timelapse export, containerization, and CI/test suite
        """
        )


if __name__ == "__main__":
    main()
