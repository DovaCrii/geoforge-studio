"""Contour line generation from TIN surfaces.

Generates elevation contour lines (isolines) from a TIN surface by
interpolating across triangle edges at specified elevation intervals.
"""

from typing import List, Tuple, Optional
from .surface import TINSurface, SurveyPoint, Triangle


def _interpolate_edge(
    p1: SurveyPoint, p2: SurveyPoint, z: float
) -> Tuple[float, float]:
    """Linearly interpolate the point on edge p1-p2 at elevation z.

    Args:
        p1: First endpoint
        p2: Second endpoint
        z: Target elevation

    Returns:
        (x, y) coordinates of the interpolated point
    """
    if abs(p2.z - p1.z) < 1e-12:
        return ((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    t = (z - p1.z) / (p2.z - p1.z)
    t = max(0.0, min(1.0, t))
    return (p1.x + t * (p2.x - p1.x), p1.y + t * (p2.y - p1.y))


def _triangle_contour_segments(
    triangle: Triangle, z: float
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Extract contour segments at elevation z from a single triangle.

    For each edge that crosses the contour level, interpolate the crossing point.
    A triangle can have 0 or 2 crossing edges (1 crossing is degenerate).

    Returns:
        List of ((x1,y1), (x2,y2)) segments
    """
    v0, v1, v2 = triangle.vertices
    edges = [(v0, v1), (v1, v2), (v2, v0)]

    crossings = []
    for a, b in edges:
        if (a.z - z) * (b.z - z) <= 0 and abs(a.z - b.z) > 1e-12:
            crossings.append(_interpolate_edge(a, b, z))

    if len(crossings) >= 2:
        return [(tuple(crossings[0]), tuple(crossings[1]))]
    return []


def generate_contours(
    surface: TINSurface,
    interval: float = 1.0,
    z_min: Optional[float] = None,
    z_max: Optional[float] = None,
) -> List[dict]:
    """Generate contour lines from a TIN surface.

    Args:
        surface: TIN surface to extract contours from
        interval: Elevation interval between contour lines (default: 1.0)
        z_min: Minimum elevation (default: auto from surface)
        z_max: Maximum elevation (default: auto from surface)

    Returns:
        List of contour dicts::
            {"elevation": float, "segments": [((x1,y1),(x2,y2)), ...], "closed": bool}
    """
    if not surface.points or not surface.triangles:
        return []

    elevations = [p.z for p in surface.points]
    if z_min is None:
        z_min = min(elevations)
    if z_max is None:
        z_max = max(elevations)

    # Round to interval
    z_min = (z_min // interval) * interval
    z_max = (z_max // interval) * interval + interval

    contours = []
    z = z_min
    while z <= z_max:
        segments = []
        for triangle in surface.triangles:
            segs = _triangle_contour_segments(triangle, z)
            segments.extend(segs)

        contours.append({
            "elevation": round(z, 6),
            "segments": segments,
        })
        z += interval

    return contours


def contour_stats(contours: List[dict]) -> dict:
    """Return statistics about generated contours.

    Args:
        contours: Output from generate_contours()

    Returns:
        Dict with count, min/max elevation, total segments
    """
    if not contours:
        return {"count": 0, "min_elevation": 0, "max_elevation": 0, "total_segments": 0}

    elevations = [c["elevation"] for c in contours if c["segments"]]
    total_segments = sum(len(c["segments"]) for c in contours)

    return {
        "count": len([c for c in contours if c["segments"]]),
        "min_elevation": min(elevations) if elevations else 0,
        "max_elevation": max(elevations) if elevations else 0,
        "total_segments": total_segments,
    }


def contours_to_overlay_geoms(
    contours: List[dict],
    major_interval: int = 5,
) -> List[dict]:
    """Convert contour data to overlay geometry dicts for map rendering.

    Args:
        contours: Output from generate_contours()
        major_interval: Every Nth contour is a major (bolder) line

    Returns:
        List of {"segments": ..., "elevation": ..., "is_major": bool}
    """
    result = []
    for contour in contours:
        if not contour["segments"]:
            continue
        is_major = (int(contour["elevation"]) % major_interval) == 0
        result.append({
            "segments": contour["segments"],
            "elevation": contour["elevation"],
            "is_major": bool(is_major),
        })
    return result


__all__ = [
    "generate_contours",
    "contour_stats",
    "contours_to_overlay_geoms",
]
