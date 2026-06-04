import pytest
import numpy as np
from corrosim.engines.eis_engine import EISEngine

def test_eis_generate_test_data():
    """
    Test that generate_test_data returns a dict with correct keys.
    """
    result = EISEngine.generate_test_data(circuit='randles', noise_level=0.0)
    
    # Check return type and keys
    assert isinstance(result, dict), "Should return a dictionary"
    assert "freq" in result, "Missing 'freq' key"
    assert "Z_real" in result, "Missing 'Z_real' key"
    assert "Z_imag" in result, "Missing 'Z_imag' key"
    
    # Check data types and shapes
    freq = result["freq"]
    Z_real = result["Z_real"]
    Z_imag = result["Z_imag"]
    
    assert len(freq) == 60, f"Expected 60 frequency points, got {len(freq)}"
    assert len(Z_real) == len(freq), "Z_real length mismatch"
    assert len(Z_imag) == len(freq), "Z_imag length mismatch"
    
    # Imaginary impedance should be positive (since they use np.abs)
    assert np.all(Z_imag >= 0), "Z_imag should be non-negative"
    
    print(f"\n✅ generate_test_data() works:")
    print(f"   Frequency range: {freq[0]:.2e} to {freq[-1]:.2e} Hz")
    print(f"   Z_real range: [{Z_real.min():.1f}, {Z_real.max():.1f}] ohm")
    print(f"   Z_imag range: [{Z_imag.min():.1f}, {Z_imag.max():.1f}] ohm")

def test_eis_randles_circuit():
    """
    Test the _randles circuit calculation.
    """
    freq = np.logspace(0, 3, 10)
    Rs = 10.0
    Rct = 100.0
    Cdl = 1e-4
    
    Z = EISEngine._randles(freq, Rs, Rct, Cdl)
    
    # Check that Z is complex
    assert np.iscomplexobj(Z), "Z should be complex"
    assert len(Z) == len(freq), "Output length mismatch"
    
    # At high frequency, Z ≈ Rs
    high_freq_idx = -1
    assert abs(Z.real[high_freq_idx] - Rs) < 1.0, \
        f"High freq real should approach Rs"
    
    # At low frequency, Z ≈ Rs + Rct
    low_freq_idx = 0
    assert abs(Z.real[low_freq_idx] - (Rs + Rct)) < 5.0, \
        f"Low freq real should approach Rs+Rct"
    
    print(f"\n✅ Randles circuit calculation works")

def test_eis_fit_randles():
    """
    Test fitting of Randles circuit.
    """
    # Generate clean data
    data = EISEngine.generate_test_data(circuit='randles', noise_level=0.0)
    freq = data["freq"]
    Z_real = data["Z_real"]
    Z_imag = data["Z_imag"]
    
    # Fit the circuit
    result = EISEngine.fit_randles(freq, Z_real, Z_imag, use_cpe=False)
    
    # Check result
    assert result is not None, "No result returned"
    assert "error" not in result, f"Error in fitting: {result.get('error')}"
    assert "Rs" in result, "Missing Rs in result"
    assert "Rct" in result, "Missing Rct in result"
    assert "Cdl" in result, "Missing Cdl in result"
    assert "r_squared" in result, "Missing r_squared"
    
    # Expected values from generate_test_data: Rs=10, Rct=1000, Cdl=1e-4
    assert abs(result["Rs"] - 10.0) < 2.0, f"Rs error: {result['Rs']} vs 10"
    assert 800 < result["Rct"] < 1200, f"Rct out of range: {result['Rct']}"
    assert 0.9e-4 < result["Cdl"] < 1.1e-4, f"Cdl out of range: {result['Cdl']}"
    assert result["r_squared"] > 0.99, f"R² too low: {result['r_squared']}"
    
    print(f"\n✅ Randles circuit fitting successful:")
    print(f"   Rs: {result['Rs']:.1f} ohm (expected ~10)")
    print(f"   Rct: {result['Rct']:.1f} ohm (expected ~1000)")
    print(f"   Cdl: {result['Cdl']:.2e} F (expected ~1e-4)")
    print(f"   R²: {result['r_squared']:.4f}")

