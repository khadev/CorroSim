"""Pitting Corrosion Analysis Tab"""

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
from ..engines.pitting_engine import PittingEngine


class PittingTab:
    """Tab for pitting corrosion analysis"""
    
    def setup(self, parent, db=None):
        self.parent = parent
        self.db = db
        self.engine = PittingEngine()
        self.test_data = None
        self.analysis_result = None
        
        ml = QVBoxLayout(parent)
        ml.setSpacing(12)
        ml.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("Pitting Corrosion Analyzer")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        ml.addWidget(title)
        
        desc = QLabel("Cyclic Polarization Analysis & Extreme Value Statistics")
        desc.setStyleSheet("color: #64748B; font-size: 13px;")
        ml.addWidget(desc)
        
        content = QHBoxLayout()
        content.setSpacing(12)
        
                # LEFT PANEL
        left = QVBoxLayout()
        left.setSpacing(8)
        
        data_card = QGroupBox("Data Source")
        dl = QVBoxLayout()
        dl.setSpacing(4)
        
        gen_btn = QPushButton("Generate Test Data")
        gen_btn.setMinimumHeight(30)
        gen_btn.clicked.connect(self._generate_test_data)
        dl.addWidget(gen_btn)
        
        import_btn = QPushButton("Import CSV Data")
        import_btn.setMinimumHeight(30)
        import_btn.clicked.connect(self._import_real_data)
        dl.addWidget(import_btn)
        
        self.data_status = QLabel("No data loaded")
        self.data_status.setStyleSheet("color: #94A3B8; font-size: 11px;")
        dl.addWidget(self.data_status)
        data_card.setLayout(dl)
        left.addWidget(data_card)
        
        param_card = QGroupBox("Parameters")
        pl = QFormLayout()
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(2, 100)
        self.threshold_spin.setValue(10)
        pl.addRow("Epit Threshold:", self.threshold_spin)
        param_card.setLayout(pl)
        left.addWidget(param_card)
        
        result_card = QGroupBox("Results")
        rl = QVBoxLayout()
        self.result_label = QLabel("Run analysis to see results")
        self.result_label.setStyleSheet("font-size: 12px; padding: 8px; color: #64748B; background: #F8FAFC; border-radius: 6px;")
        self.result_label.setWordWrap(True)
        self.result_label.setMinimumHeight(150)
        rl.addWidget(self.result_label)
        result_card.setLayout(rl)
        left.addWidget(result_card)
        
        analyze_btn = QPushButton("Analyze Pitting")
        analyze_btn.setObjectName("primaryBtn")
        analyze_btn.clicked.connect(self._run_analysis)
        left.addWidget(analyze_btn)
        left.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(300)
        content.addWidget(left_widget)
        
        # RIGHT PANEL
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, parent)
        
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, 1)
        content.addLayout(plot_layout, 1)
        
        ml.addLayout(content, 1)
    
    def _generate_test_data(self):
        self.test_data = self.engine.generate_test_data()
        self.analysis_result = None
        self.data_status.setText("Data generated. Click Analyze.")
        self.data_status.setStyleSheet("color: #10B981; font-size: 11px;")
        self._plot_cyclic()
    
    def _run_analysis(self):
        if self.test_data is None:
            self.result_label.setText("Generate test data first!")
            return
        
        result = self.engine.extract_pitting_potentials(
            self.test_data['potential'],
            self.test_data['current'],
            threshold_factor=self.threshold_spin.value()
        )
        self.analysis_result = result
        
        lines = []
        if result['Epit']: lines.append(f"Epit = {result['Epit']:.3f} V")
        if result['Erp']: lines.append(f"Erp = {result['Erp']:.3f} V")
        if result['hysteresis']: lines.append(f"Hysteresis = {result['hysteresis']:.3f} V")
        lines.append(f"Resistance: {result['pitting_resistance']}")
        
        self.result_label.setText("\n".join(lines))
        self.result_label.setStyleSheet("font-size: 12px; padding: 8px; color: #10B981; background: #D1FAE5; border-radius: 6px; font-weight: bold;")
        self._plot_cyclic()
    
    def _plot_cyclic(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self.test_data is None:
            return
        
        p = self.test_data['potential']
        c = np.abs(self.test_data['current'])
        
        ax.semilogy(p, c, 'b-', linewidth=1.5, alpha=0.7, label='Cyclic Polarization')
        
        if self.analysis_result:
            if self.analysis_result['Epit']:
                ax.axvline(self.analysis_result['Epit'], color=Theme.ERROR, linestyle='--', linewidth=2, label=f"Epit={self.analysis_result['Epit']:.2f}V")
            if self.analysis_result['Erp']:
                ax.axvline(self.analysis_result['Erp'], color=Theme.SECONDARY, linestyle='--', linewidth=2, label=f"Erp={self.analysis_result['Erp']:.2f}V")
        
        ax.set_xlabel('Potential (V)', fontweight='bold')
        ax.set_ylabel('|Current| (A)', fontweight='bold')
        ax.set_title('Cyclic Potentiodynamic Polarization', fontweight='bold')
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#FAFBFC')
        
        self.figure.tight_layout()
        self.canvas.draw()
    def _import_real_data(self):
        import pandas as pd
        path, _ = QFileDialog.getOpenFileName(self.parent, "Open Pitting Data", "", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        try:
            df = pd.read_csv(path)
            cols = [c.lower().strip() for c in df.columns]
            pc = cc = None
            for i, c in enumerate(cols):
                if 'potential' in c or 'volt' in c: pc = df.columns[i]
                elif 'current' in c or 'amp' in c: cc = df.columns[i]
            if pc is None or cc is None:
                nc = df.select_dtypes(include=[np.number]).columns
                if len(nc) >= 2: pc, cc = nc[0], nc[1]
                else: QMessageBox.warning(self.parent, "Error", "Cannot identify columns"); return
            self.test_data = {'potential': df[pc].values.astype(float), 'current': np.abs(df[cc].values.astype(float)), 'pit_depths': None}
            self.analysis_result = None
            self.data_status.setText(f"Loaded: {len(self.test_data['potential'])} points")
            self.data_status.setStyleSheet("color: #10B981; font-size: 11px;")
            self.result_label.setText("Data loaded. Click 'Analyze Pitting'.")
            self._plot_cyclic()
        except Exception as e:
            QMessageBox.critical(self.parent, "Import Error", str(e))