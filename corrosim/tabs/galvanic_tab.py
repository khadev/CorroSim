"""Galvanic Corrosion Tab"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from ..theme import Theme
from ..engines.galvanic_engine import GalvanicEngine


class GalvanicTab:
    """Tab for galvanic corrosion prediction"""
    
    def setup(self, parent):
        self.parent = parent
        self.engine = GalvanicEngine()
        
        ml = QVBoxLayout(parent)
        ml.setSpacing(12)
        ml.setContentsMargins(24, 24, 24, 24)
        
        # Header
        title = QLabel("Galvanic Corrosion Simulator")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #1E293B;")
        ml.addWidget(title)
        
        desc = QLabel("Predict corrosion between dissimilar metals in seawater")
        desc.setStyleSheet("color: #64748B; font-size: 13px; margin-bottom: 4px;")
        ml.addWidget(desc)
        
        content = QHBoxLayout()
        content.setSpacing(12)
        
        # LEFT PANEL - Inputs
        left = QVBoxLayout()
        left.setSpacing(8)
        
        # Metal selection
        metal_card = QGroupBox("Metal Selection")
        metal_form = QFormLayout()
        metal_form.setSpacing(10)
        
        self.anode_combo = QComboBox()
        self.anode_combo.addItems(self.engine.get_metal_list())
        self.anode_combo.setCurrentText('Mild Steel')
        metal_form.addRow("Anode (corroding):", self.anode_combo)
        
        self.cathode_combo = QComboBox()
        self.cathode_combo.addItems(self.engine.get_metal_list())
        self.cathode_combo.setCurrentText('Copper')
        metal_form.addRow("Cathode (noble):", self.cathode_combo)
        metal_card.setLayout(metal_form)
        left.addWidget(metal_card)
        
        # Parameters
        param_card = QGroupBox("Parameters")
        param_form = QFormLayout()
        param_form.setSpacing(10)
        
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.01, 1000)
        self.area_spin.setValue(1.0)
        self.area_spin.setDecimals(2)
        self.area_spin.setToolTip("Ratio of cathode area to anode area.\n"
                                  "Larger cathode = faster anode corrosion")
        param_form.addRow("Cathode/Anode Ratio:", self.area_spin)
        
        self.resistivity_spin = QDoubleSpinBox()
        self.resistivity_spin.setRange(0.01, 100)
        self.resistivity_spin.setValue(0.25)
        self.resistivity_spin.setDecimals(3)
        self.resistivity_spin.setSuffix(" Ω·m")
        self.resistivity_spin.setToolTip("Seawater ≈ 0.25 Ω·m\nFresh water ≈ 10-100 Ω·m")
        param_form.addRow("Resistivity:", self.resistivity_spin)
        param_card.setLayout(param_form)
        left.addWidget(param_card)
        
        # Results
        result_card = QGroupBox("Results")
        result_layout = QVBoxLayout()
        
        self.result_label = QLabel("Select metals and click Calculate")
        self.result_label.setStyleSheet("font-size: 13px; padding: 10px; color: #64748B;")
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)
        
        self.recommendation_label = QLabel("")
        self.recommendation_label.setStyleSheet("font-size: 11px; padding: 8px; color: #64748B; background: #F8FAFC; border-radius: 6px;")
        self.recommendation_label.setWordWrap(True)
        result_layout.addWidget(self.recommendation_label)
        
        result_card.setLayout(result_layout)
        left.addWidget(result_card)
        
        # Calculate button
        calc_btn = QPushButton("⚡ Calculate Galvanic Corrosion")
        calc_btn.setObjectName("primaryBtn")
        calc_btn.clicked.connect(self._calculate)
        left.addWidget(calc_btn)
        
        left.addStretch()
        
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(320)
        content.addWidget(left_widget)
        
        # RIGHT PANEL - Plot
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
    
    def _calculate(self):
        """Run galvanic corrosion calculation and update UI"""
        anode = self.anode_combo.currentText()
        cathode = self.cathode_combo.currentText()
        area_ratio = self.area_spin.value()
        resistivity = self.resistivity_spin.value()
        
        result = self.engine.calculate(anode, cathode, area_ratio, resistivity)
     
        # Check for errors
        if 'error' in result:
            self.result_label.setText(f"Error: {result['error']}")
            self.recommendation_label.setText("")
            return
        
        # Display results
        self.result_label.setText(
            f"ΔE = {result['delta_E']:.3f} V\n"
            f"Galvanic Current = {result['current_density']:.6f} A/m²\n"
            f"Corrosion Rate = {result['corrosion_rate']:.4f} mm/yr\n"
            f"Severity: {result['severity']}"
        )
        
        # Color based on severity
        self.result_label.setStyleSheet(
            f"font-size: 13px; padding: 10px; "
            f"color: {result['severity_color']}; "
            f"font-weight: bold;"
        )
        
        # Show recommendation
        self.recommendation_label.setText(result['recommendation'])
        
        # Plot galvanic series
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        metals = self.engine.get_metal_list()
        potentials = [self.engine.SERIES[m] for m in metals]
        
        # Color bars: red for active (negative), blue for noble (positive)
        bar_colors = ['#EF4444' if p < 0 else '#3B82F6' for p in potentials]
        bars = ax.barh(metals, potentials, color=bar_colors, height=0.6)
        
        # Highlight selected metals
        for i, metal in enumerate(metals):
            if metal == anode:
                bars[i].set_edgecolor('#F59E0B')  # Orange border
                bars[i].set_linewidth(3)
            elif metal == cathode:
                bars[i].set_edgecolor('#10B981')  # Green border
                bars[i].set_linewidth(3)
        
        # Add connecting line between selected metals
        if anode in metals and cathode in metals:
            idx_a = metals.index(anode)
            idx_c = metals.index(cathode)
            y_mid = (idx_a + idx_c) / 2
            ax.annotate(
                f"ΔE = {result['delta_E']:.2f} V",
                xy=(0, y_mid),
                fontsize=11,
                fontweight='bold',
                color='#F59E0B',
                ha='center'
            )
        
        ax.axvline(x=0, color='white', linewidth=2, linestyle='-')
        ax.set_xlabel('Potential (V vs SCE)', fontweight='bold')
        ax.set_title('Galvanic Series in Seawater\n(ASTM G82)', fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#FAFBFC')
        
        self.figure.tight_layout()
        self.canvas.draw()