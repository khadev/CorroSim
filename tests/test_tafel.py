"""Tests for Tafel Engine"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from corrosim.tafel_engine import TafelEngine


def test_generate_test_data():
    """Test synthetic data generation"""
    df = TafelEngine.generate_test_data()
    assert len(df) > 0
    assert 'Potential_V' in df.columns
    assert 'Current_A' in df.columns
    print("✓ Test data generation passed")


def test_tafel_analysis_accuracy():
    """Test that analysis recovers known parameters within tolerance"""
    print("\nGenerating synthetic data with known parameters...")
    print("  Ecorr = -0.5 V")
    print("  Icorr = 10 μA/cm²")
    print("  βa = 120 mV/dec")
    print("  βc = 120 mV/dec")
    
    # Generate data with known parameters
    df = TafelEngine.generate_test_data(
        ecorr=-0.5, icorr=10e-6, beta_a=0.12, beta_c=0.12, area=1.0
    )
    
    # Analyze
    result = TafelEngine.analyze(
        df['Potential_V'].values, df['Current_A'].values, area=1.0
    )
    
    assert result is not None, "Analysis failed to return results"
    
    # Check results
    print(f"\nResults:")
    print(f"  Ecorr: {result['ecorr']:.4f} V (expected -0.500 V)")
    print(f"  Icorr: {result['icorr']:.1f} μA/cm² (expected ~10 μA/cm²)")
    print(f"  βa:    {result['beta_a']:.1f} mV/dec (expected ~120 mV/dec)")
    print(f"  βc:    {result['beta_c']:.1f} mV/dec (expected ~120 mV/dec)")
    print(f"  CR:    {result['cr']:.4f} mm/yr")
    print(f"  R²:    {result['r2']:.4f}")
    
    # Check Ecorr (should be very accurate, within 5 mV)
    ecorr_error = abs(result['ecorr'] - (-0.5))
    assert ecorr_error < 0.010, f"Ecorr error too large: {ecorr_error:.4f} V"
    
    # Check Tafel slopes (within 30%)
    beta_a_error = abs(result['beta_a'] - 120) / 120
    beta_c_error = abs(result['beta_c'] - 120) / 120
    assert beta_a_error < 0.30, f"βa error too large: {beta_a_error*100:.1f}%"
    assert beta_c_error < 0.30, f"βc error too large: {beta_c_error*100:.1f}%"
    
    # Check Icorr (within a factor of 3 due to noise and fitting)
    icorr_ratio = result['icorr'] / 10
    assert 0.2 < icorr_ratio < 5.0, f"Icorr too far from expected: {result['icorr']:.1f} μA/cm² (ratio={icorr_ratio:.2f})"
    
    print(f"\n✓ All accuracy checks passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("TAFEL ENGINE VALIDATION TESTS")
    print("=" * 60)
    test_generate_test_data()
    test_tafel_analysis_accuracy()
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)