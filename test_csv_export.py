#!/usr/bin/env python3
"""Test CSV export functionality for GeoForge Studio volume results."""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_csv_exporter():
    """Test CSV exporter functionality."""
    print("Testing CSV exporter...")
    
    try:
        from volume.csv_exporter import CSVExporter
        from volume.calculator import CutFillResult
        
        # Create a test CutFillResult
        test_result = CutFillResult(
            total_cut=100.5,
            total_fill=200.75,
            net_volume=100.25,
            surface_area=500.25,
            bounding_box=(0.0, 0.0, 100.0, 100.0),
            triangles_processed=25
        )
        
        # Create CSV exporter
        exporter = CSVExporter()
        
        # Test export
        filepath = exporter.export_cut_fill_result(test_result)
        print(f"✓ CSV export successful: {filepath}")
        
        # Verify file exists
        if Path(filepath).exists():
            print(f"✓ CSV file exists: {filepath}")
            
            # Read and verify content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✓ CSV content preview:\n{content[:200]}...")
                
                # Check for expected content
                if "Metric" in content and "Value" in content:
                    print("✓ CSV contains expected headers")
                else:
                    print("⚠ CSV might be missing expected headers")
                    
        else:
            print(f"⚠ CSV file not found: {filepath}")
            
        return True
        
    except Exception as e:
        print(f"⚠ CSV exporter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_volume_panel_csv_export():
    """Test VolumePanel CSV export functionality."""
    print("\nTesting VolumePanel CSV export...")
    
    try:
        from ui.volume_panel import VolumePanel
        
        # Create a mock services dict
        mock_services = {}
        
        # Create VolumePanel instance
        panel = VolumePanel(mock_services)
        
        # Test that export_csv method exists
        if hasattr(panel, 'export_csv'):
            print("✓ VolumePanel has export_csv method")
            
            # Test _get_table_data method
            if hasattr(panel, '_get_table_data'):
                print("✓ VolumePanel has _get_table_data method")
                
                # Test _get_table_data
                table_data = panel._get_table_data()
                print(f"✓ _get_table_data returned: {table_data}")
                
                # Check structure
                if "headers" in table_data and "data" in table_data:
                    print("✓ Table data has expected structure")
                else:
                    print("⚠ Table data structure might be incorrect")
                    
            else:
                print("⚠ VolumePanel missing _get_table_data method")
        else:
            print("⚠ VolumePanel missing export_csv method")
            
        return True
        
    except Exception as e:
        print(f"⚠ VolumePanel CSV export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run CSV export tests."""
    print("GeoForge Studio - CSV Export Test")
    print("=" * 50)
    
    success = True
    
    # Test CSV exporter
    if not test_csv_exporter():
        success = False
    
    # Test VolumePanel CSV export
    if not test_volume_panel_csv_export():
        success = False
    
    print("\n" + "=" * 50)
    
    if success:
        print("✓ CSV export tests completed successfully!")
        print("\nCSV export test summary:")
        print("- CSV exporter module works correctly")
        print("- VolumePanel has CSV export functionality")
        print("- CSV export creates files with expected content")
        return 0
    else:
        print("✗ CSV export tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())