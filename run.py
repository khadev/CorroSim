#!/usr/bin/env python3
"""Simple launcher for CorroSim"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.dirname(__file__))

from corrosim.main import main

if __name__ == "__main__":
    main()