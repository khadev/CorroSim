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

Electrochemical corrosion analysis is essential for materials selection, protective-coating design, and structural integrity assessment across aerospace, marine, energy, and civil infrastructure sectors [@stern1957; @bard2001]. Despite this importance, access to integrated corrosion software is uneven. Established commercial packages—including ZView, Gamry Echem Analyst, Nova, and ZSimpWin—are powerful but limited by high licensing costs (hundreds to thousands of US dollars per seat), closed-source code, and single-technique specialization [@orazem2017].

Open-source electrochemical tools exist but are largely fragmented: individual Python scripts for Tafel fitting, standalone R packages for EIS, and web calculators for galvanic series lookup. None provide an integrated, validated, cross-platform desktop suite with a unified graphical interface, persistent database storage, and auditable source code.

CorroSim fills this gap by offering a single, freely available platform that combines multiple corrosion analysis techniques. Its MIT license guarantees unrestricted use, modification, and redistribution. The MVC architecture and modular design enable community contributions, while PyPI distribution ensures reproducible installation across operating systems. The target audience includes graduate students learning electrochemical kinetics, researchers validating coatings, and field engineers requiring rapid corrosion-rate estimates.

# Features

CorroSim provides eight integrated modules:

1. **Tafel Analysis**: Extracts corrosion potential (Ecorr), corrosion current density (icorr), and Tafel slopes (βa, βc) from potentiodynamic polarization data using Butler-Volmer kinetics. Corrosion rate is calculated via Faraday's law per ASTM G102 [@astm102].

2. **EIS Fitting**: Fits impedance spectra to equivalent circuit models (Randles, Randles-CPE, Randles-Warburg) using weighted complex nonlinear least squares. Supports Nyquist and Bode visualization.

3. **Galvanic Simulation**: Predicts galvanic corrosion between dissimilar metals using mixed-potential theory and an embedded ASTM G82 galvanic series database [@astm82].

4. **Pitting Analysis**: Estimates pitting potential and repassivation potential from cyclic polarization data per ASTM G61 [@astm61].

5. **Inhibitor Efficiency**: Calculates inhibition efficiency from corrosion rates and fits Langmuir and Freundlich adsorption isotherms.

6. **Lifetime Prediction**: Forecasts residual service life using power-law degradation models.

7. **Sample Comparison**: Enables batch ranking of multiple samples across computed metrics with export to Excel.

8. **Data Import**: Supports CSV and Excel file formats with automatic column detection.

# Validation

The numerical engines were validated against synthetic datasets with controlled noise:

- **Tafel**: Ecorr recovered within 0.4%, icorr within 5.0%, Tafel slopes within 2% (R² = 0.9996)
- **EIS**: Rs and Rct recovered within 0.1%, Cdl within 0.2% (R² = 0.9999)
- **Galvanic**: Three metal couples tested against ASTM G82 — 100% match rate for polarity and severity

All validation test scripts are included in the GitHub repository.

# Availability

CorroSim is available on PyPI (`pip install corrosim`) and GitHub (https://github.com/khadev/CorroSim) under the MIT license. It requires Python 3.8+ and runs on Windows, macOS, and Linux.

# Acknowledgements

The author declares no acknowledgements.

# References