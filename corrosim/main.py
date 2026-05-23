"""Main entry point for CorroSim"""

import sys
import time
from PyQt6.QtWidgets import QApplication

from .splash_screen import SplashScreen
from .app import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Show splash screen with loading sequence
    messages = [
        "Initializing database...",
        "Loading analysis modules...",
        "Setting up user interface...",
        "Preparing Tafel engine...",
        "Starting application..."
    ]
    delays = [0.3, 0.3, 0.3, 0.3, 0.2]
    
    splash = SplashScreen.show_loading_sequence(messages, delays)
    
    # Create and show main window
    window = MainWindow()
    splash.close()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()