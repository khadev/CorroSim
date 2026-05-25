"""EIS Analysis Tab - Professional Edition"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..theme import Theme
from ..engines.eis_engine import EISEngine


class EISTab:
    """Tab for Electrochemical Impedance Spectroscopy analysis"""

    def setup(self, parent, db=None):
        self.parent = parent
        self.db = db
        self.engine = EISEngine()
        self.eis_data = None
        self.fit_result = None

        ml = QVBoxLayout(parent)
        ml.setSpacing(10)
        ml.setContentsMargins(24, 24, 24, 24)

        # Header
        h = QHBoxLayout()
        t = QLabel("EIS Analysis")
        t.setStyleSheet("font-size:22px;font-weight:700;color:#1E293B;")
        h.addWidget(t)
        h.addStretch()
        badge = QLabel("Impedance Spectroscopy")
        badge.setStyleSheet("background:#DBEAFE;color:#2563EB;padding:6px 16px;border-radius:20px;font-weight:600;font-size:11px;")
        h.addWidget(badge)
        ml.addLayout(h)

        content = QHBoxLayout()
        content.setSpacing(12)

        # Left panel
        left = QVBoxLayout()
        left.setSpacing(6)

        # Circuit
        cc = QGroupBox("Circuit Model")
        cl = QVBoxLayout()
        self.circuit_combo = QComboBox()
        self.circuit_combo.addItems([
            "Auto-Select Best Model",
            "R(RC) - Randles",
            "R(RQ) - Randles CPE",
            "R(RW)C - Randles+Warburg",
            "R(RW)Q - Randles+Warburg CPE"
        ])
        self.circuit_combo.setMinimumHeight(28)
        cl.addWidget(QLabel("Circuit:"))
        cl.addWidget(self.circuit_combo)
        cc.setLayout(cl)
        left.addWidget(cc)

        # Data
        dc = QGroupBox("Data Source")
        dl = QVBoxLayout()
        dl.setSpacing(4)
        b1 = QPushButton("Generate Test Data")
        b1.setMinimumHeight(30)
        b1.clicked.connect(self._generate_test_data)
        dl.addWidget(b1)
        b2 = QPushButton("Import CSV Data")
        b2.setMinimumHeight(30)
        b2.clicked.connect(self._import_real_data)
        dl.addWidget(b2)
        self.data_status = QLabel("No data loaded")
        self.data_status.setStyleSheet("color:#94A3B8;font-size:11px;padding:4px;")
        self.data_status.setWordWrap(True)
        dl.addWidget(self.data_status)
        dc.setLayout(dl)
        left.addWidget(dc)

        # Results
        rc = QGroupBox("Fitted Parameters")
        rl = QVBoxLayout()
        self.result_label = QLabel("Run fit to see results")
        self.result_label.setStyleSheet("font-size:12px;padding:8px;color:#64748B;background:#F8FAFC;border-radius:6px;")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(120)
        rl.addWidget(self.result_label)
        self.kk_label = QLabel("")
        self.kk_label.setStyleSheet("font-size:10px;padding:2px 6px;")
        self.kk_label.setWordWrap(True)
        self.kk_label.setMinimumHeight(18)
        rl.addWidget(self.kk_label)
        rc.setLayout(rl)
        left.addWidget(rc)

        # Buttons
        b3 = QPushButton("Run Weighted CNLS Fit")
        b3.setObjectName("primaryBtn")
        b3.setMinimumHeight(36)
        b3.clicked.connect(self._run_fit)
        left.addWidget(b3)

        b4 = QPushButton("Export Results CSV")
        b4.setMinimumHeight(28)
        b4.clicked.connect(self._export_results)
        left.addWidget(b4)

        b5 = QPushButton("Export Parameters")
        b5.setMinimumHeight(28)
        b5.clicked.connect(self._export_parameters)
        left.addWidget(b5)

        b6 = QPushButton("Stern-Geary -> CR")
        b6.setMinimumHeight(28)
        b6.clicked.connect(self._calculate_corrosion_rate)
        left.addWidget(b6)

        left.addStretch()

        lw = QWidget()
        lw.setLayout(left)
        lw.setFixedWidth(300)
        content.addWidget(lw)

        # Right panel - Plots
        pl = QVBoxLayout()
        pl.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, parent)
        pl.addWidget(self.toolbar)
        pl.addWidget(self.canvas, 1)
        content.addLayout(pl, 1)

        ml.addLayout(content, 1)

    # ============================================================
    # DATA METHODS
    # ============================================================

    def _generate_test_data(self):
        circuit_text = self.circuit_combo.currentText()
        circuit = 'warburg' if 'Warburg' in circuit_text else 'randles'
        depressed = 'CPE' in circuit_text
        self.eis_data = self.engine.generate_test_data(circuit=circuit, depressed=depressed, noise_level=0.015)
        self.fit_result = None
        n = len(self.eis_data['freq'])
        self.data_status.setText(f"{n} points | 100 kHz - 0.01 Hz")
        self.data_status.setStyleSheet("color:#10B981;font-size:11px;padding:4px;")
        self.result_label.setText("Data generated. Click 'Run Fit'.")
        self.result_label.setStyleSheet("font-size:12px;padding:8px;color:#F59E0B;background:#FEF3C7;border-radius:6px;")
        self.kk_label.setText("")
        self._plot_data()

    def _import_real_data(self):
        import pandas as pd
        path, _ = QFileDialog.getOpenFileName(self.parent, "Open EIS Data", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        try:
            df = pd.read_csv(path)
            cols = [c.lower().strip() for c in df.columns]
            fc = rc = ic = None
            for i, c in enumerate(cols):
                if 'freq' in c or 'hz' in c: fc = df.columns[i]
                elif 'real' in c or "z'" in c: rc = df.columns[i]
                elif 'imag' in c or 'z"' in c or "z''" in c: ic = df.columns[i]
            if fc is None or rc is None or ic is None:
                nc = df.select_dtypes(include=[np.number]).columns
                if len(nc) >= 3:
                    fc, rc, ic = nc[0], nc[1], nc[2]
                else:
                    QMessageBox.warning(self.parent, "Error", "Cannot identify columns")
                    return
            self.eis_data = {
                'freq': df[fc].values.astype(float),
                'Z_real': df[rc].values.astype(float),
                'Z_imag': np.abs(df[ic].values.astype(float))
            }
            self.fit_result = None
            self.data_status.setText(f"Loaded: {len(self.eis_data['freq'])} points")
            self.data_status.setStyleSheet("color:#10B981;font-size:11px;padding:4px;")
            self.result_label.setText("Data loaded. Click 'Run Fit'.")
            self.result_label.setStyleSheet("font-size:12px;padding:8px;color:#3B82F6;background:#DBEAFE;border-radius:6px;")
            self._plot_data()
        except Exception as e:
            QMessageBox.critical(self.parent, "Import Error", str(e))

    # ============================================================
    # FITTING METHOD
    # ============================================================

    def _run_fit(self):
        if self.eis_data is None:
            self.result_label.setText("No data! Generate or import first.")
            return

        f = self.eis_data['freq']
        zr = self.eis_data['Z_real']
        zi = self.eis_data['Z_imag']
        t = self.circuit_combo.currentText()

        # Auto-detect diffusion tail
        low_freq_mask = f < np.max(f) * 0.01
        has_tail = False
        if np.sum(low_freq_mask) > 3:
            low_zi = zi[low_freq_mask]
            has_tail = np.any(np.diff(low_zi) > 0)

        # Try models
        if 'Auto' in t:
            models = [
                self.engine.fit_randles(f, zr, zi, use_cpe=False),
                self.engine.fit_randles(f, zr, zi, use_cpe=True),
                self.engine.fit_warburg(f, zr, zi, use_cpe=False),
                self.engine.fit_warburg(f, zr, zi, use_cpe=True),
            ]
            valid = [m for m in models if 'error' not in m]
            if not valid:
                self.result_label.setText("All models failed to converge")
                return
            result = max(valid, key=lambda m: m.get('r_squared', 0))
        else:
            cp = 'CPE' in t
            if 'Warburg' in t:
                result = self.engine.fit_warburg(f, zr, zi, use_cpe=cp)
            else:
                result = self.engine.fit_randles(f, zr, zi, use_cpe=cp)

        if 'error' in result:
            self.result_label.setText(f"Error: {result['error']}")
            return

        self.fit_result = result

        # Build display
        lines = [f"Circuit: {result['circuit']}", ""]
        lines.append(f"Rs  = {result['Rs']:.1f} ohm")
        lines.append(f"Rct = {result['Rct']:.1f} ohm")
        if 'Cdl' in result:
            lines.append(f"Cdl = {result['Cdl']:.2e} F")
        if 'Q' in result:
            lines.extend([f"Q   = {result['Q']:.2e}", f"a   = {result['alpha']:.4f}"])
        if 'W' in result:
            lines.append(f"W   = {result['W']:.1f}")
        lines.extend(["", f"R2  = {result['r_squared']:.4f}", f"X2  = {result['chi_squared']:.2f}"])
        if result.get('warning'):
            lines.append(f"! {result['warning']}")
        if has_tail and 'Warburg' not in result.get('circuit', ''):
            lines.append("Tip: Data shows diffusion. Try Warburg model.")

        r2 = result['r_squared']
        if r2 > 0.95:
            bg, tc = '#D1FAE5', '#065F46'
        elif r2 > 0.8:
            bg, tc = '#FEF3C7', '#92400E'
        else:
            bg, tc = '#FEE2E2', '#991B1B'

        self.result_label.setText("\n".join(lines))
        self.result_label.setStyleSheet(f"font-size:12px;padding:8px;color:{tc};background:{bg};border-radius:6px;font-weight:bold;")

        # KK validation
        kk = self.engine.linear_kramers_kronig(f, zr, zi)
        kc = '#10B981' if kk['kk_score'] > 0.8 else ('#F59E0B' if kk['kk_score'] > 0.5 else '#EF4444')
        self.kk_label.setText(f"KK: {kk['kk_score']:.3f} ({kk['data_quality']}) | Phase: {'Yes' if kk['valid_phase'] else 'No'}")
        self.kk_label.setStyleSheet(f"font-size:10px;padding:2px 6px;color:{kc};")

        self._plot_data()

    # ============================================================
    # PLOTTING
    # ============================================================

    def _plot_data(self):
        self.figure.clear()

        # Nyquist
        ax1 = self.figure.add_subplot(221)
        ax1.scatter(self.eis_data['Z_real'], self.eis_data['Z_imag'], s=25, color=Theme.PRIMARY,
                   alpha=0.7, label='Data', zorder=3, edgecolors='white', linewidth=0.5)
        if self.fit_result and 'Z_fitted' in self.fit_result:
            zf = self.fit_result['Z_fitted']
            ax1.plot(zf.real, zf.imag, '-', color=Theme.ERROR, linewidth=2, label='Fit', zorder=2)
        ax1.set_xlabel("Z' (ohm)", fontweight='bold')
        ax1.set_ylabel("-Z'' (ohm)", fontweight='bold')
        ax1.set_title('Nyquist Plot', fontweight='bold', fontsize=11)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor('#FAFBFC')
        ax1.set_aspect('equal')

        # Bode Magnitude
        ax2 = self.figure.add_subplot(222)
        freq = self.eis_data['freq']
        zm = np.sqrt(self.eis_data['Z_real']**2 + self.eis_data['Z_imag']**2)
        ax2.loglog(freq, zm, 'o', color=Theme.PRIMARY, markersize=4, alpha=0.7, label='|Z|')
        if self.fit_result and 'Z_fitted' in self.fit_result:
            zf = self.fit_result['Z_fitted']
            ax2.loglog(freq, np.sqrt(zf.real**2 + zf.imag**2), '-', color=Theme.ERROR, linewidth=2, label='Fit')
        ax2.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax2.set_ylabel('|Z| (ohm)', fontweight='bold')
        ax2.set_title('Bode Magnitude', fontweight='bold', fontsize=11)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor('#FAFBFC')

        # Bode Phase
        ax3 = self.figure.add_subplot(223)
        ph = np.angle(self.eis_data['Z_real'] + 1j * self.eis_data['Z_imag'], deg=True)
        ax3.semilogx(freq, ph, 'o', color=Theme.PRIMARY, markersize=4, alpha=0.7, label='Data')
        if self.fit_result and 'Z_fitted' in self.fit_result:
            ax3.semilogx(freq, np.angle(self.fit_result['Z_fitted'], deg=True), '-', color=Theme.ERROR, linewidth=2, label='Fit')
        ax3.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax3.set_ylabel('Phase (deg)', fontweight='bold')
        ax3.set_title('Bode Phase', fontweight='bold', fontsize=11)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_facecolor('#FAFBFC')
        ax3.set_ylim(-90, 10)

        # Residuals
        ax4 = self.figure.add_subplot(224)
        if self.fit_result and 'Z_fitted' in self.fit_result:
            zf = self.fit_result['Z_fitted']
            rr = (self.eis_data['Z_real'] - zf.real) / zm * 100
            ri = (self.eis_data['Z_imag'] - zf.imag) / zm * 100
            ax4.semilogx(freq, rr, 'o-', color=Theme.PRIMARY, markersize=3, label="Z' resid")
            ax4.semilogx(freq, ri, 's-', color=Theme.ERROR, markersize=3, label="Z'' resid")
            ax4.axhline(y=0, color='black', linewidth=0.5)
            ax4.set_ylabel('Residual (%)', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'Run fit to see residuals', ha='center', va='center',
                    transform=ax4.transAxes, color='#94A3B8')
        ax4.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax4.set_title('Fit Residuals', fontweight='bold', fontsize=11)
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, linestyle='--')
        ax4.set_facecolor('#FAFBFC')

        self.figure.tight_layout(pad=2)
        self.canvas.draw()

    # ============================================================
    # EXPORT METHODS
    # ============================================================

    def _export_results(self):
        if self.fit_result is None:
            QMessageBox.warning(self.parent, "No Results", "Run a fit first!")
            return
        path, _ = QFileDialog.getSaveFileName(self.parent, "Export Results", "eis_results.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("Frequency_Hz;Z_real_ohm;Z_imag_ohm")
                if 'Z_fitted' in self.fit_result:
                    f.write(";Z_real_fit;Z_imag_fit")
                f.write("\n")
                for i in range(len(self.eis_data['freq'])):
                    f.write(f"{self.eis_data['freq'][i]};{self.eis_data['Z_real'][i]};{self.eis_data['Z_imag'][i]}")
                    if 'Z_fitted' in self.fit_result:
                        zf = self.fit_result['Z_fitted']
                        f.write(f";{zf.real[i]};{zf.imag[i]}")
                    f.write("\n")
            QMessageBox.information(self.parent, "Success", f"Exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", str(e))

    def _export_parameters(self):
        if self.fit_result is None:
            QMessageBox.warning(self.parent, "No Results", "Run a fit first!")
            return
        path, _ = QFileDialog.getSaveFileName(self.parent, "Export Parameters", "eis_parameters.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                f.write("Parameter;Value\n")
                for k, v in self.fit_result.items():
                    if k not in ['Z_fitted']:
                        f.write(f"{k};{v}\n")
            QMessageBox.information(self.parent, "Success", f"Exported to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self.parent, "Export Error", str(e))

    # ============================================================
    # STERN-GEARY
    # ============================================================

    def _calculate_corrosion_rate(self):
        if self.fit_result is None or 'Rct' not in self.fit_result:
            QMessageBox.warning(self.parent, "No Fit", "Run EIS fit first!")
            return
        ba, ok1 = QInputDialog.getDouble(self.parent, "Tafel Slope", "ba (mV/dec):", 120, 10, 500, 1)
        if not ok1: return
        bc, ok2 = QInputDialog.getDouble(self.parent, "Tafel Slope", "bc (mV/dec):", 120, 10, 500, 1)
        if not ok2: return
        ar, ok3 = QInputDialog.getDouble(self.parent, "Electrode Area", "Area (cm2):", 1.0, 0.01, 1000, 2)
        if not ok3: return
        r = self.engine.stern_geary_corrosion_rate(self.fit_result['Rct'], ba, bc, ar)
        QMessageBox.information(self.parent, "Stern-Geary Corrosion Rate",
            f"B = {r['B_stern_geary']:.1f} mV\n"
            f"Icorr = {r['i_corr_uA_cm2']:.4f} uA/cm2\n"
            f"CR = {r['corrosion_rate_mm_yr']:.6f} mm/yr\n\n"
            f"From Rct = {r['Rct']:.1f} ohm")