"""Volume panel for GeoForge Studio application.

This module provides the volume analysis panel for displaying
volume computation results and visualizations.
"""

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from src.volume.calculator import CutFillResult, format_volume
from src.volume.csv_exporter import CSVExporter

class VolumePanel(QWidget):
    """Volume analysis panel for displaying volume computation results.
    
    This panel provides a clean, minimal interface for displaying
    volume analysis results including cut/fill calculations and
    surface statistics.
    """
    
    def __init__(self, services: dict):
        super().__init__()
        self.services = services
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the volume panel user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title label
        title_label = QLabel("📊 Volume Analysis")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Metric", "Value", "Status"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Start with a calm empty state
        self.results_table.setRowCount(1)
        self._populate_empty_state()
        
        layout.addWidget(self.results_table)
        
        # Export button
        export_button = QPushButton("📤 Export CSV")
        export_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6091;
            }
        """)
        export_button.clicked.connect(self.export_csv)
        layout.addWidget(export_button)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    def _populate_empty_state(self):
        """Populate the table with an empty-state row."""
        sample_data = [
            ("Status", "No volume results yet", "—"),
        ]
        
        for row, (metric, value, status) in enumerate(sample_data):
            self.results_table.setItem(row, 0, QTableWidgetItem(metric))
            self.results_table.setItem(row, 1, QTableWidgetItem(value))
            self.results_table.setItem(row, 2, QTableWidgetItem(status))
            
            # Style the status column
            item = self.results_table.item(row, 2)
            if status == "✓":
                item.setForeground(Qt.GlobalColor.darkGreen)
            elif status == "⚠":
                item.setForeground(Qt.GlobalColor.orange)
            else:
                item.setForeground(Qt.GlobalColor.red)
                
    def update_results(self, results: dict):
        """Update the volume analysis results.
        
        Args:
            results: Dictionary containing volume analysis results
                    Can be CutFillResult or dict with volume data
        """
        # Clear existing results
        self.clear_results()
        
        # Handle CutFillResult object
        if hasattr(results, 'total_cut') and hasattr(results, 'total_fill'):
            cut_fill_result: CutFillResult = results
            
            # Update table with cut/fill data
            row = 0
            self.results_table.setItem(row, 0, QTableWidgetItem("Total Volume"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{format_volume(cut_fill_result.total_cut + cut_fill_result.total_fill)} m³"))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Cut Volume"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{format_volume(cut_fill_result.total_cut)} m³"))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Fill Volume"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{format_volume(cut_fill_result.total_fill)} m³"))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Net Volume"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{format_volume(cut_fill_result.net_volume)} m³"))
            status = "✓" if cut_fill_result.is_balanced else ("⚠" if cut_fill_result.has_cut_fill else "✓")
            self.results_table.setItem(row, 2, QTableWidgetItem(status))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Surface Area"))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{format_volume(cut_fill_result.surface_area)} m²"))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Grid Cells"))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(cut_fill_result.triangles_processed)))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Processing Time"))
            self.results_table.setItem(row, 1, QTableWidgetItem("0.00s"))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            row += 1
            
            self.results_table.setItem(row, 0, QTableWidgetItem("Status"))
            status_text = "Balanced" if cut_fill_result.is_balanced else "Unbalanced"
            self.results_table.setItem(row, 1, QTableWidgetItem(status_text))
            self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
            
        # Handle dictionary results (backward compatibility)
        elif isinstance(results, dict):
            # Map dictionary keys to table rows
            mapping = {
                "total_volume": ("Total Volume", "m³"),
                "cut_volume": ("Cut Volume", "m³"),
                "fill_volume": ("Fill Volume", "m³"),
                "net_volume": ("Net Volume", "m³"),
                "surface_area": ("Surface Area", "m²"),
                "triangles_processed": ("Grid Cells", ""),
                "processing_time": ("Processing Time", "s"),
                "status": ("Status", "")
            }
            
            row = 0
            for key, (metric, unit) in mapping.items():
                if key in results:
                    value = results[key]
                    if unit:
                        value_str = f"{value} {unit}"
                    else:
                        value_str = str(value)
                    
                    self.results_table.setItem(row, 0, QTableWidgetItem(metric))
                    self.results_table.setItem(row, 1, QTableWidgetItem(value_str))
                    self.results_table.setItem(row, 2, QTableWidgetItem("✓"))
                    row += 1
        
        # Update status
        self.status_label.setText("Results updated")
        
    def export_csv(self):
        """Export volume results to CSV file."""
        try:
            selected_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Volume Results",
                "volume_results.csv",
                "CSV Files (*.csv)"
            )
            if not selected_path:
                self.status_label.setText("Export cancelled")
                return

            # Create CSV exporter
            selected_file = Path(selected_path)
            exporter = CSVExporter(default_directory=str(selected_file.parent))
            
            # Get current results from the table
            table_data = self._get_table_data()
            
            # Export to CSV
            filepath = exporter.export_table_data(table_data, filename=selected_file.name)
            
            # Show success message
            self.status_label.setText(f"Exported to {filepath}")
            
        except Exception as e:
            # Show error message
            self.status_label.setText(f"Export failed: {str(e)}")
            
    def _get_table_data(self) -> dict:
        """Extract current table data for CSV export.
        
        Returns:
            Dictionary containing table headers and data rows
        """
        headers = []
        data = []
        
        # Get headers
        if self.results_table.columnCount() > 0:
            headers = [self.results_table.horizontalHeaderItem(i).text() 
                      for i in range(self.results_table.columnCount())]
        
        # Get data rows
        for row in range(self.results_table.rowCount()):
            row_data = []
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            if any(row_data):  # Only add non-empty rows
                data.append(row_data)
        
        return {"headers": headers, "data": data}
        
    def clear_results(self):
        """Clear all volume analysis results."""
        for row in range(self.results_table.rowCount()):
            for col in range(self.results_table.columnCount()):
                self.results_table.setItem(row, col, None)
        self.status_label.setText("No results")

__all__ = ['VolumePanel']
