# Proposal: GeoForge Studio — MVP Foundation

## Intent

Close the gap between Emlid Studio (hardware-locked, no maps/volumes) and TBC (enterprise-priced, Windows-only). One offline tool for GNSS processing, 2D map visualization with DXF/KMZ overlays, and volume computation.

## Scope

### In Scope
- RINEX OBS/NAV reader — any brand, 2.x–4.x
- Single-baseline PPK — float + fixed ambiguity, L1
- CRS-aware 2D map, points + track display
- DXF overlay import — read-only
- KMZ/KML overlay import — read-only
- Volume tool — TIN surface, single cut/fill

### Out of Scope
- Network/adjustment LS, CAD drafting
- Point cloud, raster, orthophoto, RTK
- Web point-cloud viewer (separate project)

## Capabilities

### New Capabilities
- `rinex-reader`: Parse RINEX OBS/NAV 2.x–4.x
- `ppk-engine`: Single-baseline PPK, ambiguity resolution
- `map-visualization`: 2D survey map, CRS reprojection
- `dxf-import`: Read-only DXF overlay
- `kmz-import`: Read-only KMZ/KML overlay
- `volume-tool`: TIN surface + cut/fill

### Modified Capabilities
None.

## Approach

Python + PyQt6 (UI), Rust + maturin (GNSS core). Map rendering behind interface — Qt-native vs MapLibre GL. GDAL for DXF, pyproj for CRS.

## Proposal Question Round

5 open decisions — correct these before specs:

| Decision | Tentative | Alt |
|----------|-----------|-----|
| Stack | Python+PyQt6+Rust | C++/Qt, Electron |
| PPK | Clean-room vs RTKLIB | Wrap RTKLIB, license comm. |
| Map | Qt-native (interface) | MapLibre GL, embedded web |
| License | TBD before public launch | Open-core, comm., source-avail |
| Dist | PyInstaller/NSIS/AppImage | pip, conda |

## Risks

| Risk | L | Mitigation |
|------|---|------------|
| PPK correctness | High | RTKLIB corpus; incremental tests |
| RINEX parser fragility | Med | Test 3+ receiver brands |
| DXF spec variance | Med | Common entities first; document gaps |
| Map rendering rework | Med | Interface isolation enables swap |
| Python packaging | Med | Validate PyInstaller early |

## Rollback Plan

No deployed code. If PPK stalls: permissive library. If PyQt6 blocks: C++/Qt reusing Rust core. If stack fails: Rust CLI + Electron UI.

## Dependencies

- Rust + maturin (PyO3 GNSS core), GDAL (DXF I/O)
- pyproj + PROJ (CRS), PyQt6 (desktop)

## Success Criteria

- [ ] RINEX from 3+ brands parses cleanly
- [ ] PPK fixed solution within 5 cm of RTKLIB
- [ ] Points render on CRS-aware 2D map
- [ ] DXF + KMZ overlays display on map
- [ ] Volume cut/fill matches manual check
- [ ] All features work fully offline
