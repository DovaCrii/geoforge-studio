# Design: GeoForge Studio — MVP Foundation

## Technical Approach

Hexagonal architecture: Rust processing core (`gnss-core`) exposed via PyO3/maturin, PyQt6 desktop shell. Rust owns GNSS math (RINEX parsing, PPK solution) — the highest-risk, precision-critical path. Python owns UI orchestration, DXF/KMZ import, volume computation. The map renderer is isolated behind an ABC interface for future swap to MapLibre GL. Each `openspec/specs/{domain}/spec.md` maps to one well-defined module.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Rust↔Python bridge | maturin/PyO3 vs ctypes vs subprocess | maturin: native speed, zero-copy arrays, clean Python objects | **maturin/PyO3** |
| Map rendering | QGraphicsView vs MapLibre GL (embedded web) vs custom OpenGL | QGraphicsView: no web dep, simplest MVP. MapLibre: pro look. OpenGL: most effort | **QGraphicsView** behind ABC interface |
| DXF parsing | GDAL vs ezdxf vs custom | GDAL: heavy C runtime dep. ezdxf: pure Python, sufficient for MVP entities | **ezdxf** |
| KMZ/KML parsing | GDAL vs Python stdlib | KML is XML, stdlib `xml.etree` + `zipfile` suffices | **zipfile + xml.etree** |
| Delaunay triangulation | scipy.spatial vs Rust crate | scipy already in Python geospatial env, good enough | **scipy.spatial** |
| CRS pipeline | pyproj vs Rust proj-rs | pyproj is the geospatial Python standard, mature and well-tested | **pyproj** |

## Data Flow

```
RINEX OBS/NAV ──→ gnss-core (Rust/PyO3) ──→ Raw ECEF
                       │                          │
                 Broadcast Eph. ──→ PPK ──→ PpkSolution[]
                                                │
                                        pyproj reproject
                                        (ECEF → user CRS)
                                      ╱                ╲
                               Map Canvas         Volume Tool
                            (QGraphicsView)     (scipy TIN + cut/fill)
                                      │                │
                               DXF/KMZ layers ──→ Cut/Fill Report
```

Two processing pipelines: **(1)** RINEX → Rust PPK → pyproj → Map display, **(2)** Survey points → Delaunay TIN → Cut/fill computation.

## File Changes

| File | Action | Description |
|---|---|---|
| `gnss-core/Cargo.toml` | Create | Rust crate manifest with PyO3 |
| `gnss-core/src/lib.rs` | Create | PyO3 module entry, re-exports |
| `gnss-core/src/rinex.rs` | Create | RINEX OBS/NAV parser 2.x–4.x |
| `gnss-core/src/ppk.rs` | Create | Single-baseline PPK engine |
| `gnss-core/src/ephemeris.rs` | Create | Ephemeris + orbit computation |
| `gnss-core/src/types.rs` | Create | Shared types (Epoch, Coord, Obs) |
| `gnss-core/pyproject.toml` | Create | maturin build config |
| `src/__init__.py` | Create | Package entry |
| `src/main.py` | Create | PyQt6 app bootstrap |
| `src/ui/main_window.py` | Create | Main window layout + menus |
| `src/ui/map_canvas.py` | Create | QGraphicsView map renderer |
| `src/ui/volume_panel.py` | Create | Volume results display |
| `src/services/ppk_service.py` | Create | PPK orchestration + options |
| `src/services/project_service.py` | Create | Session/state management |
| `src/importers/dxf_importer.py` | Create | ezdxf-based DXF reader |
| `src/importers/kmz_importer.py` | Create | KML/KMZ via stdlib |
| `src/volume/surface.py` | Create | TIN via scipy.spatial |
| `src/volume/calculator.py` | Create | Cut/fill math |
| `src/volume/renderer.py` | Create | TIN mesh overlay on map |
| `requirements.txt` | Create | Python dependencies |
| `pyproject.toml` | Create | Project metadata + maturin build hooks |

## Interfaces / Contracts

**Rust → Python (PyO3 surface):**

```python
def read_rinex(path: str) -> RinexObservation: ...
def compute_ppk(base_obs, rover_obs, nav, options) -> list[PpkSolution]: ...
```

**MapRenderer port (Python ABC):**

```python
class MapRenderer(ABC):
    def set_crs(self, crs: pyproj.CRS): ...
    def add_point_layer(self, id: str, pts: list[tuple], style: PointStyle): ...
    def add_overlay(self, id: str, geom: list[OverlayGeom]): ...
    def zoom_to_extents(self): ...
```

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit (Rust) | RINEX parser, PPK math, ephemeris | `cargo test` + real RINEX corpus |
| Unit (Python) | DXF/KMZ import, cut/fill, CRS | `pytest` with sample files |
| Integration | Rust↔Python FFI boundary, full PPK pipeline | `pytest` calling maturin module |
| E2E | Open file → PPK → map → volume | Manual + scripted smoke tests |
| Map | Pan, zoom, layers, toggles | QTest (PyQt6 test framework) |

## Migration / Rollout

Greenfield project — no migration required. Future MapLibre swap path preserved via `MapRenderer` interface. Feature-flag the map backend from day one.

## Open Questions

- [ ] PPK engine: clean-room implementation vs porting RTKLIB algorithms? (license risk vs development effort tradeoff)
- [ ] QGraphicsView performance ceiling for 500k+ point datasets — validate early with stress test
- [ ] PyInstaller packaging — test early in development to catch platform issues before release
- [ ] Licensing model decision needed before public launch (not MVP-blocking)
