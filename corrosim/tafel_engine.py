"""Tafel Analysis Engine for CorroSim"""

import numpy as np
import pandas as pd
from scipy import stats
from .utils.constants import (
    EW_IRON, DENSITY_STEEL, N_ELECTRONS,
    FARADAY_CONSTANT, SECONDS_PER_YEAR,
    TAFEL_SLOPE_MIN, TAFEL_SLOPE_MAX,
    TAFEL_REGION_MIN, TAFEL_REGION_MAX
)


class TafelEngine:
    """
    Tafel polarization analysis engine.
    
    CORRECTED VERSION:
    - Proper Tafel slope calculation: β = 1/slope (V/dec)
    - The Tafel equation: η = β * log(i/icorr)
    - So log(i) = (1/β) * η + log(icorr)
    - The slope of log(i) vs E is 1/β (for anodic) or -1/β (for cathodic)
    """
    
    @staticmethod
    def generate_test_data(ecorr=-0.5, icorr=10e-6, beta_a=0.12, beta_c=0.12, area=1.0):
        """
        Generate synthetic Butler-Volmer data.
        
        icorr in A/cm², beta in V/dec
        """
        potential = np.arange(ecorr - 0.250, ecorr + 0.251, 0.002)
        overpotential = potential - ecorr
        
        i_corr_total = icorr * area
        
        # Butler-Volmer: i = icorr * (10^(η/βa) - 10^(-η/βc))
        anodic_part = 10 ** (overpotential / beta_a)
        cathodic_part = 10 ** (-overpotential / beta_c)
        total_current = i_corr_total * (anodic_part - cathodic_part)
        
        # Add 1% noise
        noise = 1 + np.random.normal(0, 0.01, len(potential))
        total_current = total_current * noise
        
        return pd.DataFrame({
            'Potential_V': potential,
            'Current_A': total_current
        })
    
    @staticmethod
    def _detect_current_unit(current_array):
        """Detect current units based on magnitude"""
        max_abs = np.max(np.abs(current_array))
        
        if max_abs < 1e-8:
            return 1.0, "A (nA range)"
        elif max_abs < 1e-4:
            return 1.0, "A (μA range)"
        elif max_abs < 0.1:
            return 1.0, "A (mA range)"
        elif max_abs < 100:
            return 0.001, "mA"
        else:
            return 1e-6, "μA"
    
    @staticmethod
    def analyze(potential, current, area=1.0, auto_detect_units=True):
        """
        Analyze Tafel polarization data.
        
        CORRECTED ALGORITHM:
        1. Find Ecorr (minimum |i|)
        2. In Tafel region (80-200mV from Ecorr):
           - log(i) vs E is linear with slope = 1/βa (anodic) or -1/βc (cathodic)
           - β = 1/|slope| (in V/dec)
        3. Extrapolate Tafel lines to Ecorr to find Icorr
        """
        try:
            p = np.array(potential, dtype=float)
            c_raw = np.array(current, dtype=float)
            
            # Step 1: Unit conversion
            if auto_detect_units:
                scale, unit = TafelEngine._detect_current_unit(c_raw)
                c = c_raw * scale
                print(f"[Tafel] Unit: {unit}")
            else:
                c = c_raw.copy()
            
            # Step 2: Filter
            valid = (np.abs(c) > 1e-15) & np.isfinite(p) & np.isfinite(c)
            p = p[valid]
            c = c[valid]
            
            if len(p) < 20:
                print("[Tafel] ERROR: Need 20+ points")
                return None
            
            # Step 3: Find Ecorr
            log_i = np.log10(np.abs(c))
            ecorr_idx = np.argmin(np.abs(c))
            ecorr = p[ecorr_idx]
            log_i_at_ecorr = log_i[ecorr_idx]
            
            print(f"[Tafel] Ecorr = {ecorr:.4f} V")
            print(f"[Tafel] log|I| at Ecorr = {log_i_at_ecorr:.4f}")
            
            # Step 4: Identify Tafel regions
            overpotential = p - ecorr
            
            # Anodic: 80-200 mV above Ecorr
            anodic_mask = (overpotential > 0.080) & (overpotential < 0.200)
            # Cathodic: 80-200 mV below Ecorr
            cathodic_mask = (overpotential < -0.080) & (overpotential > -0.200)
            
            print(f"[Tafel] Anodic pts: {np.sum(anodic_mask)}, Cathodic pts: {np.sum(cathodic_mask)}")
            
            # Step 5: Fit Tafel slopes
            # Tafel equation: log(i) = (1/βa)*(E - Ecorr) + log(icorr)  [anodic]
            #                 log(i) = -(1/βc)*(E - Ecorr) + log(icorr) [cathodic]
            # So: slope = 1/βa (anodic) or -1/βc (cathodic)
            # And: β = 1/|slope| (in V/dec)
            
            # --- Anodic fit ---
            beta_a_V = 0.12  # default 120 mV/dec
            beta_a_mV = 120
            slope_a = 1.0 / beta_a_V  # = 8.33 for 120 mV/dec
            intercept_a = log_i_at_ecorr - slope_a * ecorr
            r_a = 0.7
            
            if np.sum(anodic_mask) >= 5:
                ap = p[anodic_mask]
                al = log_i[anodic_mask]
                slope_fit, intercept_fit, r_val, _, _ = stats.linregress(ap, al)
                
                # slope_fit = 1/βa (in decades/V)
                # βa = 1/slope_fit (in V/dec)
                if abs(slope_fit) > 0.5:  # Must have reasonable slope (> 0.5 decades/V = < 2 V/dec)
                    beta_a_V = 1.0 / abs(slope_fit)
                    beta_a_mV = beta_a_V * 1000
                    slope_a = slope_fit
                    intercept_a = intercept_fit
                    r_a = r_val
                    
                    print(f"[Tafel] βa fitted: {beta_a_mV:.1f} mV/dec (slope={slope_fit:.2f} dec/V, R²={r_val**2:.4f})")
                    
                    # Validate range
                    if beta_a_mV < 20 or beta_a_mV > 500:
                        print(f"[Tafel] βa={beta_a_mV:.1f} outside range, using default 120")
                        beta_a_V = 0.12
                        beta_a_mV = 120
                        slope_a = 1.0 / beta_a_V
                        intercept_a = log_i_at_ecorr - slope_a * ecorr
                else:
                    print(f"[Tafel] Anodic slope too flat ({slope_fit:.4f} dec/V), using default")
            else:
                print("[Tafel] Not enough anodic points, using default")
            
            # --- Cathodic fit ---
            beta_c_V = 0.12
            beta_c_mV = 120
            slope_c = -1.0 / beta_c_V  # Negative for cathodic
            intercept_c = log_i_at_ecorr - slope_c * ecorr
            r_c = 0.7
            
            if np.sum(cathodic_mask) >= 5:
                cp = p[cathodic_mask]
                cl = log_i[cathodic_mask]
                slope_fit, intercept_fit, r_val, _, _ = stats.linregress(cp, cl)
                
                # slope_fit should be negative for cathodic
                if abs(slope_fit) > 0.5:
                    beta_c_V = 1.0 / abs(slope_fit)
                    beta_c_mV = beta_c_V * 1000
                    slope_c = slope_fit
                    intercept_c = intercept_fit
                    r_c = r_val
                    
                    print(f"[Tafel] βc fitted: {beta_c_mV:.1f} mV/dec (slope={slope_fit:.2f} dec/V, R²={r_val**2:.4f})")
                    
                    if beta_c_mV < 20 or beta_c_mV > 500:
                        print(f"[Tafel] βc={beta_c_mV:.1f} outside range, using default 120")
                        beta_c_V = 0.12
                        beta_c_mV = 120
                        slope_c = -1.0 / beta_c_V
                        intercept_c = log_i_at_ecorr - slope_c * ecorr
                else:
                    print(f"[Tafel] Cathodic slope too flat ({slope_fit:.4f} dec/V), using default")
            else:
                print("[Tafel] Not enough cathodic points, using default")
            
            # Step 6: Calculate Icorr from Tafel line intersection at Ecorr
            log_icorr_a = slope_a * ecorr + intercept_a
            log_icorr_c = slope_c * ecorr + intercept_c
            log_icorr = (log_icorr_a + log_icorr_c) / 2
            
            icorr_A = 10 ** log_icorr
            icorr_density = icorr_A / area
            icorr_uA_cm2 = icorr_density * 1e6
            
            print(f"[Tafel] log(Icorr) = {log_icorr:.4f}")
            print(f"[Tafel] Icorr = {icorr_uA_cm2:.2f} μA/cm²")
            
            # Step 7: Corrosion Rate
            cr = (icorr_density * EW_IRON * SECONDS_PER_YEAR * 10) / (N_ELECTRONS * FARADAY_CONSTANT * DENSITY_STEEL)
            cr = max(min(cr, 100), 1e-6)
            
            print(f"[Tafel] CR = {cr:.4f} mm/yr")
            print(f"[Tafel] βa = {beta_a_mV:.1f} mV/dec, βc = {beta_c_mV:.1f} mV/dec")
            
            r2 = min(r_a, r_c) ** 2
            
            return {
                'ecorr': ecorr,
                'icorr': icorr_uA_cm2,
                'cr': cr,
                'beta_a': beta_a_mV,
                'beta_c': beta_c_mV,
                'r2': r2,
                'slope_a': slope_a,
                'intercept_a': intercept_a,
                'slope_c': slope_c,
                'intercept_c': intercept_c,
                'p': p,
                'log_i': log_i,
                'anodic_mask': anodic_mask,
                'cathodic_mask': cathodic_mask
            }
            
        except Exception as e:
            print(f"[Tafel] Error: {e}")
            import traceback
            traceback.print_exc()
            return None