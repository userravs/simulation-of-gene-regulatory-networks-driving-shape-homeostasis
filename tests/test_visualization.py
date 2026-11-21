"""Unit tests for colorblind-safe palettes, Plotly colorscales, and timelapse export."""

from __future__ import annotations

import io
from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from core.cell_agent import cell
from core.engine import extract_orientation_grid
from visualization.palettes import (
    CELL_STATE_LABELS,
    CELL_STATE_PALETTES,
    build_discrete_plotly_colorscale,
    get_cell_state_cmap,
    get_cell_state_colors,
    get_map_state_cmap,
)
from visualization.plot import Environment
from visualization.timelapse import (
    TimelapseExporter,
    build_gif_bytes,
    render_snapshot_figure,
    render_snapshot_png_bytes,
)
from visualization.web_app import (
    compute_lgf_gradient,
    compute_phase_space_map,
    compute_step_telemetry,
    create_cell_grid_plot,
    create_grn_network_plot,
    create_homeostasis_summary_plot,
    create_phase_space_plot,
    create_telemetry_plot,
    generate_weight_matrix,
    run_batch_simulation,
    run_evolution_pass,
)


def test_palettes_and_colormaps() -> None:
    """Colorblind-safe and legacy palettes should construct valid discrete colormaps."""
    colors = get_cell_state_colors()
    assert colors == CELL_STATE_PALETTES["colorblind_safe"]
    assert len(colors) == len(CELL_STATE_LABELS) == 4
    assert len(set(colors)) == 4

    cmap = get_cell_state_cmap("colorblind_safe")
    assert cmap.N == 4

    legacy_cmap = get_cell_state_cmap("legacy")
    assert legacy_cmap.N == 4

    map_cmap = get_map_state_cmap("colorblind_safe")
    assert map_cmap.N == 5

    with pytest.raises(ValueError, match="Unknown palette"):
        get_cell_state_colors("nonexistent")

    with pytest.raises(ValueError, match="Unknown palette"):
        get_map_state_cmap("nonexistent")


def test_build_discrete_plotly_colorscale() -> None:
    """Discrete Plotly colorscale should produce stepped monotonic bins."""
    colors = get_cell_state_colors("colorblind_safe")
    scale = build_discrete_plotly_colorscale(colors)

    assert len(scale) == 2 * len(colors)
    assert scale[0] == [0.0, colors[0]]
    assert scale[1] == [0.25, colors[0]]
    assert scale[2] == [0.25, colors[1]]
    assert scale[-1] == [1.0, colors[-1]]

    stops = [entry[0] for entry in scale]
    assert stops == sorted(stops)

    with pytest.raises(ValueError, match="at least one"):
        build_discrete_plotly_colorscale([])


def test_plotly_cell_grid_plot_uses_discrete_palette() -> None:
    """create_cell_grid_plot should apply discrete zmin/zmax bounds and selected palette."""
    size = 8
    cell_grid = np.zeros((size, size), dtype=np.float64)
    sgf_grid = np.zeros((size, size), dtype=np.float64)
    lgf_grid = np.zeros((size, size), dtype=np.float64)

    fig_safe = create_cell_grid_plot(cell_grid, sgf_grid, lgf_grid)
    cells_trace = fig_safe.data[0]
    assert cells_trace.zmin == -0.5
    assert cells_trace.zmax == 3.5
    expected_safe = tuple(
        (stop, color)
        for stop, color in build_discrete_plotly_colorscale(
            get_cell_state_colors("colorblind_safe")
        )
    )
    assert cells_trace.colorscale == expected_safe

    fig_legacy = create_cell_grid_plot(cell_grid, sgf_grid, lgf_grid, palette="legacy")
    expected_legacy = tuple(
        (stop, color)
        for stop, color in build_discrete_plotly_colorscale(get_cell_state_colors("legacy"))
    )
    assert fig_legacy.data[0].colorscale == expected_legacy


