#!/usr/bin/env python3
"""Test DXF surface export functionality for GeoForge Studio."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> int:
    from services.project_service import Project, SurveyPoint
    from volume.surface import create_tin_from_points
    from exporters.dxf_surface_exporter import export_tin_surface_dxf

    project = Project(
        name="Surface Test",
        path="/tmp/geoforge-surface.gfp",
        points=[
            SurveyPoint(id="P1", name="Point 1", x=0.0, y=0.0, z=0.0),
            SurveyPoint(id="P2", name="Point 2", x=10.0, y=0.0, z=2.0),
            SurveyPoint(id="P3", name="Point 3", x=0.0, y=10.0, z=1.0),
            SurveyPoint(id="P4", name="Point 4", x=10.0, y=10.0, z=3.0),
        ],
    )

    surface = create_tin_from_points(project.points)
    out = export_tin_surface_dxf(surface, "/tmp/geoforge-surface.dxf")

    assert Path(out).exists()
    print(f"DXF surface export OK: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
