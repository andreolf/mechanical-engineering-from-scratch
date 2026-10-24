# Phase 12: Fluid Dynamics 2: Viscous Flows, Turbulence, Aero

*Fluiddynamik (Teil 2)*

Boundary layers, drag, pipe losses, turbulence, compressible flow and aerodynamics.

- **ETH reference:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)
- **Real-world anchors:** A cyclist in the Swiss wind, Rhine turbulence, a kite over Bali
- **Lessons:** 18

## 12.01 Exact viscous solutions

**Goal:** Solve Couette, Poiseuille and Stokes problems

- **Derive by hand:** Reduced NS for parallel flows
- **Code from scratch:** Stokes first problem (impulsively started plate)
- **Interactive lab:** Growing diffusion layer
- **Test that proves it:** Layer grows as sqrt(nu t)
- **Pro tool:** SciPy special
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.02 Low-Reynolds flow

**Goal:** Understand micro-swimmers and settling

- **Derive by hand:** Stokes drag F = 6 pi mu R U
- **Code from scratch:** Settling velocity of sediment in a river
- **Interactive lab:** Particle size slider
- **Test that proves it:** Matches Stokes law at low Re
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.03 Boundary layers

**Goal:** Derive Prandtl's boundary layer idea

- **Derive by hand:** Scaling delta ~ x Re_x^(-1/2)
- **Code from scratch:** Solve the Blasius equation by shooting
- **Interactive lab:** Velocity profile along a plate
- **Test that proves it:** f''(0) approx 0.332
- **Pro tool:** SciPy solve_ivp
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.04 Separation

**Goal:** Explain why flow detaches behind a boulder

- **Derive by hand:** Adverse pressure gradient
- **Code from scratch:** Thwaites method for separation point
- **Interactive lab:** Cylinder with separation marker
- **Test that proves it:** Laminar separation predicted near 104-110 degrees (literature range)
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.05 Drag

**Goal:** Estimate drag on bodies

- **Derive by hand:** Pressure vs friction drag, C_D
- **Code from scratch:** Drag of a cyclist using C_D A
- **Interactive lab:** Riding position slider
- **Test that proves it:** Power scales with v^3
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.06 Lift and airfoils

**Goal:** Explain how wings work without myths

- **Derive by hand:** Kutta condition, thin airfoil theory C_L = 2 pi alpha
- **Code from scratch:** Thin airfoil lift slope calculator
- **Interactive lab:** Airfoil with angle-of-attack slider
- **Test that proves it:** Slope 2 pi per radian
- **Pro tool:** XFOIL
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.07 Panel methods

**Goal:** Compute pressure on arbitrary airfoils

- **Derive by hand:** Source/vortex panels
- **Code from scratch:** Vortex panel method from scratch
- **Interactive lab:** Pressure distribution plot
- **Test that proves it:** Matches thin airfoil theory at small angle
- **Pro tool:** XFOIL
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.08 Turbulence phenomenology

**Goal:** Understand chaotic flow

- **Derive by hand:** Energy cascade, Kolmogorov scales
- **Code from scratch:** Generate and analyse a synthetic turbulent signal
- **Interactive lab:** Energy spectrum with -5/3 guide
- **Test that proves it:** Kolmogorov length from dissipation formula
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.09 Reynolds averaging

**Goal:** Model turbulence for engineering

- **Derive by hand:** RANS, Reynolds stresses, closure problem
- **Code from scratch:** Compute Reynolds stresses from synthetic velocity data
- **Interactive lab:** Mean vs fluctuation decomposition
- **Test that proves it:** Fluctuation mean is zero
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.10 Turbulent pipe flow

**Goal:** Predict pressure losses in real pipes

- **Derive by hand:** Darcy-Weisbach, Colebrook equation
- **Code from scratch:** Solve Colebrook for friction factor
- **Interactive lab:** Moody chart generator
- **Test that proves it:** Laminar limit f = 64/Re
- **Pro tool:** fluids (Python package)
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.11 Pipe networks

**Goal:** Design water supply systems

- **Derive by hand:** Hardy Cross method
- **Code from scratch:** Solve a looped village water network
- **Interactive lab:** Network with flow arrows
- **Test that proves it:** Mass conserved at every node
- **Pro tool:** EPANET / WNTR
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.12 Pumps and systems

**Goal:** Match pumps to pipelines

- **Derive by hand:** Pump curve vs system curve, affinity laws
- **Code from scratch:** Operating point solver
- **Interactive lab:** Pump speed slider
- **Test that proves it:** Affinity laws scale flow linearly with speed
- **Pro tool:** fluids
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.13 Compressible flow basics

**Goal:** Understand speed of sound and Mach number

- **Derive by hand:** a = sqrt(k R T), stagnation properties
- **Code from scratch:** Isentropic relations calculator
- **Interactive lab:** Mach number slider
- **Test that proves it:** T0/T = 1 + (k-1)/2 Ma^2
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.14 Nozzles and choking

**Goal:** Design converging-diverging nozzles

- **Derive by hand:** Area-Mach relation
- **Code from scratch:** Nozzle flow solver with shock location
- **Interactive lab:** CD nozzle with back-pressure slider
- **Test that proves it:** Choked mass flow independent of back pressure
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.15 Normal shocks

**Goal:** Compute jumps across shocks

- **Derive by hand:** Rankine-Hugoniot relations
- **Code from scratch:** Normal shock calculator
- **Interactive lab:** Shock tube animation
- **Test that proves it:** Entropy increases across shock
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.16 Vortex shedding

**Goal:** Explain cable singing and bridge oscillations

- **Derive by hand:** Strouhal number St ~ 0.2
- **Code from scratch:** Shedding frequency for a ski-lift cable
- **Interactive lab:** Karman street visual
- **Test that proves it:** Frequency scales with U/D
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.17 Wind and buildings

**Goal:** Estimate wind loads

- **Derive by hand:** Dynamic pressure, gust factors (labelled simplification)
- **Code from scratch:** Wind load on a signboard
- **Interactive lab:** Wind speed slider
- **Test that proves it:** Load scales with v^2
- **Pro tool:** Python
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.18 Mixing and dispersion in rivers

**Goal:** Model pollutant spread in the Limmat

- **Derive by hand:** Advection-diffusion equation
- **Code from scratch:** Gaussian plume in a channel
- **Interactive lab:** Dye release lab
- **Test that proves it:** Total mass conserved
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)
