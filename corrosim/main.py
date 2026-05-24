"""Main entry point for CorroSim"""

import sys
import time
from PyQt6.QtWidgets import QApplication


def main():
    """Application entry point"""
    # CREATE QAPPLICATION FIRST - before any other PyQt import
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Only import splash AFTER QApplication exists
    from corrosim.splash_screen import SplashScreen
    from corrosim.app import MainWindow
    
    # Show splash screen
    splash = SplashScreen()
    
    # Loading sequence
    steps = [
        (20, "Initializing database..."),
        (40, "Loading analysis modules..."),
        (60, "Setting up user interface..."),
        (80, "Preparing engines..."),
        (100, "Starting application...")
    ]
    
    for progress, message in steps:
        splash.update_progress(progress, message)
        time.sleep(0.3)
        QApplication.processEvents()
    
    # Create main window
    window = MainWindow()
    splash.close()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()