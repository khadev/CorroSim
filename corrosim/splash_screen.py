"""Professional Splash Screen for CorroSim"""

import time
from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPen, QBrush


class SplashScreen(QSplashScreen):
    """Professional splash screen with gradient design and progress bar"""
    
    # Configuration
    WIDTH = 600
    HEIGHT = 400
    BRAND_NAME = "CorroSim"
    TAGLINE = "Advanced Corrosion Analysis Platform"
    VERSION = "Version 1.5.0"
    COPYRIGHT = "© 2026 CorroSim • NanoStack-Lab"
    WEBSITE = "github.com/khadev/corrosim"
    
    def __init__(self):
        pixmap = self._create_pixmap(0, "Initializing...")
        super().__init__(pixmap)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._center_on_screen()
        self.show()
        QApplication.processEvents()
    
    def _draw_gradient_background(self, painter, pixmap):
        """Draw professional gradient background"""
        gradient = QLinearGradient(0, 0, self.WIDTH, self.HEIGHT)
        gradient.setColorAt(0.0, QColor("#0F172A"))    # Dark navy top
        gradient.setColorAt(0.4, QColor("#1E293B"))    # Slate middle
        gradient.setColorAt(0.7, QColor("#1E3A5F"))    # Blue-tinted
        gradient.setColorAt(1.0, QColor("#0F172A"))    # Dark navy bottom
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(pixmap.rect())
    
    def _draw_decorative_circles(self, painter):
        """Draw decorative background circles"""
        # Large subtle circle top-right
        painter.setBrush(QColor(37, 99, 235, 15))  # Theme blue, very transparent
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRect(self.WIDTH - 150, -80, 300, 300))
        
        # Small circle bottom-left
        painter.setBrush(QColor(5, 150, 105, 10))  # Theme green, very transparent
        painter.drawEllipse(QRect(-60, self.HEIGHT - 120, 200, 200))
        
        # Medium circle center accent
        painter.setBrush(QColor(124, 58, 237, 8))  # Purple accent
        painter.drawEllipse(QRect(self.WIDTH//2 - 100, 50, 250, 250))
    
    def _draw_logo_icon(self, painter):
        """Draw modern logo icon"""
        # Outer circle
        painter.setBrush(QColor(37, 99, 235, 30))
        painter.setPen(QPen(QColor("#2563EB"), 2))
        painter.drawEllipse(QRect(self.WIDTH//2 - 35, 70, 70, 70))
        
        # Lightning bolt symbol
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#3B82F6"))
        
        # Draw a simple lightning bolt using polygons
        bolt = [
            (self.WIDTH//2 + 8, 78),
            (self.WIDTH//2 - 8, 102),
            (self.WIDTH//2 + 2, 102),
            (self.WIDTH//2 - 5, 120),
            (self.WIDTH//2 + 12, 96),
            (self.WIDTH//2, 96),
            (self.WIDTH//2 + 10, 78)
        ]
        
        from PyQt6.QtGui import QPolygon
        from PyQt6.QtCore import QPoint
        
        points = [QPoint(x, y) for x, y in bolt]
        polygon = QPolygon(points)
        painter.drawPolygon(polygon)
    
    def _draw_brand_text(self, painter):
        """Draw brand name and tagline"""
        # Brand name
        painter.setPen(QColor("#F8FAFC"))
        font_title = QFont("Segoe UI", 36, QFont.Weight.Bold)
        font_title.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font_title)
        painter.drawText(
            QRect(0, 145, self.WIDTH, 50), 
            Qt.AlignmentFlag.AlignCenter, 
            self.BRAND_NAME
        )
        
        # Tagline
        painter.setPen(QColor("#94A3B8"))
        font_tag = QFont("Segoe UI", 13, QFont.Weight.Normal)
        painter.setFont(font_tag)
        painter.drawText(
            QRect(0, 200, self.WIDTH, 25), 
            Qt.AlignmentFlag.AlignCenter, 
            self.TAGLINE
        )
        
        # Version badge
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(37, 99, 235, 40))
        badge_rect = QRect(self.WIDTH//2 - 50, 232, 100, 24)
        painter.drawRoundedRect(QRectF(badge_rect), 12, 12)
        
        painter.setPen(QColor("#60A5FA"))
        font_ver = QFont("Segoe UI", 10, QFont.Weight.Medium)
        painter.setFont(font_ver)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, self.VERSION)
    
    def _draw_progress_section(self, painter, progress, text):
        """Draw modern progress bar and status text"""
        # Section separator line
        painter.setPen(QPen(QColor("#334155"), 1))
        painter.drawLine(80, 285, self.WIDTH - 80, 285)
        
        # Status text
        painter.setPen(QColor("#10B981"))
        font_status = QFont("Segoe UI", 10, QFont.Weight.Normal)
        painter.setFont(font_status)
        painter.drawText(
            QRect(0, 290, self.WIDTH, 25), 
            Qt.AlignmentFlag.AlignCenter, 
            text
        )
        
        # Progress bar background
        bar_x = 80
        bar_y = 322
        bar_width = self.WIDTH - 160
        bar_height = 5
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#1E293B"))
        painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_width, bar_height), 3, 3)
        
        # Progress bar fill with gradient
        if progress > 0:
            fill_width = int(bar_width * progress / 100)
            fill_gradient = QLinearGradient(bar_x, 0, bar_x + fill_width, 0)
            fill_gradient.setColorAt(0.0, QColor("#2563EB"))
            fill_gradient.setColorAt(1.0, QColor("#059669"))
            
            painter.setBrush(QBrush(fill_gradient))
            painter.drawRoundedRect(QRectF(bar_x, bar_y, fill_width, bar_height), 3, 3)
            
            # Glow dot at progress end
            if fill_width > 5:
                painter.setBrush(QColor("#F8FAFC"))
                painter.drawEllipse(QRect(bar_x + fill_width - 5, bar_y - 3, 10, 10))
    
    def _draw_footer(self, painter):
        """Draw footer with copyright and website"""
        # Copyright
        painter.setPen(QColor("#64748B"))
        font_footer = QFont("Segoe UI", 9, QFont.Weight.Normal)
        painter.setFont(font_footer)
        painter.drawText(
            QRect(0, self.HEIGHT - 35, self.WIDTH, 20), 
            Qt.AlignmentFlag.AlignCenter, 
            self.COPYRIGHT
        )
        
        # Website
        painter.setPen(QColor("#475569"))
        font_web = QFont("Segoe UI", 8, QFont.Weight.Light)
        painter.setFont(font_web)
        painter.drawText(
            QRect(0, self.HEIGHT - 18, self.WIDTH, 15), 
            Qt.AlignmentFlag.AlignCenter, 
            self.WEBSITE
        )
    
    def _create_pixmap(self, progress, text):
        """Create complete splash screen pixmap"""
        pixmap = QPixmap(self.WIDTH, self.HEIGHT)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw all layers
        self._draw_gradient_background(painter, pixmap)
        self._draw_decorative_circles(painter)
        self._draw_logo_icon(painter)
        self._draw_brand_text(painter)
        self._draw_progress_section(painter, progress, text)
        self._draw_footer(painter)
        
        painter.end()
        return pixmap
    
    def _center_on_screen(self):
        """Center splash on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.WIDTH) // 2
        y = (screen.height() - self.HEIGHT) // 2
        self.move(x, y)
    
    def update_progress(self, value, text):
        """Update progress bar and status text"""
        pixmap = self._create_pixmap(value, text)
        self.setPixmap(pixmap)
        QApplication.processEvents()
    
    @staticmethod
    def show_loading_sequence(messages, delays):
        """
        Show animated loading sequence.
        
        Parameters:
        - messages: List of status messages
        - delays: List of delays (seconds) between messages
        """
        splash = SplashScreen()
        
        for i, (msg, delay) in enumerate(zip(messages, delays)):
            progress = int((i + 1) / len(messages) * 100)
            splash.update_progress(progress, msg)
            time.sleep(delay)
        
        return splash