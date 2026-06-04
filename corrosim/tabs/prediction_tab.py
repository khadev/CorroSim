"""Lifetime Prediction Tab"""

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


class PredictionTab:
    """Tab for lifetime prediction"""
    
    def setup(self, parent):
        self.parent = parent
        
        ml = QVBoxLayout(parent)
        ml.setSpacing(12)
        ml.setContentsMargins(24, 24, 24, 24)
        
        title = QLabel("Lifetime Prediction")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        ml.addWidget(title)
        
        content = QHBoxLayout()
        content.setSpacing(12)
        
        # Left panel
        left = QVBoxLayout()
        left.setSpacing(8)
        
        # Model selection
        model_card = QGroupBox("Degradation Model")
        model_layout = QVBoxLayout()
        self.pred_model = QComboBox()
        self.pred_model.addItems(["Linear", "Power Law", "Exponential"])
        model_layout.addWidget(QLabel("Model:"))
        model_layout.addWidget(self.pred_model)
        model_card.setLayout(model_layout)
        left.addWidget(model_card)
        
        # Parameters
        param_card = QGroupBox("Parameters")
        pf = QFormLayout()
        pf.setSpacing(8)
        
        self.pred_cr0 = QDoubleSpinBox()
        self.pred_cr0.setRange(0.0001, 100)
        self.pred_cr0.setValue(0.1)
        self.pred_cr0.setSuffix(" mm/yr")
        pf.addRow("Initial CR:", self.pred_cr0)
        
        self.pred_thresh = QDoubleSpinBox()
        self.pred_thresh.setRange(0.001, 100)
        self.pred_thresh.setValue(0.5)
        self.pred_thresh.setSuffix(" mm/yr")
        pf.addRow("Failure Threshold:", self.pred_thresh)
        
        self.pred_years = QDoubleSpinBox()
        self.pred_years.setRange(1, 100)
        self.pred_years.setValue(10)
        self.pred_years.setSuffix(" years")
        pf.addRow("Analysis Period:", self.pred_years)
        
        param_card.setLayout(pf)
        left.addWidget(param_card)
        
        # Result display
        result_frame = QFrame()
        result_frame.setStyleSheet(
            f"background: linear-gradient(135deg, {Theme.SECONDARY}, {Theme.PRIMARY}); "
            f"border-radius: 8px; padding: 16px;"
        )
        rl = QVBoxLayout(result_frame)
        
        pred_title = QLabel("PREDICTED LIFETIME")
        pred_title.setStyleSheet("color: white; font-size: 12px; font-weight: 600;")
        pred_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(pred_title)
        
        self.pred_life_label = QLabel("— years")
        self.pred_life_label.setStyleSheet("color: #10B981; font-size: 36px; font-weight: 800;")
        self.pred_life_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self.pred_life_label)
        left.addWidget(result_frame)
        
        # Run button
        self.run_btn = QPushButton("🔮 Calculate Prediction")
        self.run_btn.setObjectName("primaryBtn")
        self.run_btn.clicked.connect(self._run_prediction)
        left.addWidget(self.run_btn)
        left.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(280)
        content.addWidget(left_widget)
        
        # Right panel - Plot
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
    
    def _run_prediction(self):
        try:
            cr0 = self.pred_cr0.value()
            th = self.pred_thresh.value()
            mt = self.pred_years.value()
            
            if cr0 <= 0 or th <= cr0:
                QMessageBox.warning(self.parent, "Invalid", "Check: 0 < Initial CR < Threshold")
                return
            
            model = self.pred_model.currentText()
            
            if model == "Linear":
                k = (th - cr0) / mt
                lifetime = mt if k <= 0 else (th - cr0) / k
                t = np.linspace(0, mt, 200)
                cr = cr0 + k * t
            elif model == "Power Law":
                n = 0.5
                lifetime = mt if cr0 <= 0 else min((th / cr0) ** (1/n), mt)
                t = np.linspace(0.01, mt, 200)
                cr = cr0 * (t ** n)
            else:  # Exponential
                k = np.log(th / cr0) / mt if cr0 > 0 else 0.1
                lifetime = mt if k <= 0 else min(np.log(th / cr0) / k, mt)
                t = np.linspace(0, mt, 200)
                cr = cr0 * np.exp(k * t)
            
            lifetime = max(0.1, min(lifetime, mt))
            self.pred_life_label.setText(f"{lifetime:.2f}\nyears")
            
            # Plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            ax.plot(t, cr, '-', color=Theme.PRIMARY, linewidth=2.5, label='Predicted CR')
            ax.fill_between(t, cr*0.85, cr*1.15, alpha=0.15, color=Theme.PRIMARY)
            ax.axhline(th, color=Theme.ERROR, linestyle='--', linewidth=2, label=f'Threshold: {th:.3f}')
            ax.axvline(lifetime, color=Theme.SECONDARY, linestyle='--', linewidth=2, label=f'Lifetime: {lifetime:.1f}y')
            ax.plot(lifetime, th, 'o', color=Theme.SECONDARY, markersize=10, zorder=4)
            
            ax.set_xlabel('Time (years)', fontweight='bold')
            ax.set_ylabel('Corrosion Rate (mm/yr)', fontweight='bold')
            ax.set_title(f'Lifetime Prediction - {model}', fontweight='bold')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#FAFBFC')
            ax.set_xlim(0, mt)
            ax.set_ylim(0, max(cr.max(), th) * 1.1)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", str(e))