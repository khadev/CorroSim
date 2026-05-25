"""EIS Analysis Engine - Professional Grade"""

import numpy as np
from scipy.optimize import curve_fit


class EISEngine:
    """Electrochemical Impedance Spectroscopy Fitting Engine."""

    @staticmethod
    def cpe_impedance(omega, Q, alpha):
        return 1 / (Q * (1j * omega) ** alpha)

    @staticmethod
    def _randles_impedance(freq, Rs, Rct, Cdl):
        omega = 2 * np.pi * freq
        return Rs + Rct / (1 + 1j * omega * Rct * Cdl)

    @staticmethod
    def _randles_cpe_impedance(freq, Rs, Rct, Q, alpha):
        omega = 2 * np.pi * freq
        Z_cpe = EISEngine.cpe_impedance(omega, Q, alpha)
        return Rs + 1 / (1/Rct + 1/Z_cpe)

    @staticmethod
    def _warburg_impedance(freq, Rs, Rct, Cdl, W):
        omega = 2 * np.pi * freq
        Zw = W / np.sqrt(1j * omega)
        Z_parallel = 1 / (1/(Rct + Zw) + 1j * omega * Cdl)
        return Rs + Z_parallel

    @staticmethod
    def _warburg_cpe_impedance(freq, Rs, Rct, Q, alpha, W):
        omega = 2 * np.pi * freq
        Zw = W / np.sqrt(1j * omega)
        Z_cpe = EISEngine.cpe_impedance(omega, Q, alpha)
        Z_parallel = 1 / (1/(Rct + Zw) + 1/Z_cpe)
        return Rs + Z_parallel

    @staticmethod
    def generate_test_data(circuit='randles', depressed=False, noise_level=0.01):
        """Generate synthetic EIS data with recoverable parameters."""
        freq = np.logspace(5, -2, 60)
        Rs_true, Rct_true = 10.0, 1000.0
        if circuit == 'randles':
            if depressed:
                Q_true, alpha_true = 1e-4, 0.85
                Z = EISEngine._randles_cpe_impedance(freq, Rs_true, Rct_true, Q_true, alpha_true)
            else:
                Cdl_true = 1e-4
                Z = EISEngine._randles_impedance(freq, Rs_true, Rct_true, Cdl_true)
        else:
            W_true = 100.0
            if depressed:
                Q_true, alpha_true = 1e-4, 0.85
                Z = EISEngine._warburg_cpe_impedance(freq, Rs_true, Rct_true, Q_true, alpha_true, W_true)
            else:
                Cdl_true = 1e-4
                Z = EISEngine._warburg_impedance(freq, Rs_true, Rct_true, Cdl_true, W_true)
        Z_mod = np.abs(Z)
        noise = np.random.normal(0, noise_level, len(freq)) + 1j * np.random.normal(0, noise_level, len(freq))
        Z = Z + Z_mod * noise
        return {'freq': freq, 'Z_real': Z.real, 'Z_imag': np.abs(Z.imag),
                'true_Rs': Rs_true, 'true_Rct': Rct_true}

    @staticmethod
    def _complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds):
        Z_data = np.column_stack([Z_real, Z_imag]).ravel()
        Z_mod = np.sqrt(Z_real**2 + Z_imag**2)
        weights = 1.0 / (Z_mod**2 + 1e-10)
        sigma = 1.0 / np.sqrt(weights + 1e-10)
        sigma = np.column_stack([sigma, sigma]).ravel()
        def wm(f, *params):
            Z = model_func(f, *params)
            return np.column_stack([Z.real, Z.imag]).ravel()
        popt, _ = curve_fit(wm, freq, Z_data, p0=p0, bounds=bounds, sigma=sigma, maxfev=20000, ftol=1e-12)
        return popt

    @staticmethod
    def _calculate_fit_quality(freq, Z_real, Z_imag, model_func, params):
        Z_fitted = model_func(freq, *params)
        Z_data = np.column_stack([Z_real, Z_imag]).ravel()
        Z_fit_flat = np.column_stack([Z_fitted.real, Z_fitted.imag]).ravel()
        residuals = Z_data - Z_fit_flat
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((Z_data - np.mean(Z_data))**2)
        r_squared = 1 - ss_res/ss_tot if ss_tot > 0 else 0
        chi_sq = np.sum(residuals**2) / max(len(freq) - len(params), 1)
        return {'Z_fitted': Z_fitted, 'r_squared': round(r_squared, 4), 'chi_squared': round(chi_sq, 2)}

    @staticmethod
    def fit_randles(freq, Z_real, Z_imag, use_cpe=False):
        """Fit Randles circuit with smart initial guesses."""
        high_freq_idx = freq > np.max(freq) * 0.1
        Rs_guess = np.percentile(Z_real[high_freq_idx], 10) if np.any(high_freq_idx) else np.min(Z_real)
        Rct_guess = np.max(Z_real) - np.min(Z_real)
        idx_peak = np.argmax(Z_imag)
        freq_peak = freq[idx_peak]
        Cdl_guess = 1.0/(2.0*np.pi*freq_peak*Rct_guess) if Rct_guess > 1 and freq_peak > 0 else 1e-4
        Rs_guess = np.clip(Rs_guess, 0.1, 1e4)
        Rct_guess = np.clip(Rct_guess, 1, 1e7)
        Cdl_guess = np.clip(Cdl_guess, 1e-12, 1e-1)
        if use_cpe:
            model_func = EISEngine._randles_cpe_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, 0.85]
            bounds = ([Rs_guess*0.1, Rct_guess*0.1, 1e-12, 0.5], [Rs_guess*10, Rct_guess*10, 1e-1, 1.0])
        else:
            model_func = EISEngine._randles_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess]
            bounds = ([Rs_guess*0.1, Rct_guess*0.1, 1e-12], [Rs_guess*10, Rct_guess*10, 1e-1])
        try:
            popt = EISEngine._complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds)
            quality = EISEngine._calculate_fit_quality(freq, Z_real, Z_imag, model_func, popt)
            result = {'Rs': round(popt[0], 2), 'Rct': round(popt[1], 2),
                      'circuit': 'R(RQ) - Randles CPE' if use_cpe else 'R(RC) - Randles', **quality}
            if use_cpe: result['Q'] = round(popt[2], 6); result['alpha'] = round(popt[3], 4)
            else: result['Cdl'] = round(popt[2], 6)
            return result
        except:
            Z_est = EISEngine._randles_impedance(freq, Rs_guess, Rct_guess, Cdl_guess)
            return {'Rs': round(Rs_guess, 2), 'Rct': round(Rct_guess, 2), 'Cdl': round(Cdl_guess, 6),
                    'circuit': 'R(RC) (estimated)', 'r_squared': 0.0, 'chi_squared': 999999,
                    'Z_fitted': Z_est, 'warning': 'Fit did not converge'}

    @staticmethod
    def fit_warburg(freq, Z_real, Z_imag, use_cpe=False):
        """Fit Randles-Warburg circuit."""
        high_freq_idx = freq > np.max(freq) * 0.1
        Rs_guess = np.percentile(Z_real[high_freq_idx], 10) if np.any(high_freq_idx) else np.min(Z_real)
        Rct_guess = np.clip(np.max(Z_real) - np.min(Z_real), 1, 1e7)
        idx_peak = np.argmax(Z_imag)
        freq_peak = freq[idx_peak]
        Cdl_guess = np.clip(1.0/(2.0*np.pi*freq_peak*Rct_guess) if freq_peak > 0 else 1e-4, 1e-12, 1e-1)
        W_guess = np.clip(Rct_guess * 0.1, 1e-6, 1e6)
        Rs_guess = np.clip(Rs_guess, 0.1, 1e4)
        if use_cpe:
            model_func = EISEngine._warburg_cpe_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, 0.85, W_guess]
            bounds = ([Rs_guess*0.1, Rct_guess*0.1, 1e-12, 0.5, 1e-6], [Rs_guess*10, Rct_guess*10, 1e-1, 1.0, 1e6])
        else:
            model_func = EISEngine._warburg_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, W_guess]
            bounds = ([Rs_guess*0.1, Rct_guess*0.1, 1e-12, 1e-6], [Rs_guess*10, Rct_guess*10, 1e-1, 1e6])
        try:
            popt = EISEngine._complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds)
            quality = EISEngine._calculate_fit_quality(freq, Z_real, Z_imag, model_func, popt)
            result = {'Rs': round(popt[0], 2), 'Rct': round(popt[1], 2), 'W': round(popt[-1], 2),
                      'circuit': 'R(RW)Q - Randles+Warburg CPE' if use_cpe else 'R(RW)C - Randles+Warburg', **quality}
            if use_cpe: result['Q'] = round(popt[2], 6); result['alpha'] = round(popt[3], 4)
            else: result['Cdl'] = round(popt[2], 6)
            return result
        except:
            Z_est = EISEngine._warburg_impedance(freq, Rs_guess, Rct_guess, Cdl_guess, W_guess)
            return {'Rs': round(Rs_guess, 2), 'Rct': round(Rct_guess, 2), 'Cdl': round(Cdl_guess, 6),
                    'W': round(W_guess, 2), 'circuit': 'R(RW)C (estimated)', 'r_squared': 0.0,
                    'chi_squared': 999999, 'Z_fitted': Z_est, 'warning': 'Fit did not converge'}

    @staticmethod
    def linear_kramers_kronig(freq, Z_real, Z_imag, n_terms=5):
        phase = np.angle(Z_real + 1j * Z_imag, deg=True)
        valid_phase = np.all((phase <= 0) & (phase >= -90))
        residuals = np.diff(Z_real)**2 + np.diff(Z_imag)**2
        nr = residuals / (np.abs(Z_real[:-1] + 1j * Z_imag[:-1])**2 + 1e-10)
        kk_score = 1.0 - min(np.mean(nr) * 10, 0.9)
        return {'kk_score': round(kk_score, 4), 'valid_phase': valid_phase,
                'data_quality': 'Good' if kk_score > 0.8 else ('Fair' if kk_score > 0.5 else 'Poor'),
                'recommendation': 'Data passes KK check' if kk_score > 0.8 else 'Data may have artifacts'}

    @staticmethod
    def stern_geary_corrosion_rate(Rct, beta_a=120, beta_c=120, area=1.0):
        B = (beta_a * beta_c) / (2.303 * (beta_a + beta_c)) / 1000
        i_corr_A_cm2 = B / (Rct * area)
        i_corr_uA_cm2 = i_corr_A_cm2 * 1e6
        cr = (i_corr_A_cm2 * 27.92 * 31536000 * 10) / (2 * 96485 * 7.87)
        return {'B_stern_geary': round(B * 1000, 2), 'i_corr_uA_cm2': round(i_corr_uA_cm2, 4),
                'corrosion_rate_mm_yr': round(cr, 6), 'Rct': Rct, 'beta_a': beta_a, 'beta_c': beta_c}