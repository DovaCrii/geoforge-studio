# KMZ/KML Import Specification

## Purpose

Import KMZ (compressed Keyhole Markup Language) and KML files for read-only overlay display on the 2D survey map. Supports placemarks, paths, and polygons.

## Requirements

### Requirement: Import KMZ and KML files

The system MUST read both `.kml` (XML) and `.kmz` (compressed ZIP containing KML) files, extracting geometry for overlay display.

#### Scenario: Import KML Placemarks

- GIVEN a KML file with five Point placemarks
- WHEN the user imports the file
- THEN all five placemarks are displayed as points on the map
- AND each point shows its name label on hover

#### Scenario: Import KMZ with multiple layers

- GIVEN a KMZ file containing one path and two polygon placemarks
- WHEN the user imports the file
- THEN all three geometry objects are displayed
- AND layers are grouped by their KML folder structure

#### Scenario: Empty or invalid KMZ

- GIVEN a KMZ file containing an empty KML or corrupted ZIP
- WHEN the system attempts to import it
- THEN it returns a descriptive error
- AND no empty layer is added to the map

### Requirement: Support point, line, and polygon geometry

The system MUST render KML Point, LineString, LinearRing, and Polygon geometry. Extended data and styles MAY be ignored for MVP.

#### Scenario: Polygon with style ignored

- GIVEN a KML Polygon with a colored style definition
- WHEN the system imports the file
- THEN the polygon outline is displayed at correct coordinates
- AND the style fill color is omitted (default rendering used)

### Requirement: CRS reprojection

KML coordinates are always WGS84 (EPSG:4326). The system MUST reproject all KML geometry to the map's CRS.

#### Scenario: Automatic WGS84 reprojection

- GIVEN a KML with points at known WGS84 coordinates and map CRS set to EPSG:32718
- WHEN the file is imported
- THEN all points display at correct UTM 18S positions
