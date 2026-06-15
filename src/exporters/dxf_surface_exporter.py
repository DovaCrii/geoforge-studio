"""DXF surface exporter for GeoForge Studio.

This module exports TIN surfaces as DXF 3DFACE entities.
"""

from __future__ import annotations

from pathlib import Path

import ezdxf

from volume.surface import TINSurface


class DXFSurfaceExporter:
    """Export TIN surfaces to DXF."""

    def export_surface(self, surface: TINSurface, file_path: str) -> str:
        """Export a TIN surface as DXF 3DFACE entities."""
        output = Path(file_path)
        if output.suffix.lower() != ".dxf":
            output = output.with_suffix(".dxf")

        doc = ezdxf.new(setup=True)
        msp = doc.modelspace()

        for triangle in surface.triangles:
            v1, v2, v3 = triangle.vertices
            msp.add_3dface(
                [
                    (v1.x, v1.y, v1.z),
                    (v2.x, v2.y, v2.z),
                    (v3.x, v3.y, v3.z),
                    (v3.x, v3.y, v3.z),
                ]
            )

        doc.saveas(output)
        return str(output)


def export_tin_surface_dxf(surface: TINSurface, file_path: str) -> str:
    """Convenience function to export a TIN surface to DXF."""
    return DXFSurfaceExporter().export_surface(surface, file_path)


__all__ = ["DXFSurfaceExporter", "export_tin_surface_dxf"]
