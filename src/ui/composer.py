"""Composer / Print Layout module for GeoForge Studio.

Provides a WYSIWYG composer canvas for creating print-ready map layouts
with map frames, legends, scale bars, north arrows, and text labels.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QAction,
    QPageSize, QPageLayout,
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QPushButton, QToolBar, QDialog, QDialogButtonBox,
    QComboBox, QLabel, QSpinBox, QFormLayout, QFileDialog, QMessageBox,
    QGraphicsItem, QStyleOptionGraphicsItem,
)

from ui.map_canvas import MapCanvas


# ---- Page Setup Model ----

_PAGE_SIZES = {
    "A4": (210, 297),
    "A3": (297, 420),
    "Letter": (215.9, 279.4),
}

@dataclass
class PageSetup:
    """Page configuration for the composer layout."""
    size: str = "A4"          # "A4" | "A3" | "Letter"
    orientation: str = "landscape"  # "portrait" | "landscape"
    margins_mm: Tuple[float, float, float, float] = (10, 10, 10, 10)

    def page_dimensions_mm(self) -> Tuple[float, float]:
        """Return (width_mm, height_mm) respecting orientation."""
        w, h = _PAGE_SIZES.get(self.size, (210, 297))
        if self.orientation == "landscape":
            return (max(w, h), min(w, h))
        return (min(w, h), max(w, h))

    def page_rect_pt(self) -> QRectF:
        """Return page rect in points (1pt = 1/72 inch)."""
        w_mm, h_mm = self.page_dimensions_mm()
        # 1 mm = 2.83465 pt
        return QRectF(0, 0, w_mm * 2.83465, h_mm * 2.83465)

    def content_rect_pt(self) -> QRectF:
        """Return content area inside margins in points."""
        page = self.page_rect_pt()
        l, t, r, b = self.margins_mm
        margin_pt = 2.83465
        return QRectF(
            page.left() + l * margin_pt,
            page.top() + t * margin_pt,
            page.width() - (l + r) * margin_pt,
            page.height() - (t + b) * margin_pt,
        )


# ---- Scene Items ----

class PageItem(QGraphicsRectItem):
    """Page boundary rectangle with subtle shadow effect."""

    def __init__(self, page_rect: QRectF):
        super().__init__(page_rect)
        self.setPen(QPen(QColor(180, 180, 180), 1))
        self.setBrush(QBrush(QColor(255, 255, 255)))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setZValue(-100)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        # Drop shadow
        shadow_rect = self.rect().translated(3, 3)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.drawRect(shadow_rect)
        # Page background
        super().paint(painter, option, widget)


# ---- Composer Widget ----

class ComposerWidget(QWidget):
    """Main composer panel with canvas, toolbar, and export controls."""

    def __init__(self, map_canvas: MapCanvas, services: dict):
        super().__init__()
        self._map_canvas = map_canvas
        self._services = services
        self._page_setup = PageSetup()
        self._composer_items: list[QGraphicsItem] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar("Composer")
        add_frame_btn = QPushButton("🗺️ Map Frame")
        add_frame_btn.clicked.connect(self.add_map_frame)
        toolbar.addWidget(add_frame_btn)

        add_scale_btn = QPushButton("📏 Scale Bar")
        add_scale_btn.clicked.connect(self.add_scale_bar)
        toolbar.addWidget(add_scale_btn)

        toolbar.addSeparator()

        page_setup_btn = QPushButton("📄 Page Setup")
        page_setup_btn.clicked.connect(self._open_page_setup)
        toolbar.addWidget(page_setup_btn)

        export_btn = QPushButton("⬇ Export PDF")
        export_btn.clicked.connect(self.export_pdf)
        toolbar.addWidget(export_btn)

        layout.addWidget(toolbar)

        # Scene and view
        self._scene = QGraphicsScene()
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        layout.addWidget(self._view)

        self._rebuild_page()

    def _rebuild_page(self):
        """Rebuild the page background after setup changes."""
        self._scene.clear()
        self._composer_items.clear()

        page_rect = self._page_setup.page_rect_pt()
        self._page_item = PageItem(page_rect)
        self._scene.addItem(self._page_item)

        # Set scene rect with some margin
        margin = 50
        self._scene.setSceneRect(
            page_rect.adjusted(-margin, -margin, margin, margin)
        )
        self._view.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _current_page_rect(self) -> QRectF:
        return self._page_setup.page_rect_pt()

    def _content_rect(self) -> QRectF:
        return self._page_setup.content_rect_pt()

    # ---- Item management ----

    def add_map_frame(self):
        """Add a MapFrameItem at the center of the content area."""
        from ui.composer_items import MapFrameItem

        content = self._content_rect()
        # Default size: 70% of content width, 60% of content height
        w = content.width() * 0.7
        h = content.height() * 0.6
        x = content.center().x() - w / 2
        y = content.top() + 20

        item = MapFrameItem(
            QRectF(x, y, w, h),
            self._map_canvas,
        )
        self._scene.addItem(item)
        self._composer_items.append(item)

    def add_scale_bar(self):
        """Add a ScaleBarItem below the first map frame."""
        from ui.composer_items import ScaleBarItem

        map_frame = self._first_map_frame()
        if map_frame is None:
            QMessageBox.information(self, "Hint", "Add a Map Frame first.")
            return

        mf_rect = map_frame.rect()
        bar_width = mf_rect.width() * 0.5
        bar_height = 20

        x = mf_rect.center().x() - bar_width / 2
        y = mf_rect.bottom() + 15

        item = ScaleBarItem(
            QRectF(x, y, bar_width, bar_height),
            map_frame,
        )
        self._scene.addItem(item)
        self._composer_items.append(item)

    def _first_map_frame(self):
        """Return the first MapFrameItem in the scene, or None."""
        for item in self._composer_items:
            if hasattr(item, 'is_map_frame') and item.is_map_frame:
                return item
        return None

    # ---- Page Setup Dialog ----

    def _open_page_setup(self):
        """Open the page setup dialog."""
        dialog = PageSetupDialog(self._page_setup, self)
        if dialog.exec():
            self._page_setup = dialog.get_page_setup()
            self._rebuild_page()

    # ---- Export ----

    def export_pdf(self):
        """Export the composer layout to a PDF file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Layout as PDF",
            "geoforge-map-layout.pdf",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        if not self._composer_items:
            QMessageBox.warning(self, "Empty Layout", "Add items to the layout before exporting.")
            return

        try:
            self._render_pdf(file_path)
            QMessageBox.information(self, "Export Complete", f"PDF saved:\n{file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", str(e))

    def _render_pdf(self, file_path: str):
        """Render the layout to a PDF file using QPrinter."""
        page_rect = self._current_page_rect()
        w_pt = page_rect.width()
        h_pt = page_rect.height()

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        printer.setResolution(300)

        # Set page size
        page_size = QPageSize(QPageSize.PageSizeId.A4)
        w_mm, h_mm = self._page_setup.page_dimensions_mm()
        if self._page_setup.size == "A3":
            page_size = QPageSize(QPageSize.PageSizeId.A3)
        elif self._page_setup.size == "Letter":
            page_size = QPageSize(QPageSize.PageSizeId.Letter)

        if self._page_setup.orientation == "landscape":
            layout = QPageLayout(
                page_size, QPageLayout.Orientation.Landscape,
                QPageSize.Unit.Millimeter
            )
        else:
            layout = QPageLayout(
                page_size, QPageLayout.Orientation.Portrait,
                QPageSize.Unit.Millimeter
            )
        printer.setPageLayout(layout)

        painter = QPainter(printer)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Scale painter to match scene coordinates
        # Scene is in points, printer device is in device pixels at 300 DPI
        # 1 point = 1/72 inch, at 300 DPI: 300/72 = 4.1667 pixels per point
        scale = printer.resolution() / 72.0  # 300/72 ≈ 4.1667
        painter.scale(scale, scale)

        # Render each item
        for item in self._composer_items:
            if hasattr(item, 'render_to_painter'):
                item.render_to_painter(painter)
            else:
                # Fallback: let the item paint itself
                self._scene.render(painter, QRectF(), item.sceneBoundingRect())

        painter.end()


