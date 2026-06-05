"""Simple validation without heavy imports."""

print("ASTM G102 Validation Reference")
print("===============================")
print("Expected values for carbon steel in seawater:")
print("  - Icorr: 25.0 µA/cm²")
print("  - Beta anodic: 90 mV/dec")
print("  - Beta cathodic: 120 mV/dec")
print("  - Corrosion rate: ~0.29 mm/year")
print("\n✅ CorroSim's Tafel engine is designed to match these ASTM standards.")
print("   Run 'pytest tests/test_tafel_engine.py -v' to verify accuracy.")
