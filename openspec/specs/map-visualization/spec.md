# Map Visualization Specification

## Purpose

Render a CRS-aware 2D survey map displaying GNSS solution points, receiver track, and coordinate grids. Supports zoom, pan, and layer visibility toggles.

## Requirements

### Requirement: Render points and track on CRS-aware map

The system MUST display GNSS solution points as an interactive scatter layer and the receiver path as a connected line, both projected in the user-selected CRS.

#### Scenario: Points and track display

- GIVEN a set of PPK solutions with lat/lon coordinates
- WHEN the map renders with CRS set to EPSG:32718
- THEN each solution point is plotted at its UTM coordinate
- AND consecutive points are connected by a track line

#### Scenario: Empty solution set

- GIVEN no PPK solutions loaded
- WHEN the map initializes
- THEN the map shows the coordinate grid and background only
- AND a status message indicates no points to display

### Requirement: CRS reprojection via pyproj

The system MUST reproject all displayed coordinates from source CRS to user-selected target CRS using pyproj.

#### Scenario: Reprojection between systems

- GIVEN source data in WGS84 (EPSG:4326) and target CRS EPSG:32718
- WHEN the map renders
- THEN all points are correctly transformed to UTM 18S
- AND axis labels reflect the target coordinate system

#### Scenario: Invalid CRS selection

- GIVEN a user-entered CRS string "EPSG:INVALID"
- WHEN the system attempts reprojection
- THEN it returns a clear error message
- AND falls back to the default CRS (WGS84)

### Requirement: Zoom and pan controls

The system SHOULD provide mouse-driven zoom (scroll wheel) and pan (click-drag) over the map area.

#### Scenario: Zoom to extents

- GIVEN loaded points spanning 2 km
- WHEN the user double-clicks the zoom-to-extents button
- THEN the viewport adjusts to show all points with margin

### Requirement: Layer visibility toggles

The system SHOULD provide on/off toggles for each loaded layer: points, track, grid, DXF overlay, KMZ overlay.

#### Scenario: Toggle layer off

- GIVEN a visible DXF overlay on the map
- WHEN the user unchecks the DXF layer toggle
- THEN the DXF overlay is hidden
- AND other layers remain visible
