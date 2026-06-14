# RINEX Reader Specification

## Purpose

Parse RINEX observation (OBS) and navigation (NAV) files across versions 2.x through 4.x from any GNSS receiver brand. Provides clean structured data to the PPK engine and map layers.

## Requirements

### Requirement: Parse RINEX OBS files

The system MUST parse RINEX observation files in versions 2.11, 3.x, and 4.x, extracting epoch time, pseudorange, carrier phase, SNR, and Doppler for all observed signals.

#### Scenario: Parse standard OBS file

- GIVEN a valid RINEX OBS 3.04 file from a Trimble receiver
- WHEN the system reads the file
- THEN all epochs are extracted with correct time tags
- AND pseudorange and carrier phase values match the file contents

#### Scenario: Parse unsupported version

- GIVEN a file claiming RINEX 1.0 in the header
- WHEN the system attempts to read it
- THEN it returns a clear error listing supported versions (2.11, 3.x, 4.x)

### Requirement: Parse RINEX NAV files

The system MUST parse RINEX navigation files (GPS, GLONASS, Galileo, BeiDou) in versions 2.x–4.x, extracting broadcast ephemeris parameters for use by the PPK engine.

#### Scenario: Parse GPS NAV file

- GIVEN a RINEX NAV 3.04 file with GPS ephemerides
- WHEN the system reads the file
- THEN all satellite ephemeris records are extracted with correct Keplerian elements
- AND the system reports the number of satellites found

#### Scenario: Parse mixed-constellation NAV file

- GIVEN a RINEX NAV 3.04 file containing GPS + Galileo ephemerides
- WHEN the system reads the file
- THEN ephemerides for both constellations are extracted
- AND each record is tagged with the correct constellation identifier

### Requirement: Handle malformed or partial files

The system SHOULD report file-level errors without crashing, indicating the line and nature of the problem. Partial data before the error MAY still be returned.

#### Scenario: Corrupted epoch block

- GIVEN a RINEX OBS file with one corrupted epoch (missing phase data)
- WHEN the system parses the file
- THEN it skips the corrupted epoch, logs the error with line number, and continues parsing
- AND valid epochs before and after are returned

### Requirement: Reject empty or non-RINEX files

The system MUST reject files that are empty, binary, or do not contain a valid RINEX header, returning a descriptive error.

#### Scenario: Binary file provided

- GIVEN a binary .ubx file passed as a RINEX file
- WHEN the system reads the file
- THEN it returns an error stating the file does not match RINEX format
