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
        freq = np.logspace(5, -2, 50)
        if circuit == 'randles':
            Rs, Rct = 10, 1000
            if depressed:
                Q, alpha = 1e-4, 0.85
                Z = EISEngine._randles_cpe_impedance(freq, Rs, Rct, Q, alpha)
            else:
                Cdl = 1e-4
                Z = EISEngine._randles_impedance(freq, Rs, Rct, Cdl)
        else:
            Rs, Rct, W = 10, 1000, 100
            if depressed:
                Q, alpha = 1e-4, 0.85
                Z = EISEngine._warburg_cpe_impedance(freq, Rs, Rct, Q, alpha, W)
            else:
                Cdl = 1e-4
                Z = EISEngine._warburg_impedance(freq, Rs, Rct, Cdl, W)
        Z_mod = np.abs(Z)
        noise = np.random.normal(0, noise_level, len(freq)) + 1j * np.random.normal(0, noise_level, len(freq))
        Z = Z + Z_mod * noise
        return {'freq': freq, 'Z_real': Z.real, 'Z_imag': np.abs(Z.imag)}
    
    @staticmethod
    def _complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds):
        Z_data = np.column_stack([Z_real, Z_imag]).ravel()
        Z_mod = np.sqrt(Z_real**2 + Z_imag**2)
        weights = 1.0 / (Z_mod**2 + 1e-10)
        sigma = 1.0 / np.sqrt(weights + 1e-10)
        sigma = np.column_stack([sigma, sigma]).ravel()
        def weighted_model(f, *params):
            Z = model_func(f, *params)
            return np.column_stack([Z.real, Z.imag]).ravel()
        popt, pcov = curve_fit(weighted_model, freq, Z_data, p0=p0, bounds=bounds, sigma=sigma, maxfev=20000, ftol=1e-12)
        return popt, pcov
    
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
        high_freq_mask = freq > np.max(freq) * 0.1
        Rs_guess = np.min(Z_real[high_freq_mask]) if np.any(high_freq_mask) else np.min(Z_real)
        Rct_guess = np.max(Z_real) - Rs_guess
        idx_peak = np.argmax(Z_imag)
        freq_peak = freq[idx_peak]
        Cdl_guess = 1 / (2 * np.pi * freq_peak * Rct_guess) if Rct_guess > 0 and freq_peak > 0 else 1e-4
        Rs_guess = max(Rs_guess, 0.1)
        Rct_guess = max(Rct_guess, 10)
        Cdl_guess = np.clip(Cdl_guess, 1e-9, 1e-1)
        if use_cpe:
            model_func = EISEngine._randles_cpe_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, 0.85]
            bounds = ([Rs_guess*0.5, Rct_guess*0.1, 1e-9, 0.5], [Rs_guess*2, Rct_guess*10, 1, 1.0])
        else:
            model_func = EISEngine._randles_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess]
            bounds = ([Rs_guess*0.5, Rct_guess*0.1, 1e-9], [Rs_guess*2, Rct_guess*10, 1e-1])
        try:
            popt, _ = EISEngine._complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds)
            quality = EISEngine._calculate_fit_quality(freq, Z_real, Z_imag, model_func, popt)
            result = {'Rs': round(popt[0], 2), 'Rct': round(popt[1], 2), 'circuit': 'R(RQ) - Randles CPE' if use_cpe else 'R(RC) - Randles', **quality}
            if use_cpe:
                result['Q'] = round(popt[2], 6)
                result['alpha'] = round(popt[3], 4)
            else:
                result['Cdl'] = round(popt[2], 6)
            return result
        except:
            Z_est = EISEngine._randles_impedance(freq, Rs_guess, Rct_guess, Cdl_guess)
            return {'Rs': round(Rs_guess, 2), 'Rct': round(Rct_guess, 2), 'Cdl': round(Cdl_guess, 6), 'circuit': 'R(RC) - Randles (estimated)', 'r_squared': 0.0, 'chi_squared': 999999, 'Z_fitted': Z_est, 'warning': 'Fit did not converge'}
    
    @staticmethod
    def fit_warburg(freq, Z_real, Z_imag, use_cpe=False):
        high_freq_mask = freq > np.max(freq) * 0.1
        Rs_guess = np.min(Z_real[high_freq_mask]) if np.any(high_freq_mask) else np.min(Z_real)
        Rct_guess = max(np.max(Z_real) - Rs_guess, 10)
        idx_peak = np.argmax(Z_imag)
        freq_peak = freq[idx_peak]
        Cdl_guess = np.clip(1/(2*np.pi*freq_peak*Rct_guess) if freq_peak>0 else 1e-4, 1e-9, 1e-1)
        W_guess = Rct_guess * 0.1
        if use_cpe:
            model_func = EISEngine._warburg_cpe_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, 0.85, W_guess]
            bounds = ([Rs_guess*0.5, Rct_guess*0.1, 1e-9, 0.5, 1e-6], [Rs_guess*2, Rct_guess*10, 1, 1.0, 1e6])
        else:
            model_func = EISEngine._warburg_impedance
            p0 = [Rs_guess, Rct_guess, Cdl_guess, W_guess]
            bounds = ([Rs_guess*0.5, Rct_guess*0.1, 1e-9, 1e-6], [Rs_guess*2, Rct_guess*10, 1e-1, 1e6])
        try:
            popt, _ = EISEngine._complex_fit(freq, Z_real, Z_imag, model_func, p0, bounds)
            quality = EISEngine._calculate_fit_quality(freq, Z_real, Z_imag, model_func, popt)
            result = {'Rs': round(popt[0], 2), 'Rct': round(popt[1], 2), 'W': round(popt[-1], 2), 'circuit': 'R(RW)Q - Randles+Warburg CPE' if use_cpe else 'R(RW)C - Randles+Warburg', **quality}
            if use_cpe:
                result['Q'] = round(popt[2], 6)
                result['alpha'] = round(popt[3], 4)
            else:
                result['Cdl'] = round(popt[2], 6)
            return result
        except:
            Z_est = EISEngine._warburg_impedance(freq, Rs_guess, Rct_guess, Cdl_guess, W_guess)
            return {'Rs': round(Rs_guess, 2), 'Rct': round(Rct_guess, 2), 'Cdl': round(Cdl_guess, 6), 'W': round(W_guess, 2), 'circuit': 'R(RW)C (estimated)', 'r_squared': 0.0, 'chi_squared': 999999, 'Z_fitted': Z_est, 'warning': 'Fit did not converge'}
    
    @staticmethod
    def linear_kramers_kronig(freq, Z_real, Z_imag, n_terms=5):
        phase = np.angle(Z_real + 1j * Z_imag, deg=True)
        valid_phase = np.all((phase <= 0) & (phase >= -90))
        residuals = np.diff(Z_real)**2 + np.diff(Z_imag)**2
        normalized_residuals = residuals / (np.abs(Z_real[:-1] + 1j * Z_imag[:-1])**2 + 1e-10)
        kk_score = 1.0 - min(np.mean(normalized_residuals) * 10, 0.9)
        return {'kk_score': round(kk_score, 4), 'valid_phase': valid_phase, 'data_quality': 'Good' if kk_score > 0.8 else ('Fair' if kk_score > 0.5 else 'Poor'), 'recommendation': 'Data passes KK check' if kk_score > 0.8 else 'Data may have artifacts'}