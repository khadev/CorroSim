"""
CorroSim - Professional Corrosion Analysis Platform

A comprehensive tool for electrochemical corrosion analysis including:
- Tafel polarization analysis
- Lifetime prediction
- Multi-sample comparison
- Data import/export
"""

__version__ = "1.1.0"
__author__ = "Your Name"
__description__ = "Professional Corrosion Analysis Platform"

from .tafel_engine import TafelEngine
from .database import Database
from .theme import Theme

__all__ = ['TafelEngine', 'Database', 'Theme']
