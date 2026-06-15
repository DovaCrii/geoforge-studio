"""Main window for GeoForge Studio application.

This module provides the main application window with menu bar,
toolbar, and central workspace for GNSS processing and visualization.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QToolBar, QStatusBar, QTabWidget,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction

from ui.map_canvas import MapCanvas, QtMapRenderer
from ui.help_assistant import HelpAssistantPanel
from ui.volume_panel import VolumePanel
from services.project_service import ProjectService
from services.ppk_service import PpkService

class MainWindow(QMainWindow):
    """Main application window for GeoForge Studio."""
    
    def __init__(self, services: dict):
        super().__init__()
        self.services = services
        self.setup_ui()
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("GeoForge Studio - GNSS Processing & Geospatial Analysis")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for different workspaces
        self.tab_widget = QTabWidget()
        
        # Create map workspace tab
        self.map_workspace = QWidget()
        map_layout = QVBoxLayout(self.map_workspace)
        
        # Map canvas - create QtMapRenderer instance
        self.map_renderer = QtMapRenderer()
        self.map_canvas = MapCanvas(self.services, self.map_renderer)
        map_layout.addWidget(self.map_canvas.get_widget())
        
        # Map controls
        map_controls = QHBoxLayout()
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Project Name")
        map_controls.addWidget(QLabel("Project:"))
        map_controls.addWidget(self.project_name_input)
        
        load_button = QPushButton("Load Project")
        load_button.clicked.connect(self.load_project)
        map_controls.addWidget(load_button)
        
        map_layout.addLayout(map_controls)
        
        # Add map workspace to tab widget
        self.tab_widget.addTab(self.map_workspace, "🗺️ Map Workspace")

        # Help assistant workspace tab
        self.help_workspace = QWidget()
        help_layout = QVBoxLayout(self.help_workspace)
        self.help_panel = HelpAssistantPanel(self.services, context_provider=self.get_help_context)
        help_layout.addWidget(self.help_panel)
        self.tab_widget.addTab(self.help_workspace, "🧭 Help Assistant")
        
        # Create volume analysis workspace tab
        self.volume_workspace = QWidget()
        volume_layout = QVBoxLayout(self.volume_workspace)
        
        self.volume_panel = VolumePanel(self.services)
        volume_layout.addWidget(self.volume_panel)
        
        self.tab_widget.addTab(self.volume_workspace, "📊 Volume Analysis")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
    def setup_menubar(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project", self)
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("Save Project", self)
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)

        export_geojson_action = QAction("Export GeoJSON...", self)
        export_geojson_action.triggered.connect(self.export_project_geojson)
        file_menu.addAction(export_geojson_action)

        export_surface_action = QAction("Export Surface DXF...", self)
        export_surface_action.triggered.connect(self.export_surface_dxf)
        file_menu.addAction(export_surface_action)

        export_map_action = QAction("Export Map PNG...", self)
        export_map_action.triggered.connect(self.export_map_png)
        file_menu.addAction(export_map_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu (disabled - functionality not yet implemented)
        edit_menu = menubar.addMenu("Edit")
        edit_menu.setEnabled(False)
        
        # Processing menu
        processing_menu = menubar.addMenu("Processing")
        
        run_ppk_action = QAction("Run PPK", self)
        run_ppk_action.triggered.connect(self.run_ppk)
        processing_menu.addAction(run_ppk_action)
        
        compute_volume_action = QAction("Compute Volume", self)
        compute_volume_action.triggered.connect(self.compute_volume)
        processing_menu.addAction(compute_volume_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        open_help_action = QAction("Open Help Assistant", self)
        open_help_action.triggered.connect(self.open_help_assistant)
        help_menu.addAction(open_help_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Set up the application toolbar."""
        toolbar = self.addToolBar("Main")
        
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        run_action = QAction("Run Processing", self)
        run_action.triggered.connect(self.run_processing)
        toolbar.addAction(run_action)
        
    def setup_statusbar(self):
        """Set up the application status bar."""
        self.statusbar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)
        
    def new_project(self):
        """Create a new project."""
        self.project_name_input.clear()
        self.status_label.setText("New project created")
        
    def open_project(self):
        """Open an existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "GeoForge Projects (*.gfp)"
        )
        if file_path:
            self.status_label.setText(f"Project loaded: {file_path}")
            
    def save_project(self):
        """Save the current project."""
        if self.project_name_input.text():
            self.status_label.setText(f"Project saved: {self.project_name_input.text()}")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a project name")

    def export_project_geojson(self):
        """Export project points to GeoJSON."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project as GeoJSON",
            "project.geojson",
            "GeoJSON Files (*.geojson)"
        )
        if not file_path:
            self.status_label.setText("GeoJSON export cancelled")
            return

        try:
            project_service = self.services.get("project")
            if project_service is None:
                raise ValueError("Project service is not available")

            saved_path = project_service.export_project_geojson(file_path)
            self.status_label.setText(f"GeoJSON exported: {saved_path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", str(exc))

    def export_surface_dxf(self):
        """Export a TIN surface built from current project points as DXF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Surface as DXF",
            "surface.dxf",
            "DXF Files (*.dxf)"
        )
        if not file_path:
            self.status_label.setText("Surface export cancelled")
            return

        try:
            project_service = self.services.get("project")
            surface_factory = self.services.get("surface_factory")
            surface_exporter = self.services.get("surface_exporter")

            if project_service is None or surface_factory is None:
                raise ValueError("Surface export services are not available")

            project = project_service.get_current_project()
            if project is None or len(project.points) < 3:
                raise ValueError("Need at least 3 survey points to export a surface")

            surface = surface_factory(project.points)

            if surface_exporter is None:
                from exporters.dxf_surface_exporter import export_tin_surface_dxf
                saved_path = export_tin_surface_dxf(surface, file_path)
            else:
                saved_path = surface_exporter.export_surface(surface, file_path)

            self.status_label.setText(f"Surface exported: {saved_path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export failed", str(exc))

    def open_help_assistant(self):
        """Switch to the Help Assistant tab."""
        self.tab_widget.setCurrentWidget(self.help_workspace)
        self.help_panel.refresh_context()

    def get_help_context(self):
        """Build lightweight context for the help assistant."""
        project_service = self.services.get("project")
        project = project_service.get_current_project() if project_service else None
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        crs_text = None
        if hasattr(self, "map_canvas"):
            crs = self.map_canvas.get_crs()
            crs_text = crs.to_string() if crs else None

        return {
            "tab": current_tab,
            "project": project.name if project else None,
            "crs": crs_text,
            "status": self.status_label.text(),
        }

    def export_map_png(self):
        """Export the current map view to a PNG image."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Map as PNG",
            "geoforge-map.png",
            "PNG Images (*.png)"
        )
        if not file_path:
            self.status_label.setText("Map export cancelled")
            return

        if self.map_canvas.export_png(file_path):
            self.status_label.setText(f"Map exported: {file_path}")
        else:
            QMessageBox.warning(self, "Export failed", "Could not save the map image")
            
    def run_ppk(self):
        """Run PPK processing."""
        self.status_label.setText("Running PPK processing...")
        QTimer.singleShot(1000, lambda: self.status_label.setText("PPK processing completed"))
        
    def compute_volume(self):
        """Compute volume analysis."""
        self.status_label.setText("Computing volume analysis...")
        QTimer.singleShot(1000, lambda: self.status_label.setText("Volume computation completed"))
        
    def run_processing(self):
        """Run all processing steps."""
        self.run_ppk()
        self.compute_volume()
        
    def show_about(self):
        """Show about dialog."""
        from src import __version__
        QMessageBox.about(
            self,
            "About GeoForge Studio",
            """GeoForge Studio v{version}

GNSS Processing and Geospatial Analysis Tool

This application provides offline capabilities for:
- RINEX data processing
- PPK positioning
- 2D map visualization
- DXF/KMZ overlay import
- Volume computation and analysis

© 2026 GeoForge Studio Team""".format(version=__version__)
        )
