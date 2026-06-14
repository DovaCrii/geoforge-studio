## Exploration: GeoForge Studio — Product/Market Analysis & MVP Slice

### Current State

The repo contains documentation and OpenSpec bootstrap artifacts only. No code has been written. The `openspec/config.yaml` lists no detected stack, no test runner, no build tool. The `state.yaml` marks the change as `phase: explore`.

The documented product intent is a desktop-native geospatial workstation focused on GNSS processing, 2D map visualization, DXF/KMZ import, and volume workflows. A separate web point-cloud/IFC viewer is explicitly deferred.

### Competitive Landscape

| Product | GNSS Post-Processing | 2D Map/Viewer | DXF/KMZ Import | Volume Calc | Price |
|---------|---------------------|---------------|----------------|-------------|-------|
| **Emlid Studio** | ✅ Excellent (PPK, static, stop&go, drone) | ❌ Plot only | ❌ None | ❌ None | Free |
| **Trimble Business Center** | ✅ Full suite (GNSS, adjustments, networks) | ✅ Full CAD/GIS | ✅ Full import/export | ✅ Surfaces, corridors, cut/fill | $$$$ (hundreds+/yr) |
| **QGIS** | ❌ None (live NMEA only via plugins) | ✅ Excellent GIS | ✅ Plugin-based | ⚠️ Basic via plugins | Free |
| **Global Mapper** | ❌ None (confirmed no GNSS PP support) | ✅ Good GIS | ✅ Good import | ✅ Excellent terrain/volume | $595/$1,495 perpetual |
| **GeoForge Studio (proposed)** | ✅ Hardware-agnostic RINEX PPK | ✅ Survey-native 2D map | ✅ Native DXF/KMZ | ✅ Integrated volume tool | TBD |

### Market Gap

No existing product occupies this intersection:

1. **Emlid Studio** is the closest for GNSS processing, but it's locked to Emlid hardware, has zero map visualization, and no volume or CAD capabilities. It's a post-processor, not a workstation.
2. **TBC** does everything, but at enterprise pricing and complexity that excludes independent surveyors and small firms. Windows-only.
3. **QGIS** has no GNSS processing — users must switch to Emlid Studio or RTKLIB for PPK, then export to QGIS for mapping. The context switch is friction.
4. **Global Mapper** has excellent volume and terrain tools but zero GNSS post-processing — same workflow gap.

**The gap**: A hardware-agnostic desktop app that takes RINEX/UBX from any receiver brand, post-processes to fixed coordinates, renders the results on a survey-oriented 2D map with DXF/KMZ overlay, and computes volumes — all in one offline-first session. No tool does this today at a reasonable price point.

### Affected Areas

- `openspec/config.yaml` — Needs stack selection, build tools, testing framework detected
- `openspec/specs/` — Empty; needs domain specs for GNSS, map, import, volumes
- `src/` — Does not exist yet; whole application to be built
- `mkdocs.yml` — Will need expansion as architecture docs grow

### Approaches for MVP

1. **Cross-platform native (C++/Qt or Rust/egui or Rust+wgpu/Qt)** — Best for performance with geospatial data, offline processing, native file I/O
   - Pros: Performance for large RINEX files, real native feel, GPU-accelerated map rendering, offline-first by nature
   - Cons: Longer build cycles, smaller ecosystem for geospatial widgets, harder to find contributors
   - Effort: High

2. **Electron/web-based with WebGL map rendering (Leaflet/MapLibre)** — Fastest to prototype, broad hardware support
   - Pros: Rapid UI iteration, huge ecosystem, MapLibre/Leaflet mature for 2D maps, cross-platform trivially
   - Cons: Memory constraints with large geospatial datasets, JS GC pauses during heavy computation, Electron memory footprint, harder to justify "pro" pricing for what feels like a web app
   - Effort: Medium

