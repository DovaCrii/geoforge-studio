"""Cut/fill volume calculator for GeoForge Studio.

This module provides calculations for cut and fill volumes based on TIN surface data.
Cut volume represents material to be removed, fill volume represents material to be added.
"""

from dataclasses import dataclass
from typing import List, Optional
from .surface import SurveyPoint, Triangle, TINSurface

@dataclass
class CutFillResult:
    """Result of cut/fill volume calculations."""
    total_cut: float
    total_fill: float
    net_volume: float
    surface_area: float
    bounding_box: tuple[float, float, float, float]
    triangles_processed: int
    
    @property
    def has_cut_fill(self) -> bool:
        """Check if there are any cut or fill volumes."""
        return self.total_cut > 0 or self.total_fill > 0
    
    @property
    def is_balanced(self) -> bool:
        """Check if cut and fill volumes are balanced."""
        return abs(self.total_cut - self.total_fill) < 0.001

class CutFillCalculator:
    """Calculator for cut and fill volumes from TIN surfaces."""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """Reset calculator state."""
        self._cut_volume = 0.0
        self._fill_volume = 0.0
        self._surface_area = 0.0
        self._bounding_box = (0.0, 0.0, 0.0, 0.0)
        self._triangles_processed = 0
    
    def calculate(self, surface: TINSurface) -> CutFillResult:
        """Calculate cut and fill volumes from a TIN surface.
        
        Args:
            surface: TIN surface with survey points
            
        Returns:
            CutFillResult containing calculated volumes and statistics
        """
        self.reset()
        
        # Get surface statistics
        stats = surface.get_statistics()
        self._surface_area = stats["total_area"]
        self._bounding_box = stats["bounding_box"]
        self._triangles_processed = stats["num_triangles"]
        
        # Calculate cut and fill volumes
        for triangle in surface.triangles:
            triangle_volume = triangle.volume
            
            if triangle_volume > 0:
                # Positive volume = fill (material to add)
                self._fill_volume += triangle_volume
            elif triangle_volume < 0:
                # Negative volume = cut (material to remove)
                self._cut_volume += abs(triangle_volume)
        
        net_volume = self._fill_volume - self._cut_volume
        
        return CutFillResult(
            total_cut=self._cut_volume,
            total_fill=self._fill_volume,
            net_volume=net_volume,
            surface_area=self._surface_area,
            bounding_box=self._bounding_box,
            triangles_processed=self._triangles_processed
        )
    
    def get_cut_volume(self) -> float:
        """Get total cut volume."""
        return self._cut_volume
    
    def get_fill_volume(self) -> float:
        """Get total fill volume."""
        return self._fill_volume
    
    def get_net_volume(self) -> float:
        """Get net volume (fill - cut)."""
        return self._fill_volume - self._cut_volume

# Convenience functions
def calculate_cut_fill(surface: TINSurface) -> CutFillResult:
    """Convenience function to calculate cut/fill volumes."""
    calculator = CutFillCalculator()
    return calculator.calculate(surface)

def format_volume(value: float) -> str:
    """Format volume value for display."""
    if abs(value) < 0.001:
        return "0.00"
    elif abs(value) < 1.0:
        return f"{value:.3f}"
    else:
        return f"{value:.2f}"

# Export public API
__all__ = [
    'CutFillResult',
    'CutFillCalculator',
    'calculate_cut_fill',
    'format_volume',
]
