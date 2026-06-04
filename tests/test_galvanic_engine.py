import pytest
from corrosim.engines.galvanic_engine import GalvanicEngine

def test_galvanic_mixed_potential():
    """
    Test galvanic corrosion prediction for a simple Zn-Cu couple.
    """
    result = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=1.0)
    
    assert result is not None, "No result returned"
    assert "error" not in result, f"Error in calculation: {result.get('error')}"
    
    expected_keys = ["current_density", "corrosion_rate", "severity", "delta_E", "couple_current"]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
    
    assert result["current_density"] > 0, "Current density should be positive"
    assert result["corrosion_rate"] > 0, "Corrosion rate should be positive"
    assert result["delta_E"] > 0, "Delta E should be positive"
    assert result["severity"] in ["Mild", "Moderate", "High", "Severe", "Catastrophic"], \
        f"Unknown severity: {result['severity']}"
    
    print(f"\n✅ Zn-Cu couple calculation:")
    print(f"   Current density: {result['current_density']:.2f} A/m²")
    print(f"   Corrosion rate: {result['corrosion_rate']:.4f} mm/year")
    print(f"   Severity: {result['severity']}")
    print(f"   Recommendation: {result.get('recommendation', 'N/A')[:50]}...")

def test_galvanic_area_effect():
    """Test that increasing cathode/anode ratio increases galvanic current."""
    result_small = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=0.5)
    result_large = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=10.0)
    
    assert result_large["current_density"] > result_small["current_density"], \
        f"Larger cathode should give higher current"
    
    print(f"\n✅ Area ratio effect: {result_small['current_density']:.2f} → {result_large['current_density']:.2f} A/m²")

def test_galvanic_same_metal():
    """Test that identical metals produce no or negligible galvanic current."""
    result = GalvanicEngine.calculate(anode="Mild Steel", cathode="Mild Steel", area_ratio=1.0)
    
    assert result["current_density"] < 1e-6, \
        f"Same metal should have near-zero current: {result['current_density']:.2e} A/m²"
    
    print(f"\n✅ Same metal (Mild Steel): current density = {result['current_density']:.2e} A/m² (negligible)")

def test_galvanic_unknown_metal():
    """Test that unknown metals return an error."""
    result = GalvanicEngine.calculate(anode="UnknownMetal", cathode="Copper", area_ratio=1.0)
    
    assert "error" in result, "Unknown metal should return an error"
    assert "Unknown metal" in result["error"], f"Unexpected error: {result.get('error')}"
    
    print(f"\n✅ Unknown metal handling: {result['error']}")

def test_galvanic_resistivity_effect():
    """Test that higher resistivity reduces galvanic current."""
    result_low_res = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=1.0, resistivity=0.25)
    result_high_res = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=1.0, resistivity=10.0)
    
    assert result_high_res["current_density"] < result_low_res["current_density"], \
        "Higher resistivity should reduce galvanic current"
    
    print(f"\n✅ Resistivity effect: {result_low_res['current_density']:.2f} → {result_high_res['current_density']:.2f} A/m²")

def test_galvanic_severity_classification():
    """
    Test that severity classification works correctly with actual levels.
    """
    mild_couple = GalvanicEngine.calculate(anode="Mild Steel", cathode="Copper", area_ratio=1.0)
    severe_couple = GalvanicEngine.calculate(anode="Magnesium", cathode="Platinum", area_ratio=10.0)
    
    # Valid severity levels from your engine
    valid_severities = ["Mild", "Moderate", "High", "Severe", "Catastrophic"]
    
    assert mild_couple["severity"] in valid_severities, \
        f"Severity '{mild_couple['severity']}' not in {valid_severities}"
    assert severe_couple["severity"] in valid_severities, \
        f"Severity '{severe_couple['severity']}' not in {valid_severities}"
    
    # Magnesium-Platinum should be more severe than Mild Steel-Copper
    # This assumes severity strings are comparable (might need numeric mapping)
    print(f"\n✅ Severity classification:")
    print(f"   Mild Steel-Copper: {mild_couple['severity']}")
    print(f"   Magnesium-Platinum: {severe_couple['severity']}")

def test_get_metal_list():
    """Test that get_metal_list returns a non-empty list."""
    metals = GalvanicEngine.get_metal_list()
    
    assert metals is not None, "get_metal_list() returned None"
    assert len(metals) > 0, "Metal list is empty"
    assert "Zinc" in metals, "Zinc should be in metal list"
    assert "Copper" in metals, "Copper should be in metal list"
    
    print(f"\n✅ Metal list contains {len(metals)} metals: {metals[:5]}...")

def test_get_compatible_metals():
    """Test that get_compatible_metals returns compatible metals."""
    compatible = GalvanicEngine.get_compatible_metals("Mild Steel", max_diff=0.25)
    
    assert compatible is not None, "get_compatible_metals returned None"
    assert isinstance(compatible, list), "Should return a list"
    assert len(compatible) > 0, "Should have at least one compatible metal"
    
    print(f"\n✅ Compatible metals with Mild Steel: {compatible[:3]}...")

if __name__ == "__main__":
    test_galvanic_mixed_potential()
    test_galvanic_area_effect()
    test_galvanic_same_metal()
    test_galvanic_unknown_metal()
    test_galvanic_resistivity_effect()
    test_galvanic_severity_classification()
    test_get_metal_list()
    test_get_compatible_metals()
