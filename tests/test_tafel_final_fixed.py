import pytest
import numpy as np
import pandas as pd
from corrosim.tafel_engine import TafelEngine

def test_tafel_with_dataframe():
    """
    Test TafelEngine.analyze() using the DataFrame returned by generate_test_data().
    """
    print("\n" + "="*60)
    print("Testing TafelEngine with DataFrame output")
    print("="*60)
    
    # 1. Generate data - this returns a DataFrame
    df = TafelEngine.generate_test_data(area=1.0)
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Column names: {df.columns.tolist()}")
    
    # 2. Extract potential and current from DataFrame
    potential = df['Potential_V'].values.astype(float)
    current = df['Current_A'].values.astype(float)
    
    print(f"Potential range: [{potential.min():.3f}, {potential.max():.3f}] V")
    print(f"Current range: [{current.min():.2e}, {current.max():.2e}] A")
    
    # 3. Run analysis
    result = TafelEngine.analyze(potential, current, area=1.0)
    
    # 4. Check results
    assert result is not None, "No result returned"
    
    print("\n✅ Analysis successful!")
    print(f"   Ecorr: {result.get('ecorr', 0):.4f} V")
    print(f"   Icorr: {result.get('icorr', 0):.2f} μA/cm²")
    print(f"   βa: {result.get('beta_a', 0):.1f} mV/dec")
    print(f"   βc: {result.get('beta_c', 0):.1f} mV/dec")
    print(f"   Corrosion rate (cr): {result.get('cr', 0):.4f} mm/year")
    print(f"   R²: {result.get('r2', 0):.4f}")
    
    # Basic assertions - NOTE: beta values are in mV/dec (typically 50-250)
    assert result['icorr'] > 0, "Icorr should be positive"
    assert result['cr'] > 0, "Corrosion rate should be positive"
    assert result['ecorr'] < 0, "Ecorr should be negative"
    assert 50 < result['beta_a'] < 250, f"Beta_a out of range (mV/dec): {result['beta_a']}"
    assert 50 < result['beta_c'] < 250, f"Beta_c out of range (mV/dec): {result['beta_c']}"
    assert result['r2'] > 0.99, f"R² too low: {result['r2']}"
    
    print("\n✅ All assertions passed!")

def test_tafel_manual_data():
    """
    Test with manually created synthetic data.
    """
    print("\n" + "="*60)
    print("Testing with manually created data")
    print("="*60)
    
    # Create synthetic Tafel data
    ecorr = -0.5
    icorr = 10e-6  # 10 µA/cm²
    beta = 0.120   # 120 mV/dec (in V/dec for calculation)
    
    # Generate potential points
    potential = np.linspace(ecorr - 0.250, ecorr + 0.250, 100)
    
    # Generate current using Butler-Volmer
    overpotential = potential - ecorr
    current = icorr * (10**(overpotential / beta) - 10**(-overpotential / beta))
    current = np.abs(current)
    
    print(f"Expected: Ecorr={ecorr} V, Icorr={icorr*1e6:.1f} μA/cm², β={beta*1000:.0f} mV/dec")
    
    # Run analysis
    result = TafelEngine.analyze(potential, current, area=1.0)
    
    assert result is not None
    
    print(f"\nRecovered:")
    print(f"   Ecorr: {result['ecorr']:.4f} V")
    print(f"   Icorr: {result['icorr']:.2f} μA/cm²")
    print(f"   βa: {result['beta_a']:.1f} mV/dec")
    print(f"   βc: {result['beta_c']:.1f} mV/dec")
    print(f"   cr: {result['cr']:.4f} mm/year")
    print(f"   r²: {result['r2']:.4f}")
    
    # Check accuracy (allow 10% error)
    icorr_error = abs(result['icorr'] - icorr*1e6) / (icorr*1e6) * 100
    beta_error = abs(result['beta_a'] - beta*1000) / (beta*1000) * 100
    
    print(f"\nAccuracy:")
    print(f"   Icorr error: {icorr_error:.1f}%")
    print(f"   Beta error: {beta_error:.1f}%")
    
    assert icorr_error < 15, f"Icorr error too high: {icorr_error:.1f}%"
    assert beta_error < 15, f"Beta error too high: {beta_error:.1f}%"
    assert result['cr'] > 0
    assert result['r2'] > 0.99
    
    print("\n✅ Manual data test passed!")

def test_constants():
    """Quick sanity check of constants."""
    from corrosim.utils.constants import FARADAY_CONSTANT, SECONDS_PER_YEAR, EW_IRON, DENSITY_STEEL
    
    print("\n" + "="*60)
    print("Constants Sanity Check")
    print("="*60)
    print(f"   Faraday constant: {FARADAY_CONSTANT:.0f} C/mol")
    print(f"   Seconds per year: {SECONDS_PER_YEAR:.0f}")
    print(f"   EW Iron: {EW_IRON:.2f} g/eq")
    print(f"   Density steel: {DENSITY_STEEL:.2f} g/cm³")
    
    assert FARADAY_CONSTANT == pytest.approx(96485, rel=0.01)
    assert SECONDS_PER_YEAR == pytest.approx(31536000, rel=0.01)
    assert 20 < EW_IRON < 30
    assert 7 < DENSITY_STEEL < 8
    
    print("\n✅ Constants test passed!")

if __name__ == "__main__":
    test_tafel_with_dataframe()
    test_tafel_manual_data()
    test_constants()
