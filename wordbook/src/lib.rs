use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use rayon::prelude::*;

const WORDS: &'static str = include_str!("../wordbook.txt");

#[pyfunction]
fn exists(needle: &str) -> bool {
    WORDS
        .lines()
        .collect::<Vec<&'static str>>()
        .as_slice()    
        .par_iter()
        .find_any(|x| **x == needle)
        .is_some()
}

#[pymodule]
fn wordbook(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(exists, m)?)?;
    Ok(())
}