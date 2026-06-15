"""Coordinate Reference System utilities for GeoForge Studio.

This module provides CRS transformation utilities using pyproj,
enabling coordinate reprojection between different CRS systems.
"""

from typing import Tuple, Optional
import pyproj
from pyproj.exceptions import CRSError

# Type aliases for better readability
Point2D = Tuple[float, float]
Point3D = Tuple[float, float, float]

class CRSManager:
    """Manages coordinate reference system transformations.
    
    This class provides a clean API for setting, querying, and transforming
    coordinates between different CRS systems using pyproj.
    """
    
    def __init__(self):
        self._crs: Optional[pyproj.CRS] = None
        self._transformer: Optional[pyproj.Transformer] = None
        
    def set_crs(self, crs: pyproj.CRS) -> None:
        """Set the coordinate reference system for transformations.
        
        Args:
            crs: The coordinate reference system to use
            
        Raises:
            CRSError: If the CRS is invalid
        """
        if not isinstance(crs, pyproj.CRS):
            raise TypeError(f"Expected pyproj.CRS, got {type(crs)}")
            
        self._crs = crs
        self._transformer = None  # Reset transformer
        
    def get_crs(self) -> Optional[pyproj.CRS]:
        """Get the current coordinate reference system.
        
        Returns:
            The current CRS, or None if not set
        """
        return self._crs
        
    def transform_point(self, point: Point2D, source_crs: pyproj.CRS) -> Point2D:
        """Transform a 2D point from source CRS to the current CRS.
        
        Args:
            point: The point to transform (x, y)
            source_crs: The source coordinate reference system
            
        Returns:
            Transformed point (x, y) in the current CRS
            
        Raises:
            ValueError: If CRS is not set or transformation fails
        """
        if self._crs is None:
            raise ValueError("CRS not set. Call set_crs() first.")
            
        if self._crs == source_crs:
            return point
            
        try:
            transformer = pyproj.Transformer.from_crs(
                source_crs, self._crs, always_xy=True
            )
            x, y = transformer.transform(point[0], point[1])
            return (x, y)
        except Exception as e:
            raise ValueError(f"Failed to transform point: {e}")
            
    def transform_point_3d(self, point: Point3D, source_crs: pyproj.CRS) -> Point3D:
        """Transform a 3D point from source CRS to the current CRS.
        
        Args:
            point: The point to transform (x, y, z)
            source_crs: The source coordinate reference system
            
        Returns:
            Transformed point (x, y, z) in the current CRS
            
        Raises:
            ValueError: If CRS is not set or transformation fails
        """
        if self._crs is None:
            raise ValueError("CRS not set. Call set_crs() first.")
            
        if self._crs == source_crs:
            return point
            
        try:
            transformer = pyproj.Transformer.from_crs(
                source_crs, self._crs, always_xy=True
            )
            x, y, z = transformer.transform(point[0], point[1], point[2])
            return (x, y, z)
        except Exception as e:
            raise ValueError(f"Failed to transform 3D point: {e}")
            
    def transform_points(self, points: list[Point2D], source_crs: pyproj.CRS) -> list[Point2D]:
        """Transform multiple 2D points from source CRS to the current CRS.
        
        Args:
            points: List of points to transform
            source_crs: The source coordinate reference system
            
        Returns:
            List of transformed points
        """
        return [self.transform_point(point, source_crs) for point in points]
        
    def transform_points_3d(self, points: list[Point3D], source_crs: pyproj.CRS) -> list[Point3D]:
        """Transform multiple 3D points from source CRS to the current CRS.
        
        Args:
            points: List of points to transform
            source_crs: The source coordinate reference system
            
        Returns:
            List of transformed points
        """
        return [self.transform_point_3d(point, source_crs) for point in points]
        
    def is_crs_set(self) -> bool:
        """Check if a CRS is currently set.
        
        Returns:
            True if CRS is set, False otherwise
        """
        return self._crs is not None
        
    def get_crs_info(self) -> dict:
        """Get information about the current CRS.
        
        Returns:
            Dictionary with CRS information, or empty dict if not set
        """
        if self._crs is None:
            return {}
            
        return {
            "name": self._crs.name,
            "authority": self._crs.to_authority(),
            "coordinate_system": self._crs.coordinate_system.name,
            "area": self._crs.area_of_use.name if self._crs.area_of_use else None,
        }

# Global CRS manager instance for backward compatibility
_crs_manager = CRSManager()

# Convenience functions for backward compatibility
def set_crs(crs: pyproj.CRS) -> None:
    """Set the global CRS for coordinate transformations.
    
    Args:
        crs: The coordinate reference system to use
    """
    _crs_manager.set_crs(crs)
    

def get_crs() -> Optional[pyproj.CRS]:
    """Get the current global CRS.
    
    Returns:
        The current CRS, or None if not set
    """
    return _crs_manager.get_crs()
    

def transform_point(point: Point2D, source_crs: pyproj.CRS) -> Point2D:
    """Transform a 2D point from source CRS to the current CRS.
    
    Args:
        point: The point to transform (x, y)
        source_crs: The source coordinate reference system
        
    Returns:
        Transformed point (x, y) in the current CRS
    """
    return _crs_manager.transform_point(point, source_crs)
    

def transform_point_3d(point: Point3D, source_crs: pyproj.CRS) -> Point3D:
    """Transform a 3D point from source CRS to the current CRS.
    
    Args:
        point: The point to transform (x, y, z)
        source_crs: The source coordinate reference system
        
    Returns:
        Transformed point (x, y, z) in the current CRS
    """
    return _crs_manager.transform_point_3d(point, source_crs)
    

def is_crs_set() -> bool:
    """Check if a CRS is currently set.
    
    Returns:
        True if CRS is set, False otherwise
    """
    return _crs_manager.is_crs_set()
    

def get_crs_info() -> dict:
    """Get information about the current CRS.
    
    Returns:
        Dictionary with CRS information, or empty dict if not set
    """
    return _crs_manager.get_crs_info()

__all__ = [
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