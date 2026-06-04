"""Tafel Analysis Tab"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import numpy as np
import pandas as pd
from io import StringIO

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..theme import Theme
from ..tafel_engine import TafelEngine


class TafelTab:
    """Tab for Tafel polarization analysis"""
    
    def setup(self, parent, db):
        self.parent = parent
        self.db = db
        self.engine = TafelEngine()
        self.current_data = None
        self.current_id = None
        
        ml = QVBoxLayout(parent)
        ml.setSpacing(12)
        ml.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Tafel Analysis")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        header.addWidget(title)
        header.addStretch()
        
        self.tafel_status = QLabel("No data")
        self.tafel_status.setStyleSheet(
            "background: #FEF3C7; color: #92400E; padding: 6px 16px; "
            "border-radius: 12px; font-weight: 600; font-size: 11px;"
        )
        header.addWidget(self.tafel_status)
        
        load_btn = QPushButton("📂 Load Data")
        load_btn.clicked.connect(self._load_data)
        header.addWidget(load_btn)
        ml.addLayout(header)
        
        # Content
        content = QHBoxLayout()
        content.setSpacing(12)
        
        # Left panel
        left = QVBoxLayout()
        left.setSpacing(8)
        
        # Unit selector
        unit_card = QGroupBox("Current Units")
        ul = QHBoxLayout()
        self.tafel_unit = QComboBox()
        self.tafel_unit.addItems(["Auto-detect", "Amperes (A)", "milliamperes (mA)", "microamperes (μA)"])
        ul.addWidget(self.tafel_unit)
        unit_card.setLayout(ul)
        left.addWidget(unit_card)
        
        # Area
        area_card = QGroupBox("Electrode Area")
        al = QHBoxLayout()
        al.addWidget(QLabel("Area:"))
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.001, 1000)
        self.area_spin.setValue(1.0)
        self.area_spin.setSuffix(" cm²")
        al.addWidget(self.area_spin, 1)
        area_card.setLayout(al)
        left.addWidget(area_card)
        
        # Results table
        res_card = QGroupBox("Results")
        rl = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setRowCount(6)
        self.results_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        
        params = ["Ecorr (V)", "Icorr (μA/cm²)", "CR (mm/yr)", "βa (mV/dec)", "βc (mV/dec)", "R²"]
        for i, p in enumerate(params):
            self.results_table.setItem(i, 0, QTableWidgetItem(p))
            item = QTableWidgetItem("—")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 1, item)
        
        self.results_table.resizeColumnsToContents()
        rl.addWidget(self.results_table)
        res_card.setLayout(rl)
        left.addWidget(res_card)
        
        # Buttons
        self.run_btn = QPushButton("⚡ Run Tafel Analysis")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.clicked.connect(self._run_analysis)
        left.addWidget(self.run_btn)
        
        export_row = QHBoxLayout()
        self.export_png = QPushButton("Save PNG")
        self.export_png.setEnabled(False)
        self.export_png.clicked.connect(lambda: self._export_plot('png'))
        export_row.addWidget(self.export_png)
        self.export_pdf = QPushButton("Save PDF")
        self.export_pdf.setEnabled(False)
        self.export_pdf.clicked.connect(lambda: self._export_plot('pdf'))
        export_row.addWidget(self.export_pdf)
        left.addLayout(export_row)
        left.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(300)
        content.addWidget(left_widget)
        
        # Right panel - Graph
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)
        
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, parent)
        
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas, 1)
        content.addLayout(plot_layout, 1)
        
        ml.addLayout(content, 1)
    
    def _load_data(self):
        try:
            latest = self.db.get_latest()
            if not latest:
                QMessageBox.warning(self.parent, "No Data", "Import data first")
                return
            
            self.current_id = latest[0]
            self.current_data = pd.read_csv(StringIO(latest[4]))
            self.tafel_status.setText(f"✓ {latest[1]}")
            self.tafel_status.setStyleSheet(
                "background: #D1FAE5; color: #065F46; padding: 6px 16px; "
                "border-radius: 12px; font-weight: 600; font-size: 11px;"
            )
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", str(e))
    
    def _run_analysis(self):
        if self.current_data is None:
            QMessageBox.warning(self.parent, "No Data", "Load data first")
            return
        
        try:
            pcol, ccol = None, None
            for col in self.current_data.columns:
                cl = col.lower()
                if 'potential' in cl or 'volt' in cl: pcol = col
                if 'current' in cl or 'amp' in cl: ccol = col
            
            if not pcol or not ccol:
                num_cols = list(self.current_data.select_dtypes(include=[np.number]).columns)
                if len(num_cols) >= 2:
                    pcol, ccol = num_cols[0], num_cols[1]
                else:
                    QMessageBox.critical(self.parent, "Error", "Cannot identify columns")
                    return
            
            potential = self.current_data[pcol].values
            current = self.current_data[ccol].values
            
            unit_choice = self.tafel_unit.currentText()
            auto_detect = True
            if "milliamperes" in unit_choice:
                current = current * 0.001; auto_detect = False
            elif "microamperes" in unit_choice:
                current = current * 1e-6; auto_detect = False
            elif "Amperes" in unit_choice and "micro" not in unit_choice and "milli" not in unit_choice:
                auto_detect = False
            
            results = self.engine.analyze(potential, current, self.area_spin.value(), auto_detect_units=auto_detect)
            
            if not results:
                QMessageBox.warning(self.parent, "Failed", "Analysis failed")
                return
            
            # Update table
            values = [
                f"{results['ecorr']:.4f}",
                f"{results['icorr']:.2f}",
                f"{results['cr']:.4f}",
                f"{results['beta_a']:.1f}",
                f"{results['beta_c']:.1f}",
                f"{results['r2']:.4f}"
            ]
            
            for i, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("", -1, QFont.Weight.Bold))
                self.results_table.setItem(i, 1, item)
            
            self.results_table.resizeColumnsToContents()
            
            # Plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.scatter(results['p'], results['log_i'], alpha=0.7, s=40, color=Theme.PRIMARY, label='Data', zorder=3)
            
            pr = np.linspace(results['p'].min(), results['p'].max(), 200)
            ax.plot(pr, results['slope_a']*pr + results['intercept_a'], '-', color=Theme.ERROR, linewidth=2, label=f"βa={results['beta_a']:.0f}")
            ax.plot(pr, results['slope_c']*pr + results['intercept_c'], '-', color=Theme.SECONDARY, linewidth=2, label=f"βc={results['beta_c']:.0f}")
            ax.axvline(results['ecorr'], color=Theme.WARNING, linestyle='--', linewidth=2, label=f"Ecorr={results['ecorr']:.3f}V")
            
            ax.set_xlabel('Potential (V)', fontweight='bold')
            ax.set_ylabel('log|Current| (A)', fontweight='bold')
            ax.set_title('Tafel Analysis', fontweight='bold')
            ax.legend(); ax.grid(True, alpha=0.3); ax.set_facecolor('#FAFBFC')
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.export_png.setEnabled(True); self.export_pdf.setEnabled(True)
            
            if self.current_id:
                self.db.update(self.current_id, results['ecorr'], results['icorr'], results['cr'], results['beta_a'], results['beta_c'])
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", str(e))
    
    def _export_plot(self, fmt):
        path, _ = QFileDialog.getSaveFileName(self.parent, f"Save {fmt.upper()}", f"tafel.{fmt}", f"{fmt.upper()} (*.{fmt})")
        if path:
            self.figure.savefig(path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self.parent, "Success", f"Saved to {path}")