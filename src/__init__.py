from __future__ import annotations

"""GeoForge Studio - GNSS Processing and Geospatial Analysis Tool

This package provides a complete solution for GNSS data processing,
geospatial visualization, and volume computation.
"""

__version__ = "0.1.0"
__author__ = "GeoForge Studio Team"
__email__ = "team@geoforge.studio"

from .volume import (
    SurveyPoint,
    Triangle,
    TINSurface,
    create_tin_from_points,
    create_sample_tin,
)

__all__ = [
    "SurveyPoint",
    "Triangle",
    "TINSurface",
    "create_tin_from_points",
    "create_sample_tin",
]
