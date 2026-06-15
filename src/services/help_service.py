"""Lightweight contextual help for GeoForge Studio.

Offline-first by default, with an optional local Ollama backend when available.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib import error, request


@dataclass
class HelpAnswer:
    topic: str
    answer: str
    suggestions: List[str]
    backend: str = "static"


class StaticHelpBackend:
    """Bundled help knowledge, zero runtime cost."""

    def __init__(self) -> None:
        self._topics: Dict[str, str] = {
            "rinex": (
                "RINEX files carry GNSS observation and navigation data. GeoForge Studio "
                "keeps the first slice focused on reading the structure offline."
            ),
            "ppk": (
                "PPK (post-processing kinematic) combines base and rover observations "
                "with navigation data to estimate a precise baseline after collection."
            ),
            "crs": (
                "CRS handling transforms survey data into the working map CRS. The app "
                "uses pyproj for the lightweight reprojection layer."
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
                "GeoForge Studio supports CSV volume export, GeoJSON project export, "
                "surface DXF export, and map PNG screenshots."
            ),
        }

    def answer(self, question: str, context: Optional[Dict[str, str]] = None) -> HelpAnswer:
        text = (question or "").strip().lower()
        topic = self._match_topic(text)
        context_lines = self._context_lines(context or {})

        if topic:
            answer = self._topics[topic]
            if context_lines:
                answer = f"{answer}\n\nContext: {context_lines}"
            suggestions = self._suggestions_for_topic(topic)
        else:
            answer = (
                "I can help with RINEX, PPK, CRS, DXF, KMZ, volumes, exports, and the "
                "help assistant itself. Ask a short question and I will answer from the "
                "bundled local knowledge."
            )
            if context_lines:
                answer = f"{answer}\n\nContext: {context_lines}"
            suggestions = ["RINEX", "PPK", "CRS", "DXF", "KMZ", "Volumes", "Exports"]

        return HelpAnswer(topic=topic or "general", answer=answer, suggestions=suggestions, backend="static")

    def describe_backend(self) -> str:
        return "static-local"

    def _match_topic(self, text: str) -> Optional[str]:
        for topic in self._topics:
            if topic in text:
                return topic
        return None

    def _context_lines(self, context: Dict[str, str]) -> str:
        parts: List[str] = []
        labels = {
            "tab": "tab",
            "project": "project",
            "crs": "CRS",
            "status": "status",
        }
        for key in ("tab", "project", "crs", "status"):
            value = context.get(key)
            if value:
                parts.append(f"{labels[key]} {value}")
        return "; ".join(parts)

    def _suggestions_for_topic(self, topic: str) -> List[str]:
        if topic == "export":
            return ["CSV export", "GeoJSON export", "surface DXF export", "map PNG export"]
        if topic == "volume":
            return ["TIN surface", "cut/fill", "CSV export", "surface DXF export"]
        if topic == "crs":
            return ["set CRS", "reproject points", "map export", "GeoJSON"]
        return ["RINEX", "PPK", "CRS", "DXF", "KMZ", "Exports"]


class OllamaHelpBackend:
    """Optional local AI backend via Ollama localhost HTTP API."""

    def __init__(self, model: str = "qwen2.5:0.5b", url: str = "http://localhost:11434/api/chat") -> None:
        self.model = model
        self.url = url

    def is_available(self) -> bool:
        try:
            req = request.Request(self.url.replace("/api/chat", "/api/tags"), method="GET")
            with request.urlopen(req, timeout=0.5):
                return True
        except Exception:
            return False

    def answer(self, question: str, context: Optional[Dict[str, str]] = None) -> HelpAnswer:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are GeoForge Studio's lightweight help assistant. "
                        "Be concise, practical, and avoid long answers. Focus on GNSS, "
                        "RINEX, PPK, CRS, DXF, KMZ, volumes, exports, and app navigation."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(question, context or {}),
                },
            ],
        }

        req = request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with request.urlopen(req, timeout=6.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        content = data.get("message", {}).get("content") or data.get("response") or ""
        if not content.strip():
            raise RuntimeError("Ollama returned an empty response")

        topic = self._infer_topic(question)
        return HelpAnswer(
            topic=topic,
            answer=content.strip(),
            suggestions=["RINEX", "PPK", "CRS", "DXF", "KMZ", "Exports"],
            backend=f"ollama:{self.model}",
        )

    def describe_backend(self) -> str:
        return f"ollama:{self.model}"

    def _build_prompt(self, question: str, context: Dict[str, str]) -> str:
        context_bits = []
        for key in ("tab", "project", "crs", "status"):
            value = context.get(key)
            if value:
                context_bits.append(f"{key}: {value}")
        context_text = " | ".join(context_bits) if context_bits else "no extra context"
        return (
            f"Question: {question}\n"
            f"Context: {context_text}\n\n"
            "Answer in a concise way. If the user asks about app behavior, explain the steps. "
            "If the user asks about concepts, explain them simply. Prefer bullet points when helpful."
        )

    def _infer_topic(self, question: str) -> str:
        text = (question or "").lower()
        for topic in ("rinex", "ppk", "crs", "dxf", "kmz", "volume", "export"):
            if topic in text:
                return topic
        return "general"


class HelpService:
    """Answer help questions from static knowledge or optional local AI."""

    def __init__(self, mode: Optional[str] = None, model: Optional[str] = None) -> None:
        self.static_backend = StaticHelpBackend()
        self.ollama_backend = OllamaHelpBackend(model=model or os.getenv("GEOFORGE_HELP_OLLAMA_MODEL", "qwen2.5:0.5b"))
        self.mode = (mode or os.getenv("GEOFORGE_HELP_BACKEND", "static")).strip().lower()

    def set_mode(self, mode: str) -> None:
        self.mode = (mode or "static").strip().lower()

    def describe_backend(self) -> str:
        if self.mode == "ollama":
            return self.ollama_backend.describe_backend()
        if self.mode == "auto":
            return "auto(static→ollama)"
        return self.static_backend.describe_backend()

    def available_backends(self) -> List[str]:
        backends = ["static"]
        if self.ollama_backend.is_available():
            backends.append("ollama")
        return backends

    def answer(self, question: str, context: Optional[Dict[str, str]] = None) -> HelpAnswer:
        if self.mode == "ollama":
            try:
                return self.ollama_backend.answer(question, context)
            except Exception:
                answer = self.static_backend.answer(question, context)
                answer.backend = "static-fallback"
                return answer

        if self.mode == "auto" and self.ollama_backend.is_available():
            try:
                return self.ollama_backend.answer(question, context)
            except Exception:
                pass

        return self.static_backend.answer(question, context)

    def active_label(self) -> str:
        if self.mode == "ollama":
            return self.ollama_backend.describe_backend()
        if self.mode == "auto":
            return f"auto ({self.ollama_backend.describe_backend()} fallback)"
        return self.static_backend.describe_backend()


__all__ = ["HelpAnswer", "HelpService", "StaticHelpBackend", "OllamaHelpBackend"]
