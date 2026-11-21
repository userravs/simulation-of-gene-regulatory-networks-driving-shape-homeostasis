"""Headless snapshot rendering and timelapse GIF export for GRN simulations."""

from __future__ import annotations

from collections.abc import Sequence
import io
from pathlib import Path
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
from PIL import Image

from visualization.palettes import (
    CELL_STATE_LABELS,
    DEFAULT_PALETTE,
    get_cell_state_cmap,
    get_cell_state_colors,
)


def render_snapshot_figure(
    cell_grid,
    sgf_grid: np.ndarray,
    lgf_grid: np.ndarray,
    *,
    step: int | None = None,
    palette: str = DEFAULT_PALETTE,
    sgf_vmax: float = 0.05,
    lgf_vmax: float = 3.0,
    orientation_grid: np.ndarray | None = None,
    show_compass: bool = False,
) -> Figure:
    """Render a headless 3-panel Matplotlib Figure (Cells, SGF, LGF) using Agg."""
    fig = Figure(figsize=(15, 5))
    FigureCanvasAgg(fig)
    cells_ax, sgf_ax, lgf_ax = fig.subplots(1, 3)

    title = f"Cell System — Step {step}" if step is not None else "Cell System"
    fig.suptitle(title, fontsize=14)

    cell_data = np.asarray(cell_grid, dtype=np.float64)
    sgf_data = np.asarray(sgf_grid, dtype=np.float64)
    lgf_data = np.asarray(lgf_grid, dtype=np.float64)

    cells_ax.set_title("Cells")
    sgf_ax.set_title("SGF")
    lgf_ax.set_title("LGF")

    cell_plot = cells_ax.imshow(
        cell_data,
        origin="lower",
        cmap=get_cell_state_cmap(palette),
        interpolation="none",
        vmin=-0.5,
        vmax=3.5,
    )
    if show_compass and orientation_grid is not None:
        orient = np.asarray(orientation_grid, dtype=np.float64)
        if orient.ndim == 3 and orient.shape[:2] == cell_data.shape and orient.shape[2] >= 2:
            dy = orient[:, :, 0]
            dx = orient[:, :, 1]
            mask = (cell_data > 0) & ((dy != 0.0) | (dx != 0.0))
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
                    scale=1.25,
                    width=0.008,
                    headwidth=3.5,
                )
    cbar_cells = fig.colorbar(
        cell_plot,
        ax=cells_ax,
        ticks=[0, 1, 2, 3],
        orientation="horizontal",
    )
    cbar_cells.set_ticklabels(list(CELL_STATE_LABELS))
    cbar_cells.set_label("Cell States")

    sgf_plot = sgf_ax.imshow(
        sgf_data,
        origin="lower",
        cmap="Reds",
        interpolation="none",
        vmin=0.0,
        vmax=sgf_vmax,
    )
    fig.colorbar(sgf_plot, ax=sgf_ax, orientation="horizontal")

    lgf_plot = lgf_ax.imshow(
        lgf_data,
        origin="lower",
        cmap="Blues",
        interpolation="none",
        vmin=0.0,
        vmax=lgf_vmax,
    )
    fig.colorbar(lgf_plot, ax=lgf_ax, orientation="horizontal")

    for axis in (cells_ax, sgf_ax, lgf_ax):
        axis.set_aspect("equal")
        axis.xaxis.set_visible(False)
        axis.yaxis.set_visible(False)

    fig.tight_layout()
    return fig


def render_snapshot_png_bytes(
    cell_grid,
    sgf_grid: np.ndarray,
    lgf_grid: np.ndarray,
    *,
    step: int | None = None,
    palette: str = DEFAULT_PALETTE,
    dpi: int = 150,
    sgf_vmax: float = 0.05,
    lgf_vmax: float = 3.0,
    orientation_grid: np.ndarray | None = None,
    show_compass: bool = False,
) -> bytes:
    """Render a simulation snapshot figure directly to PNG bytes without a display."""
    if dpi <= 0:
        raise ValueError("dpi must be a positive integer.")

    fig = render_snapshot_figure(
        cell_grid,
        sgf_grid,
        lgf_grid,
        step=step,
        palette=palette,
        sgf_vmax=sgf_vmax,
        lgf_vmax=lgf_vmax,
        orientation_grid=orientation_grid,
        show_compass=show_compass,
    )
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    return buffer.getvalue()


