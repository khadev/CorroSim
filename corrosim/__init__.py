"""
CorroSim - Professional Corrosion Analysis Platform

A comprehensive tool for electrochemical corrosion analysis including:
- Tafel polarization analysis
- Galvanic corrosion simulation
- EIS impedance spectroscopy
- Pitting corrosion analysis
- Inhibitor efficiency calculation
- Lifetime prediction
- Multi-sample comparison
- Data import/export
"""

__version__ = "1.5.2"
__author__ = "Oukil Khaled Ibn El-Walid"
__description__ = "Professional Corrosion Analysis Platform"

from .tafel_engine import TafelEngine
from .database import Database
from .theme import Theme

__all__ = ['TafelEngine', 'Database', 'Theme']