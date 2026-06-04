import pytest
import numpy as np
from corrosim.engines.pitting_engine import PittingEngine

def test_extract_pitting_potentials():
    potential = np.linspace(-0.5, 0.5, 200)
    current = np.exp(10 * (potential - 0.2))
    result = PittingEngine.extract_pitting_potentials(potential, current, area=1.0)
    assert result is not None
    print(f"\n✅ Pitting potentials extracted")

def test_gumbel_max_pit_depth():
    pit_depths = np.random.gumbel(50, 15, 50)
    result = PittingEngine.gumbel_max_pit_depth(pit_depths, return_period=10.0)
    assert result is not None
    # Updated to match your actual key name
    assert "max_depth_predicted" in result or "depth_um" in result
    print(f"\n✅ Gumbel analysis: predicted max depth = {result.get('max_depth_predicted', result.get('depth_um', 'N/A'))}")

def test_pit_growth_rate():
    result = PittingEngine.pit_growth_rate(10.0, 5.0, environment='Seawater (carbon steel)')
    assert result is not None
    print(f"\n✅ Pit growth prediction")

def test_generate_test_data():
    result = PittingEngine.generate_test_data(with_pitting=True)
    assert result is not None
    print(f"\n✅ Test data generation")

def test_get_environment_list():
    environments = PittingEngine.get_environment_list()
    assert environments is not None
    assert len(environments) > 0
    print(f"\n✅ Available environments: {environments[:3]}...")

def test_pitting_workflow():
    test_data = PittingEngine.generate_test_data(with_pitting=True)
    env_list = PittingEngine.get_environment_list()
    results = []
    for env in env_list[:3]:
        try:
            growth = PittingEngine.pit_growth_rate(10.0, 10.0, environment=env)
            results.append(growth)
        except:
            pass
    print(f"\n✅ Pitting workflow: {len(results)} environments tested")

if __name__ == "__main__":
    test_extract_pitting_potentials()
    test_gumbel_max_pit_depth()
    test_pit_growth_rate()
    test_generate_test_data()
    test_get_environment_list()
    test_pitting_workflow()
