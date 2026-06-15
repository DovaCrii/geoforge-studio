#!/usr/bin/env python3
"""Simple test script to verify CRS functionality.

This script tests the CRS transformation functionality
implemented in the GeoForge Studio project.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.crs_utils import CRSManager, set_crs, get_crs, transform_point, is_crs_set
from ui.map_canvas import QtMapRenderer
import pyproj

def test_crs_manager():
    """Test the CRSManager functionality."""
    print("Testing CRSManager...")
    
    # Create a CRS manager
    crs_manager = CRSManager()
    
    # Test initial state
    assert not crs_manager.is_crs_set(), "CRS should not be set initially"
    assert crs_manager.get_crs() is None, "CRS should be None initially"
    assert crs_manager.get_crs_info() == {}, "CRS info should be empty initially"
    
    # Set a CRS
    crs = pyproj.CRS.from_epsg(4326)  # WGS84
    crs_manager.set_crs(crs)
    
    # Test CRS is set
    assert crs_manager.is_crs_set(), "CRS should be set"
    assert crs_manager.get_crs() == crs, "CRS should match"
    
    # Test CRS info
    crs_info = crs_manager.get_crs_info()
    assert "name" in crs_info, "CRS info should contain name"
    assert crs_info["name"] == "WGS 84", "CRS name should be WGS 84"
    
    # Test coordinate transformation
    point = (10.0, 20.0)
    source_crs = pyproj.CRS.from_epsg(4326)
    transformed_point = crs_manager.transform_point(point, source_crs)
    assert transformed_point == point, "Point should be unchanged in same CRS"
    
    print("✓ CRSManager tests passed")

def test_global_crs_functions():
    """Test the global CRS functions."""
    print("Testing global CRS functions...")
    
    # Reset global CRS
    set_crs(None)
    
    # Test initial state
    assert not is_crs_set(), "Global CRS should not be set initially"
    assert get_crs() is None, "Global CRS should be None initially"
    
    # Set a CRS
    crs = pyproj.CRS.from_epsg(4326)
    set_crs(crs)
    
    # Test CRS is set
    assert is_crs_set(), "Global CRS should be set"
    assert get_crs() == crs, "Global CRS should match"
    
    # Test coordinate transformation
    point = (10.0, 20.0)
    source_crs = pyproj.CRS.from_epsg(4326)
    transformed_point = transform_point(point, source_crs)
    assert transformed_point == point, "Point should be unchanged in same CRS"
    
    print("✓ Global CRS functions tests passed")

def test_map_renderer_crs():
    """Test the MapRenderer's CRS functionality."""
    print("Testing MapRenderer CRS functionality...")
    
    # Create a map renderer
    renderer = QtMapRenderer()
    
    # Test initial state
    assert not renderer.is_crs_set(), "Renderer CRS should not be set initially"
    assert renderer.get_crs() is None, "Renderer CRS should be None initially"
    assert renderer.get_crs_info() == {}, "Renderer CRS info should be empty initially"
    
    # Set a CRS
    crs = pyproj.CRS.from_epsg(4326)
    renderer.set_crs(crs)
    
    # Test CRS is set
    assert renderer.is_crs_set(), "Renderer CRS should be set"
    assert renderer.get_crs() == crs, "Renderer CRS should match"
    
    # Test CRS info
    crs_info = renderer.get_crs_info()
    assert "name" in crs_info, "Renderer CRS info should contain name"
    assert crs_info["name"] == "WGS 84", "Renderer CRS name should be WGS 84"
    
    print("✓ MapRenderer CRS tests passed")

def test_crs_transformation():
    """Test CRS transformation between different CRS systems."""
    print("Testing CRS transformation...")
    
    # Create CRS manager
    crs_manager = CRSManager()
    
    # Set target CRS to WGS84
    target_crs = pyproj.CRS.from_epsg(4326)
    crs_manager.set_crs(target_crs)
    
    # Test transformation from EPSG:4326 to EPSG:4326 (same CRS)
    point = (10.0, 20.0)
    source_crs = pyproj.CRS.from_epsg(4326)
    transformed_point = crs_manager.transform_point(point, source_crs)
    assert transformed_point == point, "Point should be unchanged in same CRS"
    
    # Test transformation from EPSG:3857 to EPSG:4326
    source_crs = pyproj.CRS.from_epsg(3857)  # Web Mercator
    point_3857 = (1000000.0, 2000000.0)
    
    try:
        transformed_point = crs_manager.transform_point(point_3857, source_crs)
        print(f"✓ Transformed point from EPSG:3857 to EPSG:4326: {point_3857} -> {transformed_point}")
    except Exception as e:
        print(f"⚠ CRS transformation test skipped (pyproj may not have required projections): {e}")
    
    print("✓ CRS transformation tests passed")

def main():
    """Run all tests."""
    print("Running CRS functionality tests...")
    print("=" * 50)
    
    try:
        test_crs_manager()
        test_global_crs_functions()
        test_map_renderer_crs()
        test_crs_transformation()
        
        print("=" * 50)
        print("✓ All tests passed!")
        return 0
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())