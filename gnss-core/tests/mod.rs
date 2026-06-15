mod fixtures;

use gnss_core::ppk::{compute_single_baseline_ppk, PpkPipeline};
use gnss_core::rinex::{parse_rinex, RinexContract, RinexKind, RinexVersion};
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[test]
fn rinex_contract_supports_mvp_versions() {
    let contract = RinexContract::new();
    assert!(contract.supported_versions.contains(&RinexVersion::V3_0));
    assert!(contract.supported_kinds.contains(&RinexKind::Observation));
    let header = fixtures::create_test_rinex_header();
    assert_eq!(header.0, RinexVersion::V3_0);
}

#[test]
fn parse_rinex_returns_structured_placeholder() {
    Python::with_gil(|py| {
        let result = parse_rinex("sample.obs").unwrap();
        let dict = result.extract::<PyDict>(py).unwrap();

        assert_eq!(dict.get_item("status").unwrap().extract::<String>().unwrap(), "parsed");
        assert_eq!(dict.get_item("path").unwrap().extract::<String>().unwrap(), "sample.obs");
    });
}

#[test]
fn ppk_pipeline_uses_placeholder_states() {
    Python::with_gil(|py| {
        let (base_obs_obj, rover_obs_obj, nav_data_obj) = fixtures::create_test_ppk_inputs();
        let base_obs = base_obs_obj.extract::<&PyDict>(py).unwrap();
        let rover_obs = rover_obs_obj.extract::<&PyDict>(py).unwrap();
        let nav_data = nav_data_obj.extract::<&PyDict>(py).unwrap();

        let mut pipeline = PpkPipeline::new("single_baseline".to_string());
        pipeline.initialize(&base_obs, &rover_obs, &nav_data).unwrap();
        pipeline.resolve_ambiguities().unwrap();
        pipeline.compute_baseline().unwrap();

        assert_eq!(pipeline.stage, "completed");
        assert!(pipeline.baseline_vector.is_some());
        assert!(pipeline.residual.is_some());
    });
}

#[test]
fn compute_single_baseline_ppk_returns_structured_result() {
    Python::with_gil(|py| {
        let (base_obs_obj, rover_obs_obj, nav_data_obj) = fixtures::create_test_ppk_inputs();
        let base_obs = base_obs_obj.extract::<&PyDict>(py).unwrap();
        let rover_obs = rover_obs_obj.extract::<&PyDict>(py).unwrap();
        let nav_data = nav_data_obj.extract::<&PyDict>(py).unwrap();
        let options = PyDict::new(py);

        let result = compute_single_baseline_ppk(py, &base_obs, &rover_obs, &nav_data, &options).unwrap();

        assert_eq!(result.get_item("status").unwrap().extract::<String>().unwrap(), "success");
        assert!(result.get_item("baseline_vector").is_some());
        assert!(result.get_item("pipeline").is_some());
    });
}