def test_timelapse_exporter_headless_png_and_gif(tmp_path: Path) -> None:
    """TimelapseExporter should capture interval PNGs and assemble an animated GIF."""
    size = 10
    cell_grid = np.zeros((size, size), dtype=np.float64)
    sgf_grid = np.zeros((size, size), dtype=np.float64)
    lgf_grid = np.zeros((size, size), dtype=np.float64)

    exporter = TimelapseExporter(tmp_path / "frames", interval=2, dpi=80)
    captured = []
    for step in range(5):
        cell_grid[step, step] = step % 4
        captured.append(exporter.capture(step, cell_grid, sgf_grid, lgf_grid))

    assert [path.name if path else None for path in captured] == [
        "frame_00000.png",
        None,
        "frame_00002.png",
        None,
        "frame_00004.png",
    ]
    assert len(exporter.saved_frames) == 3

    for frame_path in exporter.saved_frames:
        assert frame_path.is_file()
        with Image.open(frame_path) as image:
            assert image.format == "PNG"
            assert image.size[0] > 0 and image.size[1] > 0

    gif_path = exporter.export_gif(duration_ms=120)
    assert gif_path.is_file()
    with Image.open(gif_path) as gif:
        assert gif.format == "GIF"
        assert getattr(gif, "n_frames", 1) == 3


def test_in_memory_snapshot_and_validation(tmp_path: Path) -> None:
    """In-memory PNG/GIF helpers and Exporter parameter validation should behave cleanly."""
    size = 6
    cell_grid = np.ones((size, size), dtype=np.float64)
    sgf_grid = np.zeros((size, size), dtype=np.float64)
    lgf_grid = np.zeros((size, size), dtype=np.float64)

    frame_a = render_snapshot_png_bytes(cell_grid, sgf_grid, lgf_grid, step=1, dpi=72)
    frame_b = render_snapshot_png_bytes(cell_grid * 2, sgf_grid, lgf_grid, step=2, dpi=72)
    gif_bytes = build_gif_bytes([frame_a, frame_b], duration_ms=150)

    with Image.open(io.BytesIO(gif_bytes)) as gif:
        assert gif.format == "GIF"
        assert getattr(gif, "n_frames", 1) == 2

    with pytest.raises(ValueError, match="interval"):
        TimelapseExporter(tmp_path, interval=0)
    with pytest.raises(ValueError, match="dpi"):
        TimelapseExporter(tmp_path, dpi=0)
    with pytest.raises(ValueError, match="Unknown palette"):
        TimelapseExporter(tmp_path, palette="invalid")
    with pytest.raises(ValueError, match="No captured frames"):
        TimelapseExporter(tmp_path).export_gif()
    with pytest.raises(ValueError, match="at least one frame"):
        build_gif_bytes([])


def test_environment_cells_grid_figure_and_timelapse_hook(tmp_path: Path) -> None:
    """Environment.CellsGridFigure and AntGridPlot should support palette and timelapse hook."""
    fig, cells_ax, sgf_ax, lgf_ax, cell_plot, sgf_plot, lgf_plot = Environment.CellsGridFigure(
        8, mode=True
    )
    assert cell_plot.cmap.N == 4
    assert cell_plot.cmap.name == "cell_states_colorblind_safe"

    exporter = TimelapseExporter(tmp_path, interval=1, dpi=72)
    cell_grid = np.zeros((8, 8), dtype=np.float64)
    chem_grid = np.zeros((8, 8, 2), dtype=np.float64)
    Environment.AntGridPlot(
        cell_grid,
        chem_grid,
        8,
        fig,
        cells_ax,
        sgf_ax,
        lgf_ax,
        cell_plot,
        sgf_plot,
        lgf_plot,
        0,
        True,
        timelapse_exporter=exporter,
    )
    assert len(exporter.saved_frames) == 1
    assert exporter.saved_frames[0].name == "frame_00000.png"


