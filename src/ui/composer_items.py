"""Composer layout items for GeoForge Studio print layouts.

Provides QGraphicsItem subclasses for map frames, scale bars, legends,
north arrows, and text labels used in the composer canvas.
"""

import math
from typing import Optional

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics,
    QImage, QPixmap,
)
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsObject, QGraphicsRectItem,
    QGraphicsView, QStyleOptionGraphicsItem, QWidget,
)

from ui.map_canvas import MapCanvas


# ---- Utility ----

def _mm_to_pt(mm: float) -> float:
    return mm * 2.83465


def _pt_to_mm(pt: float) -> float:
    return pt / 2.83465


# ---- Map Frame Item ----

class MapFrameItem(QGraphicsObject):
    """A map viewport item that displays the current map canvas content.

    Supports configurable scale modes: 'fit' (auto) and fixed scales
    (1:100, 1:500, 1:1000, etc.).
    """

    is_map_frame = True

    def __init__(self, rect: QRectF, map_canvas: MapCanvas):
        super().__init__()
        self._rect = rect
        self._map_canvas = map_canvas
        self._scale_mode: str = "fit"  # "fit" or "fixed"
        self._scale_value: int = 1000  # denominator, only used in "fixed" mode
        self._pixmap: Optional[QPixmap] = None
        self._border_color = QColor(60, 60, 60)
        self._border_width = 2.0

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

        self._render_map()

    @property
    def is_map_frame(self):
        return True

    def boundingRect(self) -> QRectF:
        return self._rect.adjusted(-2, -2, 2, 2)

    def rect(self) -> QRectF:
        return self._rect

    def set_scale_fit(self):
        """Set scale mode to auto-fit."""
        self._scale_mode = "fit"
        self._render_map()
        self.update()

    def set_scale_fixed(self, denominator: int):
        """Set a fixed map scale (e.g., 1000 for 1:1000)."""
        self._scale_mode = "fixed"
        self._scale_value = max(1, denominator)
        self._render_map()
        self.update()

    def scale_label(self) -> str:
        """Return a human-readable scale label."""
        if self._scale_mode == "fit":
            return "Scale: Fit"
        return f"1:{self._scale_value:,}"

    def _render_map(self):
        """Render the current map view into a pixmap."""
        view = self._map_canvas.renderer.get_widget()
        if not isinstance(view, QGraphicsView):
            self._pixmap = None
            return

        # Get the visible map area
        viewport_rect = view.viewport().rect()
        if viewport_rect.isEmpty():
            self._pixmap = None
            return

        # Determine source and target rects
        if self._scale_mode == "fit":
            source_rect = view.mapToScene(viewport_rect).boundingRect()
        else:
            # Fixed scale: calculate geographic extent from frame size
            view_center = view.mapToScene(viewport_rect.center())
            # Frame width in mm → ground distance at scale
            frame_w_mm = _pt_to_mm(self._rect.width())
            geo_w = frame_w_mm / 1000.0 * self._scale_value
            frame_h_mm = _pt_to_mm(self._rect.height())
            geo_h = frame_h_mm / 1000.0 * self._scale_value

            source_rect = QRectF(
                view_center.x() - geo_w / 2,
                view_center.y() - geo_h / 2,
                geo_w,
                geo_h,
            )

        if source_rect.isEmpty():
            self._pixmap = None
            return

        # Render
        try:
            frame_w = max(1, int(self._rect.width()))
            frame_h = max(1, int(self._rect.height()))
            image = QImage(frame_w, frame_h, QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            view.render(painter, target=QRectF(image.rect()), source=source_rect)
            painter.end()
            self._pixmap = QPixmap.fromImage(image)
        except Exception:
            self._pixmap = None

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ):
        # Map content
        if self._pixmap is not None:
            painter.drawPixmap(self._rect.toRect(), self._pixmap)
        else:
            # No data placeholder
            painter.fillRect(self._rect, QColor(240, 240, 240))
            painter.setPen(QColor(160, 160, 160))
            painter.setFont(QFont("sans-serif", 10))
            painter.drawText(self._rect, Qt.AlignmentFlag.AlignCenter, "No data")

        # Border
        painter.setPen(QPen(self._border_color, self._border_width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(self._rect)

        # Scale label (bottom-left corner)
        painter.setPen(QColor(40, 40, 40))
        painter.setFont(QFont("sans-serif", 7))
        label = self.scale_label()
        label_rect = QRectF(
            self._rect.left() + 4,
            self._rect.bottom() - 16,
            self._rect.width() - 8,
            14,
        )
        painter.fillRect(label_rect, QColor(255, 255, 255, 180))
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)

        # Selection handles
        if self.isSelected():
            self._draw_handles(painter)

    def _draw_handles(self, painter: QPainter):
        """Draw selection handles at corners."""
        painter.setPen(QPen(QColor(0, 120, 255), 1.5))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        size = 6
        for pos in [
            self._rect.topLeft(),
            self._rect.topRight(),
            self._rect.bottomLeft(),
            self._rect.bottomRight(),
        ]:
            painter.drawRect(QRectF(pos.x() - size / 2, pos.y() - size / 2, size, size))

    def render_to_painter(self, painter: QPainter):
        """Render this item to a QPainter (for PDF export)."""
        self._render_map()
        self.paint(painter, QStyleOptionGraphicsItem(), None)

    def mouseDoubleClickEvent(self, event):
        """Double-click: switch to Map tab and show this extent."""
        super().mouseDoubleClickEvent(event)
        # Find the parent tab widget and switch to Map tab
        parent = self.parentWidget()
        while parent is not None:
            if hasattr(parent, 'tab_widget'):
                parent.tab_widget.setCurrentIndex(0)
                break
            parent = parent.parentWidget()


# ---- Scale Bar Item ----

class ScaleBarItem(QGraphicsObject):
    """A graphical scale bar linked to a MapFrameItem.

    Auto-calculates division lengths based on the map frame's current scale.
    Displays alternating black/white bar segments with length labels.
    """

    def __init__(self, rect: QRectF, map_frame: MapFrameItem):
        super().__init__()
        self._rect = rect
        self._map_frame = map_frame
        self._divisions = 4
        self._bar_height = 12
        self._unit = "m"
        self._division_length_pt = 0.0
        self._division_value = 0.0

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

        self._recalculate()

    def boundingRect(self) -> QRectF:
        h = self._rect.height() + 20  # Extra space for labels
        return QRectF(self._rect.x(), self._rect.y(), self._rect.width(), h)

    def rect(self) -> QRectF:
        return self._rect

    def _recalculate(self):
        """Recalculate division lengths based on map frame scale."""
        bar_width_pt = self._rect.width()

        # What's the map scale?
        scale_denom = 1000  # fallback
        if self._map_frame._scale_mode == "fit":
            # Estimate: assume 1:1000 as reasonable default for fit mode
            scale_denom = 1000
        else:
            scale_denom = self._map_frame._scale_value

        # Bar width in mm → ground distance at scale
        bar_width_mm = _pt_to_mm(bar_width_pt)
        total_ground_m = bar_width_mm / 1000.0 * scale_denom

        # Calculate nice division value
        raw_div = total_ground_m / self._divisions
        nice = self._nice_number(raw_div)
        self._division_value = nice
        self._division_length_pt = bar_width_pt * (nice / total_ground_m)

        # Auto-detect unit
        if self._division_value >= 1000:
            self._unit = "km"
            self._division_value /= 1000
        else:
            self._unit = "m"

    @staticmethod
    def _nice_number(value: float) -> float:
        """Round to the nearest 'nice' number (1, 2, 5, 10, 20, 50, ...)."""
        if value <= 0:
            return 1
        exponent = math.floor(math.log10(value))
        fraction = value / (10 ** exponent)
        if fraction < 1.5:
            nice = 1
        elif fraction < 3.5:
            nice = 2
        elif fraction < 7.5:
            nice = 5
        else:
            nice = 10
        return nice * (10 ** exponent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ):
        self._recalculate()

        bar_top = self._rect.top()
        bar_left = self._rect.left()
        seg_width = self._division_length_pt

        if seg_width <= 0:
            return

        # Draw bar segments
        for i in range(self._divisions):
            x = bar_left + i * seg_width
            seg_rect = QRectF(x, bar_top, seg_width, self._bar_height)
            color = Qt.GlobalColor.black if i % 2 == 0 else Qt.GlobalColor.white
            painter.fillRect(seg_rect, QColor(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(seg_rect)

        # Draw labels
        painter.setFont(QFont("sans-serif", 7))
        painter.setPen(QColor(0, 0, 0))

        for i in range(self._divisions + 1):
            x = bar_left + i * seg_width
            value = i * self._division_value

            # Tick
            painter.drawLine(QPointF(x, bar_top), QPointF(x, bar_top + self._bar_height + 3))

            # Label
            if self._unit == "km" and value >= 1:
                label = f"{value:.1f}" if value != int(value) else f"{int(value)}"
            else:
                label = f"{int(value)}" if value == int(value) else f"{value:.1f}"

            # Draw label below tick
            text_rect = QRectF(x - 20, bar_top + self._bar_height + 4, 40, 14)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)

        # Unit label at the end
        unit_rect = QRectF(
            bar_left + self._divisions * seg_width,
            bar_top + self._bar_height + 4,
            40,
            14,
        )
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignLeft, self._unit)

        # Selection handles
        if self.isSelected():
            painter.setPen(QPen(QColor(0, 120, 255), 1.5))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            size = 5
            for pos in [
                self._rect.topLeft(),
                self._rect.topRight(),
                self._rect.bottomLeft(),
                self._rect.bottomRight(),
            ]:
                painter.drawRect(QRectF(pos.x() - size / 2, pos.y() - size / 2, size, size))

    def render_to_painter(self, painter: QPainter):
        """Render this item to a QPainter (for PDF export)."""
        self.paint(painter, QStyleOptionGraphicsItem(), None)
