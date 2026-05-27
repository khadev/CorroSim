---
title: 'CorroSim: A Multi-Module Open-Source Platform for Electrochemical Corrosion Analysis Integrating Tafel, EIS, and Galvanic Predictions'
tags:
  - Python
  - electrochemistry
  - corrosion
  - Tafel analysis
  - electrochemical impedance spectroscopy
  - galvanic corrosion
  - open-source software
  - PyQt6
authors:
  - name: Oukil Khaled ibn El-walid
    orcid: 0000-0002-6915-4548
    affiliation: 1
affiliations:
  - name: Independent Researcher, Algeria
    index: 1
date: 26 May 2026
bibliography: paper.bib
---

# Summary

CorroSim is a free, open-source, multi-module desktop application for electrochemical corrosion analysis. It integrates eight professional modules—Tafel polarization, electrochemical impedance spectroscopy (EIS), galvanic simulation, pitting analysis, inhibitor efficiency, lifetime prediction, sample comparison, and data import—within a single cross-platform Python/PyQt6 application.

Validation against synthetic datasets with known ground-truth parameters demonstrates high quantitative fidelity: Tafel analysis recovered the corrosion potential within 0.4% and corrosion current density within 5.0% (R² = 0.9996); EIS fitting of a Randles circuit yielded solution resistance and charge-transfer resistance errors below 0.1% with an overall R² = 0.9999; and galvanic simulations correctly predicted polarity and severity for three dissimilar-metal couples with 100% concordance to the ASTM G82 galvanic series.

CorroSim is distributed via the Python Package Index (`pip install corrosim`) under the MIT license and supports English and French interfaces. The source code, documentation, and validation test scripts are publicly available on GitHub at https://github.com/khadev/CorroSim.

# Statement of Need

Electrochemical corrosion analysis is essential for materials selection, protective-coating design, and structural integrity assessment across aerospace, marine, energy, and civil infrastructure sectors [@stern1957; @bard2001]. Despite this importance, access to integrated corrosion software is uneven. Established commercial packages—including ZView, Gamry Echem Analyst, Nova, and ZSimpWin—are powerful but limited by high licensing costs, closed-source code, and single-technique specialization [@orazem2017].

Open-source electrochemical tools exist but are largely fragmented. None provide an integrated, validated, cross-platform desktop suite with a unified graphical interface. CorroSim fills this gap by offering a single, freely available platform that combines multiple corrosion analysis techniques under the MIT license.

# Features

1. **Tafel Analysis**: Extracts Ecorr, icorr, and Tafel slopes from polarization data using Butler-Volmer kinetics [@stern1957; @tafel1905]. Corrosion rate via Faraday's law per ASTM G102 [@astm102].

2. **EIS Fitting**: Fits impedance spectra to Randles, Randles-CPE, and Randles-Warburg circuits using weighted CNLS [@randles1947; @orazem2017].

3. **Galvanic Simulation**: Predicts galvanic corrosion using mixed-potential theory and ASTM G82 database [@astm82; @hack1988].

4. **Pitting Analysis**: Estimates pitting potential per ASTM G61 [@astm61].

5. **Inhibitor Efficiency**: Calculates IE% and fits Langmuir/Freundlich isotherms [@langmuir1918].

6. **Lifetime Prediction**, **Sample Comparison**, **Data Import**

# Validation

- **Tafel**: Ecorr within 0.4%, icorr within 5.0% (R² = 0.9996)
- **EIS**: Rs and Rct within 0.1% (R² = 0.9999)
- **Galvanic**: 100% match with ASTM G82 for three couples

# Availability

CorroSim is available on PyPI (`pip install corrosim`) and GitHub (https://github.com/khadev/CorroSim) under the MIT license. Requires Python 3.8+.

# Acknowledgements

The author declares no acknowledgements.

# References