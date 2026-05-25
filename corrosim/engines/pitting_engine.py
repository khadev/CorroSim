"""Pitting Corrosion Analysis Engine - Professional Grade"""

import numpy as np
from scipy import stats
from scipy.ndimage import uniform_filter1d


class PittingEngine:
    """
    Pitting Corrosion Analysis Engine.
    
    Features:
    - Noise-resistant Epit/Erp detection with moving average filter
    - Gumbel extreme value statistics with Gringorten plotting positions
    - Mixed Gumbel distribution detection
    - Power law pit growth with configurable kinetics
    - ASTM G61 compliant cyclic polarization analysis
    
    REFERENCES:
    - ASTM G61 - Cyclic Potentiodynamic Polarization
    - ASTM G46 - Pitting Corrosion Examination
    - Gumbel, E.J. "Statistics of Extremes" (1958)
    - Gringorten, I.I. "A plotting rule for extreme probability paper" (1963)
    """
    
    GROWTH_RATES = {
        'Seawater (carbon steel)': 0.15,
        'Seawater (stainless 304)': 0.02,
        'Seawater (stainless 316)': 0.005,
        'Fresh water (carbon steel)': 0.05,
        'Atmospheric (carbon steel)': 0.03,
        'Soil (carbon steel)': 0.08,
        'Custom': None
    }
    
    @staticmethod
    def extract_pitting_potentials(potential, current, area=1.0,
                                    threshold_factor=10, smooth_window=5):
        """
        Extract Epit and Erp from cyclic polarization data.
        
        Uses moving average filter for noise resistance and requires
        sustained current increase for Epit detection.
        
        Parameters:
        - potential: Array of potentials (V)
        - current: Array of currents (A)
        - area: Electrode area (cm²)
        - threshold_factor: Current increase factor for Epit
        - smooth_window: Moving average window size
        
        Returns dict with Epit, Erp, hysteresis, protection potential
        """
        p = np.array(potential, dtype=float)
        c = np.abs(np.array(current, dtype=float))
        
        if smooth_window > 1 and len(c) > smooth_window:
            c_smooth = uniform_filter1d(c, size=smooth_window)
        else:
            c_smooth = c.copy()
        
        max_idx = np.argmax(p)
        forward_p = p[:max_idx+1]
        forward_c = c_smooth[:max_idx+1]
        reverse_p = p[max_idx:]
        reverse_c = c_smooth[max_idx:]
        
        passive_region = forward_c[:max(1, len(forward_c)//3)]
        passive_current = np.percentile(passive_region, 10)
        
        threshold = passive_current * threshold_factor
        sustained_points = 5
        
        epit_idx = None
        for i in range(len(forward_c) - sustained_points):
            if np.all(forward_c[i:i+sustained_points] > threshold):
                epit_idx = i
                break
        
        Epit = forward_p[epit_idx] if epit_idx is not None else None
        
        Erp = None
        if Epit is not None:
            passive_threshold = passive_current * 3
            for i in range(len(reverse_c)):
                if reverse_c[i] < passive_threshold:
                    Erp = reverse_p[i]
                    break
        
        Eprot = (Erp - 0.1) if Erp is not None else None
        hysteresis = (Epit - Erp) if (Epit is not None and Erp is not None) else None
        
        if Epit is not None and Erp is not None:
            if hysteresis and hysteresis > 0.3:
                resistance = 'Poor - Large hysteresis loop'
            elif hysteresis and hysteresis > 0.1:
                resistance = 'Fair - Moderate hysteresis'
            elif hysteresis and hysteresis > 0:
                resistance = 'Good - Small hysteresis'
            else:
                resistance = 'Excellent - No hysteresis'
        elif Epit is not None:
            resistance = 'Pitting initiated, no repassivation'
        else:
            resistance = 'No pitting detected in scan range'
        
        return {
            'Epit': round(Epit, 4) if Epit is not None else None,
            'Erp': round(Erp, 4) if Erp is not None else None,
            'Eprot': round(Eprot, 4) if Eprot is not None else None,
            'hysteresis': round(hysteresis, 4) if hysteresis is not None else None,
            'passive_current': round(passive_current / area * 1e6, 4),
            'pitting_resistance': resistance,
            'forward_potential': forward_p,
            'forward_current': forward_c,
            'reverse_potential': reverse_p,
            'reverse_current': reverse_c,
            'raw_current': c
        }
    
    @staticmethod
    def gumbel_max_pit_depth(pit_depths, return_period=10.0):
        """
        Extreme value statistics for maximum pit depth prediction.
        
        Uses Gumbel (Type I) distribution with Gringorten plotting positions.
        Detects mixed populations via curvature in Gumbel plot.
        """
        if len(pit_depths) < 5:
            return {'error': 'Need at least 5 pit depth measurements'}
        
        depths = np.sort(pit_depths)
        n = len(depths)
        
        F = (np.arange(1, n+1) - 0.44) / (n + 0.12)
        y = -np.log(-np.log(F))
        
        is_mixed = False
        if n >= 10:
            d2y = np.diff(np.diff(y))
            curvature = np.max(np.abs(d2y))
            is_mixed = curvature > 2.0
        
        slope, intercept, r_value, _, std_err = stats.linregress(y, depths)
        beta = slope
        mu = intercept
        
        T = max(return_period, 1.0)
        y_T = -np.log(-np.log(1 - 1/T)) if T > 1 else y[-1]
        max_depth = mu + beta * y_T
        
        se_prediction = std_err * np.sqrt(1 + 1/n + (y_T - np.mean(y))**2 / np.sum((y - np.mean(y))**2))
        lower_95 = max_depth - 1.96 * se_prediction
        upper_95 = max_depth + 1.96 * se_prediction
        
        return {
            'mu': round(mu, 4),
            'beta': round(beta, 4),
            'r_squared': round(r_value**2, 4),
            'max_depth_predicted': round(max(max_depth, 0), 2),
            'lower_95': round(max(lower_95, 0), 2),
            'upper_95': round(upper_95, 2),
            'return_period': T,
            'n_samples': n,
            'is_mixed_population': is_mixed,
            'warning': 'Data may contain multiple pit populations' if is_mixed else None,
            'gumbel_x': y,
            'gumbel_y': depths
        }
    
    @staticmethod
    def pit_growth_rate(initial_depth, time_years, environment='Seawater (carbon steel)',
                        exponent=0.5, custom_k=None):
        """
        Power law pit growth model: d(t) = d0 + k * t^n
        """
        if isinstance(time_years, (int, float)):
            t = np.linspace(0, time_years, 100)
        else:
            t = np.array(time_years)
        
        if custom_k is not None:
            k = custom_k
        else:
            k = PittingEngine.GROWTH_RATES.get(environment, 0.1)
        
        depths = initial_depth + k * t**exponent
        
        critical_depth = 3.0
        if k > 0:
            time_to_critical = ((critical_depth - initial_depth) / k)**(1/exponent)
        else:
            time_to_critical = float('inf')
        
        return {
            'time': t,
            'depths': depths,
            'initial_depth': initial_depth,
            'final_depth': round(depths[-1], 4),
            'growth_rate_k': round(k, 4),
            'exponent': exponent,
            'environment': environment,
            'time_to_critical': round(time_to_critical, 1) if time_to_critical != float('inf') else None,
            'critical_depth': critical_depth
        }
    
    @staticmethod
    def generate_test_data(with_pitting=True):
        """Generate synthetic cyclic polarization data for testing."""
        forward_p = np.linspace(-0.5, 1.0, 200)
        forward_c = np.zeros(200)
        
        if with_pitting:
            passive_mask = forward_p < 0.3
            forward_c[passive_mask] = 1e-6 + np.random.normal(0, 5e-8, np.sum(passive_mask))
            pitting_mask = forward_p >= 0.3
            forward_c[pitting_mask] = 1e-6 * np.exp((forward_p[pitting_mask] - 0.3) * 12)
            forward_c[pitting_mask] += np.random.normal(0, 1e-5, np.sum(pitting_mask))
        else:
            forward_c = 1e-6 + np.random.normal(0, 5e-8, 200)
        
        reverse_p = np.linspace(1.0, -0.5, 200)
        reverse_c = np.zeros(200)
        
        if with_pitting:
            reverse_c = 1e-3 * np.exp(-(1.0 - reverse_p) * 6)
            reverse_c += 1e-6
            reverse_c[reverse_p < 0.15] = 1e-6
        else:
            reverse_c = 1e-6 + np.random.normal(0, 5e-8, 200)
        
        reverse_c = np.abs(reverse_c)
        
        potential = np.concatenate([forward_p, reverse_p])
        current = np.concatenate([forward_c, reverse_c])
        
        np.random.seed(42)
        pit_depths = np.random.gumbel(loc=0.15, scale=0.05, size=30)
        pit_depths = pit_depths[pit_depths > 0]
        
        return {
            'potential': potential,
            'current': current,
            'expected_Epit': 0.3 if with_pitting else None,
            'expected_Erp': 0.15 if with_pitting else None,
            'pit_depths': pit_depths
        }
    
    @staticmethod
    def get_environment_list():
        """Return list of predefined environments."""
        return list(PittingEngine.GROWTH_RATES.keys())