"""Inhibitor Efficiency Tab - Professional Edition"""

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
from ..engines.inhibitor_engine import InhibitorEngine


class InhibitorTab:
    """Tab for corrosion inhibitor efficiency analysis"""

    def setup(self, parent, db=None):
        self.parent = parent
        self.db = db
        self.engine = InhibitorEngine()

        ml = QVBoxLayout(parent)
        ml.setSpacing(8)
        ml.setContentsMargins(24, 24, 24, 24)

        h = QHBoxLayout()
        t = QLabel("Inhibitor Efficiency Calculator")
        t.setStyleSheet("font-size:22px;font-weight:700;color:#1E293B;")
        h.addWidget(t)
        h.addStretch()
        badge = QLabel("Adsorption & Synergy")
        badge.setStyleSheet("background:#DBEAFE;color:#2563EB;padding:6px 16px;border-radius:20px;font-weight:600;font-size:11px;")
        h.addWidget(badge)
        ml.addLayout(h)

        content = QHBoxLayout()
        content.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(6)

        ec = QGroupBox("Basic Efficiency")
        el = QFormLayout()
        el.setSpacing(4)
        self.cr0_spin = QDoubleSpinBox()
        self.cr0_spin.setRange(0.0001, 1000); self.cr0_spin.setValue(1.0)
        self.cr0_spin.setSuffix(" mm/yr"); self.cr0_spin.setDecimals(4)
        el.addRow("CR (uninhibited):", self.cr0_spin)
        self.cri_spin = QDoubleSpinBox()
        self.cri_spin.setRange(0.0001, 1000); self.cri_spin.setValue(0.1)
        self.cri_spin.setSuffix(" mm/yr"); self.cri_spin.setDecimals(4)
        el.addRow("CR (inhibited):", self.cri_spin)
        ec.setLayout(el)
        left.addWidget(ec)

        dc = QGroupBox("Isotherm Data (Conc vs IE%)")
        dl = QVBoxLayout()
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(2); self.data_table.setRowCount(6)
        self.data_table.setHorizontalHeaderLabels(["Conc (ppm)", "IE (%)"])
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setMinimumHeight(100)
        sample_data = [(1, 45), (5, 72), (10, 85), (20, 92), (50, 96), (100, 98)]
        for i, (c, ie) in enumerate(sample_data):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(c)))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(ie)))
        dl.addWidget(self.data_table)
        dc.setLayout(dl)
        left.addWidget(dc)

        rc = QGroupBox("Results")
        rl = QVBoxLayout()
        self.result_label = QLabel("Enter values and click a button")
        self.result_label.setStyleSheet("font-size:11px;padding:6px;color:#64748B;background:#F8FAFC;border-radius:6px;")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(80)
        rl.addWidget(self.result_label)
        rc.setLayout(rl)
        left.addWidget(rc)

        b1 = QPushButton("Calculate Basic Efficiency")
        b1.setObjectName("primaryBtn"); b1.setMinimumHeight(32)
        b1.clicked.connect(self._calculate); left.addWidget(b1)
        b2 = QPushButton("Auto-Fit Best Isotherm")
        b2.setMinimumHeight(28); b2.clicked.connect(self._auto_fit); left.addWidget(b2)
        b3 = QPushButton("Langmuir Fit")
        b3.setMinimumHeight(26); b3.clicked.connect(self._fit_langmuir); left.addWidget(b3)
        b4 = QPushButton("Freundlich Fit")
        b4.setMinimumHeight(26); b4.clicked.connect(self._fit_freundlich); left.addWidget(b4)
        b5 = QPushButton("Synergy Analysis")
        b5.setMinimumHeight(26); b5.clicked.connect(self._synergy); left.addWidget(b5)
        left.addStretch()

        left_widget = QWidget()
        left_widget.setLayout(left)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left_widget)
        scroll.setFixedWidth(330)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content.addWidget(scroll)

        pl = QVBoxLayout()
        pl.setContentsMargins(0, 0, 0, 0)
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, parent)
        pl.addWidget(self.toolbar)
        pl.addWidget(self.canvas, 1)
        content.addLayout(pl, 1)

        ml.addLayout(content, 1)

    def _get_table_data(self):
        c_list, ie_list = [], []
        for i in range(self.data_table.rowCount()):
            c_item = self.data_table.item(i, 0)
            ie_item = self.data_table.item(i, 1)
            if c_item and ie_item:
                try:
                    c = float(c_item.text().strip())
                    ie = float(ie_item.text().strip())
                    if c > 0 and 0 < ie <= 100: c_list.append(c); ie_list.append(ie)
                except ValueError: continue
        return c_list, ie_list

    def _calculate(self):
        cr0, cri = self.cr0_spin.value(), self.cri_spin.value()
        result = self.engine.calculate_efficiency(cr0, cri)
        if 'error' in result: self.result_label.setText(result['error']); return
        self.result_label.setText(f"IE = {result['efficiency_pct']:.1f}%\nGrade: {result['grade']}\nSurface Coverage = {result['surface_coverage']:.3f}\nCR0 = {result['cr_uninhibited']:.4f} mm/yr\nCRi = {result['cr_inhibited']:.4f} mm/yr")
        self.result_label.setStyleSheet("font-size:11px;padding:6px;color:#065F46;background:#D1FAE5;border-radius:6px;font-weight:bold;")

    def _auto_fit(self):
        c, ie = self._get_table_data()
        if len(c) < 3: self.result_label.setText("Need at least 3 data points"); return
        lang, freu = self.engine.fit_langmuir(c, ie), self.engine.fit_freundlich(c, ie)
        lines, best = ["=== Auto-Fit Results ===\n"], None
        if 'error' not in lang: lines.append(f"Langmuir: R2={lang['r_squared']:.4f}, K={lang['K_ads']:.1f}, G={lang['delta_G_kJ_mol']:.1f} kJ/mol"); best = ('Langmuir', lang)
        if 'error' not in freu: lines.append(f"Freundlich: R2={freu['r_squared']:.4f}, Kf={freu['Kf']:.4f}, n={freu['n']:.2f}")
        if best is None and 'error' not in freu: best = ('Freundlich', freu)
        if best: lines.append(f"\nBest: {best[0]} (R2={best[1]['r_squared']:.4f})")
        if best and 'interpretation' in best[1]: lines.append(best[1]['interpretation'])
        self.result_label.setText("\n".join(lines))
        self.result_label.setStyleSheet("font-size:11px;padding:6px;color:#1E40AF;background:#DBEAFE;border-radius:6px;font-weight:bold;")
        self._plot_isotherm(c, ie, best[0] if best else 'Data')

    def _fit_langmuir(self):
        c, ie = self._get_table_data()
        if len(c) < 3: self.result_label.setText("Need at least 3 data points"); return
        result = self.engine.fit_langmuir(c, ie)
        if 'error' in result: self.result_label.setText(result['error']); return
        self.result_label.setText(f"Langmuir Isotherm\nK_ads = {result['K_ads']:.1f}\nG = {result['delta_G_kJ_mol']:.1f} kJ/mol\nR2 = {result['r_squared']:.4f}\n{result['interpretation']}")
        self._plot_isotherm(c, ie, 'Langmuir')

    def _fit_freundlich(self):
        c, ie = self._get_table_data()
        if len(c) < 3: self.result_label.setText("Need at least 3 data points"); return
        result = self.engine.fit_freundlich(c, ie)
        if 'error' in result: self.result_label.setText(result['error']); return
        self.result_label.setText(f"Freundlich Isotherm\nKf = {result['Kf']:.4f}\nn = {result['n']:.2f}\nR2 = {result['r_squared']:.4f}")

    def _synergy(self):
        ie_a, ok1 = QInputDialog.getDouble(self.parent, "IE Inhibitor A", "IE% alone:", 60, 0, 100, 1)
        if not ok1: return
        ie_b, ok2 = QInputDialog.getDouble(self.parent, "IE Inhibitor B", "IE% alone:", 50, 0, 100, 1)
        if not ok2: return
        ie_mix, ok3 = QInputDialog.getDouble(self.parent, "IE Mixture", "IE% combined:", 90, 0, 100, 1)
        if not ok3: return
        result = self.engine.calculate_synergy(ie_a, ie_b, ie_mix)
        self.result_label.setText(f"Synergy S = {result['S_parameter']:.3f}\nEffect: {result['effect']}\nIE(A)={result['ie_a']:.1f}% | IE(B)={result['ie_b']:.1f}% | IE(Mix)={result['ie_mixture']:.1f}%")

    def _plot_isotherm(self, C, IE, model_name):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(C, IE, 'o-', color=Theme.PRIMARY, linewidth=2, markersize=8, label='Data')
        ax.set_xlabel('Concentration (ppm)', fontweight='bold')
        ax.set_ylabel('IE (%)', fontweight='bold')
        ax.set_title(f'{model_name} Adsorption Isotherm', fontweight='bold', fontsize=13)
        ax.legend(fontsize=10); ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#FAFBFC'); ax.set_ylim(0, 105)
        self.figure.tight_layout(); self.canvas.draw()