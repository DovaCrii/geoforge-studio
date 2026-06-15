"""Project service for managing GeoForge Studio projects.

This module provides functionality for creating, loading, and managing
GNSS processing projects with their associated data and settings.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

@dataclass
class SurveyPoint:
    """Represents a survey point with GNSS coordinates."""
    
    id: str
    name: str
    x: float
    y: float
    z: float
    crs: str = "EPSG:4978"
    remarks: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "crs": self.crs,
            "remarks": self.remarks,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SurveyPoint':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            z=data["z"],
            crs=data.get("crs", "EPSG:4978"),
            remarks=data.get("remarks", ""),
        )

@dataclass
class Project:
    """Represents a GeoForge Studio project."""
    
    name: str
    path: str
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    points: List[SurveyPoint] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    
    def add_point(self, point: SurveyPoint):
        """Add a survey point to the project."""
        self.points.append(point)
        self.modified_at = datetime.now()
        
    def remove_point(self, point_id: str):
        """Remove a survey point from the project."""
        self.points = [p for p in self.points if p.id != point_id]
        self.modified_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "path": self.path,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "points": [p.to_dict() for p in self.points],
            "settings": self.settings,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create from dictionary representation."""
        project = cls(
            name=data["name"],
            path=data["path"],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            points=[SurveyPoint.from_dict(p) for p in data["points"]],
            settings=data.get("settings", {}),
        )
        return project

class ProjectService:
    """Service for managing projects."""
    
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.recent_projects: List[str] = []
        
    def create_project(self, name: str, path: str) -> Project:
        """Create a new project."""
        project = Project(name=name, path=path)
        self.current_project = project
        self.recent_projects.append(path)
        return project
        
    def load_project(self, path: str) -> Project:
        """Load a project from file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Project file not found: {path}")
            
        with open(path, 'r') as f:
            data = json.load(f)
            
        project = Project.from_dict(data)
        self.current_project = project
        self.recent_projects.append(path)
        return project
        
    def save_project(self, project: Optional[Project] = None) -> bool:
        """Save a project to file."""
        if project is None:
            if self.current_project is None:
                raise ValueError("No project to save")
            project = self.current_project
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(project.path), exist_ok=True)
        
        # Save project
        with open(project.path, 'w') as f:
            json.dump(project.to_dict(), f, indent=2)
            
        return True
        
    def get_current_project(self) -> Optional[Project]:
        """Get the current project."""
        return self.current_project
        
    def set_current_project(self, project: Project):
        """Set the current project."""
        self.current_project = project
        
    def get_recent_projects(self) -> List[str]:
        """Get recent projects."""
        return self.recent_projects.copy()
        
    def clear_recent_projects(self):
        """Clear recent projects list."""
        self.recent_projects.clear()
        
    def export_project(self, project: Optional[Project] = None, format: str = "json") -> str:
        """Export project to different format."""
        if project is None:
            if self.current_project is None:
                raise ValueError("No project to export")
            project = self.current_project
            
        if format.lower() == "json":
            return json.dumps(project.to_dict(), indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")