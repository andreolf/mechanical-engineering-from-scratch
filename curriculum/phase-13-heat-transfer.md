# Phase 13: Heat Transfer

*Wärmeübertragung*

Conduction, convection, radiation and heat exchangers derived and simulated.

- **ETH reference:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives
- **Real-world anchors:** Keeping a Bali house cool, an alpine hut warm, a CPU alive
- **Lessons:** 14

## 13.01 Conduction and Fourier's law

**Goal:** Derive heat flux from temperature gradients

- **Derive by hand:** q = -k grad T
- **Code from scratch:** 1D steady conduction through a wall
- **Interactive lab:** Wall with thermal conductivity slider
- **Test that proves it:** Linear profile in homogeneous wall
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.02 Thermal resistance networks

**Goal:** Analyse layered walls like circuits

- **Derive by hand:** R = L/(k A), series and parallel
- **Code from scratch:** Wall resistance network solver
- **Interactive lab:** Insulation layer builder for an alpine hut
- **Test that proves it:** Heat flow equals delta T / R_total
- **Pro tool:** Python
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.03 Cylindrical and spherical conduction

**Goal:** Insulate pipes correctly

- **Derive by hand:** R = ln(r2/r1)/(2 pi k L), critical radius
- **Code from scratch:** Critical insulation radius calculator
- **Interactive lab:** Pipe insulation thickness slider
- **Test that proves it:** Critical radius = k/h
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.04 Fins

**Goal:** Cool engines and electronics

- **Derive by hand:** Fin equation m^2 = h P/(k A), efficiency
- **Code from scratch:** Fin temperature profile solver
- **Interactive lab:** Fin length slider
- **Test that proves it:** Long fin heat rate sqrt(h P k A) theta_b
- **Pro tool:** SciPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.05 Transient conduction: lumped

**Goal:** Decide when lumped models work

- **Derive by hand:** Biot number, exponential cooling
- **Code from scratch:** Lumped cooling of a coconut in a fridge (stated assumptions)
- **Interactive lab:** Biot slider with validity warning
- **Test that proves it:** Valid when Bi < 0.1
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.06 Transient conduction: distributed

**Goal:** Solve heating of thick bodies

- **Derive by hand:** Heat equation, Heisler-style solutions
- **Code from scratch:** 1D/2D transient conduction FD solver
- **Interactive lab:** Temperature heat-map animation
- **Test that proves it:** Converges to analytic series
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.07 Convection fundamentals

**Goal:** Understand h and the boundary layer

- **Derive by hand:** Nusselt number, thermal boundary layer
- **Code from scratch:** Compute h from Nu correlations
- **Interactive lab:** Flow speed slider over a plate
- **Test that proves it:** Laminar plate Nu ~ Re^(1/2) Pr^(1/3)
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.08 Forced convection correlations

**Goal:** Use correlations responsibly

- **Derive by hand:** Dittus-Boelter, Gnielinski (range of validity)
- **Code from scratch:** Correlation library with validity checks
- **Interactive lab:** Pipe flow heat-transfer calculator
- **Test that proves it:** Raises warning outside validity range
- **Pro tool:** ht (Python package)
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.09 Natural convection

**Goal:** Model hot plates and room air

- **Derive by hand:** Grashof, Rayleigh, Boussinesq approximation
- **Code from scratch:** Natural convection h on a vertical plate
- **Interactive lab:** Rayleigh slider
- **Test that proves it:** Transition near Ra ~ 1e9 (typical criterion)
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.10 Radiation

**Goal:** Compute radiative exchange

- **Derive by hand:** Stefan-Boltzmann, emissivity, view factors
- **Code from scratch:** View factor by Monte Carlo ray casting
- **Interactive lab:** Tropical roof vs reflective paint
- **Test that proves it:** Parallel plates view factor approaches 1 when large
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.11 Solar energy

**Goal:** Model solar gain in Bali vs Zurich

- **Derive by hand:** Solar geometry, irradiance on tilted planes
- **Code from scratch:** Solar position and panel yield model with labelled inputs
- **Interactive lab:** Sun path visual for both locations
- **Test that proves it:** Noon elevation matches 90 - latitude + declination
- **Pro tool:** pvlib
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.12 Heat exchangers: LMTD

**Goal:** Size heat exchangers

- **Derive by hand:** Log-mean temperature difference
- **Code from scratch:** LMTD design calculator
- **Interactive lab:** Parallel vs counterflow profiles
- **Test that proves it:** Counterflow needs less area for same duty
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.13 Heat exchangers: effectiveness-NTU

**Goal:** Rate exchangers when outlets are unknown

- **Derive by hand:** epsilon-NTU relations
- **Code from scratch:** epsilon-NTU solver
- **Interactive lab:** NTU slider
- **Test that proves it:** Same result as LMTD when outlets known
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.14 Electronics and battery cooling

**Goal:** Apply everything to a real thermal design

- **Derive by hand:** Thermal network + convection + radiation
- **Code from scratch:** Thermal model of an e-bike battery pack
- **Interactive lab:** Load profile with temperature trace
- **Test that proves it:** Steady state consistent with resistance network
- **Pro tool:** Python
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives
