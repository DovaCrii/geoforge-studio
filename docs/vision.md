# Vision 🛰️

GeoForge Studio is a desktop-native geospatial workstation for survey and GNSS work.

It is designed to stay offline-first, readable, and focused on the core tasks survey users do repeatedly.

## First slice

GeoForge Studio currently ships with the following capabilities:

### Core Processing
- **GNSS Post-Processing**: RINEX observation and navigation file parsing, PPK algorithms
- **Volume Analysis**: TIN surface generation from survey points, cut/fill volume calculations
- **Map Visualization**: 2D map rendering with coordinate reference system support

### Import Capabilities
- **DXF Import**: Read-only import of common DXF entities (lines, polylines)
- **KMZ/KML Import**: Read-only import of KML placemarks and basic geometry

### Export Workflows
- **GeoJSON Export**: Save project survey points as GeoJSON
- **Surface DXF Export**: Save TIN surfaces as DXF 3DFACE entities
- **Map Screenshot Export**: Save the current map view as PNG

### Help Assistant
- **Local Help Assistant**: Lightweight offline contextual guidance with a future local-AI extension point

## Product intent

The app should feel professional, clear, and optimized for field-to-office workflows.
Dark mode first, geospatial accents, and a calm Apple-like visual hierarchy.

## Non-goals for now

**Known limitations and non-goals for the first release:**

- Full CAD authoring suite
- IFC-heavy workflows
- Web point-cloud viewer inside the first product
- Advanced 3D visualization
- Real-time GNSS streaming
- Cloud storage integration
- Multi-user collaboration

## Current status

GeoForge Studio is production-ready for the core survey workflow tasks listed above. The application is designed to be minimal, focused, and offline-first, with a clean user experience that prioritizes survey professionals' needs.
