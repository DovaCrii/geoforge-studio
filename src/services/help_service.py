"""Lightweight contextual help for GeoForge Studio.

This service provides low-consumption, offline-first guidance using bundled
knowledge snippets. It is designed to be an extension point for a future
local-model backend (e.g. Ollama) without requiring it today.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class HelpAnswer:
    topic: str
    answer: str
    suggestions: List[str]
    backend: str = "static"


class HelpService:
    """Answer simple help questions from bundled knowledge snippets."""

    def __init__(self) -> None:
        self.backend = "static"
        self._topics: Dict[str, str] = {
            "rinex": (
                "RINEX files carry GNSS observation and navigation data. "
                "In GeoForge Studio, the first slice focuses on reading the file "
                "structure and keeping the core processing offline-first."
            ),
            "ppk": (
                "PPK (post-processing kinematic) combines base and rover observations "
                "with navigation data to estimate a precise baseline after collection."
            ),
            "crs": (
                "CRS handling is used to transform survey data into the working map CRS. "
                "The app currently uses pyproj for the lightweight reprojection layer."
            ),
            "dxf": (
                "DXF import is read-only and focuses on common overlay entities such as "
                "lines and polylines so survey data can be reviewed without editing."
            ),
            "kmz": (
                "KMZ/KML import is read-only and is intended for basic placemarks and "
                "overlay geometry, keeping the workflow simple and visual."
            ),
            "volume": (
                "Volume analysis uses a TIN surface plus cut/fill calculations. The UI "
                "shows the result in a compact table and supports CSV export."
            ),
            "export": (
                "GeoForge Studio now supports CSV volume export, GeoJSON project export, "
                "surface DXF export, and map PNG screenshots."
            ),
        }

    def answer(self, question: str, context: Optional[Dict[str, str]] = None) -> HelpAnswer:
        text = (question or "").strip().lower()
        topic = self._match_topic(text)
        context_lines = self._context_lines(context or {})

        if topic:
            answer = self._topics[topic]
            answer = f"{answer}\n\nContext: {context_lines}" if context_lines else answer
            suggestions = self._suggestions_for_topic(topic)
        else:
            answer = (
                "I can help with RINEX, PPK, CRS, DXF, KMZ, volumes, and exports. "
                "Ask me a short question and I will answer using the local help knowledge."
            )
            if context_lines:
                answer = f"{answer}\n\nContext: {context_lines}"
            suggestions = ["RINEX", "PPK", "CRS", "DXF", "KMZ", "Volumes", "Exports"]

        return HelpAnswer(topic=topic or "general", answer=answer, suggestions=suggestions, backend=self.backend)

    def describe_backend(self) -> str:
        return "static-local"

    def _match_topic(self, text: str) -> Optional[str]:
        for topic in self._topics:
            if topic in text:
                return topic
        if any(word in text for word in ("help", "how do i", "what is", "what does")):
            return None
        return None

    def _context_lines(self, context: Dict[str, str]) -> str:
        parts: List[str] = []
        for key in ("tab", "project", "crs", "status"):
            value = context.get(key)
            if value:
                parts.append(f"{key}: {value}")
        return " | ".join(parts)

    def _suggestions_for_topic(self, topic: str) -> List[str]:
        if topic == "export":
            return ["CSV export", "GeoJSON export", "surface DXF export", "map PNG export"]
        if topic == "volume":
            return ["TIN surface", "cut/fill", "CSV export", "surface DXF export"]
        if topic == "crs":
            return ["set CRS", "reproject points", "map export", "GeoJSON"]
        return ["RINEX", "PPK", "CRS", "DXF", "KMZ", "Exports"]


__all__ = ["HelpAnswer", "HelpService"]
