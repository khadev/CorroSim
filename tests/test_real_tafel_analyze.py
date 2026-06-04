import pytest
import numpy as np
from corrosim.tafel_engine import TafelEngine

def test_tafel_analyze_with_synthetic_data():
    """
    Test TafelEngine.analyze() with synthetic Butler-Volmer data.
    """
    
    # 1. Generate synthetic test data using your own generator
    ecorr = -0.5      # V
    icorr = 10e-6     # A/cm² (10 µA/cm²)
    beta_a = 0.12     # V/dec (120 mV/dec)
    beta_c = 0.12     # V/dec (120 mV/dec)
    area = 1.0        # cm²
    
    # Use your built-in generator
    potential, current = TafelEngine.generate_test_data(
        ecorr=ecorr, 
        icorr=icorr, 
        beta_a=beta_a, 
        beta_c=beta_c, 
        area=area
    )
    
    # 2. Run analysis
    result = TafelEngine.analyze(potential, current, area=area)
    
    # 3. Print results to see what we got
    print("\n" + "="*50)
    print("Tafel Analysis Results:")
    print("="*50)
    for key, value in result.items():
        if isinstance(value, float):
            print(f"  {key:20s}: {value:.6e}")
        else:
            print(f"  {key:20s}: {value}")
    
    # 4. Basic sanity checks
    assert result is not None, "No result returned"
    assert "ecorr" in result, "ecorr not in results"
    assert "icorr" in result, "icorr not in results"
    assert "beta_a" in result, "beta_a not in results"
    assert "beta_c" in result, "beta_c not in results"
    assert "corrosion_rate" in result, "corrosion_rate not in results"
    
    # 5. Physical plausibility checks
    assert result["ecorr"] < 0, f"ecorr should be negative, got {result['ecorr']}"
    assert result["icorr"] > 0, f"icorr should be positive, got {result['icorr']}"
    assert result["beta_a"] > 0, f"beta_a should be positive, got {result['beta_a']}"
    assert result["beta_c"] > 0, f"beta_c should be positive, got {result['beta_c']}"
    assert result["corrosion_rate"] > 0, f"CR should be positive, got {result['corrosion_rate']}"
    
    # 6. Accuracy checks (allow some error due to fitting)
    # Your synthetic values: icorr = 10 µA/cm², beta = 120 mV/dec
    icorr_measured = result["icorr"] * 1e6  # Convert A to µA if needed
    
    print("\n" + "="*50)
    print("Accuracy Check:")
    print(f"  Expected icorr: 10.00 µA/cm²")
    print(f"  Measured icorr: {icorr_measured:.2f} µA/cm²")
    print(f"  Expected βa: 120 mV/dec")
    print(f"  Measured βa: {result['beta_a']*1000:.1f} mV/dec")
    print(f"  Expected βc: 120 mV/dec")
    print(f"  Measured βc: {result['beta_c']*1000:.1f} mV/dec")
    print(f"  Corrosion rate: {result['corrosion_rate']:.4f} mm/year")
    
    # Allow up to 20% error due to noise/fitting
    assert icorr_measured == pytest.approx(10.0, rel=0.20), f"icorr accuracy too low"
    assert result["beta_a"]*1000 == pytest.approx(120, rel=0.20), f"beta_a accuracy too low"
    assert result["beta_c"]*1000 == pytest.approx(120, rel=0.20), f"beta_c accuracy too low"
    
    print("\n✅ All tests passed!")

def test_tafel_analyze_with_noise():
    """
    Test robustness with noisy data.
    """
    # Generate data
    potential, current = TafelEngine.generate_test_data(area=1.0)
    
    # Add significant noise (10% of current values)
    noise = np.random.normal(0, 0.1 * np.abs(current), len(current))
    current_noisy = current + noise
    current_noisy = np.abs(current_noisy)  # Ensure no negative currents
    
    # Run analysis on noisy data
    result = TafelEngine.analyze(potential, current_noisy, area=1.0)
    
    # Should still produce reasonable results
    assert result["icorr"] > 0, "icorr should still be positive with noise"
    assert result["corrosion_rate"] > 0, "CR should still be positive"
    assert 0 < result["beta_a"] < 1, f"Beta a out of range: {result['beta_a']}"
    assert 0 < result["beta_c"] < 1, f"Beta c out of range: {result['beta_c']}"
    
    print(f"\n✅ Noisy data test passed!")
    print(f"   icorr (with noise): {result['icorr']*1e6:.2f} µA/cm²")
    print(f"   corrosion rate: {result['corrosion_rate']:.4f} mm/year")

if __name__ == "__main__":
    test_tafel_analyze_with_synthetic_data()
    test_tafel_analyze_with_noise()
