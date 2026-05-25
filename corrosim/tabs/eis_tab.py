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
        ml.setSpacing(12)
        ml.setContentsMargins(24, 24, 24, 24)
        
        header = QHBoxLayout()
        title = QLabel("EIS Analysis")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        header.addWidget(title)
        header.addStretch()
        
        badge = QLabel("Impedance Spectroscopy")
        badge.setStyleSheet("background: #DBEAFE; color: #2563EB; padding: 6px 16px; "
                           "border-radius: 20px; font-weight: 600; font-size: 11px;")
        header.addWidget(badge)
        ml.addLayout(header)
        
        desc = QLabel("Equivalent Circuit Fitting with Weighted CNLS and CPE Support")
        desc.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 4px;")
        ml.addWidget(desc)
        
        content = QHBoxLayout()
        content.setSpacing(12)
        
        left = QVBoxLayout()
        left.setSpacing(8)
        
        circuit_card = QGroupBox("Equivalent Circuit Model")
        cl = QVBoxLayout()
        cl.setSpacing(8)
        
        self.circuit_combo = QComboBox()
        self.circuit_combo.addItems([
            "R(RC) - Randles",
            "R(RQ) - Randles CPE (depressed)",
            "R(RW)C - Randles+Warburg",
            "R(RW)Q - Randles+Warburg CPE"
        ])
        cl.addWidget(QLabel("Circuit:"))
        cl.addWidget(self.circuit_combo)
        
        self.cpe_info = QLabel("CPE: Z = 1/(Q*(jw)^a), a<1 for real electrodes")
        self.cpe_info.setStyleSheet("color: #64748B; font-size: 10px; font-style: italic;")
        self.cpe_info.setWordWrap(True)
        cl.addWidget(self.cpe_info)
        circuit_card.setLayout(cl)
        left.addWidget(circuit_card)
        
        data_card = QGroupBox("Data Source")
        dl = QVBoxLayout()
        dl.setSpacing(6)
        gen_btn = QPushButton("Generate Synthetic Data")
        gen_btn.clicked.connect(self._generate_test_data)
        dl.addWidget(gen_btn)
        self.data_status = QLabel("No data loaded")
        self.data_status.setStyleSheet("color: #94A3B8; font-size: 11px;")
        dl.addWidget(self.data_status)
        data_card.setLayout(dl)
        left.addWidget(data_card)
        
        result_card = QGroupBox("Fitted Parameters")
        rl = QVBoxLayout()
        rl.setSpacing(4)
        self.result_label = QLabel("Run fit to see results")
        self.result_label.setStyleSheet("font-size: 12px; padding: 8px; color: #64748B; "
                                        "background: #F8FAFC; border-radius: 6px;")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(120)
        rl.addWidget(self.result_label)
        self.kk_label = QLabel("")
        self.kk_label.setStyleSheet("font-size: 11px; padding: 4px 8px;")
        rl.addWidget(self.kk_label)
        result_card.setLayout(rl)
        left.addWidget(result_card)
        
        fit_btn = QPushButton("Run Weighted CNLS Fit")
        fit_btn.setObjectName("primaryBtn")
        fit_btn.clicked.connect(self._run_fit)
        left.addWidget(fit_btn)
        left.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(300)
        content.addWidget(left_widget)
        
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)
        
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, parent)
        
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, 1)
        content.addLayout(plot_layout, 1)
        
        ml.addLayout(content, 1)
    
    def _generate_test_data(self):
        circuit_text = self.circuit_combo.currentText()
        if 'Warburg' in circuit_text:
            circuit = 'warburg'
        else:
            circuit = 'randles'
        depressed = 'CPE' in circuit_text or 'depressed' in circuit_text
        self.eis_data = self.engine.generate_test_data(circuit=circuit, depressed=depressed, noise_level=0.015)
        self.fit_result = None
        n_points = len(self.eis_data['freq'])
        self.data_status.setText(f"Ready: {n_points} points | 100 kHz - 0.01 Hz")
        self.data_status.setStyleSheet("color: #10B981; font-size: 11px;")
        self.result_label.setText("Data generated. Click 'Run Fit' to analyze.")
        self.result_label.setStyleSheet("font-size: 12px; padding: 8px; color: #F59E0B; background: #FEF3C7; border-radius: 6px;")
        self.kk_label.setText("")
        self._plot_data()
    
    def _run_fit(self):
        if self.eis_data is None:
            self.result_label.setText("Generate or load data first!")
            return
        freq = self.eis_data['freq']
        Z_real = self.eis_data['Z_real']
        Z_imag = self.eis_data['Z_imag']
        circuit_text = self.circuit_combo.currentText()
        use_cpe = 'CPE' in circuit_text or 'depressed' in circuit_text
        if 'Warburg' in circuit_text:
            result = self.engine.fit_warburg(freq, Z_real, Z_imag, use_cpe=use_cpe)
        else:
            result = self.engine.fit_randles(freq, Z_real, Z_imag, use_cpe=use_cpe)
        if 'error' in result:
            self.result_label.setText(f"Error: {result['error']}")
            return
        self.fit_result = result
        lines = [f"Circuit: {result['circuit']}", ""]
        lines.append(f"Rs  = {result['Rs']:.1f} ohm")
        lines.append(f"Rct = {result['Rct']:.1f} ohm")
        if 'Cdl' in result:
            lines.append(f"Cdl = {result['Cdl']:.2e} F")
        if 'Q' in result:
            lines.append(f"Q   = {result['Q']:.2e}")
            lines.append(f"a   = {result['alpha']:.4f}")
        if 'W' in result:
            lines.append(f"W   = {result['W']:.1f}")
        lines.append("")
        lines.append(f"R2  = {result['r_squared']:.4f}")
        lines.append(f"X2  = {result['chi_squared']:.2f}")
        if result.get('warning'):
            lines.append(f"! {result['warning']}")
        if result['r_squared'] > 0.95:
            bg, tc = '#D1FAE5', '#065F46'
        elif result['r_squared'] > 0.8:
            bg, tc = '#FEF3C7', '#92400E'
        else:
            bg, tc = '#FEE2E2', '#991B1B'
        self.result_label.setText("\n".join(lines))
        self.result_label.setStyleSheet(f"font-size: 12px; padding: 8px; color: {tc}; background: {bg}; border-radius: 6px; font-weight: bold;")
        kk = self.engine.linear_kramers_kronig(freq, Z_real, Z_imag)
        kk_color = '#10B981' if kk['kk_score'] > 0.8 else ('#F59E0B' if kk['kk_score'] > 0.5 else '#EF4444')
        self.kk_label.setText(f"KK Score: {kk['kk_score']:.3f} ({kk['data_quality']}) | Phase valid: {'Yes' if kk['valid_phase'] else 'No'}")
        self.kk_label.setStyleSheet(f"font-size: 11px; padding: 4px 8px; color: {kk_color};")
        self._plot_data()
    
    def _plot_data(self):
        self.figure.clear()
        ax1 = self.figure.add_subplot(221)
        ax1.scatter(self.eis_data['Z_real'], self.eis_data['Z_imag'], s=25, color=Theme.PRIMARY, alpha=0.7, label='Data', zorder=3, edgecolors='white', linewidth=0.5)
        if self.fit_result and 'Z_fitted' in self.fit_result:
            Z_fit = self.fit_result['Z_fitted']
            ax1.plot(Z_fit.real, Z_fit.imag, '-', color=Theme.ERROR, linewidth=2, label='Fit', zorder=2)
        ax1.set_xlabel("Z' (ohm)", fontweight='bold')
        ax1.set_ylabel("-Z'' (ohm)", fontweight='bold')
        ax1.set_title('Nyquist Plot', fontweight='bold', fontsize=11)
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_facecolor('#FAFBFC')
        ax1.set_aspect('equal')
        
        ax2 = self.figure.add_subplot(222)
        freq = self.eis_data['freq']
        Z_mod = np.sqrt(self.eis_data['Z_real']**2 + self.eis_data['Z_imag']**2)
        ax2.loglog(freq, Z_mod, 'o', color=Theme.PRIMARY, markersize=4, alpha=0.7, label='|Z|')
        if self.fit_result and 'Z_fitted' in self.fit_result:
            Z_fit = self.fit_result['Z_fitted']
            Z_mod_fit = np.sqrt(Z_fit.real**2 + Z_fit.imag**2)
            ax2.loglog(freq, Z_mod_fit, '-', color=Theme.ERROR, linewidth=2, label='Fit')
        ax2.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax2.set_ylabel('|Z| (ohm)', fontweight='bold')
        ax2.set_title('Bode Magnitude', fontweight='bold', fontsize=11)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_facecolor('#FAFBFC')
        
        ax3 = self.figure.add_subplot(223)
        phase_data = np.angle(self.eis_data['Z_real'] + 1j * self.eis_data['Z_imag'], deg=True)
        ax3.semilogx(freq, phase_data, 'o', color=Theme.PRIMARY, markersize=4, alpha=0.7, label='Data')
        if self.fit_result and 'Z_fitted' in self.fit_result:
            Z_fit = self.fit_result['Z_fitted']
            phase_fit = np.angle(Z_fit, deg=True)
            ax3.semilogx(freq, phase_fit, '-', color=Theme.ERROR, linewidth=2, label='Fit')
        ax3.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax3.set_ylabel('Phase (deg)', fontweight='bold')
        ax3.set_title('Bode Phase', fontweight='bold', fontsize=11)
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_facecolor('#FAFBFC')
        ax3.set_ylim(-90, 10)
        
        ax4 = self.figure.add_subplot(224)
        if self.fit_result and 'Z_fitted' in self.fit_result:
            Z_fit = self.fit_result['Z_fitted']
            resid_real = (self.eis_data['Z_real'] - Z_fit.real) / Z_mod * 100
            resid_imag = (self.eis_data['Z_imag'] - Z_fit.imag) / Z_mod * 100
            ax4.semilogx(freq, resid_real, 'o-', color=Theme.PRIMARY, markersize=3, label="Z' resid")
            ax4.semilogx(freq, resid_imag, 's-', color=Theme.ERROR, markersize=3, label="Z'' resid")
            ax4.axhline(y=0, color='black', linewidth=0.5)
            ax4.set_ylabel('Residual (%)', fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'Run fit to see residuals', ha='center', va='center', transform=ax4.transAxes, color='#94A3B8')
        ax4.set_xlabel('Frequency (Hz)', fontweight='bold')
        ax4.set_title('Fit Residuals', fontweight='bold', fontsize=11)
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3, linestyle='--')
        ax4.set_facecolor('#FAFBFC')
        
        self.figure.tight_layout(pad=2)
        self.canvas.draw()