"""Volume renderer for GeoForge Studio.

This module provides basic volume visualization capabilities for the display pipeline.
It can render cut/fill volume data as simple text-based visualizations or prepare
for more advanced graphical representations.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from src.volume.calculator import CutFillResult

@dataclass
class VolumeVisualization:
    """Represents a volume visualization."""
    title: str
    data: str
    metadata: dict
    timestamp: float

class VolumeRenderer:
    """Basic volume renderer for display pipeline.
    
    This renderer provides minimal visualization capabilities for volume data,
    suitable for integration with the existing UI components.
    """
    
    def __init__(self):
        self._last_visualization: Optional[VolumeVisualization] = None
    
    def render_cut_fill(self, result: CutFillResult) -> VolumeVisualization:
        """Render cut/fill volume data as visualization.
        
        Args:
            result: CutFillResult containing volume data
            
        Returns:
            VolumeVisualization object with rendered data
        """
        # Create simple text-based visualization
        lines = []
        lines.append(f"=== Volume Analysis ===")
        lines.append(f"Cut Volume: {result.total_cut:.2f} m³")
        lines.append(f"Fill Volume: {result.total_fill:.2f} m³")
        lines.append(f"Net Volume: {result.net_volume:.2f} m³")
        lines.append(f"Surface Area: {result.surface_area:.2f} m²")
        lines.append(f"Triangles Processed: {result.triangles_processed}")
        lines.append(f"Status: {'Balanced' if result.is_balanced else 'Unbalanced'}")
        
        data = "\n".join(lines)
        
        visualization = VolumeVisualization(
            title="Cut/Fill Volume Analysis",
            data=data,
            metadata={
                "cut_volume": result.total_cut,
                "fill_volume": result.total_fill,
                "net_volume": result.net_volume,
                "surface_area": result.surface_area,
                "is_balanced": result.is_balanced,
                "has_cut_fill": result.has_cut_fill,
            },
            timestamp=0.0  # Would use time.time() in real implementation
        )
        
        self._last_visualization = visualization
        return visualization
    
    def get_last_visualization(self) -> Optional[VolumeVisualization]:
        """Get the last rendered visualization."""
        return self._last_visualization
    
    def clear(self) -> None:
        """Clear the last visualization."""
        self._last_visualization = None

# Convenience functions
def create_volume_renderer() -> VolumeRenderer:
    """Create a volume renderer instance."""
    return VolumeRenderer()

# Export public API
__all__ = [
    'VolumeVisualization',
    'VolumeRenderer',
    'create_volume_renderer',
]