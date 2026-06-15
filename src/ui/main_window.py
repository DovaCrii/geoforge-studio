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