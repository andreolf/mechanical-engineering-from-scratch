# Phase 09: Materials & Manufacturing

*Werkstoffe und Fertigung*

Atoms to alloys to finished parts: why materials behave as they do and how things are made.

- **ETH reference:** Werkstoffe und Fertigung; Engineering Design and Material Selection
- **Real-world anchors:** Swiss watch steels, aluminium bike frames, Bali bamboo and teak; Swiss precision machining, Bali bamboo workshops, a maker space 3D printer
- **Lessons:** 30

## 09.01 Atomic bonding and stiffness

**Goal:** Explain where Young's modulus comes from

- **Derive by hand:** Lennard-Jones potential, stiffness = curvature at minimum
- **Code from scratch:** Derive E from a pair potential
- **Interactive lab:** Interatomic potential with draggable atoms
- **Test that proves it:** Stiffness equals second derivative at r0
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.02 Crystal structures

**Goal:** Recognise FCC, BCC, HCP

- **Derive by hand:** Packing factor, coordination numbers
- **Code from scratch:** Generate lattices and compute packing factor
- **Interactive lab:** 3D lattice viewer
- **Test that proves it:** FCC packing factor = 0.74
- **Pro tool:** ASE
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.03 Defects and dislocations

**Goal:** Explain why metals are ductile

- **Derive by hand:** Theoretical vs real shear strength
- **Code from scratch:** Estimate ideal shear strength G/(2 pi)
- **Interactive lab:** Dislocation glide animation
- **Test that proves it:** Ideal strength orders of magnitude above measured
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.04 The tensile test

**Goal:** Read a stress-strain curve

- **Derive by hand:** Engineering vs true stress, necking (Considere)
- **Code from scratch:** Process raw tensile data: E, yield (0.2%), UTS
- **Interactive lab:** Interactive tensile curve
- **Test that proves it:** 0.2% offset yield correctly extracted
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.05 Hardening mechanisms

**Goal:** Make metals stronger

- **Derive by hand:** Hall-Petch, solid solution, precipitation
- **Code from scratch:** Fit Hall-Petch to grain-size data
- **Interactive lab:** Grain size slider
- **Test that proves it:** Fitted slope recovers synthetic constant
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.06 Phase diagrams

**Goal:** Read alloy phase diagrams

- **Derive by hand:** Lever rule
- **Code from scratch:** Lever-rule calculator for a binary diagram
- **Interactive lab:** Click a point, get phase fractions
- **Test that proves it:** Fractions sum to 1
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.07 Steel and heat treatment

**Goal:** Understand quench, temper and the iron-carbon diagram

- **Derive by hand:** Fe-C diagram, TTT curves qualitative
- **Code from scratch:** Phase fraction tool for plain carbon steel
- **Interactive lab:** Cooling-rate slider over TTT sketch
- **Test that proves it:** Eutectoid composition near 0.76% C (textbook value)
- **Pro tool:** Thermo-Calc concepts (open: pycalphad)
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.08 Diffusion

**Goal:** Model carburising and drying

- **Derive by hand:** Fick's laws, erf solution
- **Code from scratch:** Solve carburising depth
- **Interactive lab:** Concentration profile over time
- **Test that proves it:** Depth grows with sqrt(D t)
- **Pro tool:** SciPy special.erf
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.09 Polymers

**Goal:** Understand viscoelastic behaviour

- **Derive by hand:** Maxwell and Kelvin-Voigt models
- **Code from scratch:** Simulate creep and relaxation
- **Interactive lab:** Spring-dashpot builder
- **Test that proves it:** Maxwell relaxes exponentially with tau = eta/E
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.10 Composites

**Goal:** Design with fibres

- **Derive by hand:** Rule of mixtures (Voigt/Reuss bounds)
- **Code from scratch:** Laminate stiffness for a carbon bike frame ply
- **Interactive lab:** Fibre angle slider
- **Test that proves it:** Longitudinal modulus follows Voigt bound
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.11 Natural materials: bamboo and wood

**Goal:** Engineer with Bali bamboo responsibly

- **Derive by hand:** Anisotropy, graded fibre density
- **Code from scratch:** Bending stiffness of a hollow bamboo culm
- **Interactive lab:** Culm wall thickness slider
- **Test that proves it:** Hollow culm stiffness-to-weight beats solid rod
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.12 Fracture mechanics

**Goal:** Predict crack growth

- **Derive by hand:** Griffith energy balance, K_I = Y sigma sqrt(pi a)
- **Code from scratch:** Critical crack size calculator
- **Interactive lab:** Crack length slider with fracture threshold
- **Test that proves it:** Fracture when K_I >= K_IC
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.13 Fatigue

**Goal:** Design parts that survive millions of cycles

- **Derive by hand:** S-N curves, Basquin, Goodman mean-stress correction
- **Code from scratch:** Goodman diagram and life estimate
- **Interactive lab:** Load-cycle slider on a crank
- **Test that proves it:** Infinite life inside the Goodman line
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.14 Corrosion

**Goal:** Keep alpine and tropical structures alive

- **Derive by hand:** Galvanic series, Faraday's law for corrosion rate
- **Code from scratch:** Corrosion rate from current density
- **Interactive lab:** Galvanic couple picker
- **Test that proves it:** Rate proportional to current
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.15 Material selection charts

