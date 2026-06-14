# Volume Tool Specification

## Purpose

Compute cut and fill volumes between two surfaces using TIN (triangulated irregular network) interpolation from surveyed points. Designed for stockpile and excavation volume estimation.

## Requirements

### Requirement: TIN surface from point cloud

The system MUST construct a TIN surface from a set of 3D points using Delaunay triangulation in the horizontal plane.

#### Scenario: Surface from survey points

- GIVEN 500+ surveyed points forming a stockpile shape
- WHEN the user selects "Generate Surface"
- THEN a TIN mesh is constructed via Delaunay triangulation
- AND the mesh is displayed as a colored elevation layer on the map

#### Scenario: Insufficient points

- GIVEN fewer than 3 distinct non-collinear points
- WHEN the user attempts to generate a surface
- THEN the system returns an error: minimum 3 points required for triangulation

### Requirement: Single cut/fill volume

The system MUST compute cut volume, fill volume, and net volume between a design surface and a surveyed surface, reporting values in cubic meters (or user-selected unit).

#### Scenario: Simple cut calculation

- GIVEN a flat design surface at 100 m elevation and surveyed points mostly above 100 m
- WHEN the user computes volume between the two surfaces
- THEN the system reports cut volume (material above design) as approximately 0
- AND fill volume (excavation below design) as a positive number
- AND net volume as fill - cut

#### Scenario: Design surface same as surveyed

- GIVEN a design surface identical to the surveyed surface
- WHEN the user computes volume
- THEN cut and fill volumes are both reported as 0
- AND net volume is 0

### Requirement: Volume reporting

The system SHALL report cut, fill, and net volumes separately, along with the planimetric area of the surface. Results SHOULD be formatted in a table for export.

#### Scenario: Volume results display

- GIVEN a completed TIN volume calculation
- WHEN the results panel opens
- THEN cut volume, fill volume, net volume, and area are displayed
- AND the user may copy or export the table
