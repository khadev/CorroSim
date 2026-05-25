"""Inhibitor Efficiency Analysis Engine"""

import numpy as np


class InhibitorEngine:
    """Corrosion Inhibitor Efficiency Calculator."""

    @staticmethod
    def calculate_efficiency(cr_uninhibited, cr_inhibited):
        if cr_uninhibited <= 0:
            return {'error': 'Uninhibited corrosion rate must be > 0'}
        ie = (cr_uninhibited - cr_inhibited) / cr_uninhibited * 100
        ie = np.clip(ie, 0, 100)
        if ie > 95: grade = 'Outstanding'
        elif ie > 90: grade = 'Excellent'
        elif ie > 80: grade = 'Good'
        elif ie > 70: grade = 'Fair'
        elif ie > 50: grade = 'Poor'
        else: grade = 'Ineffective'
        return {'efficiency_pct': round(ie, 2), 'grade': grade,
                'cr_uninhibited': cr_uninhibited, 'cr_inhibited': cr_inhibited,
                'surface_coverage': round(ie / 100, 4)}

    @staticmethod
    def fit_langmuir(concentration, efficiency):
        theta = np.array(efficiency) / 100.0
        C = np.array(concentration)
        valid = (theta > 0.01) & (theta < 0.99)
        if np.sum(valid) < 3:
            return {'error': 'Need at least 3 valid data points'}
        Cv, tv = C[valid], theta[valid]
        y = Cv / tv
        slope, intercept = np.polyfit(Cv, y, 1)
        r_sq = np.corrcoef(Cv, y)[0, 1]**2
        K_ads = 1.0 / intercept if intercept > 0 else 0
        R, T = 8.314, 298
        delta_G = -R * T * np.log(55.5 * K_ads) / 1000 if K_ads > 0 else 0
        return {'K_ads': round(K_ads, 2), 'delta_G_kJ_mol': round(delta_G, 2),
                'r_squared': round(r_sq, 4), 'isotherm_type': 'Langmuir',
                'interpretation': InhibitorEngine._interpret_delta_G(delta_G)}

    @staticmethod
    def fit_freundlich(concentration, efficiency):
        theta = np.array(efficiency) / 100.0
        C = np.array(concentration)
        valid = (theta > 0.01) & (C > 0)
        if np.sum(valid) < 3:
            return {'error': 'Need at least 3 valid data points'}
        log_C, log_t = np.log(C[valid]), np.log(theta[valid])
        slope, intercept = np.polyfit(log_C, log_t, 1)
        r_sq = np.corrcoef(log_C, log_t)[0, 1]**2
        return {'Kf': round(np.exp(intercept), 4), 'n': round(1.0/slope if slope != 0 else 1, 2),
                'r_squared': round(r_sq, 4), 'isotherm_type': 'Freundlich'}

    @staticmethod
    def calculate_synergy(ie_alone_a, ie_alone_b, ie_mixture):
        a, b, m = ie_alone_a/100.0, ie_alone_b/100.0, ie_mixture/100.0
        S = (1 - a - b + a*b) / (1 - m if m < 1 else 0.001)
        if S > 1.2: effect = 'Strong Synergism'
        elif S > 1.0: effect = 'Weak Synergism'
        elif S > 0.8: effect = 'Additive'
        else: effect = 'Antagonism'
        return {'S_parameter': round(S, 3), 'effect': effect,
                'ie_a': ie_alone_a, 'ie_b': ie_alone_b, 'ie_mixture': ie_mixture}

    @staticmethod
    def _interpret_delta_G(delta_G):
        if delta_G < -40: return 'Chemisorption (strong, irreversible)'
        elif delta_G < -20: return 'Mixed physisorption/chemisorption'
        elif delta_G < 0: return 'Physisorption (weak, reversible)'
        else: return 'No spontaneous adsorption'