**Goal:** Choose materials systematically

- **Derive by hand:** Performance indices, e.g. E^(1/2)/rho for light stiff beams
- **Code from scratch:** Ashby-style chart from an open dataset you assemble
- **Interactive lab:** Interactive selection line
- **Test that proves it:** Index ranking matches derivation
- **Pro tool:** Matplotlib
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.16 Sustainability and embodied energy

**Goal:** Compare materials by footprint

- **Derive by hand:** Life-cycle energy = mass * embodied energy per kg
- **Code from scratch:** Compare frame materials using cited data you collect
- **Interactive lab:** Material footprint bars
- **Test that proves it:** Totals reproduce input data
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.17 Manufacturing process map

**Goal:** Pick the right process family

- **Derive by hand:** Process selection by volume, material, tolerance
- **Code from scratch:** Process selector rule engine
- **Interactive lab:** Interactive process map
- **Test that proves it:** Selector reproduces textbook examples
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.18 Metal cutting mechanics

**Goal:** Understand chip formation

- **Derive by hand:** Merchant's circle, shear angle
- **Code from scratch:** Cutting force model
- **Interactive lab:** Rake angle slider
- **Test that proves it:** Force decreases with rake angle in the model
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.19 Tool life and economics

**Goal:** Choose cutting speeds

- **Derive by hand:** Taylor tool life V T^n = C, cost minimisation
- **Code from scratch:** Optimal cutting speed calculator
- **Interactive lab:** Cost vs speed curve
- **Test that proves it:** Optimum where derivative is zero
- **Pro tool:** SciPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.20 CNC and G-code

**Goal:** Turn geometry into toolpaths

- **Derive by hand:** Toolpath offsets, interpolation
- **Code from scratch:** Write a G-code generator for a 2D pocket
- **Interactive lab:** G-code toolpath simulator
- **Test that proves it:** Toolpath stays inside boundary with tool radius offset
- **Pro tool:** FreeCAD Path / CAM
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.21 Turning and milling

**Goal:** Compute feeds, speeds and surface finish

- **Derive by hand:** Ra ~ f^2/(32 r)
- **Code from scratch:** Surface roughness estimator
- **Interactive lab:** Feed slider with surface profile
- **Test that proves it:** Roughness scales with feed squared
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.22 Sheet metal forming

**Goal:** Bend sheet without cracking

- **Derive by hand:** Bend allowance, springback
- **Code from scratch:** Flat pattern calculator
- **Interactive lab:** Bend angle slider
- **Test that proves it:** Bend allowance formula satisfied
- **Pro tool:** FreeCAD SheetMetal
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.23 Bulk forming

**Goal:** Understand forging and extrusion

- **Derive by hand:** Slab method, flow stress
- **Code from scratch:** Extrusion force estimate
- **Interactive lab:** Ram speed and ratio sliders
- **Test that proves it:** Force increases with extrusion ratio
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.24 Casting

**Goal:** Design castings that solidify soundly

- **Derive by hand:** Chvorinov's rule t = B (V/A)^n
- **Code from scratch:** Riser sizing tool
- **Interactive lab:** Solidification order animation
- **Test that proves it:** Riser solidifies after casting
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.25 Injection moulding

**Goal:** Understand plastic part design

- **Derive by hand:** Fill pressure, cooling time ~ thickness^2
- **Code from scratch:** Cooling time estimator
- **Interactive lab:** Wall thickness slider
- **Test that proves it:** Time scales with thickness squared
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.26 Welding and joining physics

**Goal:** Control heat input

- **Derive by hand:** Rosenthal moving heat source (simplified)
- **Code from scratch:** Weld pool temperature field
- **Interactive lab:** Torch speed slider
- **Test that proves it:** Peak temperature decreases with speed
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.27 Additive manufacturing

**Goal:** Print functional parts

- **Derive by hand:** Layer adhesion, anisotropy, overhang angles
- **Code from scratch:** Slicer from scratch: slice an STL into layers and perimeters
- **Interactive lab:** Layer-by-layer preview
- **Test that proves it:** Sliced area matches cross-section area
- **Pro tool:** PrusaSlicer / CuraEngine
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.28 Metrology on the shop floor

**Goal:** Measure what you make

- **Derive by hand:** Measurement uncertainty, Abbe principle
- **Code from scratch:** Uncertainty budget for a caliper measurement
- **Interactive lab:** Abbe error visual
- **Test that proves it:** Combined uncertainty via root sum of squares
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.29 Quality and statistical process control

**Goal:** Keep processes in control

- **Derive by hand:** Control charts, Cp and Cpk
- **Code from scratch:** SPC chart generator
- **Interactive lab:** Process drift simulation
- **Test that proves it:** Cpk computed correctly on synthetic data
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.30 Building with bamboo

**Goal:** Apply manufacturing thinking to natural materials

- **Derive by hand:** Joint strength, treatment, variability
- **Code from scratch:** Statistical design value from bamboo test data you gather
- **Interactive lab:** Joint type comparison
- **Test that proves it:** 5th-percentile design value computed
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection
