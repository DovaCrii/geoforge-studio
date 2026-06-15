use gnss_core::rinex::{RinexKind, RinexVersion};
use gnss_core::types::{Epoch, Ephemeris, PpkSolution};
use pyo3::prelude::*;
use pyo3::types::PyDict;

pub fn create_test_epoch() -> Epoch {
    Epoch::new(1000.0, "G01".to_string(), 100.0, 1000.0, 45.0)
}

pub fn create_test_ephemeris() -> Ephemeris {
    Ephemeris::new(
        "G01".to_string(),
        1,
        0,
        0.0,
        5000.0,
        0.001,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )
}

pub fn create_test_ppk_solution() -> PpkSolution {
    let rover_epoch = Epoch::new(1000.5, "G02".to_string(), 100.5, 1000.5, 45.5);
    PpkSolution::new(create_test_epoch(), rover_epoch, (10.0, 20.0, 5.0), false, 0.5, 1000.5)
}

pub fn create_test_rinex_header() -> (RinexVersion, RinexKind) {
    (RinexVersion::V3_0, RinexKind::Observation)
}

pub fn create_test_ppk_inputs() -> (PyObject, PyObject, PyObject) {
    Python::with_gil(|py| {
        let base_obs = PyDict::new(py);
        base_obs.set_item("epoch", 1000.0).unwrap();
        let rover_obs = PyDict::new(py);
        rover_obs.set_item("epoch", 1000.5).unwrap();
        let nav_data = PyDict::new(py);
        nav_data.set_item("sat_id", "G01").unwrap();
        (base_obs.into(), rover_obs.into(), nav_data.into())
    })
}
