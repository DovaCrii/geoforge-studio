#!/usr/bin/env python3
"""Test GeoJSON export functionality for GeoForge Studio."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> int:
    from services.project_service import Project, SurveyPoint
    from exporters.geojson_exporter import export_project_points_geojson

    project = Project(
        name="GeoJSON Test",
        path="/tmp/geoforge-test.gfp",
        points=[
            SurveyPoint(id="P1", name="Point 1", x=1.0, y=2.0, z=3.0, crs="EPSG:4326"),
            SurveyPoint(id="P2", name="Point 2", x=4.0, y=5.0, z=6.0, crs="EPSG:4326"),
        ],
    )

    out = Path("/tmp/geoforge-test.geojson")
    saved = export_project_points_geojson(project, str(out))
    data = json.loads(Path(saved).read_text(encoding="utf-8"))

    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2
    assert data["features"][0]["properties"]["id"] == "P1"

    print(f"GeoJSON export OK: {saved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
