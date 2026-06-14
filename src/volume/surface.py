"""Volume computation module for GeoForge Studio.

This module provides TIN surface generation and volume computation capabilities
for survey points and terrain modeling.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from scipy.spatial import Delaunay

@dataclass
class SurveyPoint:
    """Represents a survey point with 3D coordinates."""
    x: float
    y: float
    z: float
    id: Optional[str] = None
    name: Optional[str] = None

    def to_array(self) -> np.ndarray:
        """Convert to numpy array for computation."""
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_array(cls, arr: np.ndarray, id: Optional[str] = None, name: Optional[str] = None) -> 'SurveyPoint':
        """Create from numpy array."""
        return cls(arr[0], arr[1], arr[2], id, name)

@dataclass
class Triangle:
    """Represents a triangular facet in a TIN surface."""
    vertices: Tuple[SurveyPoint, SurveyPoint, SurveyPoint]
    id: Optional[str] = None

    @property
    def area(self) -> float:
        """Calculate triangle area in the XY plane."""
        v1, v2, v3 = self.vertices
        return 0.5 * abs((v2.x - v1.x) * (v3.y - v1.y) - (v3.x - v1.x) * (v2.y - v1.y))

    @property
    def volume(self) -> float:
        """Calculate triangle volume (area * average Z)."""
        v1, v2, v3 = self.vertices
        avg_z = (v1.z + v2.z + v3.z) / 3.0
        return self.area * avg_z

    @property
    def centroid(self) -> Tuple[float, float, float]:
        """Calculate triangle centroid."""
        v1, v2, v3 = self.vertices
        return (
            (v1.x + v2.x + v3.x) / 3.0,
            (v1.y + v2.y + v3.y) / 3.0,
            (v1.z + v2.z + v3.z) / 3.0
        )

class TINSurface:
    """TIN (Triangulated Irregular Network) surface representation."""

    def __init__(self, points: List[SurveyPoint]):
        """Create TIN surface from survey points.

        Args:
            points: List of survey points with 3D coordinates
        """
        if len(points) < 3:
            raise ValueError("At least 3 points required for TIN surface")

        self.points = points
        self.triangles = self._generate_triangulation()

    def _generate_triangulation(self) -> List[Triangle]:
        """Generate Delaunay triangulation from points."""
        # Extract XY coordinates for triangulation
        xy_coords = np.array([(p.x, p.y) for p in self.points])

        # Generate Delaunay triangulation
        tri = Delaunay(xy_coords)

        # Create triangle objects
        triangles = []
        for i, simplex in enumerate(tri.simplices):
            triangle_points = (
                self.points[simplex[0]],
                self.points[simplex[1]],
                self.points[simplex[2]]
            )
            triangle = Triangle(triangle_points, id=f"tri_{i}")
            triangles.append(triangle)

        return triangles

    def get_total_area(self) -> float:
        """Calculate total surface area."""
        return sum(triangle.area for triangle in self.triangles)

    def get_total_volume(self) -> float:
        """Calculate total volume under the surface."""
        return sum(triangle.volume for triangle in self.triangles)

    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box (min_x, min_y, max_x, max_y)."""
        if not self.points:
            return (0.0, 0.0, 0.0, 0.0)

        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]

        return (min(xs), min(ys), max(xs), max(ys))

    def get_statistics(self) -> dict:
        """Get surface statistics."""
        areas = [t.area for t in self.triangles]
        volumes = [t.volume for t in self.triangles]

        return {
            "num_points": len(self.points),
            "num_triangles": len(self.triangles),
            "total_area": sum(areas),
            "total_volume": sum(volumes),
            "avg_triangle_area": np.mean(areas) if areas else 0.0,
            "avg_triangle_volume": np.mean(volumes) if volumes else 0.0,
            "bounding_box": self.get_bounding_box(),
        }

    def add_point(self, point: SurveyPoint) -> None:
        """Add a new point to the surface and regenerate triangulation."""
        self.points.append(point)
        self.triangles = self._generate_triangulation()

    def remove_point(self, point_id: str) -> bool:
        """Remove a point by ID and regenerate triangulation."""
        original_count = len(self.points)
        self.points = [p for p in self.points if p.id != point_id]

        if len(self.points) < 3:
            # Restore if we don't have enough points
            self.points = self.points[:original_count]
            return False

        self.triangles = self._generate_triangulation()
        return True

    def get_point_by_id(self, point_id: str) -> Optional[SurveyPoint]:
        """Get a point by its ID."""
        for point in self.points:
            if point.id == point_id:
                return point
        return None

    def get_triangles_by_area(self, min_area: float = 0.0) -> List[Triangle]:
        """Get triangles with area greater than or equal to min_area."""
        return [t for t in self.triangles if t.area >= min_area]

    def get_triangles_by_volume(self, min_volume: float = 0.0) -> List[Triangle]:
        """Get triangles with volume greater than or equal to min_volume."""
        return [t for t in self.triangles if t.volume >= min_volume]

    def export_to_dict(self) -> dict:
        """Export surface data to dictionary."""
        return {
            "points": [
                {
                    "x": p.x,
                    "y": p.y,
                    "z": p.z,
                    "id": p.id,
                    "name": p.name,
                }
                for p in self.points
            ],
            "triangles": [
                {
                    "vertices": [
                        {"x": v.x, "y": v.y, "z": v.z, "id": v.id}
                        for v in triangle.vertices
                    ],
                    "id": triangle.id,
                }
                for triangle in self.triangles
            ],
            "statistics": self.get_statistics(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'TINSurface':
        """Create TIN surface from dictionary."""
        points = []
        for point_data in data["points"]:
            point = SurveyPoint(
                x=point_data["x"],
                y=point_data["y"],
                z=point_data["z"],
                id=point_data.get("id"),
                name=point_data.get("name"),
            )
            points.append(point)

        surface = cls(points)

        # Restore triangle IDs
        for i, triangle_data in enumerate(data["triangles"]):
            vertices = []
            for vertex_data in triangle_data["vertices"]:
                vertex = SurveyPoint(
                    x=vertex_data["x"],
                    y=vertex_data["y"],
                    z=vertex_data["z"],
                    id=vertex_data.get("id"),
                )
                vertices.append(vertex)

            surface.triangles[i].id = triangle_data.get("id", f"tri_{i}")

        return surface

    def __str__(self) -> str:
        """String representation of the surface."""
        stats = self.get_statistics()
        return (f"TINSurface(points={stats['num_points']}, "
                f"triangles={stats['num_triangles']}, "
                f"area={stats['total_area']:.2f} m²)")

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"TINSurface(points={len(self.points)}, triangles={len(self.triangles)})"

# Convenience functions for common TIN operations
def create_tin_from_points(points: List[SurveyPoint]) -> TINSurface:
    """Create TIN surface from list of survey points."""
    return TINSurface(points)

def create_sample_tin() -> TINSurface:
    """Create a sample TIN surface for testing."""
    points = [
        SurveyPoint(0.0, 0.0, 0.0, id="p1", name="Point 1"),
        SurveyPoint(10.0, 0.0, 5.0, id="p2", name="Point 2"),
        SurveyPoint(0.0, 10.0, 3.0, id="p3", name="Point 3"),
        SurveyPoint(10.0, 10.0, 8.0, id="p4", name="Point 4"),
        SurveyPoint(5.0, 5.0, 2.0, id="p5", name="Point 5"),
    ]
    return TINSurface(points)

# Export public API
__all__ = [
    'SurveyPoint',
    'Triangle',
    'TINSurface',
    'create_tin_from_points',
    'create_sample_tin',
]