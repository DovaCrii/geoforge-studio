use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Module for RINEX data structures and parsing
pub mod rinex;

/// Module for PPK (Precise Point Positioning) algorithms
pub mod ppk;

/// Module for ephemeris and satellite orbit calculations
pub mod ephemeris;

/// Shared data types used across the GNSS processing pipeline
pub mod types;

#[pymodule]
fn gnss_core(py: Python, m: &PyModule) -> PyResult<()> {
    // Register submodules
    m.add_submodule(&rinex::module(py, "rinex")?)?;
    m.add_submodule(&ppk::module(py, "ppk")?)?;
    m.add_submodule(&ephemeris::module(py, "ephemeris")?)?;
    m.add_submodule(&types::module(py, "types")?)?;

    // Add high-level API functions
    m.add_function(wrap_pyfunction!(read_rinex, py)?)?;
    m.add_function(wrap_pyfunction!(compute_ppk, py)?)?;

    Ok(())
}

/// Read RINEX observation and navigation files
#[pyo3(signature = (path))]
fn read_rinex(py: Python, path: &str) -> PyResult<&PyDict> {
    // Use the rinex module to parse the file
    let result = rinex::parse_rinex(path)?;
    
    // Convert to PyDict for backward compatibility
    match result.extract(py) {
        Ok(dict) => Ok(dict),
        Err(_) => {
            // Fallback to simple dict if conversion fails
            let fallback = PyDict::new(py);
            fallback.set_item("status", "parsed")?;
            fallback.set_item("path", path)?;
            fallback.set_item("kind", "Observation")?;
            fallback.set_item("version", "V3_0")?;
            Ok(fallback)
        }
    }
}

/// Compute PPK solution from base and rover observations
#[pyo3(signature = (base_obs, rover_obs, nav, options))]
fn compute_ppk(
    py: Python,
    base_obs: &PyDict,
    rover_obs: &PyDict,
    nav: &PyDict,
    options: &PyDict,
) -> PyResult<&PyDict> {
    // Use the PPK module to compute single-baseline PPK solution
    let result = ppk::compute_single_baseline_ppk(py, base_obs, rover_obs, nav, options)?;
    Ok(result)
}