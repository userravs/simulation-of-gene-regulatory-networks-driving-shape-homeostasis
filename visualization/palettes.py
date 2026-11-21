"""Colorblind-safe and legacy color palettes for cellular automata visualizations."""

from __future__ import annotations

from collections.abc import Sequence
from matplotlib.colors import ListedColormap

DEFAULT_PALETTE = "colorblind_safe"

CELL_STATE_LABELS: tuple[str, str, str, str] = ("Empty", "Quiet", "Moving", "Divided")

# Okabe-Ito qualitative palette provides strong luminance and chromatic contrast
# across deuteranopia, protanopia, and tritanopia.
CELL_STATE_PALETTES: dict[str, tuple[str, str, str, str]] = {
    "colorblind_safe": ("#F8F9FA", "#0072B2", "#E69F00", "#CC79A7"),
    "legacy": ("#FFFFFF", "#008000", "#0000FF", "#FF0000"),
}

MAP_STATE_PALETTES: dict[str, tuple[str, str, str, str, str]] = {
    "colorblind_safe": ("#E69F00", "#009E73", "#D55E00", "#0072B2", "#F8F9FA"),
    "legacy": ("#FFFF00", "#008000", "#FF0000", "#0000FF", "#FFFFFF"),
}


def get_cell_state_colors(palette: str = DEFAULT_PALETTE) -> tuple[str, str, str, str]:
    """Return the 4-color tuple for cellular states (Empty, Quiet, Moving, Divided)."""
    if palette not in CELL_STATE_PALETTES:
        supported = ", ".join(sorted(CELL_STATE_PALETTES))
        raise ValueError(f"Unknown palette '{palette}'. Choose from: {supported}.")
    return CELL_STATE_PALETTES[palette]


def get_cell_state_cmap(palette: str = DEFAULT_PALETTE) -> ListedColormap:
    """Return a discrete Matplotlib ListedColormap for cellular states 0..3."""
    return ListedColormap(list(get_cell_state_colors(palette)), name=f"cell_states_{palette}")


def get_map_state_cmap(palette: str = DEFAULT_PALETTE) -> ListedColormap:
    """Return a discrete Matplotlib ListedColormap for 5-state phase-space maps."""
    if palette not in MAP_STATE_PALETTES:
        supported = ", ".join(sorted(MAP_STATE_PALETTES))
        raise ValueError(f"Unknown palette '{palette}'. Choose from: {supported}.")
    return ListedColormap(list(MAP_STATE_PALETTES[palette]), name=f"map_states_{palette}")


def build_discrete_plotly_colorscale(colors: Sequence[str]) -> list[list[float | str]]:
    """Build a stepped Plotly colorscale with discrete equal-width categorical bands."""
    if len(colors) == 0:
        raise ValueError("colors must contain at least one color entry.")

    n_colors = len(colors)
    colorscale: list[list[float | str]] = []
    for idx, color in enumerate(colors):
        colorscale.append([idx / n_colors, color])
        colorscale.append([(idx + 1) / n_colors, color])
    return colorscale
