"""Theme and styling constants for CorroSim"""

class Theme:
    """Professional color theme"""
    
    # Primary Colors
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1D4ED8"
    PRIMARY_LIGHT = "#DBEAFE"
    
    # Secondary Colors
    SECONDARY = "#059669"
    SECONDARY_DARK = "#047857"
    
    # Accent
    ACCENT = "#7C3AED"
    
    # Background Colors
    BG_MAIN = "#F1F5F9"
    BG_WHITE = "#FFFFFF"
    BG_CARD = "#FFFFFF"
    
    # Text Colors
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    
    # Border
    BORDER = "#E2E8F0"
    
    # Status Colors
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"
    
    # Sidebar
    SIDEBAR_BG = "#1E293B"
    SIDEBAR_HOVER = "#334155"
    SIDEBAR_TEXT = "#F8FAFC"


# =============================================================================
# GLOBAL STYLESHEETS
# =============================================================================

GLOBAL_STYLE = f"""
QMainWindow {{ background-color: {Theme.BG_MAIN}; }}
QGroupBox {{ 
    font-weight: 600; font-size: 13px; 
    color: {Theme.TEXT_PRIMARY}; 
    border: 1px solid {Theme.BORDER}; 
    border-radius: 8px; 
    margin-top: 12px; 
    padding: 16px 12px 12px 12px; 
    background-color: {Theme.BG_WHITE}; 
}}
QGroupBox::title {{ 
    subcontrol-origin: margin; 
    left: 16px; 
    padding: 0 8px; 
    color: {Theme.PRIMARY}; 
    background-color: {Theme.BG_WHITE}; 
}}
QLabel {{ 
    color: {Theme.TEXT_PRIMARY}; 
    font-size: 12px; 
    background: transparent; 
    border: none; 
}}
QLineEdit, QDoubleSpinBox, QComboBox {{ 
    padding: 8px 12px; 
    border: 1px solid {Theme.BORDER}; 
    border-radius: 6px; 
    background-color: {Theme.BG_WHITE}; 
    font-size: 12px; 
    color: {Theme.TEXT_PRIMARY}; 
    min-height: 20px; 
}}
QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {{ 
    border-color: {Theme.PRIMARY}; 
}}
QPushButton {{ 
    padding: 8px 16px; 
    border-radius: 6px; 
    font-size: 12px; 
    font-weight: 600; 
    border: none; 
    background-color: {Theme.PRIMARY}; 
    color: white; 
}}
QPushButton:hover {{ background-color: {Theme.PRIMARY_DARK}; }}
QPushButton#primaryBtn {{ 
    background-color: {Theme.SECONDARY}; 
    font-size: 13px; 
    padding: 12px 24px; 
}}
QPushButton#primaryBtn:hover {{ background-color: {Theme.SECONDARY_DARK}; }}
QTableWidget {{ 
    border: 1px solid {Theme.BORDER}; 
    border-radius: 8px; 
    gridline-color: {Theme.BORDER}; 
    background-color: {Theme.BG_WHITE}; 
    alternate-background-color: #F8FAFC; 
    font-size: 12px; 
}}
QTableWidget::item {{ padding: 8px 12px; }}
QHeaderView::section {{ 
    background-color: {Theme.SIDEBAR_BG}; 
    color: {Theme.SIDEBAR_TEXT}; 
    padding: 10px 12px; 
    font-weight: 600; 
    font-size: 11px; 
    border: none; 
}}
QScrollBar:vertical {{ 
    border: none; 
    background: transparent; 
    width: 8px; 
}}
QScrollBar::handle:vertical {{ 
    background: #CBD5E1; 
    border-radius: 4px; 
    min-height: 20px; 
}}
QTabWidget::pane {{ border: none; background: transparent; }}
QStatusBar {{ 
    background-color: {Theme.SIDEBAR_BG}; 
    color: {Theme.SIDEBAR_TEXT}; 
    font-size: 11px; 
    padding: 4px 12px; 
}}
"""

SIDEBAR_STYLE = f"""
QWidget#sidebar {{ background-color: {Theme.SIDEBAR_BG}; }}
QPushButton {{ 
    color: {Theme.SIDEBAR_TEXT}; 
    text-align: left; 
    padding: 10px 16px; 
    background: transparent; 
    border-radius: 8px; 
    font-size: 13px; 
    font-weight: 500; 
    border: none; 
}}
QPushButton:hover {{ background-color: {Theme.SIDEBAR_HOVER}; }}
QPushButton[active="true"] {{ 
    background-color: {Theme.PRIMARY}; 
    font-weight: 600; 
}}
"""
DARK_STYLE = f"""
QMainWindow {{ background-color: #0D1117; }}
QGroupBox {{ font-weight: 600; font-size: 13px; color: #F0F6FC; border: 1px solid #30363D; border-radius: 8px; margin-top: 12px; padding: 16px 12px 12px 12px; background-color: #161B22; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 16px; padding: 0 8px; color: #58A6FF; background-color: #161B22; }}
QLabel {{ color: #F0F6FC; font-size: 12px; background: transparent; border: none; }}
QLineEdit, QDoubleSpinBox, QComboBox {{ padding: 8px 12px; border: 1px solid #30363D; border-radius: 6px; background-color: #21262D; font-size: 12px; color: #F0F6FC; min-height: 20px; }}
QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {{ border-color: #58A6FF; }}
QPushButton {{ padding: 8px 16px; border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid #30363D; background-color: #21262D; color: #F0F6FC; }}
QPushButton:hover {{ background-color: #30363D; }}
QPushButton#primaryBtn {{ background-color: #238636; font-size: 13px; padding: 12px 24px; border: none; }}
QPushButton#primaryBtn:hover {{ background-color: #2EA043; }}
QTableWidget {{ border: 1px solid #30363D; border-radius: 8px; gridline-color: #30363D; background-color: #161B22; alternate-background-color: #1C2128; font-size: 12px; color: #F0F6FC; }}
QTableWidget::item {{ padding: 8px 12px; }}
QHeaderView::section {{ background-color: #21262D; color: #58A6FF; padding: 10px 12px; font-weight: 600; font-size: 11px; border: none; border-right: 1px solid #30363D; }}
QScrollBar:vertical {{ border: none; background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: #30363D; border-radius: 4px; min-height: 20px; }}
QScrollBar::handle:vertical:hover {{ background: #58A6FF; }}
QTabWidget::pane {{ border: none; background: transparent; }}
QStatusBar {{ background-color: #010409; color: #8B949E; font-size: 11px; padding: 4px 12px; }}
QMenuBar {{ background-color: #161B22; color: #F0F6FC; border-bottom: 1px solid #30363D; }}
QMenuBar::item:selected {{ background-color: #21262D; }}
QMenu {{ background-color: #161B22; color: #F0F6FC; border: 1px solid #30363D; }}
QMenu::item:selected {{ background-color: #21262D; }}
"""
