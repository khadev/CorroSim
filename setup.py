#!/usr/bin/env python3
"""Setup script for CorroSim"""

from setuptools import setup, find_packages

# Read requirements directly instead of from file
requirements = [
    "PyQt6>=6.5.0",
    "matplotlib>=3.7.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scipy>=1.10.0",
    "openpyxl>=3.1.0",
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="corrosim",
    version="1.5.1",
    license="MIT",
    description="A comprehensive desktop application with 8 professional modules: Tafel, Galvanic, EIS, Pitting, Inhibitor, Prediction, Comparison, and Data Import.",
    author="oukil khaled ibn El-walid",
    author_email="oukil.khaled@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/khadev/CorroSim",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "corrosim=corrosim.main:main",
        ],
    },
)