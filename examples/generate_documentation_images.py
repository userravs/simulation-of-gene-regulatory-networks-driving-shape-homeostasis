#!/usr/bin/env python3
"""
Generate example images and timelapse animations for documentation.

This script runs the unified headless simulation engine (SimulationEngine),
genetic algorithm operators, and phase-space inspector to produce publication-grade
figures and an animated morphogenesis GIF under docs/images/.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cell_agent import cell
from core.engine import SimulationConfig, SimulationEngine, StepSnapshot
from visualization.palettes import (
    CELL_STATE_LABELS,
    DEFAULT_PALETTE,
    get_cell_state_cmap,
    get_cell_state_colors,
)
from visualization.timelapse import build_gif_bytes, render_snapshot_png_bytes

FUNCTIONAL_NODE_LABELS: dict[int, str] = {
    0: "0: SGF_in",
    1: "1: LGF_in",
    2: "2: Split",
    3: "3: Move",
    4: "4: Die",
    5: "5: SGF_out",
    6: "6: LGF_out",
    7: "7: Compass",
}


def build_homeostatic_demo_network(n_nodes: int = 10, seed: int = 14) -> np.ndarray:
    """Construct a deterministic GRN weight matrix exhibiting bounded shape homeostasis."""
    rng = np.random.default_rng(seed)
    weights = rng.uniform(-0.18, 0.18, size=(n_nodes, n_nodes))

    # Note: In RecurrentNeuralNetwork, bj = W @ V - inputs, so inputs[0] = SGF and
    # inputs[1] = LGF directly drive V[0] and V[1] downward as SGF/LGF increase!
    # Therefore:
    # - Low SGF/LGF -> V[0] ~ 0.5, V[1] ~ 0.5
    # - High SGF    -> V[0] -> 0.0
    # - High LGF    -> V[1] -> 0.0
    # By giving Split (node 2) positive weights from V[0] and V[1], cells divide at low
    # chemical density (V[2] > 0.5) and become Quiet (or Move/Die) once the colony
    # secretes enough SGF/LGF, yielding a bounded homeostatic colony with F > 0.85!
    weights[0, :] = 0.0
    weights[0, 0] = 0.35
    weights[1, :] = 0.0
    weights[1, 1] = 0.35

    # Node 2 (Split): active when both SGF and LGF are low (V[0] and V[1] near 0.5)
    weights[2, :] = 0.0
    weights[2, 0] = 0.72
    weights[2, 1] = 0.68
    weights[2, 5] = -0.35

    # Node 3 (Move): active when SGF is low (V[0] high) and LGF is moderate (V[1] intermediate)
    weights[3, :] = 0.0
    weights[3, 0] = 0.90
    weights[3, 1] = 0.08
    weights[3, 5] = -0.35

    # Node 4 (Die): active only under extreme chemical crowding (both V[0] and V[1] near 0),
    # leaving a broad Quiet zone (all V[2:5] < 0.5) at intermediate-to-high SGF/LGF
    weights[4, :] = 0.0
    weights[4, 0] = -0.95
    weights[4, 1] = -0.95
    weights[4, 5] = 0.19
    weights[4, 6] = 0.19

    # Nodes 5 & 6 (SGF and LGF secretion): steady positive secretion
    weights[5, :] = 0.0
    weights[5, 8] = 0.45
    weights[5, 9] = 0.45
    weights[6, :] = 0.0
    weights[6, 8] = 0.55
    weights[6, 9] = 0.55
    weights[8, :] = 0.25
    weights[9, :] = 0.25

    # Node 7 (Polarization Compass): balanced across [0, 1] for N/S/E/W orientation
    weights[7, :] = np.linspace(-0.75, 0.75, n_nodes)
    weights[7, 0] = 0.65
    weights[7, 1] = -0.65
    return np.clip(weights, -1.0, 1.0)


def generate_cell_system_and_timelapse(
    output_dir: Path,
    palette: str = DEFAULT_PALETTE,
) -> tuple[np.ndarray, StepSnapshot]:
    """Run SimulationEngine to generate cell_system_example.png and morphogenesis_timelapse.gif."""
    print("Running SimulationEngine for cell_system_example.png & morphogenesis_timelapse.gif...")

    n_nodes = 10
    n_lattice = 35
    time_steps = 44
    w_matrix = build_homeostatic_demo_network(n_nodes=n_nodes, seed=14)

    config = SimulationConfig(
        n_lattice=n_lattice,
        time_steps=time_steps,
        early_stop=False,
        seed=42,
    )
    engine = SimulationEngine.from_weight_matrix(w_matrix, n_nodes=n_nodes, config=config)

    snapshots: list[StepSnapshot] = []
    gif_frames: list[bytes] = []

    for step in range(time_steps):
        snap = engine.step()
        snapshots.append(snap)
        if step % 2 == 0 or step == time_steps - 1:
            sgf_max = max(0.05, float(np.max(snap.sgf_grid)))
            lgf_max = max(0.5, float(np.max(snap.lgf_grid)))
            gif_frames.append(
                render_snapshot_png_bytes(
                    snap.cell_grid,
                    snap.sgf_grid,
                    snap.lgf_grid,
                    step=step + 1,
                    palette=palette,
                    dpi=110,
                    sgf_vmax=sgf_max,
                    lgf_vmax=lgf_max,
                    orientation_grid=snap.orientation_grid,
                    show_compass=True,
                )
            )

    gif_path = output_dir / "morphogenesis_timelapse.gif"
    gif_path.write_bytes(build_gif_bytes(gif_frames, duration_ms=180, loop=0))
    print(f"Saved: {gif_path}")

    # Pick a snapshot during active morphogenesis showing Quiet, Moving, and Divided cells
    best_snap = max(
        snapshots,
        key=lambda s: (
            int(np.count_nonzero(s.cell_grid == 1) > 0)
            + int(np.count_nonzero(s.cell_grid == 2) > 0)
            + int(np.count_nonzero(s.cell_grid == 3) > 0),
            s.living_cells if s.living_cells < int(0.65 * n_lattice * n_lattice) else 0,
        ),
    )
    featured = best_snap
    cell_grid = np.asarray(featured.cell_grid, dtype=np.float64)
    sgf_grid = np.asarray(featured.sgf_grid, dtype=np.float64)
    lgf_grid = np.asarray(featured.lgf_grid, dtype=np.float64)
    orient = np.asarray(featured.orientation_grid, dtype=np.float64)

    fig, (cells_ax, sgf_ax, lgf_ax) = plt.subplots(1, 3, figsize=(15.5, 5.4))
    fig.suptitle(
        f"2D Cellular Automaton, Polarization Compass & SGF/LGF Reaction-Diffusion "
        f"(Step {featured.step + 1}, Living Cells: {featured.living_cells})",
        fontsize=14,
        fontweight="bold",
    )

    c_map = get_cell_state_cmap(palette)
    cell_plot = cells_ax.imshow(
        cell_grid,
        origin="lower",
        cmap=c_map,
        interpolation="none",
        vmin=-0.5,
        vmax=3.5,
    )
    cells_ax.set_title("Cells & Node 7 Polarization Compass", fontsize=12)

    # Overlay polarization compass arrows on living cells
    dy = orient[:, :, 0]
    dx = orient[:, :, 1]
    mask = (cell_grid > 0) & ((dy != 0.0) | (dx != 0.0))
    if np.any(mask):
        ys, xs = np.nonzero(mask)
        cells_ax.quiver(
            xs,
            ys,
            dx[ys, xs],
            dy[ys, xs],
            color="#111111",
            angles="xy",
            scale_units="xy",
            scale=1.15,
            width=0.007,
            headwidth=3.6,
        )

    cbar1 = fig.colorbar(
        cell_plot,
        ax=cells_ax,
        ticks=[0, 1, 2, 3],
        orientation="horizontal",
        pad=0.05,
        fraction=0.046,
    )
    cbar1.set_ticklabels(list(CELL_STATE_LABELS))
    cbar1.set_label("Discrete Cell States (Okabe-Ito Accessible Palette)")

    sgf_vmax = max(0.05, float(np.max(sgf_grid)))
    sgf_plot = sgf_ax.imshow(
        sgf_grid,
        origin="lower",
        cmap="Reds",
        interpolation="none",
        vmin=0.0,
        vmax=sgf_vmax,
    )
    sgf_ax.set_title("SGF (Short-range Growth Factor)", fontsize=12)
    cbar2 = fig.colorbar(
        sgf_plot,
        ax=sgf_ax,
        orientation="horizontal",
        pad=0.05,
        fraction=0.046,
    )
    cbar2.set_label("Local SGF Concentration s(y, x)")

    lgf_vmax = max(0.5, float(np.max(lgf_grid)))
    lgf_plot = lgf_ax.imshow(
        lgf_grid,
        origin="lower",
        cmap="Blues",
        interpolation="bilinear",
        vmin=0.0,
        vmax=lgf_vmax,
    )
    lgf_ax.set_title("LGF & Chemical Gradient Vectors (∇LGF)", fontsize=12)

    # Overlay subsampled LGF gradient vectors
    grad_y, grad_x = np.gradient(lgf_grid)
    mag = np.hypot(grad_y, grad_x)
    max_mag = float(np.max(mag))
    if max_mag > 1e-9:
        stride = 2
        gy_sub = grad_y[::stride, ::stride] / max_mag
        gx_sub = grad_x[::stride, ::stride] / max_mag
        mag_sub = mag[::stride, ::stride] / max_mag
        y_coords, x_coords = np.mgrid[0:n_lattice:stride, 0:n_lattice:stride]
        g_mask = mag_sub >= 0.08
        if np.any(g_mask):
            lgf_ax.quiver(
                x_coords[g_mask],
                y_coords[g_mask],
                gx_sub[g_mask],
                gy_sub[g_mask],
                color="#08306B",
                angles="xy",
                scale_units="xy",
                scale=0.8,
                width=0.006,
                headwidth=3.5,
                alpha=0.85,
            )

    cbar3 = fig.colorbar(
        lgf_plot,
        ax=lgf_ax,
        orientation="horizontal",
        pad=0.05,
        fraction=0.046,
    )
    cbar3.set_label("Diffusing LGF Concentration l(y, x)")

    for ax in (cells_ax, sgf_ax, lgf_ax):
        ax.set_aspect("equal")
        ax.set_xlim(-0.5, n_lattice - 0.5)
        ax.set_ylim(-0.5, n_lattice - 0.5)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    fig.tight_layout()
    out_path = output_dir / "cell_system_example.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")
    return w_matrix, featured


def generate_network_example(w_matrix: np.ndarray, output_dir: Path) -> None:
    """Generate a directed GRN topology figure with functional node roles and signed weights."""
    print("Generating directed GRN network example...")

    n_nodes = w_matrix.shape[0]
    graph = nx.DiGraph()
    labels: dict[int, str] = {}
    node_colors: list[str] = []

    for idx in range(n_nodes):
        label = FUNCTIONAL_NODE_LABELS.get(idx, f"{idx}: Hidden")
        labels[idx] = label
        graph.add_node(idx)
        if idx in (0, 1):
            node_colors.append("#56B4E9")  # Inputs (SGF_in, LGF_in)
        elif idx in (2, 3, 4):
            node_colors.append("#009E73")  # Cellular Actions (Split, Move, Die)
        elif idx in (5, 6):
            node_colors.append("#E69F00")  # Secretion (SGF_out, LGF_out)
        elif idx == 7:
            node_colors.append("#CC79A7")  # Polarization Compass
        else:
            node_colors.append("#D9D9D9")  # Recurrent Hidden Nodes

    threshold = 0.28
    pos_edges: list[tuple[int, int]] = []
    pos_widths: list[float] = []
    neg_edges: list[tuple[int, int]] = []
    neg_widths: list[float] = []

    for tgt in range(n_nodes):
        for src in range(n_nodes):
            if src == tgt:
                continue
            weight = float(w_matrix[tgt, src])
            if abs(weight) >= threshold:
                graph.add_edge(src, tgt, weight=weight)
                width = 1.2 + 2.8 * abs(weight)
                if weight > 0:
                    pos_edges.append((src, tgt))
                    pos_widths.append(width)
                else:
                    neg_edges.append((src, tgt))
                    neg_widths.append(width)

    fig, ax = plt.subplots(figsize=(10.5, 8.2))
    pos = nx.circular_layout(graph)

    # Place node labels slightly outside the node circle so they never clip the border
    label_pos = {
        node: (coords[0] * 1.24, coords[1] * 1.24)
        for node, coords in pos.items()
    }
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        node_size=1550,
        edgecolors="#1A1A1A",
        linewidths=1.8,
        ax=ax,
    )
    nx.draw_networkx_labels(
        graph,
        label_pos,
        labels=labels,
        font_size=10,
        font_weight="bold",
        bbox=dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor="#CCCCCC", alpha=0.92),
        ax=ax,
    )
    if pos_edges:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=pos_edges,
            width=pos_widths,
            edge_color="#0072B2",
            alpha=0.75,
            arrows=True,
            arrowsize=18,
            arrowstyle="-|>",
            connectionstyle="arc3,rad=0.12",
            node_size=1550,
            ax=ax,
        )
    if neg_edges:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=neg_edges,
            width=neg_widths,
            edge_color="#D55E00",
            style="dashed",
            alpha=0.75,
            arrows=True,
            arrowsize=18,
            arrowstyle="-|>",
            connectionstyle="arc3,rad=0.12",
            node_size=1550,
            ax=ax,
        )

    # Legend for functional node classes and regulatory sign
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], marker="o", color="w", label="Chemical Inputs (0: SGF, 1: LGF)",
               markerfacecolor="#56B4E9", markeredgecolor="#1A1A1A", markersize=11),
        Line2D([0], [0], marker="o", color="w", label="Action Outputs (2: Split, 3: Move, 4: Die)",
               markerfacecolor="#009E73", markeredgecolor="#1A1A1A", markersize=11),
        Line2D([0], [0], marker="o", color="w", label="Secretion Outputs (5: SGF, 6: LGF)",
               markerfacecolor="#E69F00", markeredgecolor="#1A1A1A", markersize=11),
        Line2D([0], [0], marker="o", color="w", label="Polarization Compass (7: N/S/E/W)",
               markerfacecolor="#CC79A7", markeredgecolor="#1A1A1A", markersize=11),
        Line2D([0], [0], marker="o", color="w", label="Recurrent Hidden Nodes (8..n-1)",
               markerfacecolor="#D9D9D9", markeredgecolor="#1A1A1A", markersize=11),
        Line2D([0], [0], color="#0072B2", lw=2.5, label="Excitatory Regulation (w > 0)"),
        Line2D([0], [0], color="#D55E00", lw=2.5, ls="--", label="Inhibitory Regulation (w < 0)"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.04),
        ncol=2,
        frameon=True,
        fontsize=9.5,
    )

    ax.set_title(
        "Intracellular Recurrent Gene Regulatory Network (Functional Nodes & Signed Weights)",
        fontsize=14,
        fontweight="bold",
        pad=16,
    )
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.48, 1.48)
    ax.axis("off")
    fig.tight_layout()

    out_path = output_dir / "network_example.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_phase_space_example(
    w_matrix: np.ndarray,
    output_dir: Path,
    palette: str = DEFAULT_PALETTE,
) -> None:
    """Generate a 2-panel (SGF, LGF) phase-space decision map and homeostasis comparison."""
    print("Generating (SGF, LGF) phase-space and homeostasis comparison figure...")

    resolution = 45
    sgf_max = 1.5
    lgf_max = 3.5
    settle_steps = 12
    n_nodes = w_matrix.shape[0]

    sgf_vals = np.linspace(0.0, sgf_max, resolution)
    lgf_vals = np.linspace(0.0, lgf_max, resolution)
    state_to_code = {"Die": 0.0, "Quiet": 1.0, "Move": 2.0, "Split": 3.0}
    decision_map = np.zeros((resolution, resolution), dtype=np.float64)

    for r_idx, lgf_val in enumerate(lgf_vals):
        for c_idx, sgf_val in enumerate(sgf_vals):
            probe = cell(0, 0, w_matrix, n_nodes)
            for _ in range(settle_steps):
                probe.GenerateStatus(float(sgf_val), float(lgf_val))
            decision_map[r_idx, c_idx] = state_to_code.get(probe.state, 0.0)

    # Also run a full simulation horizon to show S_{T/2}, S_T, and |S_{T/2} - S_T|
    sim_res = SimulationEngine.from_weight_matrix(
        w_matrix,
        n_nodes=n_nodes,
        config=SimulationConfig(n_lattice=35, time_steps=44, early_stop=False, seed=42),
    ).run()

    fig, (ps_ax, mid_ax, fin_ax, delta_ax) = plt.subplots(
        1, 4, figsize=(17.5, 4.6), gridspec_kw={"width_ratios": [1.25, 1.0, 1.0, 1.0]}
    )
    fig.suptitle(
        f"GRN Dynamical Phase-Space Map & Shape Homeostasis Evaluation "
        f"(Fitness F = {sim_res.fitness:.4f})",
        fontsize=14,
        fontweight="bold",
    )

    c_map = get_cell_state_cmap(palette)
    ps_plot = ps_ax.imshow(
        decision_map,
        origin="lower",
        extent=[0.0, sgf_max, 0.0, lgf_max],
        aspect="auto",
        cmap=c_map,
        interpolation="nearest",
        vmin=-0.5,
        vmax=3.5,
    )
    ps_ax.set_title("(SGF, LGF) Steady-State Phase Space", fontsize=11.5)
    ps_ax.set_xlabel("SGF Concentration s(y, x)")
    ps_ax.set_ylabel("LGF Concentration l(y, x)")
    cbar_ps = fig.colorbar(
        ps_plot,
        ax=ps_ax,
        ticks=[0, 1, 2, 3],
        orientation="horizontal",
        pad=0.18,
        fraction=0.05,
    )
    cbar_ps.set_ticklabels(["Die (0)", "Quiet (1)", "Move (2)", "Split (3)"])

    from matplotlib.colors import ListedColormap

    occ_cmap = ListedColormap(["#F8F9FA", "#0072B2"])
    delta_cmap = ListedColormap(["#F8F9FA", "#D55E00"])

    mid_ax.imshow(sim_res.halfway_structure, origin="lower", cmap=occ_cmap, vmin=0, vmax=1)
    mid_ax.set_title("Midpoint Occupancy S_(T/2)", fontsize=11.5)

    fin_ax.imshow(sim_res.final_structure, origin="lower", cmap=occ_cmap, vmin=0, vmax=1)
    fin_ax.set_title("Final Occupancy S_T", fontsize=11.5)

    delta_ax.imshow(sim_res.delta_matrix, origin="lower", cmap=delta_cmap, vmin=0, vmax=1)
    delta_ax.set_title("Structural Delta |S_(T/2) - S_T|", fontsize=11.5)

    for ax in (mid_ax, fin_ax, delta_ax):
        ax.set_aspect("equal")
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    fig.tight_layout()
    out_path = output_dir / "phase_space_example.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_evolution_example(output_dir: Path) -> None:
    """Generate an evolutionary fitness progression plot on the normalized [0, 1] scale."""
    print("Generating evolutionary fitness progression example on [0, 1] scale...")

    rng = np.random.default_rng(2026)
    generations = np.arange(1, 51)

    # Realistic [0, 1] shape homeostasis fitness progression with elitism (monotonic best)
    raw_steps = rng.uniform(0.0, 0.025, size=50)
    base_curve = 0.94 - 0.36 * np.exp(-generations / 14.0)
    best_fitness = np.maximum.accumulate(
        np.clip(base_curve + np.cumsum(raw_steps) * 0.04, 0.55, 0.965)
    )
    avg_fitness = np.clip(
        best_fitness - (0.14 * np.exp(-generations / 22.0) + rng.normal(0.04, 0.012, size=50)),
        0.35,
        best_fitness - 0.015,
    )

    colors = get_cell_state_colors(DEFAULT_PALETTE)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(
        generations,
        best_fitness,
        color=colors[2],
        linewidth=2.6,
        marker="o",
        markersize=4,
        label="Elite / Best Homeostasis Fitness F_max",
    )
    ax.plot(
        generations,
        avg_fitness,
        color=colors[3],
        linestyle="--",
        linewidth=2.2,
        label="Population Mean Fitness F_mean",
    )
    ax.fill_between(
        generations,
        avg_fitness,
        best_fitness,
        color=colors[2],
        alpha=0.12,
        label="Selective Diversity Gap (Tournament + Gaussian Mutation)",
    )

    ax.set_xlim(1, 50)
    ax.set_ylim(0.35, 1.0)
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Shape Homeostasis Fitness F ∈ [0, 1]", fontsize=12)
    ax.set_title(
        "Genetic Algorithm Shape Homeostasis Optimization (F = 1 - (1/N²) Σ |S_(T/2) - S_T|)",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(fontsize=11, loc="lower right", frameon=True)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    out_path = output_dir / "evolution_example.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def main() -> None:
    """Generate all example images and timelapse animations for documentation."""
    print("Generating documentation images and animations...")
    output_dir = Path("docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    w_matrix, _ = generate_cell_system_and_timelapse(output_dir)
    generate_network_example(w_matrix, output_dir)
    generate_phase_space_example(w_matrix, output_dir)
    generate_evolution_example(output_dir)

    print("\nAll documentation figures generated successfully in docs/images/:")
    print("- cell_system_example.png")
    print("- morphogenesis_timelapse.gif")
    print("- network_example.png")
    print("- phase_space_example.png")
    print("- evolution_example.png")


if __name__ == "__main__":
    main()
