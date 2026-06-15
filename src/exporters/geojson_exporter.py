"""GeoJSON exporter for GeoForge Studio.

This module exports project survey points to a GeoJSON FeatureCollection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from services.project_service import Project, SurveyPoint


class GeoJSONExporter:
    """Export project data to GeoJSON."""

    def export_project_points(self, project: "Project", file_path: str) -> str:
        """Export survey points as GeoJSON FeatureCollection."""
        features = [self._point_to_feature(point) for point in project.points]

        geojson = {
            "type": "FeatureCollection",
            "name": project.name,
            "features": features,
            "properties": {
                "project_path": project.path,
                "point_count": len(project.points),
            },
        }

        output = Path(file_path)
        if output.suffix.lower() != ".geojson":
            output = output.with_suffix(".geojson")

        output.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
        return str(output)

    def _point_to_feature(self, point: "SurveyPoint") -> Dict[str, Any]:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [point.x, point.y, point.z],
            },
            "properties": {
                "id": point.id,
                "name": point.name,
                "crs": point.crs,
                "remarks": point.remarks,
            },
        }


def export_project_points_geojson(project: "Project", file_path: str) -> str:
    """Convenience function to export project points as GeoJSON."""
    return GeoJSONExporter().export_project_points(project, file_path)


__all__ = ["GeoJSONExporter", "export_project_points_geojson"]
