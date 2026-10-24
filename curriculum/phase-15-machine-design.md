# Phase 15: Machine Elements & Design

*Maschinenkonstruktion / Dimensionierung*

Dimensioning shafts, bearings, gears, bolts and welds: from load to safe, buildable part.

- **ETH reference:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses
- **Real-world anchors:** Bike drivetrains, ski-lift grips, Swiss watch gears, a Bali scooter
- **Lessons:** 18

## 15.01 The design process

**Goal:** Go from need to concept to detail

- **Derive by hand:** Requirements, morphological box, evaluation matrix
- **Code from scratch:** Weighted decision matrix tool
- **Interactive lab:** Concept scoring board
- **Test that proves it:** Ranking reproducible from weights
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.02 Safety factors and reliability

**Goal:** Pick safety factors with reasons

- **Derive by hand:** Stress-strength interference, reliability index
- **Code from scratch:** Monte Carlo failure probability
- **Interactive lab:** Overlapping distributions
- **Test that proves it:** Analytical normal-normal result matched
- **Pro tool:** SciPy stats
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.03 Tolerances and fits

**Goal:** Make parts that assemble

- **Derive by hand:** ISO fits, tolerance stack-up (worst case vs RSS)
- **Code from scratch:** Stack-up calculator
- **Interactive lab:** Stack chain visual
- **Test that proves it:** RSS <= worst case
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.04 Shaft design

**Goal:** Size shafts for strength and fatigue

- **Derive by hand:** Combined bending-torsion, Goodman-based shaft equations
- **Code from scratch:** Shaft diameter calculator
- **Interactive lab:** Load layout editor
- **Test that proves it:** Larger safety factor yields larger diameter
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.05 Keys, splines and press fits

**Goal:** Transmit torque from hub to shaft

- **Derive by hand:** Lame thick-cylinder equations for interference
- **Code from scratch:** Press-fit pressure and torque capacity
- **Interactive lab:** Interference slider
- **Test that proves it:** Contact pressure matches Lame solution
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.06 Rolling bearings

**Goal:** Choose bearings by life

- **Derive by hand:** L10 = (C/P)^p with p = 3 for ball bearings
- **Code from scratch:** Bearing life calculator
- **Interactive lab:** Load vs life curve
- **Test that proves it:** Doubling load cuts life by factor 8
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.07 Plain bearings and lubrication

**Goal:** Understand hydrodynamic lubrication

- **Derive by hand:** Reynolds equation for thin films
- **Code from scratch:** 1D Reynolds equation solver for a slider bearing
- **Interactive lab:** Pressure build-up in a wedge
- **Test that proves it:** Load capacity positive only for converging wedge
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.08 Gear geometry

**Goal:** Understand involute gears

- **Derive by hand:** Involute curve, base circle, law of gearing
- **Code from scratch:** Generate involute profiles
- **Interactive lab:** Meshing gear animation
- **Test that proves it:** Constant velocity ratio along line of action
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.09 Gear strength

**Goal:** Size gears against bending and pitting

- **Derive by hand:** Lewis bending equation, Hertz contact basics
- **Code from scratch:** Gear stress estimates
- **Interactive lab:** Module/face-width sliders
- **Test that proves it:** Stress decreases with module
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.10 Gear trains and planetary gears

**Goal:** Design transmissions

- **Derive by hand:** Willis equation for planetary sets
- **Code from scratch:** Planetary ratio solver
- **Interactive lab:** Animated planetary gearbox (e-bike hub)
- **Test that proves it:** Willis relation satisfied
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.11 Belts and chains

**Goal:** Design bike and conveyor drives

- **Derive by hand:** Chain kinematics, polygonal effect, belt tensions
- **Code from scratch:** Chain speed fluctuation calculator
- **Interactive lab:** Chainring tooth-count slider
- **Test that proves it:** Fluctuation decreases with tooth count
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.12 Bolted joints

**Goal:** Design joints that do not loosen

- **Derive by hand:** Joint diagram, preload, stiffness ratio
- **Code from scratch:** Bolted joint diagram tool
- **Interactive lab:** Preload slider
- **Test that proves it:** External load share follows stiffness ratio
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.13 Welded joints

**Goal:** Size welds

- **Derive by hand:** Throat stress, fatigue classes concept
- **Code from scratch:** Fillet weld stress calculator
- **Interactive lab:** Weld layout editor
- **Test that proves it:** Stress inversely proportional to throat size
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.14 Springs

**Goal:** Design helical springs

- **Derive by hand:** k = G d^4/(8 D^3 n), Wahl factor
- **Code from scratch:** Spring designer
- **Interactive lab:** Coil count slider
- **Test that proves it:** Stiffness matches formula
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.15 Clutches and brakes

**Goal:** Size friction devices

- **Derive by hand:** Uniform wear vs uniform pressure torque
- **Code from scratch:** Disc brake torque for a bike
- **Interactive lab:** Brake lever force slider
- **Test that proves it:** Uniform wear torque <= uniform pressure
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.16 Linkages and mechanisms

**Goal:** Synthesise motion

- **Derive by hand:** Freudenstein equation
- **Code from scratch:** Three-position linkage synthesis
- **Interactive lab:** Linkage designer
- **Test that proves it:** Synthesised linkage passes through targets
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.17 Ski-lift grip and cable design

**Goal:** Integrate elements on a Swiss anchor

- **Derive by hand:** Friction grip force, cable tension, safety factors
- **Code from scratch:** Detachable grip clamp force model (educational)
- **Interactive lab:** Slope and load sliders
- **Test that proves it:** Grip holds when friction capacity > slope component times SF
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.18 Design review and documentation

**Goal:** Ship designs others can build

- **Derive by hand:** Calculation reports, traceability
- **Code from scratch:** Auto-generate a calculation report from your Python modules
- **Interactive lab:** Report preview
- **Test that proves it:** Report reproduces all numbers from code
- **Pro tool:** Jupyter / Quarto
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses
