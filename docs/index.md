# GeoForge Studio docs 🗺️

This folder is the human-readable entry point for the project.

## Quick path ✨

1. Read `vision.md`
2. Read `roadmap.md`
3. Read `openspec/config.yaml`
4. Continue with SDD exploration and proposal

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

## What is NOT included ❌

**Known limitations and non-goals for the first release:**

- Full CAD authoring suite
- IFC-heavy workflows
- Web point-cloud viewer
- Advanced 3D visualization
- Real-time GNSS streaming
- Cloud storage integration
- Multi-user collaboration

## Details

| Area | Decision |
| --- | --- |
| Product | Desktop-native GNSS and geospatial workstation |
| First slice | GNSS processing, 2D map view, DXF/KMZ import, volumes |
| Out of scope | Full CAD suite, IFC-heavy workflows, web point-cloud viewer |
| Source of truth | `openspec/` |
| Workflow | OpenSpec / SDD |

## Checklist

- [ ] I know what GeoForge Studio is trying to solve.
- [ ] I know where the planning artifacts live.
- [ ] I know the first slice and what is excluded.

## Next step

Explore export workflows and production deployment options.
