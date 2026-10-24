# Phase 06: Strength of Materials (Deformable Solids)

*Mechanik 2: Deformierbare Festkörper*

Stress, strain, beams, torsion, buckling and energy methods: how parts deform and when they fail.

- **ETH reference:** Mechanik 2 (Deformable Solids)
- **Real-world anchors:** Bike frames, Swiss rail tracks, bamboo beams in Bali
- **Lessons:** 22

## 06.01 Stress

**Goal:** Understand stress as force per area on a cut

- **Derive by hand:** Cauchy stress vector t = sigma n
- **Code from scratch:** Compute traction on any plane from a stress tensor
- **Interactive lab:** Rotate a cutting plane and see traction
- **Test that proves it:** Traction equals sigma.n
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.02 Strain

**Goal:** Measure deformation

- **Derive by hand:** Small strain epsilon = (grad u + grad u^T)/2
- **Code from scratch:** Strain from a displacement field on a grid
- **Interactive lab:** Deforming grid with strain colouring
- **Test that proves it:** Rigid rotation produces zero small strain at first order
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.03 Hooke's law

**Goal:** Relate stress and strain

- **Derive by hand:** Isotropic elasticity with E, nu; Lame constants
- **Code from scratch:** 3D Hooke's law in matrix (Voigt) form
- **Interactive lab:** Stress-strain slider for steel, aluminium, bamboo
- **Test that proves it:** Uniaxial test returns E and lateral contraction nu
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.04 Axial bars

**Goal:** Compute stretch of rods and cables

- **Derive by hand:** delta = N L/(E A)
- **Code from scratch:** Stepped bar elongation solver
- **Interactive lab:** Rod with load and area sliders
- **Test that proves it:** Matches closed form for stepped bar
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.05 Statically indeterminate bars

**Goal:** Use compatibility when statics is not enough

- **Derive by hand:** Equilibrium + compatibility + constitutive law
- **Code from scratch:** Solve a bar fixed at both ends with a midpoint load
- **Interactive lab:** Wall reactions as load moves
- **Test that proves it:** Reactions sum to applied load
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.06 Thermal stress

**Goal:** Predict stress from temperature change

- **Derive by hand:** epsilon_th = alpha delta T
- **Code from scratch:** Compute stress in a constrained rail on a hot day
- **Interactive lab:** Rail temperature slider with buckling warning
- **Test that proves it:** Stress = -E alpha delta T for fully constrained bar
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.07 Stress transformation and Mohr's circle

**Goal:** Find principal stresses and max shear

- **Derive by hand:** Rotation of 2D stress; Mohr's circle
- **Code from scratch:** Mohr's circle generator
- **Interactive lab:** Rotate element and track point on Mohr's circle
- **Test that proves it:** Principal stresses equal eigenvalues of sigma
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.08 Failure criteria

**Goal:** Decide if a part yields

- **Derive by hand:** Tresca, von Mises; distortion energy derivation
- **Code from scratch:** von Mises and Tresca calculators
- **Interactive lab:** Yield surfaces in principal stress space
- **Test that proves it:** Pure shear yields at tau = sigma_y/sqrt(3) under von Mises
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.09 Beam bending: Euler-Bernoulli

**Goal:** Derive the bending stress formula

