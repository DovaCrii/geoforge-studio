# GeoForge Studio docs 🗺️

Start here when you need the current product shape, the stack, or the delivery plan.

## Quick path

1. `vision.md` — what the product is for
2. `architecture.md` — how the app is put together
3. `roadmap.md` — what must ship next
4. `CONTRIBUTING.md` — how to run and verify locally

## Current state

| Area | Status |
|---|---|
| Map + overlays | Working |
| DXF / KMZ import | Working |
| Exports | Working |
| Help assistant | Working |
| GNSS / PPK core | In progress |

## Non-goals for now

- Full CAD authoring suite
- IFC-heavy workflows
- Web point-cloud viewer inside this product
- Advanced 3D visualization
- Real-time GNSS streaming

## Where decisions live

| Topic | File |
|---|---|
| Product intent | `vision.md` |
| Stack and boundaries | `architecture.md` |
| Delivery order | `roadmap.md` |
| Local setup | `CONTRIBUTING.md` |
| SDD artifacts | `openspec/` |

## Notes

- Keep the docs honest: do not overclaim GNSS/PPK readiness.
- Prefer warnings and graceful fallback over hard failure.
- Use icons sparingly; they should help scanning, not decorate everything.