@pytest.mark.parametrize(
    "network_type",
    ["Random", "Erdős-Rényi", "Watts-Strogatz", "Barabási-Albert"],
)
def test_generate_weight_matrix_deterministic_seeding(network_type: str) -> None:
    """generate_weight_matrix should be strictly reproducible for a given seed."""
    w_a = generate_weight_matrix(12, network_type, seed=42)
    w_b = generate_weight_matrix(12, network_type, seed=42)
    w_c = generate_weight_matrix(12, network_type, seed=99)

    assert np.array_equal(w_a, w_b)
    assert not np.array_equal(w_a, w_c)


def test_create_cell_grid_plot_enforces_square_aspect_ratio() -> None:
    """All three panels in create_cell_grid_plot should lock a 1:1 square aspect ratio."""
    grid = np.zeros((10, 10), dtype=np.float64)
    fig = create_cell_grid_plot(grid, grid, grid, step=7)

    assert "Step 7" in fig.layout.title.text
    assert fig.layout.yaxis.scaleanchor == "x"
    assert fig.layout.yaxis.scaleratio == 1
    assert fig.layout.yaxis2.scaleanchor == "x2"
    assert fig.layout.yaxis2.scaleratio == 1
    assert fig.layout.yaxis3.scaleanchor == "x3"
    assert fig.layout.yaxis3.scaleratio == 1


def test_batch_simulation_telemetry_and_homeostasis_plots() -> None:
    """Batch simulation should emit telemetry and build telemetry/homeostasis figures."""
    w_matrix = generate_weight_matrix(8, "Random", seed=1)
    result, snapshots, telemetry = run_batch_simulation(
        w_matrix,
        time_steps=10,
        n_nodes=8,
        n_lattice=12,
        seed=1,
        early_stop=False,
    )

    assert len(snapshots) == 10
    assert len(telemetry) == 10
    first = compute_step_telemetry(snapshots[0])
    assert first == telemetry[0]
    assert first["step"] == 1
    assert first["living_cells"] >= 0
    assert first["sgf_max"] >= first["sgf_mean"] >= 0.0
    assert first["lgf_max"] >= first["lgf_mean"] >= 0.0

    telemetry_fig = create_telemetry_plot(telemetry)
    assert len(telemetry_fig.data) == 8

    homeostasis_fig = create_homeostasis_summary_plot(result)
    assert len(homeostasis_fig.data) == 3
    assert f"{result.fitness:.4f}" in homeostasis_fig.layout.title.text
    assert homeostasis_fig.layout.yaxis.scaleanchor == "x"
    assert homeostasis_fig.layout.yaxis2.scaleanchor == "x2"
    assert homeostasis_fig.layout.yaxis3.scaleanchor == "x3"


def test_compute_and_plot_phase_space_map() -> None:
    """compute_phase_space_map and create_phase_space_plot should evaluate (SGF, LGF) grids."""
    w_matrix = generate_weight_matrix(8, "Random", seed=42)
    decision_map, sgf_vals, lgf_vals = compute_phase_space_map(
        w_matrix,
        resolution=6,
        sgf_max=0.5,
        lgf_max=2.0,
        settle_steps=4,
    )

    assert decision_map.shape == (6, 6)
    assert sgf_vals.shape == (6,)
    assert lgf_vals.shape == (6,)
    assert set(np.unique(decision_map)).issubset({0.0, 1.0, 2.0, 3.0})

    fig = create_phase_space_plot(w_matrix, resolution=5, settle_steps=3)
    assert len(fig.data) == 1
    assert fig.data[0].zmin == -0.5
    assert fig.data[0].zmax == 3.5

    with pytest.raises(ValueError, match="at least 8 nodes"):
        compute_phase_space_map(np.zeros((4, 4)))
    with pytest.raises(ValueError, match="resolution"):
        compute_phase_space_map(w_matrix, resolution=1)


