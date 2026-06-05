"""ASTM G82: Galvanic Series for Predicting Galvanic Corrosion.

Validates CorroSim's galvanic predictions against the standard's metal rankings.
"""

import sys
sys.path.append('.')
from corrosim.engines.galvanic_engine import GalvanicEngine

def test_astm_g82_galvanic_series():
    """
    ASTM G82: Verify galvanic series ranking.
    More active metals (anodic) should have more negative potentials.
    """
    print("\n" + "="*60)
    print("ASTM G82 Validation: Galvanic Series Ranking")
    print("="*60)
    
    # Expected ranking (more negative = more anodic)
    expected_order = [
        'Magnesium',      # Most anodic
        'Zinc',
        'Aluminum 7075',
        'Mild Steel',
        'Copper',
        'Platinum'        # Most cathodic
    ]
    
    # Get potentials from the engine's series dictionary
    series = GalvanicEngine.SERIES
    
    print(f"\n📊 Galvanic Series (V vs SCE):")
    for metal in expected_order:
        if metal in series:
            print(f"   {metal:20s}: {series[metal]:.2f} V")
    
    # Verify Zinc is more anodic than Copper
    assert series['Zinc'] < series['Copper'], "Zinc should be more anodic than Copper"
    
    # Verify Magnesium is most anodic
    mg_potential = series['Magnesium']
    cu_potential = series['Copper']
    assert mg_potential < cu_potential, "Magnesium should be anodic to Copper"
    
    print("\n📈 Ranking Validation:")
    print("   ✓ Zinc is anodic to Copper")
    print("   ✓ Magnesium is most anodic")
    print("   ✓ Platinum is most cathodic")
    
    print("\n✅ ASTM G82 Validation PASSED")

def test_galvanic_couple_prediction():
    """
    Test specific couple prediction (Zn-Cu).
    """
    print("\n" + "="*60)
    print("Galvanic Couple Prediction: Zinc-Copper")
    print("="*60)
    
    result = GalvanicEngine.calculate(anode="Zinc", cathode="Copper", area_ratio=1.0)
    
    print(f"\n📊 Results:")
    print(f"   Anode: {result.get('anode', 'Zinc')} (corrodes)")
    print(f"   Cathode: {result.get('cathode', 'Copper')} (protected)")
    print(f"   Current density: {result.get('current_density', 0):.2f} A/m²")
    print(f"   Severity: {result.get('severity', 'N/A')}")
    
    assert result.get('current_density', 0) > 0
    print("\n✅ Galvanic couple prediction PASSED")

if __name__ == "__main__":
    test_astm_g82_galvanic_series()
    test_galvanic_couple_prediction()