def build_gif_bytes(
    frame_png_bytes: Sequence[bytes],
    *,
    duration_ms: int = 200,
    loop: int = 0,
) -> bytes:
    """Assemble in-memory PNG frame buffers into an animated GIF byte stream."""
    if len(frame_png_bytes) == 0:
        raise ValueError("frame_png_bytes must contain at least one frame.")
    if duration_ms <= 0:
        raise ValueError("duration_ms must be a positive integer.")
    if loop < 0:
        raise ValueError("loop must be zero or a positive integer.")

    rgb_frames: list[Image.Image] = []
    for raw_frame in frame_png_bytes:
        with Image.open(io.BytesIO(raw_frame)) as image:
            if image.mode in ("RGBA", "LA"):
                canvas = Image.new("RGB", image.size, (255, 255, 255))
                canvas.paste(image, mask=image.getchannel("A"))
                rgb_frames.append(canvas)
            else:
                rgb_frames.append(image.convert("RGB"))

    target_size = rgb_frames[0].size
    normalized_frames: list[Image.Image] = []
    for frame in rgb_frames:
        if frame.size == target_size:
            normalized_frames.append(frame)
        else:
            padded = Image.new("RGB", target_size, (255, 255, 255))
            padded.paste(frame, (0, 0))
            normalized_frames.append(padded)

    output = io.BytesIO()
    normalized_frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=normalized_frames[1:],
        duration=duration_ms,
        loop=loop,
    )
    return output.getvalue()


class TimelapseExporter:
    """Collect periodic simulation snapshots on disk and assemble animated GIFs."""

    def __init__(
        self,
        output_dir: str | Path,
        *,
        interval: int = 1,
        prefix: str = "frame",
        dpi: int = 150,
        palette: str = DEFAULT_PALETTE,
        sgf_vmax: float = 0.05,
        lgf_vmax: float = 3.0,
        show_compass: bool = False,
    ) -> None:
        """Configure snapshot interval, output directory, DPI, and palette."""
        if interval < 1:
            raise ValueError("interval must be >= 1.")
        if dpi <= 0:
            raise ValueError("dpi must be a positive integer.")
        get_cell_state_colors(palette)

        self.output_dir = Path(output_dir)
        self.interval = interval
        self.prefix = prefix
        self.dpi = dpi
        self.palette = palette
        self.sgf_vmax = sgf_vmax
        self.lgf_vmax = lgf_vmax
        self.show_compass = show_compass
        self.saved_frames: list[Path] = []

    def should_capture(self, step: int) -> bool:
        """Return True if the given step index falls on the capture interval."""
        return step >= 0 and step % self.interval == 0

    def capture(
        self,
        step: int,
        cell_grid,
        sgf_grid: np.ndarray,
        lgf_grid: np.ndarray,
        *,
        orientation_grid: np.ndarray | None = None,
        force: bool = False,
    ) -> Path | None:
        """Save a PNG snapshot for the given step when scheduled or forced."""
        if not force and not self.should_capture(step):
            return None

        self.output_dir.mkdir(parents=True, exist_ok=True)
        png_bytes = render_snapshot_png_bytes(
            cell_grid,
            sgf_grid,
            lgf_grid,
            step=step,
            palette=self.palette,
            dpi=self.dpi,
            sgf_vmax=self.sgf_vmax,
            lgf_vmax=self.lgf_vmax,
            orientation_grid=orientation_grid,
            show_compass=self.show_compass,
        )
        frame_path = self.output_dir / f"{self.prefix}_{step:05d}.png"
        frame_path.write_bytes(png_bytes)
        self.saved_frames.append(frame_path)
        return frame_path

    def export_gif(
        self,
        gif_path: str | Path | None = None,
        *,
        duration_ms: int = 200,
        loop: int = 0,
    ) -> Path:
        """Assemble all captured PNG snapshots into an animated GIF file."""
        if len(self.saved_frames) == 0:
            raise ValueError("No captured frames available to export GIF.")

        target_path = (
            Path(gif_path)
            if gif_path is not None
            else self.output_dir / f"{self.prefix}_timelapse.gif"
        )
        target_path.parent.mkdir(parents=True, exist_ok=True)
        gif_bytes = build_gif_bytes(
            [frame_path.read_bytes() for frame_path in self.saved_frames],
            duration_ms=duration_ms,
            loop=loop,
        )
        target_path.write_bytes(gif_bytes)
        return target_path
