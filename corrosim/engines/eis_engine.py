"""EIS Analysis Engine"""
import numpy as np
from scipy.optimize import curve_fit

class EISEngine:

    @staticmethod
    def _randles(freq, Rs, Rct, Cdl):
        w = 2*np.pi*freq
        return Rs + Rct/(1 + 1j*w*Rct*Cdl)

    @staticmethod
    def _warburg(freq, Rs, Rct, Cdl, W):
        w = 2*np.pi*freq
        Zw = W/np.sqrt(1j*w)
        return Rs + 1/(1/(Rct+Zw) + 1j*w*Cdl)

    @staticmethod
    def generate_test_data(circuit='randles', noise_level=0.005):
        freq = np.logspace(5, -2, 60)
        Rs, Rct = 10.0, 1000.0
        if circuit == 'randles':
            Z = EISEngine._randles(freq, Rs, Rct, 1e-4)
        else:
            Z = EISEngine._warburg(freq, Rs, Rct, 1e-4, 80.0)
        nr = np.random.normal(0, noise_level*np.abs(Z.real))
        ni = np.random.normal(0, noise_level*np.abs(Z.imag))
        Z = Z + nr + 1j*ni
        return {'freq': freq, 'Z_real': Z.real, 'Z_imag': np.abs(Z.imag)}

    @staticmethod
    def fit_randles(freq, Z_real, Z_imag, use_cpe=False):
        hm = freq > np.max(freq)*0.1
        Rs = np.min(Z_real[hm]) if np.any(hm) else np.min(Z_real)
        Rct = max(np.max(Z_real)-np.min(Z_real), 10)
        ip = np.argmax(Z_imag)
        C = 1/(2*np.pi*freq[ip]*Rct) if freq[ip]>0 and Rct>0 else 1e-4
        C = np.clip(C, 1e-12, 1e-1)
        Rs, Rct = np.clip(Rs, 0.1, 1e4), np.clip(Rct, 1, 1e7)
        Z_data = np.column_stack([Z_real, Z_imag]).ravel()
        def obj(f, rs, rct, cdl):
            Z = EISEngine._randles(f, rs, rct, cdl)
            return np.column_stack([Z.real, np.abs(Z.imag)]).ravel()
        try:
            p, _ = curve_fit(obj, freq, Z_data, p0=[Rs, Rct, C],
                           bounds=([0.1, 1, 1e-12], [1e4, 1e7, 1e-1]), maxfev=20000)
            Zf = EISEngine._randles(freq, *p)
            Zf_flat = np.column_stack([Zf.real, np.abs(Zf.imag)]).ravel()
            ss_r = np.sum((Z_data-Zf_flat)**2)
            ss_t = np.sum((Z_data-np.mean(Z_data))**2)
            r2 = 1-ss_r/ss_t if ss_t>0 else 0
            x2 = ss_r/max(len(freq)-3, 1)
            return {'Rs': round(p[0],2), 'Rct': round(p[1],2), 'Cdl': round(p[2],6),
                    'circuit': 'R(RC)', 'r_squared': round(r2,4), 'chi_squared': round(x2,2), 'Z_fitted': Zf}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def fit_warburg(freq, Z_real, Z_imag, use_cpe=False):
        hm = freq > np.max(freq)*0.1
        Rs = np.min(Z_real[hm]) if np.any(hm) else np.min(Z_real)
        Rct = max(np.max(Z_real)-np.min(Z_real), 10)
        ip = np.argmax(Z_imag)
        C = 1/(2*np.pi*freq[ip]*Rct) if freq[ip]>0 and Rct>0 else 1e-4
        C = np.clip(C, 1e-12, 1e-1)
        Rs, Rct = np.clip(Rs, 0.1, 1e4), np.clip(Rct, 1, 1e7)
        W = 80.0
        Z_data = np.column_stack([Z_real, Z_imag]).ravel()
        def obj(f, rs, rct, cdl, w):
            Z = EISEngine._warburg(f, rs, rct, cdl, w)
            return np.column_stack([Z.real, np.abs(Z.imag)]).ravel()
        try:
            p, _ = curve_fit(obj, freq, Z_data, p0=[Rs, Rct, C, W],
                           bounds=([0.1, 1, 1e-12, 1], [1e4, 1e7, 1e-1, 500]), maxfev=20000)
            Zf = EISEngine._warburg(freq, *p)
            Zf_flat = np.column_stack([Zf.real, np.abs(Zf.imag)]).ravel()
            ss_r = np.sum((Z_data-Zf_flat)**2)
            ss_t = np.sum((Z_data-np.mean(Z_data))**2)
            r2 = 1-ss_r/ss_t if ss_t>0 else 0
            x2 = ss_r/max(len(freq)-4, 1)
            return {'Rs': round(p[0],2), 'Rct': round(p[1],2), 'Cdl': round(p[2],6),
                    'W': round(p[3],2), 'circuit': 'R(RW)C', 'r_squared': round(r2,4),
                    'chi_squared': round(x2,2), 'Z_fitted': Zf}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def linear_kramers_kronig(freq, Z_real, Z_imag, n_terms=5):
        phase = np.angle(Z_real+1j*Z_imag, deg=True)
        vp = np.all((phase<=0)&(phase>=-90))
        r = np.diff(Z_real)**2+np.diff(Z_imag)**2
        nr = r/(np.abs(Z_real[:-1]+1j*Z_imag[:-1])**2+1e-10)
        ks = 1.0-min(np.mean(nr)*10, 0.9)
        return {'kk_score': round(ks,4), 'valid_phase': vp, 'data_quality': 'Good' if ks>0.8 else ('Fair' if ks>0.5 else 'Poor')}

    @staticmethod
    def stern_geary_corrosion_rate(Rct, beta_a=120, beta_c=120, area=1.0):
        B = (beta_a*beta_c)/(2.303*(beta_a+beta_c))/1000
        i = B/(Rct*area)
        ic = i*1e6
        cr = (i*27.92*31536000*10)/(2*96485*7.87)
        return {'B_stern_geary': round(B*1000,2), 'i_corr_uA_cm2': round(ic,4), 'corrosion_rate_mm_yr': round(cr,6), 'Rct': Rct}