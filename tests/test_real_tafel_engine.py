import pytest
from corrosim.tafel_engine import TafelEngine

def test_faraday_rate_from_engine():
    # Create an instance of your TafelEngine
    engine = TafelEngine()
    
    # Call the method that calculates corrosion rate
    # NOTE: Replace 'calculate_corrosion_rate' with your actual method name
    # and 'Fe' with how you specify material
    rate = engine.calculate_corrosion_rate(
        icorr_uA_cm2=10.0,
        material="Fe"  # or equivalent_weight=27.92, density=7.87
    )
    
    # Iron should give ~0.116 mm/year for 10 µA/cm²
    expected_rate = 0.116
    assert rate == pytest.approx(expected_rate, rel=0.01)
    print(f"\n✅ Real engine calculated: {rate:.4f} mm/year")
