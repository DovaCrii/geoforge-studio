"""GeoForge Studio - Main Application Entry Point

This module provides the desktop application bootstrap for GeoForge Studio,
a GNSS processing and geospatial analysis tool with offline capabilities.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from ui.main_window import MainWindow
from services.project_service import ProjectService
from services.ppk_service import PpkService
from importers.dxf_importer import DxfImporter
from importers.kmz_importer import KmzImporter
from volume.surface import create_tin_from_points
from volume.calculator import CutFillCalculator
from volume.renderer import VolumeRenderer

class GeoForgeStudio:
    """Main application class for GeoForge Studio."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.splash = None
        self.main_window = None
        self.services = {}
        
    def show_splash(self):
        """Show splash screen during startup."""
        self.splash = QSplashScreen(QPixmap(100, 100))
        self.splash.show()
        self.splash.showMessage(
            "Loading GeoForge Studio...\nInitializing services...",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.White
        )
        
    def initialize_services(self):
        """Initialize all application services."""
        if self.splash:
            self.splash.showMessage(
                "Loading GeoForge Studio...\nInitializing services...",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                Qt.GlobalColor.White
            )
            
        # Initialize core services
        self.services['project'] = ProjectService()
        self.services['ppk'] = PpkService()
        self.services['dxf'] = DxfImporter()
        self.services['kmz'] = KmzImporter()
        self.services['surface_factory'] = create_tin_from_points
        self.services['volume_calculator'] = CutFillCalculator()
        self.services['renderer'] = VolumeRenderer()
        
        if self.splash:
            self.splash.showMessage(
                "Loading GeoForge Studio...\nServices initialized.",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                Qt.GlobalColor.White
            )
            
    def create_main_window(self):
        """Create and configure the main application window."""
        if self.splash:
            self.splash.close()
            self.splash = None
            
        self.main_window = MainWindow(self.services)
        self.main_window.show()
        
    def run(self) -> int:
        """Run the application."""
        self.show_splash()
        
        # Initialize services with a small delay to show splash
        QTimer.singleShot(1000, self.initialize_services)
        QTimer.singleShot(2000, self.create_main_window)
        
        return self.app.exec()

def main():
    """Application entry point."""
    app = GeoForgeStudio()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())
