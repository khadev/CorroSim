"""Unit conversion helpers for corrosion analysis."""

def current_to_amperes(value, unit):
    """Convert current to amperes (A)."""
    unit = unit.lower()
    if unit in ['a', 'amp', 'ampere']:
        return float(value)
    elif unit in ['ma', 'milliamp']:
        return float(value) * 1e-3
    elif unit in ['ua', 'microamp']:
        return float(value) * 1e-6
    elif unit in ['na', 'nanoamp']:
        return float(value) * 1e-9
    else:
        raise ValueError(f"Unknown current unit: {unit}")

def potential_to_volts(value, unit):
    """Convert potential to volts (V)."""
    unit = unit.lower()
    if unit in ['v', 'volt']:
        return float(value)
    elif unit in ['mv', 'millivolt']:
        return float(value) * 1e-3
    else:
        raise ValueError(f"Unknown potential unit: {unit}")

def corrosion_rate_to_mm_per_year(value, unit):
    """Convert corrosion rate to mm/year."""
    unit = unit.lower()
    if unit in ['mm/yr', 'mm/year']:
        return float(value)
    elif unit in ['mpy', 'mils/year']:
        return float(value) * 0.0254
    else:
        raise ValueError(f"Unknown corrosion rate unit: {unit}")

def corrosion_rate_from_mmpy(value_mm_per_year, target_unit):
    """Convert from mm/year to target unit."""
    target = target_unit.lower()
    if target in ['mm/yr', 'mm/year']:
        return value_mm_per_year
    elif target in ['mpy', 'mils/year']:
        return value_mm_per_year / 0.0254
    else:
        raise ValueError(f"Unknown target unit: {target_unit}")

# Convenience aliases
uA_to_A = lambda uA: uA * 1e-6
mA_to_A = lambda mA: mA * 1e-3
mV_to_V = lambda mV: mV * 1e-3
V_to_mV = lambda V: V * 1e3
A_to_uA = lambda A: A * 1e6
A_to_mA = lambda A: A * 1e3
