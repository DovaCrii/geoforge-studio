"""CSV exporter for GeoForge Studio volume results.

This module provides CSV export functionality for volume analysis results.
"""

import csv
import os
from datetime import datetime
from typing import Dict, Any, Union
from src.volume.calculator import CutFillResult

class CSVExporter:
    """CSV exporter for volume analysis results."""
    
    def __init__(self, default_directory: str = "."):
        """Initialize CSV exporter.
        
        Args:
            default_directory: Default directory for saving CSV files
        """
        self.default_directory = default_directory
    
    def export_cut_fill_result(self, result: CutFillResult, filename: str = None) -> str:
        """Export CutFillResult to CSV file.
        
        Args:
            result: CutFillResult object containing volume data
            filename: Output filename (defaults to timestamped name)
            
        Returns:
            Path to the saved CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"volume_results_{timestamp}.csv"
        
        filepath = os.path.join(self.default_directory, filename)
        
        # Prepare data for CSV export
        data = [
            ["Metric", "Value", "Unit", "Status"],
            ["Total Volume", f"{result.total_cut + result.total_fill:.3f}", "m³", "✓"],
            ["Cut Volume", f"{result.total_cut:.3f}", "m³", "✓"],
            ["Fill Volume", f"{result.total_fill:.3f}", "m³", "✓"],
            ["Net Volume", f"{result.net_volume:.3f}", "m³", "✓"],
            ["Surface Area", f"{result.surface_area:.3f}", "m²", "✓"],
            ["Grid Cells", str(result.triangles_processed), "", "✓"],
            ["Processing Time", "0.00", "s", "✓"],
            ["Status", "Balanced" if result.is_balanced else "Unbalanced", "", "✓"],
            ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", "✓"]
        ]
        
        # Write to CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        
        return filepath
    
    def export_table_data(self, table_data: Dict[str, Any], filename: str = None) -> str:
        """Export table data to CSV file.
        
        Args:
            table_data: Dictionary containing table data
            filename: Output filename (defaults to timestamped name)
            
        Returns:
            Path to the saved CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"volume_table_{timestamp}.csv"
        
        filepath = os.path.join(self.default_directory, filename)
        
        # Convert table data to CSV format
        # This assumes table_data has a structure similar to what VolumePanel uses
        rows = []
        
        # Add header
        if "headers" in table_data:
            rows.append(table_data["headers"])
        
        # Add data rows
        if "data" in table_data:
            for row in table_data["data"]:
                rows.append(row)
        
        # Write to CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
        
        return filepath

# Convenience functions
def export_volume_results(result: CutFillResult, directory: str = ".") -> str:
    """Export volume results to CSV file.
    
    Args:
        result: CutFillResult object containing volume data
        directory: Directory to save the CSV file
        
    Returns:
        Path to the saved CSV file
    """
    exporter = CSVExporter(default_directory=directory)
    return exporter.export_cut_fill_result(result)

# Export public API
__all__ = [
    'CSVExporter',
    'export_volume_results',
]