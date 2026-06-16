# Contributing to GeoForge Studio

Thanks for helping improve GeoForge Studio.

## Local setup

1. Create a Python environment.
2. Install dependencies from the project instructions.
3. Run the smoke test:

```bash
QT_QPA_PLATFORM=offscreen python smoke_test.py
```

## What to verify before sending changes

- ✅ App still imports
- ✅ Smoke test passes
- ✅ Import/export flows still work
- ✅ UI warnings do not crash the app

## Working rules

- Keep changes small and reversible.
- Prefer explicit warnings over silent failure.
- Do not claim GNSS/PPK readiness unless the code proves it.
- Update docs when user-facing behavior changes.

## Notes

- There is no `LICENSE` file yet.
- The repo should stay private until licensing and release posture are defined.