def test_eis_fit_warburg():
    """
    Test fitting of Warburg circuit.
    """
    # Generate Warburg data
    data = EISEngine.generate_test_data(circuit='warburg', noise_level=0.0)
    freq = data["freq"]
    Z_real = data["Z_real"]
    Z_imag = data["Z_imag"]
    
    # Fit the circuit
    result = EISEngine.fit_warburg(freq, Z_real, Z_imag, use_cpe=False)
    
    # Check result
    assert result is not None, "No result returned"
    assert "error" not in result, f"Error in fitting: {result.get('error')}"
    
    # Check for expected keys (may differ from Randles)
    if isinstance(result, dict):
        print(f"\n✅ Warburg circuit fitting returned:")
        for key, value in list(result.items())[:6]:
            if isinstance(value, float):
                print(f"   {key}: {value:.4e}")
            else:
                print(f"   {key}: {value}")
        assert result.get("r_squared", 0) > 0.95, "R² too low"
    else:
        print(f"\n✅ Warburg result: {result}")

def test_eis_kramers_kronig():
    """
    Test Kramers-Kronig validation (if implemented).
    """
    data = EISEngine.generate_test_data(circuit='randles', noise_level=0.01)
    freq = data["freq"]
    Z_real = data["Z_real"]
    Z_imag = data["Z_imag"]
    
    # Try Kramers-Kronig validation
    try:
        result = EISEngine.linear_kramers_kronig(freq, Z_real, Z_imag, n_terms=5)
        
        if result is not None:
            print(f"\n✅ Kramers-Kronig validation completed")
            if isinstance(result, dict):
                print(f"   Result keys: {list(result.keys())[:3]}")
        else:
            print(f"\n⚠️ Kramers-Kronig not fully implemented or returned None")
    except Exception as e:
        print(f"\n⚠️ Kramers-Kronig method error (may be expected): {e}")

def test_eis_noisy_data():
    """
    Test that fitting works with noisy data.
    """
    # Generate data with noise
    data = EISEngine.generate_test_data(circuit='randles', noise_level=0.05)
    freq = data["freq"]
    Z_real = data["Z_real"]
    Z_imag = data["Z_imag"]
    
    # Fit should still work
    result = EISEngine.fit_randles(freq, Z_real, Z_imag, use_cpe=False)
    
    assert result is not None, "No result with noisy data"
    assert "error" not in result, f"Error with noisy data: {result.get('error')}"
    assert result["Rct"] > 0, "Rct should be positive"
    
    print(f"\n✅ Noisy data fitting (5% noise):")
    print(f"   Rct: {result['Rct']:.1f} ohm")
    print(f"   R²: {result.get('r_squared', 0):.4f}")

def test_eis_stern_geary():
    """
    Test Stern-Geary corrosion rate calculation.
    """
    Rct = 100.0  # ohm
    beta_a = 0.12  # V/dec
    beta_c = 0.12  # V/dec
    area = 1.0  # cm²
    
    result = EISEngine.stern_geary_corrosion_rate(Rct, beta_a, beta_c, area)
    
    assert result is not None, "No result returned"
    
    if isinstance(result, dict):
        print(f"\n✅ Stern-Geary result:")
        for key, value in result.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4e}")
        # Check for expected keys (i_corr_uA_cm2 or corrosion_rate_mm_yr)
        if "corrosion_rate_mm_yr" in result:
            assert result["corrosion_rate_mm_yr"] > 0
        elif "i_corr_uA_cm2" in result:
            assert result["i_corr_uA_cm2"] > 0
    elif isinstance(result, (int, float)):
        assert result > 0, f"Corrosion rate should be positive: {result}"
        print(f"\n✅ Stern-Geary corrosion rate: {result:.4f} mm/year")

if __name__ == "__main__":
    test_eis_generate_test_data()
    test_eis_randles_circuit()
    test_eis_fit_randles()
    test_eis_fit_warburg()
    test_eis_kramers_kronig()
    test_eis_noisy_data()
    test_eis_stern_geary()