def test_create_grn_network_plot_and_evolution_pass() -> None:
    """create_grn_network_plot and run_evolution_pass should return valid figures and genomes."""
    w_matrix = generate_weight_matrix(10, "Erdős-Rényi", seed=7)
    net_fig = create_grn_network_plot(w_matrix, weight_threshold=0.05)

    assert len(net_fig.data) == 3
    assert [trace.name for trace in net_fig.data] == [
        "Excitatory (w > 0)",
        "Inhibitory (w < 0)",
        "GRN Nodes",
    ]
    assert len(net_fig.data[2].text) == 10
    assert net_fig.data[2].text[0] == "0: SGF_in"
    assert net_fig.data[2].text[7] == "7: Compass"

    best_mat, best_score, best_hist, avg_hist = run_evolution_pass(
        8,
        pop_size=4,
        n_generations=3,
        time_steps=6,
        n_lattice=8,
        elite_num=1,
        tournament_size=2,
        seed=42,
    )
    assert best_mat.shape == (8, 8)
    assert 0.0 <= best_score <= 1.0
    assert len(best_hist) == 3
    assert len(avg_hist) == 3
    assert np.isclose(best_score, max(best_hist))


def test_extract_orientation_grid_and_vector_overlays(tmp_path: Path) -> None:
    """Polarization compass vectors and LGF gradient overlays should render in Plotly and Agg."""
    weights = np.zeros((8, 8), dtype=np.float64)
    c_north = cell(1, 1, weights, 8)
    c_north.V[7] = 0.10
    c_south = cell(2, 2, weights, 8)
    c_south.V[7] = 0.35
    c_east = cell(3, 3, weights, 8)
    c_east.V[7] = 0.60
    c_west = cell(4, 4, weights, 8)
    c_west.V[7] = 0.85

    orient = extract_orientation_grid([c_north, c_south, c_east, c_west], 6)
    assert orient.shape == (6, 6, 2)
    assert tuple(orient[1, 1]) == (-1.0, 0.0)
    assert tuple(orient[2, 2]) == (1.0, 0.0)
    assert tuple(orient[3, 3]) == (0.0, 1.0)
    assert tuple(orient[4, 4]) == (0.0, -1.0)

    cell_grid = np.zeros((6, 6), dtype=np.float64)
    for y_idx in (1, 2, 3, 4):
        cell_grid[y_idx, y_idx] = 2.0
    sgf_grid = np.zeros((6, 6), dtype=np.float64)
    lgf_grid = np.linspace(0.0, 3.0, 36, dtype=np.float64).reshape(6, 6)

    grad_y, grad_x = compute_lgf_gradient(lgf_grid)
    assert grad_y.shape == (6, 6)
    assert grad_x.shape == (6, 6)
    assert float(np.max(np.hypot(grad_y, grad_x))) > 0.0

    fig_overlays = create_cell_grid_plot(
        cell_grid,
        sgf_grid,
        lgf_grid,
        step=3,
        orientation_grid=orient,
        show_compass=True,
        show_lgf_gradient=True,
    )
    assert [trace.name for trace in fig_overlays.data] == [
        "Cells",
        "SGF",
        "LGF",
        "Polarization Compass",
        "LGF Gradient",
    ]
    compass_trace = fig_overlays.data[3]
    assert list(compass_trace.marker.symbol) == [
        "triangle-down",
        "triangle-up",
        "triangle-right",
        "triangle-left",
    ]
    assert fig_overlays.data[0].colorbar.orientation == "h"
    assert fig_overlays.data[1].colorbar.orientation == "h"
    assert fig_overlays.data[2].colorbar.orientation == "h"

    dense_net_fig = create_grn_network_plot(generate_weight_matrix(25, "Random", seed=42))
    dense_labels = list(dense_net_fig.data[2].text)
    assert dense_labels[0] == "0: SGF_in"
    assert dense_labels[7] == "7: Compass"
    assert dense_labels[8] == "8"

    mpl_fig = render_snapshot_figure(
        cell_grid,
        sgf_grid,
        lgf_grid,
        step=3,
        orientation_grid=orient,
        show_compass=True,
    )
    assert len(mpl_fig.axes[0].collections) >= 1

    exporter = TimelapseExporter(tmp_path / "compass_frames", interval=1, show_compass=True)
    frame_path = exporter.capture(
        0,
        cell_grid,
        sgf_grid,
        lgf_grid,
        orientation_grid=orient,
    )
    assert frame_path is not None and frame_path.exists()
