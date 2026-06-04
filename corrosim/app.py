"""Main Application Window"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .theme import Theme, GLOBAL_STYLE, SIDEBAR_STYLE, DARK_STYLE
from .database import Database
from .tabs import ImportTab, TafelTab, PredictionTab, ComparisonTab
from .tabs.galvanic_tab import GalvanicTab
from .tabs.eis_tab import EISTab
from .tabs.pitting_tab import PittingTab
from .tabs.inhibitor_tab import InhibitorTab
from matplotlib.figure import Figure
from .utils.translations import Translator


class MainWindow(QMainWindow):
    """Main application window for CorroSim"""

    def __init__(self):
        super().__init__()
        self.tr = Translator.get()
        self.setWindowTitle("CorroSim Analysis Platform")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.db = Database()
        self.nav_buttons = []
        self.sidebar_buttons = []
        self.dark_mode = False
        self.setStyleSheet(GLOBAL_STYLE)
        self._setup_ui()
        self._setup_menu()
        self.statusBar().showMessage("Ready - Import data to begin")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self._create_sidebar()
        self._create_tabs()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.tabs, 1)
        self.switch_tab(0)

    def _create_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(SIDEBAR_STYLE)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(6)
        self.logo_label = QLabel("⚡ CorroSim")
        self.logo_label.setStyleSheet("font-size: 18px; font-weight: 700; color: white; background: transparent;")
        layout.addWidget(self.logo_label)
        layout.addSpacing(20)
        self.nav_label = QLabel("NAVIGATION")
        self.nav_label.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: 600; background: transparent;")
        layout.addWidget(self.nav_label)
        tabs = [
            ("📁", "tab.import", 0), ("⚡", "tab.tafel", 1), ("🔮", "tab.prediction", 2),
            ("📊", "tab.compare", 3), ("🔗", "tab.galvanic", 4), ("🔬", "tab.eis", 5),
            ("🕳️", "tab.pitting", 6), ("🧪", "tab.inhibitor", 7),
        ]
        for icon, key, idx in tabs:
            btn = QPushButton(f"  {icon}  {self.tr.tr(key)}")
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, i=idx: self.switch_tab(i))
            self.nav_buttons.append(btn)
            self.sidebar_buttons.append((btn, key))
            layout.addWidget(btn)
        layout.addStretch()
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #334155; max-height: 1px;")
        layout.addWidget(sep)
        self.db_status = QLabel("● Database Connected")
        self.db_status.setStyleSheet("color: #10B981; font-size: 10px; background: transparent; padding: 8px;")
        layout.addWidget(self.db_status)

    def _create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.import_widget = QWidget()
        self.tafel_widget = QWidget()
        self.prediction_widget = QWidget()
        self.comparison_widget = QWidget()
        self.galvanic_widget = QWidget()
        self.eis_widget = QWidget()
        self.pitting_widget = QWidget()
        self.inhibitor_widget = QWidget()
        self.tabs.addTab(self.import_widget, "Import")
        self.tabs.addTab(self.tafel_widget, "Tafel")
        self.tabs.addTab(self.prediction_widget, "Prediction")
        self.tabs.addTab(self.comparison_widget, "Compare")
        self.tabs.addTab(self.galvanic_widget, "Galvanic")
        self.tabs.addTab(self.eis_widget, "EIS")
        self.tabs.addTab(self.pitting_widget, "Pitting")
        self.tabs.addTab(self.inhibitor_widget, "Inhibitor")
        self.import_tab = ImportTab()
        self.import_tab.setup(parent=self.import_widget, db=self.db,
                              switch_tab_callback=self.switch_tab, load_tafel_callback=self._load_tafel_data)
        self.tafel_tab = TafelTab()
        self.tafel_tab.setup(parent=self.tafel_widget, db=self.db)
        self.prediction_tab = PredictionTab()
        self.prediction_tab.setup(parent=self.prediction_widget)
        self.comparison_tab = ComparisonTab()
        self.comparison_tab.setup(parent=self.comparison_widget, db=self.db)
        self.galvanic_tab = GalvanicTab()
        self.galvanic_tab.setup(parent=self.galvanic_widget)
        self.eis_tab = EISTab()
        self.eis_tab.setup(parent=self.eis_widget, db=self.db)
        self.pitting_tab = PittingTab()
        self.pitting_tab.setup(parent=self.pitting_widget, db=self.db)
        self.inhibitor_tab = InhibitorTab()
        self.inhibitor_tab.setup(parent=self.inhibitor_widget, db=self.db)

    def switch_tab(self, index):
        self.tabs.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _load_tafel_data(self):
        if hasattr(self, 'tafel_tab'):
            self.tafel_tab._load_data()

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        export_action = QAction("Export PDF Report", self)
        export_action.triggered.connect(self._export_pdf_report)
        file_menu.addAction(export_action)
        theme_action = QAction("Toggle Dark Mode", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self._toggle_theme)
        file_menu.addAction(theme_action)
        lang_menu = menubar.addMenu("Language")
        en_action = QAction("English", self)
        en_action.triggered.connect(lambda: self._switch_lang("en"))
        lang_menu.addAction(en_action)
        fr_action = QAction("Français", self)
        fr_action.triggered.connect(lambda: self._switch_lang("fr"))
        lang_menu.addAction(fr_action)
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _switch_lang(self, lang):
        self.tr.set_language(lang)
        self.nav_label.setText(self.tr.tr("sidebar.navigation"))
        for btn, key in self.sidebar_buttons:
            icon = btn.text().strip()[:2]
            btn.setText(f"  {icon}  {self.tr.tr(key)}")
        self.db_status.setText(f"● {self.tr.tr('sidebar.database')}")
        self.statusBar().showMessage(f"Language: {'English' if lang == 'en' else 'Français'}")

    def _export_pdf_report(self):
        from matplotlib.backends.backend_pdf import PdfPages
        import datetime
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF Report", "corrosim_report.pdf", "PDF Files (*.pdf)")
        if not path: return
        try:
            with PdfPages(path) as pdf:
                fig = Figure(figsize=(8.5, 11))
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.9, "CorroSim Analysis Report", transform=ax.transAxes, ha='center', fontsize=20, fontweight='bold')
                ax.text(0.5, 0.85, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", transform=ax.transAxes, ha='center', fontsize=12)
                ax.axis('off')
                pdf.savefig(fig)
                if hasattr(self.tafel_tab, 'figure'): pdf.savefig(self.tafel_tab.figure)
                if hasattr(self.eis_tab, 'figure'): pdf.savefig(self.eis_tab.figure)
                if hasattr(self.galvanic_tab, 'figure'): pdf.savefig(self.galvanic_tab.figure)
            QMessageBox.information(self, "Success", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.statusBar().showMessage("Dark mode enabled")
        else:
            self.setStyleSheet(GLOBAL_STYLE)
            self.statusBar().showMessage("Light mode enabled")

    def _show_about(self):
        QMessageBox.about(self, "About CorroSim",
            "<h3>CorroSim Analysis Platform</h3><p>Version 1.5.0</p>"
            "<p>Professional Corrosion Analysis Suite</p><hr>"
            "<p><b>8 Modules:</b></p><ul>"
            "<li>Tafel Polarization Analysis</li>"
            "<li>Galvanic Corrosion Simulator</li>"
            "<li>EIS Impedance Spectroscopy</li>"
            "<li>Pitting Corrosion Analyzer</li>"
            "<li>Inhibitor Efficiency Calculator</li>"
            "<li>Lifetime Prediction</li>"
            "<li>Multi-Sample Comparison</li>"
            "<li>Data Import & Export</li></ul>"
            "<p>2026 CorroSim By NanoStack-Lab</p>")

    def closeEvent(self, event):
        self.db.close()
        event.accept()