"""Main Application Window"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .theme import Theme, GLOBAL_STYLE, SIDEBAR_STYLE
from .database import Database
from .tabs import ImportTab, TafelTab, PredictionTab, ComparisonTab
from .tabs.galvanic_tab import GalvanicTab


class MainWindow(QMainWindow):
    """Main application window for CorroSim"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CorroSim Analysis Platform")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.db = Database()
        self.nav_buttons = []
        
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
        
        logo = QLabel("⚡ CorroSim")
        logo.setStyleSheet("font-size: 18px; font-weight: 700; color: white; background: transparent;")
        layout.addWidget(logo)
        layout.addSpacing(20)
        
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: 600; background: transparent;")
        layout.addWidget(nav_label)
        
        tabs = [
            ("📁", "Import", 0),
            ("⚡", "Tafel", 1),
            ("🔮", "Prediction", 2),
            ("📊", "Compare", 3),
            ("🔗", "Galvanic", 4),
        ]
        
        for icon, text, idx in tabs:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, i=idx: self.switch_tab(i))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #334155; max-height: 1px;")
        layout.addWidget(sep)
        
        status = QLabel("● Database Connected")
        status.setStyleSheet("color: #10B981; font-size: 10px; background: transparent; padding: 8px;")
        layout.addWidget(status)
    
    def _create_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        
        # Create all tab widgets
        self.import_widget = QWidget()
        self.tafel_widget = QWidget()
        self.prediction_widget = QWidget()
        self.comparison_widget = QWidget()
        self.galvanic_widget = QWidget()
        
        self.tabs.addTab(self.import_widget, "Import")
        self.tabs.addTab(self.tafel_widget, "Tafel")
        self.tabs.addTab(self.prediction_widget, "Prediction")
        self.tabs.addTab(self.comparison_widget, "Compare")
        self.tabs.addTab(self.galvanic_widget, "Galvanic")
        
        # Setup Import Tab
        self.import_tab = ImportTab()
        self.import_tab.setup(
            parent=self.import_widget,
            db=self.db,
            switch_tab_callback=self.switch_tab,
            load_tafel_callback=self._load_tafel_data
        )
        
        # Setup Tafel Tab
        self.tafel_tab = TafelTab()
        self.tafel_tab.setup(parent=self.tafel_widget, db=self.db)
        
        # Setup Prediction Tab
        self.prediction_tab = PredictionTab()
        self.prediction_tab.setup(parent=self.prediction_widget)
        
        # Setup Comparison Tab
        self.comparison_tab = ComparisonTab()
        self.comparison_tab.setup(parent=self.comparison_widget, db=self.db)
        
        # Setup Galvanic Tab
        self.galvanic_tab = GalvanicTab()
        self.galvanic_tab.setup(parent=self.galvanic_widget)
    
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
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {Theme.BG_WHITE};
                border-bottom: 1px solid {Theme.BORDER};
                padding: 2px;
            }}
            QMenuBar::item {{
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{
                background-color: {Theme.PRIMARY_LIGHT};
            }}
        """)
        
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _show_about(self):
        QMessageBox.about(
            self,
            "About CorroSim",
            "<h3>⚡ CorroSim Analysis Platform</h3>"
            "<p>Version 1.0.0</p>"
            "<p>Professional Corrosion Analysis Tool</p>"
            "<hr>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Tafel Polarization Analysis</li>"
            "<li>Galvanic Corrosion Simulation</li>"
            "<li>Lifetime Prediction Models</li>"
            "<li>Multi-Sample Comparison</li>"
            "<li>Data Export (PNG, PDF, Excel)</li>"
            "</ul>"
            "<p>© 2026 CorroSim By NanoStack-Lab</p>"
        )
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()