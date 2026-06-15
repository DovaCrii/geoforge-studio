"""Help assistant panel for GeoForge Studio."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
)

from services.help_service import HelpService


class HelpAssistantPanel(QWidget):
    """A lightweight offline-first help assistant."""

    def __init__(self, services: dict, context_provider: Optional[Callable[[], dict]] = None):
        super().__init__()
        self.services = services
        self.context_provider = context_provider
        self.help_service = services.get("help") or HelpService()
        self._setup_ui()
        self._set_intro()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("🧭 Help Assistant")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(title)

        self.context_label = QLabel("Offline contextual help")
        self.context_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.context_label)

        self.backend_label = QLabel("Backend: static")
        self.backend_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.backend_label)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("Ask about RINEX, PPK, CRS, DXF, KMZ, volumes, or exports")
        self.question_input.returnPressed.connect(self.ask_question)
        layout.addWidget(self.question_input)

        actions = QHBoxLayout()
        ask_button = QPushButton("Ask")
        ask_button.clicked.connect(self.ask_question)
        actions.addWidget(ask_button)

        ai_button = QPushButton("Try local AI")
        ai_button.clicked.connect(self.try_local_ai)
        actions.addWidget(ai_button)

        refresh_button = QPushButton("Refresh context")
        refresh_button.clicked.connect(self.refresh_context)
        actions.addWidget(refresh_button)
        layout.addLayout(actions)

        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        self.response_view.setPlaceholderText("Answers appear here.")
        layout.addWidget(self.response_view)

    def _set_intro(self) -> None:
        self.response_view.setPlainText(
            "Ask a short question and get a lightweight offline answer.\n"
            "This panel is local-first and can later grow into an Ollama-backed helper."
        )
        self.refresh_context()

    def refresh_context(self) -> None:
        context = self._context()
        pieces = []
        if context.get("tab"):
            pieces.append(f"Tab: {context['tab']}")
        if context.get("project"):
            pieces.append(f"Project: {context['project']}")
        if context.get("crs"):
            pieces.append(f"CRS: {context['crs']}")
        self.context_label.setText(" | ".join(pieces) if pieces else "Offline contextual help")
        self.backend_label.setText(f"Backend: {self.help_service.describe_backend()}")

    def ask_question(self) -> None:
        question = self.question_input.text().strip()
        if not question:
            self.response_view.setPlainText("Type a question first.")
            return

        answer = self.help_service.answer(question, self._context())
        self.backend_label.setText(f"Backend: {answer.backend}")
        self.response_view.setPlainText(
            f"Topic: {answer.topic}\n"
            f"Backend: {answer.backend}\n\n"
            f"{answer.answer}\n\n"
            f"Suggestions: {', '.join(answer.suggestions)}"
        )

    def try_local_ai(self) -> None:
        """Prefer the local AI backend when available, otherwise fallback."""
        if hasattr(self.help_service, "set_mode"):
            self.help_service.set_mode("ollama")
        self.refresh_context()
        self.ask_question()

    def _context(self) -> dict:
        if self.context_provider:
            return self.context_provider() or {}
        return {}


__all__ = ["HelpAssistantPanel"]
