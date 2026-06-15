#!/usr/bin/env python3
"""Test script for cut/fill volume calculations.

This script tests the cut/fill volume calculation functionality
implemented in GeoForge Studio.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from volume.surface import SurveyPoint, create_sample_tin
from volume.calculator import CutFillCalculator, CutFillResult, format_volume

def test_cut_fill_calculator():
    """Test the CutFillCalculator functionality."""
    print("Testing CutFillCalculator...")
    
    # Create a sample TIN surface
    surface = create_sample_tin()
    
    # Create calculator and calculate cut/fill
    calculator = CutFillCalculator()
    result = calculator.calculate(surface)
    
    # Verify result structure
    assert isinstance(result, CutFillResult), "Result should be CutFillResult instance"
    assert hasattr(result, 'total_cut'), "Result should have total_cut attribute"
    assert hasattr(result, 'total_fill'), "Result should have total_fill attribute"
    assert hasattr(result, 'net_volume'), "Result should have net_volume attribute"
    assert hasattr(result, 'surface_area'), "Result should have surface_area attribute"
    assert hasattr(result, 'bounding_box'), "Result should have bounding_box attribute"
    assert hasattr(result, 'triangles_processed'), "Result should have triangles_processed attribute"
    
    # Verify properties
    assert result.triangles_processed == 4, f"Expected 4 triangles, got {result.triangles_processed}"
    assert result.surface_area > 0, "Surface area should be positive"
    assert len(result.bounding_box) == 4, "Bounding box should have 4 values"
    
    # Test helper methods
    assert isinstance(result.has_cut_fill, bool), "has_cut_fill should be boolean"
    assert isinstance(result.is_balanced, bool), "is_balanced should be boolean"
    
    # Test format_volume function
    formatted = format_volume(1234.567)
    assert isinstance(formatted, str), "format_volume should return string"
    assert formatted == "1234.57", f"Expected '1234.57', got '{formatted}'"
    
    print(f"✓ CutFillCalculator tests passed")
    print(f"  - Total cut: {result.total_cut:.2f} m³")
    print(f"  - Total fill: {result.total_fill:.2f} m³")
    print(f"  - Net volume: {result.net_volume:.2f} m³")
    print(f"  - Surface area: {result.surface_area:.2f} m²")
    print(f"  - Triangles processed: {result.triangles_processed}")
    print(f"  - Has cut/fill: {result.has_cut_fill}")
    print(f"  - Is balanced: {result.is_balanced}")

def test_convenience_functions():
    """Test convenience functions."""
    print("\nTesting convenience functions...")
    
    # Create a sample TIN surface
    surface = create_sample_tin()
    
    # Test calculate_cut_fill function
    from volume.calculator import calculate_cut_fill
    result = calculate_cut_fill(surface)
    
    assert isinstance(result, CutFillResult), "calculate_cut_fill should return CutFillResult"
    assert result.triangles_processed == 4, "Should process 4 triangles"
    
    print("✓ Convenience functions tests passed")

def test_volume_panel_integration():
    """Test volume panel integration (basic import test)."""
    print("\nTesting volume panel integration...")
    
    # Test that volume_panel can be imported
    try:
        from ui.volume_panel import VolumePanel
        print("✓ VolumePanel import successful")
    except ImportError as e:
        print(f"⚠ VolumePanel import failed (expected in test environment): {e}")
    
    # Test that calculator can be imported
    try:
        from volume.calculator import CutFillCalculator
        print("✓ CutFillCalculator import successful")
    except ImportError as e:
        print(f"⚠ CutFillCalculator import failed: {e}")
    
    # Test that renderer can be imported
    try:
        from volume.renderer import VolumeRenderer
        print("✓ VolumeRenderer import successful")
    except ImportError as e:
        print(f"⚠ VolumeRenderer import failed: {e}")

def main():
    """Run all tests."""
    print("Running cut/fill volume calculation tests...")
    print("=" * 60)
    
    try:
        test_cut_fill_calculator()
        test_convenience_functions()
        test_volume_panel_integration()
        
        print("=" * 60)
        print("✓ All tests passed!")
        return 0
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())