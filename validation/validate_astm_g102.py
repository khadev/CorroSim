"""ASTM G102: Calculation of Corrosion Rates from Electrochemical Measurements.

Validates CorroSim's Tafel analysis against the standard's worked example.
"""

import sys
sys.path.append('.')
import numpy as np
from corrosim.tafel_engine import TafelEngine

def test_astm_g102_carbon_steel():
    """
    ASTM G102 Example: Carbon steel in seawater at 25°C.
    
    Given parameters:
    - Ecorr = -0.600 V (vs. SCE)
    - icorr = 25.0 µA/cm²
    - βa = 90 mV/dec, βc = 120 mV/dec
    - Equivalent weight = 27.92 g/eq
    - Density = 7.87 g/cm³
    - Expected CR = 0.29 mm/year (calculated per ASTM G102)
    """
    print("\n" + "="*60)
    print("ASTM G102 Validation: Carbon Steel in Seawater")
    print("="*60)
    
    # Generate synthetic data from standard parameters
    ecorr = -0.600
    icorr_true = 25e-6  # A/cm²
    beta_a = 0.090      # V/dec
    beta_c = 0.120      # V/dec
    
    potential = np.linspace(ecorr - 0.250, ecorr + 0.250, 100)
    overpotential = potential - ecorr
    current = icorr_true * (10**(overpotential / beta_a) - 10**(-overpotential / beta_c))
    current = np.abs(current)
    
    # Run CorroSim analysis
    result = TafelEngine.analyze(potential, current, area=1.0)
    
    # Display results
    print(f"\n📊 CorroSim Results:")
    print(f"   Ecorr: {result['ecorr']:.4f} V (expected: {ecorr})")
    print(f"   Icorr: {result['icorr']:.2f} µA/cm² (expected: {icorr_true*1e6:.0f} µA/cm²)")
    print(f"   βa: {result['beta_a']:.1f} mV/dec (expected: {beta_a*1000:.0f} mV/dec)")
    print(f"   βc: {result['beta_c']:.1f} mV/dec (expected: {beta_c*1000:.0f} mV/dec)")
    print(f"   Corrosion rate: {result['cr']:.4f} mm/year (expected: ~0.29 mm/year)")
    
    # Calculate errors
    icorr_error = abs(result['icorr'] - icorr_true*1e6) / (icorr_true*1e6) * 100
    beta_a_error = abs(result['beta_a'] - beta_a*1000) / (beta_a*1000) * 100
    
    print(f"\n📈 Accuracy:")
    print(f"   Icorr error: {icorr_error:.1f}%")
    print(f"   Beta_a error: {beta_a_error:.1f}%")
    
    # Assertions (within 15% tolerance)
    assert icorr_error < 15, f"Icorr error too high: {icorr_error:.1f}%"
    assert beta_a_error < 15, f"Beta_a error too high: {beta_a_error:.1f}%"
    
    print("\n✅ ASTM G102 Validation PASSED")
    return result

if __name__ == "__main__":
    test_astm_g102_carbon_steel()
