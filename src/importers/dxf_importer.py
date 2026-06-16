"""DXF importer for GeoForge Studio.

This module provides functionality for importing DXF files as overlays
on the map canvas. Currently supports read-only import of common DXF entities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math
import ezdxf
from ezdxf.math import Vec3

@dataclass
class DxfEntity:
    """Represents a DXF entity."""
    
    handle: str
    layer: str
    type: str
    points: List[Tuple[float, float, float]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "handle": self.handle,
            "layer": self.layer,
            "type": self.type,
            "points": self.points,
            "attributes": self.attributes,
        }

@dataclass
class DxfImportResult:
    """Result of DXF import operation."""
    
    success: bool
    entities: List[DxfEntity] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    message: str = ""
    file_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "entities": [e.to_dict() for e in self.entities],
            "warnings": self.warnings,
            "message": self.message,
            "file_path": self.file_path,
        }

class DxfImporter:
    """Importer for DXF files."""
    
    def __init__(self):
        self.supported_entities = {
            "LINE", "LWPOLYLINE", "POLYLINE", "CIRCLE", "ARC", "ELLIPSE"
        }
        self.supported_layers = {
            "GROUND", "SURVEY", "POINTS", "CONTOURS", "OVERLAY"
        }
        
    def import_dxf(self, file_path: str) -> DxfImportResult:
        """Import DXF file and return entities."""
        warnings: List[str] = []
        
        try:
            # Validate file exists
            if not file_path:
                return DxfImportResult(
                    success=False,
                    message="No file path provided",
                    file_path=file_path
                )
            
            from pathlib import Path
            if not Path(file_path).exists():
                return DxfImportResult(
                    success=False,
                    message=f"File not found: {file_path}",
                    file_path=file_path
                )
            
            if not file_path.lower().endswith('.dxf'):
                return DxfImportResult(
                    success=False,
                    message="File is not a DXF file (needs .dxf extension)",
                    file_path=file_path
                )
                
            # Try to read DXF file
            try:
                doc = ezdxf.readfile(file_path)
            except ezdxf.DXFStructureError as e:
                return DxfImportResult(
                    success=False,
                    message=f"Invalid or corrupted DXF file: {e}",
                    file_path=file_path
                )
            
            if doc is None:
                return DxfImportResult(
                    success=False,
                    message="Failed to read DXF file (returned empty)",
                    file_path=file_path
                )
                
            entities = []
            skipped_unsupported = 0
            skipped_layer = 0
            skipped_error = 0
            
            # Process modelspace entities
            for entity in doc.modelspace():
                entity_type = entity.dxftype()
                
                if entity_type not in self.supported_entities:
                    skipped_unsupported += 1
                    continue

                entity_layer = getattr(entity.dxf, "layer", "")
                if entity_layer not in self.supported_layers:
                    skipped_layer += 1
                    continue

                # Extract entity data with per-entity error handling
                try:
                    points = self._extract_points(entity)
                    if not points:
                        warnings.append(f"Skipped {entity_type} on layer '{entity_layer}' — no points extracted")
                        skipped_error += 1
                        continue
                    
                    entity_data = DxfEntity(
                        handle=str(entity.dxf.handle),
                        layer=entity_layer,
                        type=entity_type,
                        points=points,
                        attributes=self._extract_attributes(entity)
                    )
                    entities.append(entity_data)
                except Exception as e:
                    warnings.append(f"Skipped {entity_type} (handle {getattr(entity.dxf, 'handle', '?')}): {e}")
                    skipped_error += 1
            
            # Build summary message
            parts = [f"Imported {len(entities)} entities"]
            if skipped_unsupported:
                parts.append(f"{skipped_unsupported} unsupported types skipped")
            if skipped_layer:
                parts.append(f"{skipped_layer} skipped by layer filter")
            if skipped_error:
                parts.append(f"{skipped_error} skipped due to errors")
            
            return DxfImportResult(
                success=True,
                entities=entities,
                warnings=warnings,
                message="; ".join(parts),
                file_path=file_path
            )
            
        except Exception as e:
            return DxfImportResult(
                success=False,
                warnings=warnings,
                message=f"Error importing DXF file: {str(e)}",
                file_path=file_path
            )
            
    def _extract_points(self, entity) -> List[Tuple[float, float, float]]:
        """Extract points from DXF entity."""
        points = []
        
        if entity.dxftype() == "LINE":
            points = [
                (entity.dxf.start.x, entity.dxf.start.y, 0.0),
                (entity.dxf.end.x, entity.dxf.end.y, 0.0)
            ]
        elif entity.dxftype() in ("LWPOLYLINE", "POLYLINE"):
            for vertex in entity.vertices:
                points.append((vertex.dxf.x, vertex.dxf.y, 0.0))
        elif entity.dxftype() == "CIRCLE":
            center = (entity.dxf.center.x, entity.dxf.center.y, 0.0)
            radius = entity.dxf.radius
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x = center[0] + radius * math.cos(rad)
                y = center[1] + radius * math.sin(rad)
                points.append((x, y, 0.0))
        elif entity.dxftype() == "ARC":
            center = (entity.dxf.center.x, entity.dxf.center.y, 0.0)
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            
            for angle in range(int(start_angle), int(end_angle) + 1, 30):
                rad = math.radians(angle)
                x = center[0] + radius * math.cos(rad)
                y = center[1] + radius * math.sin(rad)
                points.append((x, y, 0.0))
            
        return points
        
    def _extract_attributes(self, entity) -> Dict[str, Any]:
        """Extract attributes from DXF entity."""
        attributes = {}
        
        try:
            if hasattr(entity.dxf, 'color'):
                attributes['color'] = entity.dxf.color
            if hasattr(entity.dxf, 'linetype'):
                attributes['linetype'] = entity.dxf.linetype
            if hasattr(entity.dxf, 'linewidth'):
                attributes['linewidth'] = entity.dxf.linewidth
                
        except Exception:
            pass
            
        return attributes
        
    def get_supported_entities(self) -> List[str]:
        """Get list of supported DXF entity types."""
        return list(self.supported_entities)
        
    def get_supported_layers(self) -> List[str]:
        """Get list of supported DXF layers."""
        return list(self.supported_layers)
        
    def validate_dxf_file(self, file_path: str) -> bool:
        """Validate if DXF file can be imported."""
        try:
            if not file_path or not file_path.endswith('.dxf'):
                return False
                
            doc = ezdxf.readfile(file_path)
            return doc is not None
            
        except Exception:
            return False
        
    def get_import_info(self) -> Dict[str, Any]:
        """Get information about DXF import capabilities."""
        return {
            "service": "DXF Importer",
            "version": "0.1.0",
            "supported_entities": self.get_supported_entities(),
            "supported_layers": self.get_supported_layers(),
            "status": "ready",
        }