- **Derive by hand:** Plane sections remain plane; sigma = M y / I
- **Code from scratch:** Bending stress field over a cross-section
- **Interactive lab:** Cantilever with draggable load and stress colours ([Cantilever beam (hero)](#hero))
- **Test that proves it:** Max stress equals M c / I
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.10 Second moment of area

**Goal:** Pick efficient cross-sections

- **Derive by hand:** I = int y^2 dA; parallel axis theorem
- **Code from scratch:** Section property calculator for I, T, box, tube
- **Interactive lab:** Compare sections at equal mass
- **Test that proves it:** I-section beats rectangle at equal area
- **Pro tool:** sectionproperties
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.11 Beam deflection

**Goal:** Compute how far a beam bends

- **Derive by hand:** EI w'''' = q, boundary conditions
- **Code from scratch:** Integrate the beam equation numerically and symbolically
- **Interactive lab:** Live deflected shape vs load position
- **Test that proves it:** Cantilever tip deflection equals PL^3/(3EI)
- **Pro tool:** SymPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.12 Superposition and indeterminate beams

**Goal:** Solve continuous beams

- **Derive by hand:** Superposition of standard cases + compatibility
- **Code from scratch:** Propped cantilever via superposition
- **Interactive lab:** Support removal to see moment redistribution
- **Test that proves it:** Prop reaction under uniform load q equals 3qL/8
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.13 Shear stress in beams

**Goal:** Find where shear peaks

- **Derive by hand:** Jourawski formula tau = V Q /(I b)
- **Code from scratch:** Shear distribution over rectangular and I sections
- **Interactive lab:** Shear profile plot by section
- **Test that proves it:** Rectangle max shear equals 1.5 V/A
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.14 Torsion of circular shafts

**Goal:** Size a drive shaft

- **Derive by hand:** tau = T r / J, phi = T L /(G J)
- **Code from scratch:** Shaft stress and twist calculator
- **Interactive lab:** Twisting shaft with rotating grid lines
- **Test that proves it:** Hollow shaft J matches pi(D^4-d^4)/32
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.15 Thin-walled torsion

**Goal:** Analyse bike frame tubes and boxes

- **Derive by hand:** Bredt-Batho shear flow q = T/(2A_m)
- **Code from scratch:** Torsional stiffness of closed vs open sections
- **Interactive lab:** Slit tube comparison
- **Test that proves it:** Open section dramatically less stiff than closed
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.16 Combined loading

**Goal:** Superpose axial, bending and torsion

- **Derive by hand:** Superposition then von Mises
- **Code from scratch:** Check a crank arm under pedalling load
- **Interactive lab:** Pedal force slider with stress hotspot
- **Test that proves it:** Hotspot location matches hand analysis
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.17 Strain energy

**Goal:** Use energy to compute deflections

- **Derive by hand:** U = int sigma epsilon /2 dV
- **Code from scratch:** Strain energy of bar, beam, shaft
- **Interactive lab:** Energy bar chart per load type
- **Test that proves it:** Energy equals work of external load P delta/2
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.18 Castigliano's theorem

**Goal:** Find deflections from energy derivatives

- **Derive by hand:** delta_i = dU/dP_i
- **Code from scratch:** Deflection of a curved bar (bike hook)
- **Interactive lab:** Load point selector
- **Test that proves it:** Matches direct integration
- **Pro tool:** SymPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.19 Buckling of columns

**Goal:** Predict when slender members fail suddenly

- **Derive by hand:** Euler buckling P_cr = pi^2 E I/(K L)^2
- **Code from scratch:** Eigenvalue solution of discretised column
- **Interactive lab:** Compress a column until it snaps sideways
- **Test that proves it:** Discrete critical load converges to Euler
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.20 Imperfections and real buckling

**Goal:** Understand why real columns fail below Euler

- **Derive by hand:** Imperfect column amplification 1/(1 - P/P_cr)
- **Code from scratch:** Imperfect column load-deflection curve
- **Interactive lab:** Imperfection slider
- **Test that proves it:** Deflection grows without bound as P approaches P_cr
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.21 Pressure vessels

**Goal:** Size a tank or pipe wall

- **Derive by hand:** Thin wall: sigma_hoop = p r / t, sigma_axial = p r/(2t)
- **Code from scratch:** Penstock wall thickness calculator for an alpine hydro plant
- **Interactive lab:** Pressure slider with hoop stress
- **Test that proves it:** Hoop stress is twice axial stress
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.22 Stress concentrations

**Goal:** Understand why parts crack at holes and fillets

- **Derive by hand:** Kirsch solution: K_t = 3 for a hole in a plate
- **Code from scratch:** Plot Kirsch stress field around a hole
- **Interactive lab:** Plate with hole stress heat-map
- **Test that proves it:** Peak stress equals 3 times remote stress
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)
