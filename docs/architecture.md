# Architecture 🧩

GeoForge Studio uses a simple desktop stack with clear boundaries: UI in Python, geospatial helpers in Python modules, and a Rust/PyO3 GNSS core.

## Stack

| Layer | Technology | Role |
|---|---|---|
| UI | PyQt6 | Main window, map canvas, volume panel, help assistant |
| Geospatial logic | Python | Importers, exporters, CRS utilities, volume workflow |
| GNSS core | Rust + PyO3 | RINEX / PPK / ephemeris foundation |
| Math / geometry | scipy, pyproj, ezdxf | TIN, coordinate transforms, DXF handling |

## Main boundaries

| Module | Responsibility |
|---|---|
| `src/ui/main_window.py` | App shell, menus, actions, tab routing |
| `src/ui/map_canvas.py` | Map rendering, overlays, zoom, clear/reset |
| `src/ui/help_assistant.py` | Contextual help panel and backend selection |
| `src/importers/*` | Read-only DXF and KMZ/KML import |
| `src/exporters/*` | GeoJSON and DXF surface export |
| `src/volume/*` | TIN and cut/fill calculations |
| `gnss-core/*` | Native GNSS processing bridge |

## Data flow

1. User imports data or loads a project.
2. Importers normalize geometry and metadata.
3. The map canvas renders overlays or points.
4. Volume tools build a TIN and compute cut/fill.
5. Exporters write handoff formats for downstream use.

## UX safety rules

- Missing inputs should trigger warnings, not crashes.
- Failed imports should preserve the current view.
- Heavy GNSS work should be isolated from the UI thread.

## License and release note

The repo is licensed under Apache-2.0. Keep the repo private until the release posture is decided.
