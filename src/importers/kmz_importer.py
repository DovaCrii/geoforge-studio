"""KMZ/KML importer for GeoForge Studio.

This module provides functionality for importing KMZ and KML files as overlays
on the map canvas. Currently supports read-only import of basic KML placemarks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

@dataclass
class KmlPlacemark:
    """Represents a KML placemark."""
    
    name: str
    description: str = ""
    coordinates: List[Tuple[float, float, float]] = field(default_factory=list)
    style_url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates,
            "style_url": self.style_url,
        }

@dataclass
class KmlImportResult:
    """Result of KML/KMZ import operation."""
    
    success: bool
    placemarks: List[KmlPlacemark] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    message: str = ""
    file_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "placemarks": [p.to_dict() for p in self.placemarks],
            "warnings": self.warnings,
            "message": self.message,
            "file_path": self.file_path,
        }

class KmzImporter:
    """Importer for KMZ and KML files."""
    
    def __init__(self):
        self.supported_formats = {".kml", ".kmz"}
        
    def _validate_file(self, file_path: str, expected_ext: str) -> Optional[str]:
        """Validate file exists and has correct extension. Returns error message or None."""
        if not file_path:
            return "No file path provided"
        from pathlib import Path
        if not Path(file_path).exists():
            return f"File not found: {file_path}"
        if not file_path.lower().endswith(expected_ext):
            return f"File is not a {expected_ext} file (needs {expected_ext} extension)"
        return None
    
    def import_kmz(self, file_path: str) -> KmlImportResult:
        """Import KMZ file and return placemarks."""
        warnings: List[str] = []
        
        error = self._validate_file(file_path, '.kmz')
        if error:
            return KmlImportResult(success=False, message=error, file_path=file_path)
        
        try:
            # Check if it's a KMZ file (zip archive)
            if not zipfile.is_zipfile(file_path):
                return KmlImportResult(
                    success=False,
                    message="File is not a valid KMZ archive",
                    file_path=file_path
                )
                
            # Extract KML from KMZ
            try:
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    # Check for corrupt zip
                    bad_file = zipf.testzip()
                    if bad_file:
                        return KmlImportResult(
                            success=False,
                            message=f"Corrupted KMZ archive: '{bad_file}' is damaged",
                            file_path=file_path
                        )
                    
                    kml_files = [f for f in zipf.namelist() if f.lower().endswith('.kml')]
                    if not kml_files:
                        return KmlImportResult(
                            success=False,
                            message="No KML file found in KMZ archive",
                            file_path=file_path
                        )
                        
                    # Read the first KML file
                    kml_content = zipf.read(kml_files[0]).decode('utf-8')
            except (zipfile.BadZipFile, EOFError) as e:
                return KmlImportResult(
                    success=False,
                    message=f"Invalid or corrupted KMZ file: {e}",
                    file_path=file_path
                )
                
            # Parse KML content
            result = self._parse_kml_content(kml_content, file_path)
            result.warnings = warnings
            return result
            
        except Exception as e:
            return KmlImportResult(
                success=False,
                message=f"Error importing KMZ file: {str(e)}",
                file_path=file_path
            )
            
    def import_kml(self, file_path: str) -> KmlImportResult:
        """Import KML file and return placemarks."""
        warnings: List[str] = []
        
        error = self._validate_file(file_path, '.kml')
        if error:
            return KmlImportResult(success=False, message=error, file_path=file_path)
        
        try:
            # Read KML file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    kml_content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                return KmlImportResult(
                    success=False,
                    message=f"Error reading KML file: {e}",
                    file_path=file_path
                )
                
            # Parse KML content
            result = self._parse_kml_content(kml_content, file_path)
            result.warnings = warnings
            return result
            
        except Exception as e:
            return KmlImportResult(
                success=False,
                message=f"Error importing KML file: {str(e)}",
                file_path=file_path
            )
            
    def _parse_kml_content(self, kml_content: str, file_path: str) -> KmlImportResult:
        """Parse KML content and extract placemarks."""
        warnings: List[str] = []
        
        try:
            root = ET.fromstring(kml_content)
            
            # Define namespace
            ns = {
                'kml': 'http://www.opengis.net/kml/2.2',
                'gx': 'http://www.google.com/kml/ext/2.2'
            }
            
            placemarks = []
            skipped_bad_coords = 0
            skipped_parse_error = 0
            
            # Find all placemark elements
            for placemark in root.findall('.//kml:Placemark', ns):
                try:
                    name = placemark.findtext('.//kml:name', namespaces=ns) or "Unnamed Placemark"
                    description = placemark.findtext('.//kml:description', namespaces=ns) or ""
                    style_url = placemark.findtext('.//kml:styleUrl', namespaces=ns) or ""
                    
                    # Extract coordinates
                    coordinates = []
                    coord_elements = placemark.findall('.//kml:coordinates', ns)
                    
                    for coord_elem in coord_elements:
                        coord_text = coord_elem.text
                        if coord_text:
                            for coord_str in coord_text.strip().split():
                                coords = coord_str.split(',')
                                if len(coords) >= 2:
                                    try:
                                        x = float(coords[0])
                                        y = float(coords[1])
                                        z = float(coords[2]) if len(coords) > 2 else 0.0
                                        coordinates.append((x, y, z))
                                    except ValueError:
                                        continue
                    
                    if not coordinates:
                        warnings.append(f"Skipped placemark '{name}' — no valid coordinates found")
                        skipped_bad_coords += 1
                        continue
                    
                    placemark_obj = KmlPlacemark(
                        name=name,
                        description=description,
                        coordinates=coordinates,
                        style_url=style_url
                    )
                    
                    placemarks.append(placemark_obj)
                except Exception as e:
                    warnings.append(f"Skipped a placemark due to parse error: {e}")
                    skipped_parse_error += 1
                    
            parts = [f"Imported {len(placemarks)} placemarks"]
            if skipped_bad_coords:
                parts.append(f"{skipped_bad_coords} skipped (no valid coordinates)")
            if skipped_parse_error:
                parts.append(f"{skipped_parse_error} skipped (parse errors)")
            
            return KmlImportResult(
                success=True,
                placemarks=placemarks,
                warnings=warnings,
                message="; ".join(parts),
                file_path=file_path
            )
            
        except ET.ParseError as e:
            return KmlImportResult(
                success=False,
                message=f"Invalid KML XML: {e}",
                file_path=file_path
            )
        except Exception as e:
            return KmlImportResult(
                success=False,
                message=f"Error parsing KML content: {str(e)}",
                file_path=file_path
            )
            
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return list(self.supported_formats)
        
    def validate_kmz_file(self, file_path: str) -> bool:
        """Validate if KMZ file can be imported."""
        try:
            if not file_path or not file_path.lower().endswith('.kmz'):
                return False
                
            return zipfile.is_zipfile(file_path)
            
        except Exception:
            return False
            
    def validate_kml_file(self, file_path: str) -> bool:
        """Validate if KML file can be imported."""
        try:
            if not file_path or not file_path.lower().endswith('.kml'):
                return False
                
            # Check if file exists and is readable
            return Path(file_path).exists()
            
        except Exception:
            return False
        
    def get_import_info(self) -> Dict[str, Any]:
        """Get information about KML/KMZ import capabilities."""
        return {
            "service": "KML/KMZ Importer",
            "version": "0.1.0",
            "supported_formats": self.get_supported_formats(),
            "status": "ready",
        }
