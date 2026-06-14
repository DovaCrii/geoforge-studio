# PPK Engine Specification

## Purpose

Compute single-baseline post-processed kinematic (PPK) positions from base and rover RINEX observation files with broadcast ephemeris. Produces float and fixed ambiguity solutions on L1.

## Requirements

### Requirement: Single-baseline PPK

The system MUST compute rover positions relative to a single base station using double-differenced carrier phase and pseudorange observations on L1.

#### Scenario: Fixed solution from good data

- GIVEN base and rover RINEX OBS files with >10 common satellites and clean signals
- WHEN the PPK engine processes the基线eline
- THEN the output contains fixed ambiguity positions
- AND each epoch includes time, coordinates (lat/lon/ht), and quality flags

#### Scenario: Insufficient common satellites

- GIVEN base and rover files with fewer than 4 common satellites for a given epoch
- WHEN the PPK engine processes the baseline
- THEN that epoch is marked as "no solution"
- AND the reason (insufficient satellites) is reported

### Requirement: Float and fixed ambiguity resolution

The system SHALL produce a float solution for every epoch with enough data, and SHOULD resolve integer ambiguities when the ratio test passes a configurable threshold.

#### Scenario: Float-only solution

- GIVEN base and rover files with multipath-affected signals precluding ambiguity fixing
- WHEN the engine cannot resolve ambiguities to integers
- THEN the epoch is output as a float solution with a "float" quality flag
- AND the float solution includes estimated covariance

### Requirement: Output in requested CRS

The system MUST output final coordinates in the CRS specified by the user, using pyproj for reprojection from the internal geocentric frame.

#### Scenario: CRS reprojection

- GIVEN a user-specified output CRS of EPSG:32718 (UTM 18S)
- WHEN the PPK engine produces final positions
- THEN all coordinates are transformed from ECEF to UTM 18S
- AND zone and hemisphere are reported

### Requirement: Solution quality reporting

The engine SHOULD report per-epoch quality metrics: ratio factor, RMS residual, number of satellites, and GDOP.

#### Scenario: View solution diagnostics

- GIVEN a completed PPK processing run
- WHEN the user inspects any epoch
- THEN ratio, RMS, satellite count, and GDOP are accessible
