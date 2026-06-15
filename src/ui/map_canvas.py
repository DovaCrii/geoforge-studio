"""Map renderer abstraction for GeoForge Studio.

This module provides the MapRenderer interface and Qt-native QGraphicsView backend
for displaying geospatial data in GeoForge Studio.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
import pyproj

# Import CRS utilities
from ui.crs_utils import (
    CRSManager,
    Point2D,
    Point3D,
    set_crs,
    get_crs,
    transform_point,
    transform_point_3d,
    is_crs_set,
    get_crs_info,
)

# Type aliases for better readability
Point = Point2D
Geometry = List[Point3D]

class PointStyle:
    """Style configuration for point rendering."""
    
    def __init__(
        self,
        color: QColor = QColor(0, 120, 255),
        size: float = 5.0,
        pen_width: float = 1.0
    ):
        self.color = color
        self.size = size
        self.pen_width = pen_width

class OverlayGeom:
    """Represents overlay geometry (lines, polygons, etc.)."""
    
    def __init__(
        self,
        geom_type: str,
        points: Geometry,
        color: QColor = QColor(128, 128, 128),
        pen_width: float = 2.0
    ):
        self.geom_type = geom_type  # "line", "polygon", "circle"
        self.points = points
        self.color = color
        self.pen_width = pen_width

class MapRenderer(ABC):
    """Abstract base class for map renderers.
    
    This interface defines the contract for map rendering backends.
    The default implementation uses QGraphicsView for Qt-native rendering.
    """
    
    @abstractmethod
    def set_crs(self, crs: pyproj.CRS) -> None:
        """Set the coordinate reference system for the map.
        
        Args:
            crs: The coordinate reference system to use
        """
        pass
    
    @abstractmethod
    def add_point_layer(
        self,
        id: str,
        points: List[Point3D],
        style: PointStyle,
        source_crs: Optional[pyproj.CRS] = None,
    ) -> None:
        """Add a point layer to the map.
        
        Args:
            id: Unique identifier for the layer
            points: List of 3D points (x, y, z) in the map's CRS
            style: Style configuration for the points
        """
        pass
    
    @abstractmethod
    def add_overlay(
        self,
        id: str,
        geometry: List[OverlayGeom],
        source_crs: Optional[pyproj.CRS] = None,
    ) -> None:
        """Add an overlay geometry layer to the map.
        
        Args:
            id: Unique identifier for the overlay layer
            geometry: List of overlay geometries
        """
        pass
    
    @abstractmethod
    def zoom_to_extents(self) -> None:
        """Zoom the map to show all data layers."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all layers from the map."""
        pass
    
    @abstractmethod
    def get_widget(self) -> QWidget:
        """Get the Qt widget that displays the map.
        
        Returns:
            The Qt widget containing the map visualization
        """
        pass

