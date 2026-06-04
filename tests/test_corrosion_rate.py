import pytest
import numpy as np

def corrosion_rate_mm_per_year(icorr_uA_per_cm2, equivalent_weight_g_eq, density_g_per_cm3):
    constant = 0.00327
    return (icorr_uA_per_cm2 * equivalent_weight_g_eq * constant) / density_g_per_cm3

def test_corrosion_rate_iron():
    icorr = 10.0
    ew_iron = 27.92
    density_iron = 7.87
    rate = corrosion_rate_mm_per_year(icorr, ew_iron, density_iron)
    expected_rate = 0.116
    assert rate == pytest.approx(expected_rate, rel=0.01)
    assert rate > 0
    print(f"\nCalculated corrosion rate for iron: {rate:.4f} mm/year")
