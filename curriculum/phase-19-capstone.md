# Phase 19: Capstone Projects

*Fokus-Projekt / Bachelor-Arbeit style capstone*

Integrate everything: derive, simulate, build, measure and publish a working machine or study.

- **ETH reference:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)
- **Real-world anchors:** Real projects in Bali and Switzerland, each with a public artifact
- **Lessons:** 10

## 19.01 Capstone method

**Goal:** Plan a project that ends with evidence

- **Derive by hand:** Requirements, risk, verification matrix
- **Code from scratch:** Project template repo with verification matrix
- **Interactive lab:** Gantt and risk board
- **Test that proves it:** Every requirement has a test
- **Pro tool:** git, Quarto
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.02 Coconut eddy: from field video to CFD

**Goal:** Reproduce the Bali boulder eddy

- **Derive by hand:** Strouhal, recirculation, particle residence time
- **Code from scratch:** Combine video particle tracking with your CFD solver
- **Interactive lab:** Coconut lab extended ([The coconut that never escapes](https://andreolf.github.io/coconut-lab/))
- **Test that proves it:** Model residence time compared with your measurement, discrepancy explained
- **Pro tool:** OpenFOAM, OpenCV
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.03 Subak weir network

**Goal:** Model a full terrace water-sharing network

- **Derive by hand:** Weir equations + network mass balance
- **Code from scratch:** Network simulator with seasonal inflow assumptions
- **Interactive lab:** Subak lab extended ([Subak rice terraces](https://andreolf.github.io/subak-lab/))
- **Test that proves it:** Mass balance closes at every terrace
- **Pro tool:** NumPy, EPANET concepts
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.04 Bamboo footbridge

**Goal:** Design and analyse a small bamboo footbridge

- **Derive by hand:** Truss/frame FEM, vibration comfort checks (educational)
- **Code from scratch:** Full design calculation in your FEM
- **Interactive lab:** Break-the-bridge lab with bamboo properties ([Break the bridge](#lab-truss))
- **Test that proves it:** Safety factors computed and documented; not a substitute for a licensed engineer
- **Pro tool:** FEniCSx / CalculiX
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.05 Micro-hydro turbine for a village

**Goal:** Size a Pelton or crossflow turbine

- **Derive by hand:** Euler turbine equation, penstock losses
- **Code from scratch:** Turbine sizing tool
- **Interactive lab:** Head and flow sliders
- **Test that proves it:** Power within efficiency bounds
- **Pro tool:** Python, FreeCAD
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.06 Alpine pumped-storage study

**Goal:** Evaluate a pumped-storage scheme

- **Derive by hand:** Energy, hydraulics, water hammer
- **Code from scratch:** Integrated model with stated assumptions
- **Interactive lab:** Reservoir operation animation
- **Test that proves it:** Energy balance closes
- **Pro tool:** Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.07 E-bike drivetrain

**Goal:** Design a hub gearbox and its thermal limits

- **Derive by hand:** Planetary gears, bearing life, heat transfer
- **Code from scratch:** Integrated drivetrain calculation
- **Interactive lab:** Drivetrain configurator
- **Test that proves it:** All elements pass life/strength checks in the model
- **Pro tool:** CadQuery, Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.08 Flywheel energy store

**Goal:** Design a safe small flywheel

- **Derive by hand:** Rotor stress, bearings, containment
- **Code from scratch:** Flywheel design report
- **Interactive lab:** Flywheel lab ([Gyroscope & flywheel](#lab-flywheel))
- **Test that proves it:** Burst margin documented
- **Pro tool:** FreeCAD, CalculiX
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.09 Wind-loaded structure

**Goal:** Analyse a sign or small tower

- **Derive by hand:** Wind load, vortex shedding, fatigue
- **Code from scratch:** Coupled analysis pipeline
- **Interactive lab:** Wind lab
- **Test that proves it:** Fatigue life estimate reported with assumptions
- **Pro tool:** Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.10 Publish your artifact

**Goal:** Ship it like open source

- **Derive by hand:** Licensing, reproducibility, documentation
- **Code from scratch:** Publish repo, README, and an interactive web lab
- **Interactive lab:** Your own Break-the-machine page
- **Test that proves it:** Fresh clone reproduces all figures
- **Pro tool:** GitHub Pages, three.js
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)
