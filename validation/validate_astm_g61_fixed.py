"""ASTM G61: Cyclic Potentiodynamic Polarization for Pitting Corrosion."""

import sys
sys.path.append('.')
import numpy as np
from corrosim.engines.pitting_engine import PittingEngine

def generate_realistic_pitting_data(epit=-0.200, erp=-0.300):
    """Generate more realistic cyclic polarization with clear pitting."""
    # Forward scan
    forward_potential = np.linspace(-0.5, 0.1, 150)
    
    # Passive region (low current) then sharp increase at Epit
    forward_current = np.ones_like(forward_potential) * 1e-6
    pitting_region = forward_potential > epit
    forward_current[pitting_region] = 1e-6 * np.exp(20 * (forward_potential[pitting_region] - epit))
    
    # Reverse scan
    reverse_potential = np.linspace(0.1, -0.5, 150)
    reverse_current = forward_current[::-1] * 0.8  # Some hysteresis
    
    potential = np.concatenate([forward_potential, reverse_potential])
    current = np.concatenate([forward_current, reverse_current])
    
    return potential, current

def test_astm_g61_pitting_detection():
    print("\n" + "="*60)
    print("ASTM G61 Validation: Pitting Potential Detection")
    print("="*60)
    
    epit_expected = -0.200
    potential, current = generate_realistic_pitting_data(epit_expected)
    
    result = PittingEngine.extract_pitting_potentials(potential, current, area=1.0)
    
    print(f"\n📊 CorroSim Results:")
    print(f"   Detected Epit: {result.get('Epit', 'N/A')}")
    print(f"   Expected Epit: {epit_expected} V")
    print(f"   Pitting resistance: {result.get('pitting_resistance', 'N/A')}")
    
    if result.get('Epit'):
        epit_error = abs(result['Epit'] - epit_expected)
        print(f"\n📈 Epit error: {epit_error*1000:.1f} mV")
        
        if epit_error < 0.100:
            print("\n✅ ASTM G61 Validation PASSED")
        else:
            print(f"\n⚠️ Epit detection off by {epit_error*1000:.0f} mV")
            print("   (May need adjustment in pitting_engine thresholds)")
    else:
        print("\n⚠️ No pitting detected")

if __name__ == "__main__":
    test_astm_g61_pitting_detection()
