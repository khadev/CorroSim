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
---

**Author:** Oukil Khaled ibn El-walid  
**ORCID:** 0000-0002-6915-4548  
**Affiliation:** Independent Researcher, Algeria  
**Email:** oukil.khaled@gmail.com

# Summary

CorroSim is a free, open-source, multi-module desktop application for electrochemical corrosion analysis. It integrates eight professional modules—Tafel polarization, electrochemical impedance spectroscopy (EIS), galvanic simulation, pitting analysis, inhibitor efficiency, lifetime prediction, sample comparison, and data import—within a single cross-platform Python/PyQt6 application.

Validation against synthetic datasets with known ground-truth parameters demonstrates high quantitative fidelity: Tafel analysis recovered the corrosion potential within 0.4% and corrosion current density within 5.0% (R² = 0.9996); EIS fitting of a Randles circuit yielded solution resistance and charge-transfer resistance errors below 0.1% with an overall R² = 0.9999; and galvanic simulations correctly predicted polarity and severity for three dissimilar-metal couples with 100% concordance to the ASTM G82 galvanic series.

CorroSim is distributed via the Python Package Index (`pip install corrosim`) under the MIT license and supports English and French interfaces. The source code is on GitHub at https://github.com/khadev/CorroSim.

# Statement of Need

Electrochemical corrosion analysis is essential for materials selection and structural integrity assessment across aerospace, marine, and energy sectors. Commercial tools like ZView, Gamry, Nova, and ZSimpWin are expensive, closed-source, and single-technique. Open-source alternatives are fragmented. CorroSim fills this gap as a free, integrated, multi-module platform.

# Features

1. **Tafel Analysis**: Extracts Ecorr, icorr, and Tafel slopes using Butler-Volmer kinetics (Stern & Geary, 1957; Tafel, 1905). Corrosion rate via Faraday's law per ASTM G102.

2. **EIS Fitting**: Fits impedance spectra to Randles, Randles-CPE, and Randles-Warburg circuits using weighted CNLS (Randles, 1947; Orazem & Tribollet, 2017).

3. **Galvanic Simulation**: Predicts galvanic corrosion using mixed-potential theory and ASTM G82 database (ASTM G82, 2021).

4. **Pitting Analysis**: Estimates pitting potential per ASTM G61 (ASTM G61, 2018).

5. **Inhibitor Efficiency**: Calculates IE% and fits Langmuir/Freundlich isotherms (Langmuir, 1918).

6. **Lifetime Prediction, Sample Comparison, Data Import**

# Validation

- **Tafel**: Ecorr within 0.4%, icorr within 5.0% (R² = 0.9996)
- **EIS**: Rs and Rct within 0.1% (R² = 0.9999)
- **Galvanic**: 100% match with ASTM G82 for three couples

# Availability

CorroSim is available on PyPI (`pip install corrosim`) and GitHub (https://github.com/khadev/CorroSim) under the MIT license. Requires Python 3.8+.

# Acknowledgements

The author declares no acknowledgements.

# References

1. Stern, M., & Geary, A. L. (1957). Electrochemical polarization. *Journal of the Electrochemical Society*, 104(1), 56-63.
2. Tafel, J. (1905). Über die Polarisation bei kathodischer Wasserstoffentwicklung. *Zeitschrift für Physikalische Chemie*, 50(1), 641-712.
3. Bard, A. J., & Faulkner, L. R. (2001). *Electrochemical Methods* (2nd ed.). Wiley.
4. Orazem, M. E., & Tribollet, B. (2017). *Electrochemical Impedance Spectroscopy* (2nd ed.). Wiley.
5. Randles, J. E. B. (1947). Kinetics of rapid electrode reactions. *Discussions of the Faraday Society*, 1, 11-19.
6. ASTM G82-98(2021). Standard Guide for Galvanic Series. ASTM International.
7. ASTM G61-86(2018). Standard Test Method for Cyclic Polarization. ASTM International.
8. ASTM G102-89(2015). Standard Practice for Calculation of Corrosion Rates. ASTM International.
9. Langmuir, I. (1918). The adsorption of gases on plane surfaces. *Journal of the American Chemical Society*, 40(9), 1361-1403.
10. Hack, H. P. (1988). *Galvanic Corrosion*. ASTM International.