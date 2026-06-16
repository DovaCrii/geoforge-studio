# GeoForge Studio 🛰️

Desktop-native geospatial workstation for GNSS, survey, and volume workflows.

## Snapshot

| Area | Status |
|---|---|
| Map + overlays | ✅ Working |
| DXF / KMZ import | ✅ Working |
| Exports | ✅ Working |
| Help assistant | ✅ Working |
| GNSS / PPK core | ⚠️ In progress |
| License | Apache-2.0 |

## What works today

- 🗺️ 2D map visualization with CRS support
- 📥 Read-only DXF / KMZ / KML import as overlays
- 📤 GeoJSON, surface DXF, CSV, and PNG exports
- 📊 Volume analysis with TIN cut/fill calculations
- 🧭 Local offline help assistant with backend selection
- 🧪 Smoke tests and fixture-based verification

## What is still in progress

- GNSS/RINEX parsing and PPK engine are not production-grade yet
- Project persistence is still being hardened
- Commercial packaging is still evolving

## UI panels

| Panel | What it does |
|---|---|
| Map workspace | Shows survey points and imported overlays |
| Volume analysis | Calculates cut/fill from TIN surfaces |
| Help assistant | Gives contextual guidance without leaving the app |

## Product principles

- Offline-first by default
- Fail with warnings, not with crashes
- Keep missing inputs visible to the user
- Prefer clear, minimal UI over feature clutter

## Docs path

1. `docs/vision.md` — product intent and non-goals
2. `docs/architecture.md` — stack and module boundaries
3. `docs/roadmap.md` — real delivery priorities
4. `CONTRIBUTING.md` — local setup and workflow
5. `openspec/` — SDD source of truth

## Release posture

This repository can stay **private** while the GNSS/PPK core matures.
The repo is now licensed under Apache-2.0.

## Visual language

- Dark, elegant, minimal
- Geospatial accents, not noisy colors
- Clean spacing and soft contrast
- Symbols/icons used sparingly for scanability
