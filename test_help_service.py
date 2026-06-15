#!/usr/bin/env python3
"""Test lightweight help assistant functionality for GeoForge Studio."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> int:
    from services.help_service import HelpService

    service = HelpService()
    answer = service.answer("What is PPK?", {"tab": "Help Assistant", "project": "Demo"})

    assert answer.topic == "ppk"
    assert "Context:" in answer.answer
    print("Help service OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
