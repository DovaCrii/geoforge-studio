"""PDF volume report exporter for GeoForge Studio.

Generates a PDF report with volume analysis results, statistics,
and a simple contour/terrain visualization using pycairo.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from dataclasses import dataclass

from .surface import TINSurface, SurveyPoint
from .calculator import CutFillResult, format_volume
from .contour import generate_contours

try:
    import cairo
    HAS_CAIRO = True
except ImportError:
    HAS_CAIRO = False


# Layout constants (points)
PAGE_W, PAGE_H = 595.28, 841.89  # A4 portrait
MARGIN = 50
COLOR_BG = (0.95, 0.95, 0.95)
COLOR_TEXT = (0.15, 0.15, 0.15)
COLOR_ACCENT = (0.2, 0.4, 0.7)
COLOR_CUT = (0.8, 0.2, 0.15)
COLOR_FILL = (0.15, 0.6, 0.3)
COLOR_CONTOUR = (0.4, 0.3, 0.2)


@dataclass
class VolumeReport:
    """Generated volume report metadata."""
    path: str
    page_count: int
    generated_at: str


def _draw_text(
    ctx: cairo.Context,
    text: str,
    x: float,
    y: float,
    font_size: float = 10,
    bold: bool = False,
    color: Tuple[float, float, float] = COLOR_TEXT,
    align: str = "left",
) -> float:
    """Draw text and return the X position after drawing."""
    ctx.set_source_rgb(*color)
    ctx.set_font_size(font_size)
    # Simple bold via pseudo-family (cairo doesn't support bold directly without font face)
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)

    if align == "right":
        ext = ctx.text_extents(text)
        x = x - ext.width

    ctx.move_to(x, y)
    ctx.show_text(text)

    ext = ctx.text_extents(text)
    return x + ext.width


def _draw_line(
    ctx: cairo.Context,
    x1: float, y1: float,
    x2: float, y2: float,
    width: float = 1.0,
    color: Tuple[float, float, float] = COLOR_TEXT,
) -> None:
    ctx.set_source_rgb(*color)
    ctx.set_line_width(width)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()


def _draw_contour_preview(
    ctx: cairo.Context,
    surface: TINSurface,
    x: float, y: float,
    width: float, height: float,
    interval: float = 1.0,
) -> None:
    """Draw a simplified contour map preview in the given rect."""
    # Background box
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(x, y, width, height)
    ctx.fill()
    ctx.set_source_rgb(0.8, 0.8, 0.8)
    ctx.set_line_width(0.5)
    ctx.rectangle(x, y, width, height)
    ctx.stroke()

    # Get bounding box of surface
    bbox = surface.get_bounding_box()
    bx_min, by_min, bx_max, by_max = bbox
    bx_range = bx_max - bx_min if bx_max > bx_min else 1.0
    by_range = by_max - by_min if by_max > by_min else 1.0

    def _map(px: float, py: float) -> Tuple[float, float]:
        sx = x + 10 + (px - bx_min) / bx_range * (width - 20)
        sy = y + 10 + (by_max - py) / by_range * (height - 20)
        return sx, sy

    # Draw contour segments
    contours = generate_contours(surface, interval=interval)

    # Draw surface points
    ctx.set_source_rgb(COLOR_ACCENT[0], COLOR_ACCENT[1], COLOR_ACCENT[2])
    ctx.set_line_width(2.0)
    ctx.set_dash([])
    for pt in surface.points:
        sx, sy = _map(pt.x, pt.y)
        ctx.arc(sx, sy, 1.5, 0, 6.2832)
        ctx.fill()

    # Draw contour lines
    major_interval = max(1, int(interval * 5))
    for contour in contours:
        if not contour["segments"]:
            continue
        is_major = (int(contour["elevation"]) % major_interval) == 0
        ctx.set_source_rgb(*COLOR_CONTOUR)
        ctx.set_line_width(1.5 if is_major else 0.7)
        if not is_major:
            ctx.set_dash([3, 3])
        else:
            ctx.set_dash([])

        for seg in contour["segments"]:
            (x1, y1), (x2, y2) = seg
            sx1, sy1 = _map(x1, y1)
            sx2, sy2 = _map(x2, y2)
            ctx.move_to(sx1, sy1)
            ctx.line_to(sx2, sy2)
            ctx.stroke()

    ctx.set_dash([])


def generate_volume_report(
    surface: TINSurface,
    result: CutFillResult,
    filepath: str,
    title: str = "Volume Analysis Report",
    project: str = "",
    contour_interval: float = 1.0,
) -> VolumeReport:
    """Generate a PDF volume report.

    Args:
        surface: TIN surface data
        result: Cut/fill calculation result
        filepath: Output PDF path
        title: Report title
        project: Project name (optional)
        contour_interval: Contour interval for the preview map

    Returns:
        VolumeReport metadata

    Raises:
        RuntimeError: If pycairo is not installed
    """
    if not HAS_CAIRO:
        raise RuntimeError(
            "pycairo is required for PDF generation. "
            "Install it with: pip install pycairo"
        )

    surface_surface = cairo.PDFSurface(filepath, PAGE_W, PAGE_H)
    ctx = cairo.Context(surface_surface)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Page 1: Header + Summary ──
    # Title
    _draw_text(ctx, title, MARGIN, MARGIN + 20, font_size=22, bold=True, color=COLOR_ACCENT)
    y = MARGIN + 50
    if project:
        _draw_text(ctx, f"Project: {project}", MARGIN, y, font_size=11, color=(0.4, 0.4, 0.4))
        y += 18
    _draw_text(ctx, f"Generated: {now}", MARGIN, y, font_size=10, color=(0.4, 0.4, 0.4))
    y += 30

    # Separator
    _draw_line(ctx, MARGIN, y, PAGE_W - MARGIN, y, width=1.5, color=COLOR_ACCENT)
    y += 25

    # Volume summary table
    col1_x = MARGIN
    col2_x = MARGIN + 200
    row_h = 20

    def _summary_row(label: str, value: str, color=COLOR_TEXT, bold_val=False):
        nonlocal y
        _draw_text(ctx, label, col1_x, y, font_size=10, bold=False, color=color)
        _draw_text(ctx, value, col2_x, y, font_size=10, bold=bold_val, color=color)
        y += row_h

    _draw_text(ctx, "Volume Summary", col1_x, y, font_size=13, bold=True)
    y += row_h + 4

    _summary_row("Cut Volume:", f"{result.total_cut:.2f} m³", color=COLOR_CUT)
    _summary_row("Fill Volume:", f"{result.total_fill:.2f} m³", color=COLOR_FILL)
    _summary_row("Net Volume:", f"{result.net_volume:.2f} m³", bold_val=True)
    _summary_row("Surface Area:", f"{result.surface_area:.2f} m²")
    _summary_row("Triangles:", str(result.triangles_processed))
    _summary_row("Status:", "Balanced" if result.is_balanced else "Unbalanced",
                 color=(0.15, 0.6, 0.3) if result.is_balanced else COLOR_CUT,
                 bold_val=True)
    y += 10

    # Volume bar visualization
    bar_x = MARGIN
    bar_y = y
    bar_width = PAGE_W - 2 * MARGIN
    bar_height = 24
    total = max(result.total_cut + result.total_fill, 0.01)
    cut_w = bar_width * (result.total_cut / total)
    fill_w = bar_width * (result.total_fill / total)

    _draw_text(ctx, "Cut", bar_x, bar_y - 6, font_size=8, color=COLOR_CUT)
    ctx.set_source_rgb(*COLOR_CUT)
    ctx.rectangle(bar_x, bar_y, cut_w, bar_height)
    ctx.fill()

    fill_x = bar_x + cut_w
    _draw_text(ctx, "Fill", fill_x + 4, bar_y - 6, font_size=8, color=COLOR_FILL)
    ctx.set_source_rgb(*COLOR_FILL)
    ctx.rectangle(fill_x, bar_y, fill_w, bar_height)
    ctx.fill()

    y = bar_y + bar_height + 20

    # ── Contour preview ──
    _draw_text(ctx, "Contour Map Preview", MARGIN, y, font_size=13, bold=True)
    y += 8
    preview_size = min(PAGE_W - 2 * MARGIN, 280)
    _draw_contour_preview(ctx, surface, MARGIN, y, preview_size, preview_size,
                          interval=contour_interval)
    y += preview_size + 20

    # ── Surface statistics (if space) ──
    if y < PAGE_H - 80:
        _draw_text(ctx, "Surface Statistics", MARGIN, y, font_size=13, bold=True)
        y += row_h + 4
        stats = surface.get_statistics()
        for key, val in stats.items():
            label = key.replace("_", " ").title() + ":"
            value_str = f"{val:.2f}" if isinstance(val, float) else str(val)
            _draw_text(ctx, label, MARGIN, y, font_size=9)
            _draw_text(ctx, value_str, MARGIN + 180, y, font_size=9)
            y += 16

    surface_surface.finish()

    page_count = 1  # A4 fits it — extend to page 2 if needed in future
    return VolumeReport(
        path=filepath,
        page_count=page_count,
        generated_at=now,
    )


__all__ = [
    "VolumeReport",
    "generate_volume_report",
]