3. **Python desktop (PyQt/PySide + modern GPU backend)** — Sweet spot for geospatial workflows, rapid iteration
   - Pros: GDAL/rasterio/shapely/pyproj ecosystem is unmatched for geospatial data handling, fast prototyping, can fall back to C++/Rust extensions for hot paths (RINEX processing)
   - Cons: Python packaging/distribution is painful, startup time slower, GIL can bite on multi-core processing
   - Effort: Medium

### Recommendation

**Approach 3 (Python desktop)** as the pragmatic choice, with a clear migration path:

- Use **Rust** (via PyO3/maturin) for the GNSS RINEX processing core — this is the computationally intensive, precision-critical path
- Use **PyQt6** for the desktop UI — mature, native-feeling, works offline
- Use **Modern OpenGL/MapLibre GL Native bindings** or a lightweight Qt-based map widget for 2D map rendering (avoids Electron memory overhead)
- This gives the "native, professional" feel of TBC at a fraction of the complexity, with the geospatial Python ecosystem for format handling (GDAL for DXF, pyproj for coordinate transforms)

**Narrowest viable MVP slice**:

```
Phase 1 MVP — "Single Pile, Single Plot"
├── RINEX observation file reader (any brand, OBS/NAV)
├── Simple PPK engine (single baseline, float+fixed, L1-only first)
├── Result display on 2D map (points + track, CRS-aware)
├── DXF background overlay import (read-only)
├── KMZ overlay import (read-only)
└── Basic volume tool (surface from points, single cut/fill)
```

This slice targets the exact pain point: a surveyor returns from the field with raw GNSS logs and a topo of a stockpile, needs to post-process, see it on a map with the design DXF, and compute the volume — without opening three different applications.

What it explicitly NOT for MVP:
- Network/adjustment engine (TBC-level least squares)
- Full CAD drafting
- Point cloud processing
- Raster/orthophoto support
- Real-time GNSS/RTK (post-processing only)

### Risks

- **Stack lock-in risk**: Choosing Python+PyQt early is reversible for the UI layer but committing to a map rendering approach is harder to change. Must isolate rendering behind an interface.
- **RINEX parsing complexity**: RINEX 3.x and 4.x have significant variations. A naive parser will break on real-world files from Trimble, Leica, and Septentrio receivers. Must test against a corpus of diverse files.
- **PPK engine correctness**: RTKLIB exists as reference but is GPL-licensed. Writing a clean-room PPK engine is research-grade work — Kalman filter, ambiguity resolution, tropospheric models. This is the single highest-risk component.
- **Surveyor expectations**: Users coming from TBC expect least-squares network adjustments, not just single-baseline PPK. Must set clear expectations.
- **DXF import complexity**: DXF has 20+ years of spec variations, entity types, and extended data. Even "read-only" import is non-trivial.
- **Platform distribution**: If Python-based, packaging for Windows/macOS/Linux without requiring Python runtime is essential. PyInstaller/Nuitka/AppImage all have failure modes.

### Ready for Proposal

Yes. The market gap is well-defined and defensible. The MVP slice is clearly scoped. The biggest open question is **final stack commitment** (especially map rendering approach) — recommend that the proposal phase either confirms the Python+Rust+PyQt approach or picks an alternative with clear tradeoffs.

**Most important product decisions to settle in proposal**:

1. **Stack**: Python+Rust+PyQt6 (recommended) vs C++/Qt vs Electron
2. **PPK engine**: Build from scratch (clean-room) vs wrap RTKLIB (GPL — may force open-source) vs license a commercial engine
3. **Map rendering**: Qt-native custom widget vs MapLibre GL Native bindings vs embedded web view
4. **Licensing model**: Open-core (free GNSS, paid volumes/maps) vs commercial-only vs source-available
5. **Distribution**: Native installers vs AppImage/DMG/NSIS vs pip install

### Open Questions

- Should the first MVP release target a specific GNSS receiver(s) for validation, or truly hardware-agnostic from day one?
- What is the target price point? (Emlid Studio is free, TBC is ~$3K+/yr — the gap is wide)
- Is there an existing PPK library that can be used under a permissive license, or must we build from scratch?
