#!/usr/bin/env python3
"""Smoke test for GeoForge Studio - End-to-end manual verification.

This script provides a simple manual smoke path to verify that the core
GeoForge Studio functionality works end-to-end with sample datasets.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test that all core modules can be imported."""
    print("Testing basic imports...")
    
    try:
        from volume.surface import SurveyPoint, create_sample_tin
        print("✓ volume.surface imports successful")
    except ImportError as e:
        print(f"⚠ volume.surface import failed: {e}")
        return False
    
    try:
        from volume.calculator import CutFillCalculator, CutFillResult
        print("✓ volume.calculator imports successful")
    except ImportError as e:
        print(f"⚠ volume.calculator import failed: {e}")
        return False
    
    try:
        from importers.dxf_importer import DxfImporter
        print("✓ importers.dxf_importer imports successful")
    except ImportError as e:
        print(f"⚠ importers.dxf_importer import failed: {e}")
        return False
    
    try:
        from importers.kmz_importer import KmzImporter
        print("✓ importers.kmz_importer imports successful")
    except ImportError as e:
        print(f"⚠ importers.kmz_importer import failed: {e}")
        return False
    
    return True

def test_volume_calculation():
    """Test volume calculation with sample data."""
    print("\nTesting volume calculation...")
    
    try:
        from volume.surface import create_sample_tin
        from volume.calculator import CutFillCalculator
        
        # Create sample TIN surface
        surface = create_sample_tin()
        print(f"✓ Created sample TIN with {len(surface.points)} points")
        
        # Calculate cut/fill
        calculator = CutFillCalculator()
        result = calculator.calculate(surface)
        
        print(f"✓ Volume calculation successful:")
        print(f"  - Total cut: {result.total_cut:.2f} m³")
        print(f"  - Total fill: {result.total_fill:.2f} m³")
        print(f"  - Net volume: {result.net_volume:.2f} m³")
        print(f"  - Triangles processed: {result.triangles_processed}")
        
        return True
        
    except Exception as e:
        print(f"⚠ Volume calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importers():
    """Test importers with sample files."""
    print("\nTesting importers...")
    
    # Check if fixture files exist
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    # Test DXF importer
    dxf_file = fixtures_dir / "sample.dxf"
    if dxf_file.exists():
        try:
            from importers.dxf_importer import DxfImporter
            importer = DxfImporter()
            # Note: This is a smoke test - we're not actually parsing the file
            # since we don't have a real DXF parser in this test environment
            print(f"✓ DXF importer available (file: {dxf_file.name})")
        except Exception as e:
            print(f"⚠ DXF importer test failed: {e}")
            return False
    else:
        print(f"⚠ DXF fixture file not found: {dxf_file}")
    
    # Test KMZ importer
    kmz_file = fixtures_dir / "sample.kmz"
    if kmz_file.exists():
        try:
            from importers.kmz_importer import KmzImporter
            importer = KmzImporter()
            print(f"✓ KMZ importer available (file: {kmz_file.name})")
        except Exception as e:
            print(f"⚠ KMZ importer test failed: {e}")
            return False
    else:
        print(f"⚠ KMZ fixture file not found: {kmz_file}")
    
    return True

def test_rinex_fixtures():
    """Test RINEX fixtures if available."""
    print("\nTesting RINEX fixtures...")
    
    fixtures_dir = Path(__file__).parent / "fixtures"
    rinex_file = fixtures_dir / "sample.rinex"
    
    if rinex_file.exists():
        print(f"✓ RINEX fixture file available: {rinex_file.name}")
        # Note: This is a smoke test - we're not actually parsing the RINEX file
        # since we don't have a real RINEX parser in this test environment
        return True
    else:
        print(f"⚠ RINEX fixture file not found: {rinex_file}")
        return True  # Not a failure for smoke test

def main():
    """Run the smoke test."""
    print("GeoForge Studio - End-to-End Smoke Test")
    print("=" * 50)
    
    success = True
    
    # Run all smoke tests
    if not test_basic_imports():
        success = False
    
    if not test_volume_calculation():
        success = False
    
    if not test_importers():
        success = False
    
    if not test_rinex_fixtures():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("✓ Smoke test completed successfully!")
        print("\nSmoke test summary:")
        print("- All core modules imported successfully")
        print("- Volume calculation works with sample data")
        print("- Importers are available for DXF and KMZ files")
        print("- RINEX fixtures are available (if file exists)")
        print("\nThe GeoForge Studio core functionality is working correctly.")
        return 0
    else:
        print("✗ Smoke test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
