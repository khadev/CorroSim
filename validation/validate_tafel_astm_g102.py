"""Validate Tafel analysis against ASTM G102 reference example."""

import sys
sys.path.append('.')
import numpy as np
from corrosim.tafel_engine import TafelEngine

def test_astm_g102_example():
    ecorr = -0.600
    icorr = 25e-6
    beta_a = 0.090
    beta_c = 0.120
    area = 1.0
    
    potential = np.linspace(ecorr - 0.250, ecorr + 0.250, 100)
    overpotential = potential - ecorr
    current = icorr * (10**(overpotential / beta_a) - 10**(-overpotential / beta_c))
    current = np.abs(current)
    
    result = TafelEngine.analyze(potential, current, area=area)
    
    print(f"Expected icorr: 25.0 µA/cm²")
    print(f"CorroSim icorr: {result['icorr']:.2f} µA/cm²")
    print(f"Corrosion rate: {result['cr']:.4f} mm/year")
    
    assert abs(result['icorr'] - 25.0) / 25.0 < 0.20
    print("✅ ASTM G102 validation PASSED")

if __name__ == "__main__":
    test_astm_g102_example()
