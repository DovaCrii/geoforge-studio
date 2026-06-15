use pyo3::prelude::*;
use pyo3::types::PyList;

/// Represents a single GNSS observation epoch
#[pyclass]
#[derive(Debug, Clone)]
pub struct Epoch {
    pub time: f64,
    pub sat_id: String,
    pub carrier_phase: f64,
    pub pseudorange: f64,
    pub snr: f64,
}

#[pymethods]
impl Epoch {
    #[new]
    pub fn new(time: f64, sat_id: String, carrier_phase: f64, pseudorange: f64, snr: f64) -> Self {
        Self {
            time,
            sat_id,
            carrier_phase,
            pseudorange,
            snr,
        }
    }

    fn __repr__(&self) -> String {
        format!("Epoch(time={}, sat_id={}, carrier_phase={}, pseudorange={})", 
                self.time, self.sat_id, self.carrier_phase, self.pseudorange)
    }
}

/// Represents a satellite ephemeris data
#[pyclass]
#[derive(Debug, Clone)]
pub struct Ephemeris {
    pub sat_id: String,
    pub sv_id: u32,
    pub health: u8,
    pub tgd: f64,
    pub sqrt_a: f64,
    pub e: f64,
    pub i_0: f64,
    pub omega_0: f64,
    pub m_0: f64,
    pub delta_n: f64,
    pub i_dot: f64,
    pub omega_dot: f64,
    pub dot_omega_i: f64,
    pub c_uc: f64,
    pub c_us: f64,
    pub c_rc: f64,
    pub c_rs: f64,
    pub toe: f64,
    pub toc: f64,
    pub af0: f64,
    pub af1: f64,
    pub af2: f64,
}

#[pymethods]
impl Ephemeris {
    #[new]
    pub fn new(
        sat_id: String,
        sv_id: u32,
        health: u8,
        tgd: f64,
        sqrt_a: f64,
        e: f64,
        i_0: f64,
        omega_0: f64,
        m_0: f64,
        delta_n: f64,
        i_dot: f64,
        omega_dot: f64,
        dot_omega_i: f64,
        c_uc: f64,
        c_us: f64,
        c_rc: f64,
        c_rs: f64,
        toe: f64,
        toc: f64,
        af0: f64,
        af1: f64,
        af2: f64,
    ) -> Self {
        Self {
            sat_id,
            sv_id,
            health,
            tgd,
            sqrt_a,
            e,
            i_0,
            omega_0,
            m_0,
            delta_n,
            i_dot,
            omega_dot,
            dot_omega_i,
            c_uc,
            c_us,
            c_rc,
            c_rs,
            toe,
            toc,
            af0,
            af1,
            af2,
        }
    }

    fn __repr__(&self) -> String {
        format!("Ephemeris(sat_id={}, sv_id={})", self.sat_id, self.sv_id)
    }
}

/// Represents a PPK solution result
#[pyclass]
#[derive(Debug, Clone)]
pub struct PpkSolution {
    pub base_epoch: Epoch,
    pub rover_epoch: Epoch,
    pub baseline_vector: (f64, f64, f64),
    pub ambiguity_status: bool,
    pub residual: f64,
    pub solution_time: f64,
}

#[pymethods]
impl PpkSolution {
    #[new]
    pub fn new(
        base_epoch: Epoch,
        rover_epoch: Epoch,
        baseline_vector: (f64, f64, f64),
        ambiguity_status: bool,
        residual: f64,
        solution_time: f64,
    ) -> Self {
        Self {
            base_epoch,
            rover_epoch,
            baseline_vector,
            ambiguity_status,
            residual,
            solution_time,
        }
    }

    fn __repr__(&self) -> String {
        format!("PpkSolution(baseline={}, residual={})", 
                self.baseline_vector, self.residual)
    }
}

/// Module initialization
#[pymodule]
fn module(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Epoch>()?;
    m.add_class::<Ephemeris>()?;
    m.add_class::<PpkSolution>()?;
    Ok(())
}
