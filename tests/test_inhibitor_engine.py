import pytest
import numpy as np
from corrosim.engines.inhibitor_engine import InhibitorEngine

def test_inhibitor_efficiency_calculation():
    """Test basic inhibitor efficiency calculation."""
    # 50% efficiency (your code: ≤50% = Ineffective)
    result = InhibitorEngine.calculate_efficiency(10.0, 5.0)
    
    assert result is not None
    assert "error" not in result
    assert result["efficiency_pct"] == 50.0
    assert result["grade"] == "Ineffective"  # 50% is not > 50%
    assert result["surface_coverage"] == 0.5
    
    # 75% efficiency (should be "Fair" since >70% and ≤80%)
    result = InhibitorEngine.calculate_efficiency(10.0, 2.5)
    assert result["efficiency_pct"] == 75.0
    assert result["grade"] == "Fair"
    
    # 85% efficiency (should be "Good")
    result = InhibitorEngine.calculate_efficiency(10.0, 1.5)
    assert result["efficiency_pct"] == 85.0
    assert result["grade"] == "Good"
    
    # 95% efficiency (should be "Excellent" since >90%)
    result = InhibitorEngine.calculate_efficiency(10.0, 0.5)
    assert result["efficiency_pct"] == 95.0
    assert result["grade"] == "Excellent"
    
    # 100% efficiency
    result = InhibitorEngine.calculate_efficiency(10.0, 0.0)
    assert result["efficiency_pct"] == 100.0
    assert result["grade"] == "Outstanding"
    
    # 0% efficiency
    result = InhibitorEngine.calculate_efficiency(10.0, 10.0)
    assert result["efficiency_pct"] == 0.0
    assert result["grade"] == "Ineffective"
    
    print(f"\n✅ Inhibitor efficiency grades work correctly")

def test_inhibitor_edge_cases():
    """Test edge cases and error handling."""
    result = InhibitorEngine.calculate_efficiency(0, 5.0)
    assert "error" in result
    result = InhibitorEngine.calculate_efficiency(10.0, -5.0)
    assert result["efficiency_pct"] == 100.0

def test_langmuir_isotherm_fitting():
    concentration = [10, 20, 50, 100, 200]
    efficiency = [40, 55, 70, 80, 85]
    result = InhibitorEngine.fit_langmuir(concentration, efficiency)
    assert result is not None
    assert "error" not in result
    assert result["r_squared"] > 0.9
    print(f"\n✅ Langmuir: K_ads={result['K_ads']}, ΔG°={result['delta_G_kJ_mol']} kJ/mol")

def test_freundlich_isotherm_fitting():
    concentration = [10, 20, 50, 100, 200]
    efficiency = [35, 50, 65, 75, 82]
    result = InhibitorEngine.fit_freundlich(concentration, efficiency)
    assert result is not None
    assert result["r_squared"] > 0.9
    print(f"\n✅ Freundlich: Kf={result['Kf']}, n={result['n']}")

def test_synergy_parameter():
    result = InhibitorEngine.calculate_synergy(30, 30, 85)
    assert result["S_parameter"] > 1.2
    assert result["effect"] == "Strong Synergism"
    result = InhibitorEngine.calculate_synergy(40, 40, 65)
    assert result["effect"] in ["Additive", "Weak Synergism"]
    result = InhibitorEngine.calculate_synergy(50, 50, 40)
    assert result["S_parameter"] < 0.8
    assert result["effect"] == "Antagonism"
    print(f"\n✅ Synergy calculation works")

def test_delta_g_interpretation():
    result = InhibitorEngine._interpret_delta_G(-50)
    assert "Chemisorption" in result
    result = InhibitorEngine._interpret_delta_G(-30)
    assert "Mixed" in result
    result = InhibitorEngine._interpret_delta_G(-10)
    assert "Physisorption" in result

def test_inhibitor_workflow():
    conc = [10, 25, 50, 100, 250, 500]
    eff = [30, 48, 65, 78, 86, 90]
    langmuir = InhibitorEngine.fit_langmuir(conc, eff)
    freundlich = InhibitorEngine.fit_freundlich(conc, eff)
    assert langmuir["r_squared"] > 0.85
    assert freundlich["r_squared"] > 0.85
    print(f"\n✅ Workflow: Langmuir R²={langmuir['r_squared']}, Freundlich R²={freundlich['r_squared']}")

if __name__ == "__main__":
    test_inhibitor_efficiency_calculation()
    test_inhibitor_edge_cases()
    test_langmuir_isotherm_fitting()
    test_freundlich_isotherm_fitting()
    test_synergy_parameter()
    test_delta_g_interpretation()
    test_inhibitor_workflow()
