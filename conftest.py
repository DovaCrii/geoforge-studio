"""pytest configuration for GeoForge Studio.

Ensures QApplication is initialized before any PyQt6 widget tests run.
Use QT_QPA_PLATFORM=offscreen for headless test environments.
"""

import os
import sys

# Force offscreen platform for headless environments (must be set before
# any PyQt6 import, as Qt uses this at library load time).
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Keep a module-level reference so QApplication is not GC'd
_qapp = None


def pytest_configure(config):
    """Initialize QApplication once before any test runs."""
    global _qapp
    if _qapp is None:
        from PyQt6.QtWidgets import QApplication
        _qapp = QApplication.instance() or QApplication(sys.argv)
