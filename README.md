# GeoForge Studio 🛰️

Desktop-native geospatial workstation for GNSS and survey workflows.

GeoForge Studio starts with a focused first slice:

- GNSS post-processing (RINEX parsing, PPK algorithms)
- 2D map visualization with CRS support
- DXF / KMZ import (read-only overlays)
- Volume calculations (TIN surfaces, cut/fill analysis)

## Why this exists 🌍

The goal is to bridge the gap between rigid GNSS tools and heavy GIS/CAD suites.
The first release is intentionally narrow: do the core survey work well, keep it offline,
and make the UX clean.

## Current capabilities ✅

GeoForge Studio currently ships with the following functionality:

### Core Processing
- **GNSS Post-Processing**: RINEX observation and navigation file parsing, PPK algorithms
- **Volume Analysis**: TIN surface generation from survey points, cut/fill volume calculations
- **Map Visualization**: 2D map rendering with coordinate reference system support

### Import Capabilities
- **DXF Import**: Read-only import of common DXF entities (lines, polylines)
- **KMZ/KML Import**: Read-only import of KML placemarks and basic geometry

### Development & Testing
- **Smoke Testing**: End-to-end verification with sample datasets
- **Fixtures**: Sample RINEX, DXF, and KMZ files for testing

### Export Workflows
- **GeoJSON Export**: Save project survey points as GeoJSON
- **Surface DXF Export**: Save TIN surfaces as DXF 3DFACE entities
- **Map Screenshot Export**: Save the current map view as PNG

### Help Assistant
- **Local Help Assistant**: Lightweight offline contextual guidance with a future local-AI extension point

## What is NOT included ❌

**Known limitations and non-goals for the first release:**

- Full CAD authoring suite
- IFC-heavy workflows
- Web point-cloud viewer
- Advanced 3D visualization
- Real-time GNSS streaming
- Cloud storage integration
- Multi-user collaboration

## Reading path 📚

1. `docs/index.md` — project overview and navigation
2. `docs/vision.md` — product scope and non-goals
3. `docs/roadmap.md` — phased delivery plan
4. `openspec/` — SDD proposal/spec/design/tasks source of truth

## Structure 🧭

| Path | Purpose |
| --- | --- |
| `docs/` | Human-readable docs (local + GitHub) |
| `openspec/` | SDD artifacts and active change state |
| `.atl/` | Agent/skill registry for the workflow |

## Visual language 🎨

- Dark, elegant, minimal UI
- Geospatial accents, not noisy colors
- Drone / survey symbolism used sparingly
- Clean spacing, soft cards, subtle contrast

## Status

- Public repo: GitHub
- Branch: `main`
- Released: GeoForge Studio v0.1.0

## Next step 🚀

Explore export workflows and production deployment options.
