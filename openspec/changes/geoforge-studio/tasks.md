# Tasks: GeoForge Studio — MVP Foundation

## Review Workload Forecast

- Estimated changed lines: 1200–1600
- Chained PRs recommended: Yes
- Decision needed before apply: Yes
- First slice: Foundation + GNSS core + app shell

## 1. Foundation and build system

- [x] 1.1 Create the Python package skeleton and project metadata.

  - Create `pyproject.toml`.
  - Create `requirements.txt`.
  - Create `src/__init__.py`.

- [x] 1.2 Create the Rust core crate and maturin bridge.

  - Create `gnss-core/Cargo.toml`.
  - Create `gnss-core/pyproject.toml`.
  - Create `gnss-core/src/lib.rs`.
  - Create shared Rust types in `gnss-core/src/types.rs`.

- [x] 1.3 Create the desktop app bootstrap.

  - Create `src/main.py`.
  - Create `src/ui/main_window.py`.

## 2. GNSS core pipeline

- [x] 2.1 Implement RINEX domain types and parsing entry points.

  - Add parser module boundaries.
  - Add reading contracts for OBS/NAV 2.x–4.x.

- [ ] 2.2 Implement single-baseline PPK flow.

  - Add orbit/ephemeris module.
  - Add ambiguity-resolution pipeline.
  - Expose a Python-callable API via PyO3.

- [ ] 2.3 Add core validation fixtures and tests.

  - Add real RINEX samples.
  - Add Rust unit tests for parser and solver.

## 3. UI shell and map view

3.1 Create the map renderer abstraction.

- Add `MapRenderer` interface.
- Add Qt-native `QGraphicsView` backend.

3.2 Create the main geospatial workspace.

- Add project/session orchestration service.
- Add map panel and results panel.

3.3 Add CRS handling.

- Integrate `pyproj`.
- Ensure coordinates reproject correctly to the user CRS.

## 4. Import layers

4.1 Add DXF overlay import (read-only).

- Create `src/importers/dxf_importer.py`.
- Validate supported common entities.

4.2 Add KMZ/KML overlay import (read-only).

- Create `src/importers/kmz_importer.py`.
- Handle zipped KML + basic placemark geometry.

## 5. Volume workflow

5.1 Add TIN surface generation.

- Create `src/volume/surface.py`.
- Generate triangulation from survey points.

5.2 Add cut/fill calculations and display.

- Create `src/volume/calculator.py`.
- Create `src/ui/volume_panel.py`.
- Create `src/volume/renderer.py`.

## 6. Verification and docs

6.1 Add sample datasets and smoke checks.

- Add small RINEX/DXF/KMZ fixtures.
- Add an end-to-end manual smoke path.

6.2 Update public docs after implementation.

- Keep README and docs aligned with shipped capabilities.
- Document limitations and non-goals clearly.