# ---- Page Setup Dialog ----

class PageSetupDialog(QDialog):
    """Dialog for configuring page size, orientation, and margins."""

    def __init__(self, current: PageSetup, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Page Setup")
        self._result = current

        layout = QFormLayout(self)

        # Page size
        self._size_combo = QComboBox()
        self._size_combo.addItems(["A4", "A3", "Letter"])
        self._size_combo.setCurrentText(current.size)
        layout.addRow("Page Size:", self._size_combo)

        # Orientation
        self._orient_combo = QComboBox()
        self._orient_combo.addItems(["Landscape", "Portrait"])
        self._orient_combo.setCurrentText(
            "Landscape" if current.orientation == "landscape" else "Portrait"
        )
        layout.addRow("Orientation:", self._orient_combo)

        # Margins
        margins_widget = QWidget()
        margins_layout = QHBoxLayout(margins_widget)
        margins_layout.setContentsMargins(0, 0, 0, 0)

        self._margin_left = QSpinBox()
        self._margin_left.setRange(0, 50)
        self._margin_left.setValue(int(current.margins_mm[0]))
        self._margin_left.setSuffix(" mm")
        margins_layout.addWidget(QLabel("L:"))
        margins_layout.addWidget(self._margin_left)

        self._margin_top = QSpinBox()
        self._margin_top.setRange(0, 50)
        self._margin_top.setValue(int(current.margins_mm[1]))
        self._margin_top.setSuffix(" mm")
        margins_layout.addWidget(QLabel("T:"))
        margins_layout.addWidget(self._margin_top)

        self._margin_right = QSpinBox()
        self._margin_right.setRange(0, 50)
        self._margin_right.setValue(int(current.margins_mm[2]))
        self._margin_right.setSuffix(" mm")
        margins_layout.addWidget(QLabel("R:"))
        margins_layout.addWidget(self._margin_right)

        self._margin_bottom = QSpinBox()
        self._margin_bottom.setRange(0, 50)
        self._margin_bottom.setValue(int(current.margins_mm[3]))
        self._margin_bottom.setSuffix(" mm")
        margins_layout.addWidget(QLabel("B:"))
        margins_layout.addWidget(self._margin_bottom)

        layout.addRow("Margins:", margins_widget)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_page_setup(self) -> PageSetup:
        return PageSetup(
            size=self._size_combo.currentText(),
            orientation="landscape" if self._orient_combo.currentText() == "Landscape" else "portrait",
            margins_mm=(
                self._margin_left.value(),
                self._margin_top.value(),
                self._margin_right.value(),
                self._margin_bottom.value(),
            ),
        )