class QtMapRenderer(MapRenderer):
    """Qt-native QGraphicsView implementation of MapRenderer.
    
    This is the default implementation using Qt's QGraphicsView for
    displaying geospatial data. It provides basic map functionality
    including CRS transformation, point rendering, and overlay display.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__()
        
        # Create the QGraphicsView and QGraphicsScene
        self._scene = QGraphicsScene()
        self._view = QGraphicsView(self._scene, parent)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Initialize state
        self._crs_manager = CRSManager()
        self._layers: Dict[str, Any] = {}
        self._overlays: Dict[str, Any] = {}
        self._zoom_factor = 1.2
        
        # Configure view
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        # Set up coordinate system
        self._setup_coordinate_system()
    
    def _setup_coordinate_system(self) -> None:
        """Set up the coordinate system for the map."""
        # Default to WGS84 (EPSG:4326)
        crs = pyproj.CRS.from_epsg(4326)
        self._crs_manager.set_crs(crs)
        
        # Configure scene coordinates
        self._scene.setSceneRect(-180, -90, 360, 180)
        self._view.setSceneRect(self._scene.sceneRect())
    
    def set_crs(self, crs: pyproj.CRS) -> None:
        """Set the coordinate reference system for the map."""
        self._crs_manager.set_crs(crs)
        # Note: In a full implementation, we would transform existing data
        # to the new CRS. For now, we just store the CRS.
    
    def add_point_layer(
        self,
        id: str,
        points: List[Point3D],
        style: PointStyle,
        source_crs: Optional[pyproj.CRS] = None,
    ) -> None:
        """Add a point layer to the map."""
        if not self._crs_manager.is_crs_set():
            raise RuntimeError("CRS not set. Call set_crs() first.")
        
        # Create QGraphicsItem for each point
        items = []
        for point in points:
            x, y, z = point
            if source_crs is not None:
                x, y, z = self._crs_manager.transform_point_3d((x, y, z), source_crs)
            
            # Create a simple circle item for the point
            from PyQt6.QtWidgets import QGraphicsEllipseItem
            
            # Convert to scene coordinates (simplified transformation)
            # In a real implementation, we would transform coordinates
            # from their source CRS to the map's CRS
            scene_x = x
            scene_y = y
            
            item = QGraphicsEllipseItem(
                scene_x - style.size / 2,
                scene_y - style.size / 2,
                style.size,
                style.size
            )
            
            # Set style
            pen = QPen(style.color, style.pen_width)
            brush = QBrush(style.color)
            item.setPen(pen)
            item.setBrush(brush)
            
            self._scene.addItem(item)
            items.append(item)
        
        # Store layer reference
        self._layers[id] = {
            'type': 'point_layer',
            'items': items,
            'style': style
        }
    
    def add_overlay(
        self,
        id: str,
        geometry: List[OverlayGeom],
        source_crs: Optional[pyproj.CRS] = None,
    ) -> None:
        """Add an overlay geometry layer to the map."""
        items = []
        
        for geom in geometry:
            if geom.geom_type == "line":
                from PyQt6.QtWidgets import QGraphicsLineItem
                
                for i in range(len(geom.points) - 1):
                    x1, y1, _ = geom.points[i]
                    x2, y2, _ = geom.points[i + 1]

                    if source_crs is not None:
                        x1, y1 = self._crs_manager.transform_point((x1, y1), source_crs)
                        x2, y2 = self._crs_manager.transform_point((x2, y2), source_crs)
                    
                    line = QGraphicsLineItem(int(x1), int(y1), int(x2), int(y2))
                    pen = QPen(geom.color, geom.pen_width)
                    line.setPen(pen)
                    
                    self._scene.addItem(line)
                    items.append(line)
                    
            elif geom.geom_type == "polygon":
                from PyQt6.QtWidgets import QGraphicsPolygonItem
                from PyQt6.QtGui import QPolygonF
                
                polygon_points = [QPointF(x, y) for x, y, _ in geom.points]
                if source_crs is not None:
                    polygon_points = [
                        QPointF(*self._crs_manager.transform_point((x, y), source_crs))
                        for x, y, _ in geom.points
                    ]
                polygon = QPolygonF(polygon_points)
                
                qpolygon = QGraphicsPolygonItem(polygon)
                pen = QPen(geom.color, geom.pen_width)
                brush = QBrush(geom.color, Qt.BrushStyle.Dense4Pattern)
                qpolygon.setPen(pen)
                qpolygon.setBrush(brush)
                
                self._scene.addItem(qpolygon)
                items.append(qpolygon)
        
        # Store overlay reference
        self._overlays[id] = {
            'type': 'overlay',
            'items': items,
            'geometry': geometry
        }
    
    def zoom_to_extents(self) -> None:
        """Zoom the map to show all data layers."""
        if not self._layers and not self._overlays:
            return
        
        # Calculate extents from all layers and overlays
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = float('-inf'), float('-inf')
        
        # Check point layers
        for layer_data in self._layers.values():
            # In a full implementation, we would track the actual points
            # For now, use a reasonable default
            min_x, min_y = -180, -90
            max_x, max_y = 180, 90
        
        # Check overlays
        for overlay_data in self._overlays.values():
            for geom in overlay_data['geometry']:
                for x, y, _ in geom.points:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
        
        # Apply zoom
        if min_x != float('inf'):
            margin = 0.1  # 10% margin
            width = max_x - min_x
            height = max_y - min_y
            
            scene_rect = QRectF(
                min_x - width * margin,
                min_y - height * margin,
                width * (1 + 2 * margin),
                height * (1 + 2 * margin)
            )
            
            self._view.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_in(self) -> None:
        """Zoom in the view."""
        self._view.scale(self._zoom_factor, self._zoom_factor)

    def zoom_out(self) -> None:
        """Zoom out the view."""
        factor = 1 / self._zoom_factor
        self._view.scale(factor, factor)
    
    def clear(self) -> None:
        """Clear all layers from the map."""
        # Remove all items from the scene
        self._scene.clear()
        
        # Clear layer and overlay references
        self._layers.clear()
        self._overlays.clear()
    
    def get_widget(self) -> QWidget:
        """Get the Qt widget that displays the map."""
        return self._view
        
    def get_crs(self) -> Optional[pyproj.CRS]:
        """Get the current coordinate reference system.
        
        Returns:
            The current CRS, or None if not set
        """
        return self._crs_manager.get_crs()
        
    def get_crs_info(self) -> dict:
        """Get information about the current CRS.
        
        Returns:
            Dictionary with CRS information, or empty dict if not set
        """
        return self._crs_manager.get_crs_info()
        
    def is_crs_set(self) -> bool:
        """Check if a CRS is currently set.
        
        Returns:
            True if CRS is set, False otherwise
        """
        return self._crs_manager.is_crs_set()

# Convenience function for creating map renderers
def create_map_renderer(backend: str = "qt") -> MapRenderer:
    """Create a map renderer with the specified backend.
    
    Args:
        backend: The backend to use (currently only "qt" is supported)
    
    Returns:
        A MapRenderer instance
    
    Raises:
        ValueError: If the backend is not supported
    """
    if backend.lower() == "qt":
        return QtMapRenderer()
    else:
        raise ValueError(f"Unsupported map renderer backend: {backend}")

class MapCanvas(QWidget):
    """Map canvas widget for displaying geospatial data.
    
    This widget provides a container for the map renderer and handles
    user interactions for map navigation.
    """
    
    def __init__(self, services: dict, renderer: MapRenderer):
        super().__init__()
        self.services = services
        self.renderer = renderer
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the map canvas user interface."""
        self.setWindowTitle("Map Canvas")
        self.setMinimumSize(800, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add the renderer's widget to the layout
        layout.addWidget(self.renderer.get_widget())
        
        # Add some basic controls
        controls = QHBoxLayout()
        
        zoom_in_button = QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.zoom_in)
        controls.addWidget(zoom_in_button)
        
        zoom_out_button = QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.zoom_out)
        controls.addWidget(zoom_out_button)
        
        zoom_extents_button = QPushButton("Zoom to Extents")
        zoom_extents_button.clicked.connect(self.zoom_to_extents)
        controls.addWidget(zoom_extents_button)
        
        layout.addLayout(controls)
    
    def zoom_in(self):
        """Zoom in the map."""
        if hasattr(self.renderer, 'zoom_in'):
            self.renderer.zoom_in()
    
    def zoom_out(self):
        """Zoom out the map."""
        if hasattr(self.renderer, 'zoom_out'):
            self.renderer.zoom_out()
    
    def zoom_to_extents(self):
        """Zoom to show all data."""
        if hasattr(self.renderer, 'zoom_to_extents'):
            self.renderer.zoom_to_extents()
    
    def load_project(self, project_name: str):
        """Load a project and display its data on the map."""
        # This would load project data and display it on the map
        # For now, just show a message
        print(f"Loading project: {project_name}")
        
        # Example: Add some sample data
        if self.services and 'ppk' in self.services:
            # Get PPK solutions from services
            solutions = self.services['ppk'].get_solutions()

            if solutions:
                # Convert solutions to points in WGS84 order (lon, lat, elev)
                points = [(sol.longitude, sol.latitude, sol.elevation) for sol in solutions]
                
                # Create point style
                from PyQt6.QtGui import QColor
                style = PointStyle(
                    color=QColor(255, 0, 0),
                    size=8.0,
                    pen_width=2.0
                )

                # Add point layer to map renderer
                self.renderer.add_point_layer(
                    "solutions",
                    points,
                    style,
                    source_crs=pyproj.CRS.from_epsg(4326),
                )

                # Zoom to extents
                self.renderer.zoom_to_extents()

    def load_dxf_overlay(self, import_result) -> None:
        """Render imported DXF entities on the map as overlays."""
        if not import_result or not getattr(import_result, "success", False):
            return

        from PyQt6.QtGui import QColor

        geometries = []
        for entity in getattr(import_result, "entities", []):
            points = list(getattr(entity, "points", []) or [])
            if len(points) < 2:
                continue

            geom_type = "polygon" if len(points) >= 4 and points[0][:2] == points[-1][:2] else "line"
            geometries.append(
                OverlayGeom(
                    geom_type=geom_type,
                    points=points,
                    color=QColor(64, 200, 255),
                    pen_width=2.0,
                )
            )

        if geometries:
            self.renderer.add_overlay(f"dxf:{getattr(import_result, 'file_path', 'import')}", geometries)
            self.renderer.zoom_to_extents()

    def load_kml_overlay(self, import_result) -> None:
        """Render imported KML/KMZ placemarks on the map."""
        if not import_result or not getattr(import_result, "success", False):
            return

        from PyQt6.QtGui import QColor

        point_layer = []
        geometries = []

        for placemark in getattr(import_result, "placemarks", []):
            coords = list(getattr(placemark, "coordinates", []) or [])
            if not coords:
                continue

            if len(coords) == 1:
                point_layer.extend(coords)
                continue

            geom_type = "polygon" if len(coords) >= 4 and coords[0][:2] == coords[-1][:2] else "line"
            geometries.append(
                OverlayGeom(
                    geom_type=geom_type,
                    points=coords,
                    color=QColor(120, 220, 120),
                    pen_width=2.0,
                )
            )

        if point_layer:
            style = PointStyle(color=QColor(120, 220, 120), size=7.0, pen_width=1.5)
            self.renderer.add_point_layer(
                f"kml-points:{getattr(import_result, 'file_path', 'import')}",
                point_layer,
                style,
            )

        if point_layer and not geometries:
            self.renderer.zoom_to_extents()

        if geometries:
            self.renderer.add_overlay(f"kml:{getattr(import_result, 'file_path', 'import')}", geometries)
            self.renderer.zoom_to_extents()
    
    def get_widget(self) -> QWidget:
        """Get the Qt widget that displays the map."""
        return self

    def export_png(self, file_path: str) -> bool:
        """Export the current map view to a PNG file."""
        return self.renderer.get_widget().grab().save(file_path, "PNG")
        
    def get_crs(self) -> Optional[pyproj.CRS]:
        """Get the current coordinate reference system.
        
        Returns:
            The current CRS, or None if not set
        """
        return self.renderer.get_crs()
        
    def get_crs_info(self) -> dict:
        """Get information about the current CRS.
        
        Returns:
            Dictionary with CRS information, or empty dict if not set
        """
        return self.renderer.get_crs_info()
        
    def is_crs_set(self) -> bool:
        """Check if a CRS is currently set.
        
        Returns:
            True if CRS is set, False otherwise
        """
        return self.renderer.is_crs_set()

__all__ = [
    'MapRenderer',
    'QtMapRenderer',
    'PointStyle',
    'OverlayGeom',
    'create_map_renderer',
    'MapCanvas',
    'CRSManager',
    'set_crs',
    'get_crs',
    'transform_point',
    'transform_point_3d',
    'is_crs_set',
    'get_crs_info',
    'Point2D',
    'Point3D',
]
