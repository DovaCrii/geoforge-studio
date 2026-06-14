# DXF Import Specification

## Purpose

Import DXF files for read-only overlay display on the 2D survey map. Supports common 2D entities and basic geographic referencing.

## Requirements

### Requirement: Read DXF R12 through R2018

The system MUST read DXF files in ASCII format from versions R12 through R2018, extracting geometry for display.

#### Scenario: Import valid DXF file

- GIVEN an ASCII DXF R2010 file with POINT, LINE, and LWPOLYLINE entities
- WHEN the user imports the file
- THEN all entities are parsed and displayed as an overlay on the map

#### Scenario: Unsupported DXF version

- GIVEN a DXF file claiming version AC1006 (R10)
- WHEN the user imports the file
- THEN the system returns an error listing supported versions (R12–R2018)

### Requirement: Support common 2D entities

The system MUST support POINT, LINE, LWPOLYLINE, CIRCLE, and POLYLINE entities for overlay display. Unsupported entities SHOULD be skipped with a logged warning.

#### Scenario: Mixed entity types

- GIVEN a DXF file containing LINES, LWPOLYLINES, and 3DFACE entities
- WHEN the file is imported
- THEN LINES and LWPOLYLINES are displayed
- AND 3DFACE entities are skipped with a logged warning

### Requirement: CRS reprojection on import

The system SHOULD accept an optional source CRS for the DXF. If provided, coordinates are reprojected to the map CRS. If absent, raw coordinates are used (assumed same CRS as map).

#### Scenario: DXF with source CRS

- GIVEN a DXF in EPSG:4326 and the map in EPSG:32718
- WHEN the user provides the source CRS during import
- THEN all DXF entities are displayed at correct UTM 18S coordinates

### Requirement: File-level validation

The system MUST reject malformed DXF files with a descriptive error, and SHOULD handle files with warnings when recovery is possible.

#### Scenario: Truncated DXF

- GIVEN a DXF file missing the ENDSEC for ENTITIES
- WHEN the system attempts to import it
- THEN it returns a parse error describing the truncation
