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

    try:
        from exporters.geojson_exporter import GeoJSONExporter
        from exporters.dxf_surface_exporter import DXFSurfaceExporter
        print("✓ exporters imports successful")
    except ImportError as e:
        print(f"⚠ exporters import failed: {e}")
        return False

    try:
        from services.help_service import HelpService
        print("✓ services.help_service import successful")
    except ImportError as e:
        print(f"⚠ help service import failed: {e}")
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

def test_exports():
    """Test export workflows with sample data."""
    print("\nTesting exports...")

    try:
        from services.project_service import Project, SurveyPoint
        from exporters.geojson_exporter import export_project_points_geojson
        from volume.surface import create_sample_tin
        from exporters.dxf_surface_exporter import export_tin_surface_dxf

        project = Project(
            name="Smoke Project",
            path="/tmp/geoforge-smoke.gfp",
            points=[
                SurveyPoint(id="P1", name="Point 1", x=1.0, y=2.0, z=3.0),
                SurveyPoint(id="P2", name="Point 2", x=4.0, y=5.0, z=6.0),
                SurveyPoint(id="P3", name="Point 3", x=7.0, y=8.0, z=9.0),
            ],
        )

        geojson_path = export_project_points_geojson(project, "/tmp/geoforge-smoke.geojson")
        print(f"✓ GeoJSON export successful: {geojson_path}")

        surface = create_sample_tin()
        dxf_path = export_tin_surface_dxf(surface, "/tmp/geoforge-smoke.dxf")
        print(f"✓ Surface DXF export successful: {dxf_path}")

        return True
    except Exception as e:
        print(f"⚠ Export smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_help_assistant():
    """Test the lightweight help assistant service."""
    print("\nTesting help assistant...")

    try:
        from services.help_service import HelpService

        service = HelpService()
        answer = service.answer("Explain CRS", {"tab": "Help Assistant", "project": "Smoke Project"})
        print(f"✓ Help assistant response topic: {answer.topic}")
        print(f"✓ Help assistant backend: {answer.backend}")
        return True
    except Exception as e:
        print(f"⚠ Help assistant smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importer_error_handling():
    """Test that importers handle malformed files gracefully."""
    print("\nTesting importer error handling...")
    success = True
    
    try:
        from importers.dxf_importer import DxfImporter
        
        # Test 1: Non-existent file
        importer = DxfImporter()
        result = importer.import_dxf("/tmp/nonexistent_file.dxf")
        assert not result.success, "Should fail for nonexistent file"
        assert "not found" in result.message.lower(), f"Unexpected message: {result.message}"
        print("✓ DXF: nonexistent file returns error message")
        
        # Test 2: Empty file
        empty_dxf = Path("/tmp/geoforge-test-empty.dxf")
        empty_dxf.write_text("")
        result = importer.import_dxf(str(empty_dxf))
        assert not result.success, "Should fail for empty DXF"
        empty_dxf.unlink(missing_ok=True)
        print("✓ DXF: empty file handled without crash")
        
    except Exception as e:
        print(f"⚠ DXF error handling test failed: {e}")
        success = False
    
    try:
        from importers.kmz_importer import KmzImporter
        
        # Test 3: Non-existent file
        importer = KmzImporter()
        result = importer.import_kmz("/tmp/nonexistent_file.kmz")
        assert not result.success, "Should fail for nonexistent file"
        assert "not found" in result.message.lower(), f"Unexpected message: {result.message}"
        print("✓ KMZ: nonexistent file returns error message")
        
        # Test 4: Corrupt zip
        corrupt_kmz = Path("/tmp/geoforge-test-corrupt.kmz")
        corrupt_kmz.write_bytes(b"not a zip file content here")
        result = importer.import_kmz(str(corrupt_kmz))
        assert not result.success, "Should fail for corrupt KMZ"
        corrupt_kmz.unlink(missing_ok=True)
        print("✓ KMZ: corrupt file handled without crash")
        
        # Test 5: KML with invalid file path
        result = importer.import_kml("")
        assert not result.success, "Should fail for empty path"
        print("✓ KML: empty path returns error")
        
    except Exception as e:
        print(f"⚠ KMZ error handling test failed: {e}")
        success = False
    
    return success


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

    if not test_exports():
        success = False

    if not test_help_assistant():
        success = False
    
    if not test_rinex_fixtures():
        success = False

    if not test_importer_error_handling():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("✓ Smoke test completed successfully!")
        print("\nSmoke test summary:")
        print("- All core modules imported successfully")
        print("- Volume calculation works with sample data")
        print("- Importers are available for DXF and KMZ files")
        print("- Export workflows are available for GeoJSON and surface DXF")
        print("- Local help assistant is available")
        print("- RINEX fixtures are available (if file exists)")
        print("- Importers handle malformed files without crashing")
        print("- File validation and error messages work correctly")
        print("\nThe GeoForge Studio core functionality is working correctly.")
        return 0
    else:
        print("✗ Smoke test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
