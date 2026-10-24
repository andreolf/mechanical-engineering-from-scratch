# Phase 11: Fluid Dynamics 1: Foundations

*Fluiddynamik (Teil 1)*

Fluid statics, kinematics, conservation laws, Bernoulli, momentum and dimensional analysis.

- **ETH reference:** Fluiddynamik
- **Real-world anchors:** The Limmat, the Rhine Falls, a coconut in a Bali river eddy
- **Lessons:** 20

## 11.01 What is a fluid

**Goal:** Define fluids, viscosity and the continuum

- **Derive by hand:** Newton's law of viscosity tau = mu du/dy
- **Code from scratch:** Couette flow velocity profile
- **Interactive lab:** Shear between plates with speed slider
- **Test that proves it:** Linear profile for Newtonian fluid
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.02 Fluid statics

**Goal:** Compute pressure in still fluids

- **Derive by hand:** dp/dz = -rho g
- **Code from scratch:** Manometer and pressure-with-depth calculator
- **Interactive lab:** Manometer lab
- **Test that proves it:** Pressure at 10 m water approx 98 kPa gauge
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.03 Buoyancy and stability

**Goal:** Explain why a coconut floats and boats stay upright

- **Derive by hand:** Archimedes, metacentric height
- **Code from scratch:** Floating draft and metacentric height of a boat
- **Interactive lab:** Tilting hull with metacentre
- **Test that proves it:** Stable iff GM > 0
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.04 Flow kinematics

**Goal:** Describe flow fields

- **Derive by hand:** Eulerian vs Lagrangian, streamlines, pathlines, streaklines
- **Code from scratch:** Trace particles in an unsteady field
- **Interactive lab:** Streamline vs pathline toggle
- **Test that proves it:** Steady flow: all three coincide
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.05 Material derivative

**Goal:** Follow a fluid parcel

- **Derive by hand:** D/Dt = d/dt + u . grad
- **Code from scratch:** Compute material acceleration numerically
- **Interactive lab:** Particle acceleration arrows
- **Test that proves it:** Matches analytical example
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.06 Conservation of mass

**Goal:** Derive continuity

- **Derive by hand:** Reynolds transport theorem, div u = 0 for incompressible
- **Code from scratch:** Check divergence of discrete velocity fields
- **Interactive lab:** Pipe contraction with flow rate counter
- **Test that proves it:** Flow rate equal at all sections
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.07 Bernoulli's equation

**Goal:** Derive it and know when it lies

- **Derive by hand:** Euler equation along a streamline; assumptions
- **Code from scratch:** Venturi meter calculator
- **Interactive lab:** Pipe flow lab: change diameter, watch speed and pressure ([Pipe flow & Bernoulli](#lab-pipe))
- **Test that proves it:** Pressure drop matches Bernoulli in inviscid limit
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.08 Torricelli and draining tanks

**Goal:** Apply Bernoulli to outflow

- **Derive by hand:** v = sqrt(2 g h), quasi-steady assumption
- **Code from scratch:** Tank draining time
- **Interactive lab:** Draining tank animation
- **Test that proves it:** Time matches analytic for constant area
- **Pro tool:** SciPy
- **ETH course:** Fluiddynamik

## 11.09 Momentum theorem

**Goal:** Compute forces from flows

- **Derive by hand:** Control-volume momentum balance
- **Code from scratch:** Force on a pipe bend and on a jet hitting a plate
- **Interactive lab:** Jet deflector lab
- **Test that proves it:** Force equals mass flow times velocity change
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.10 Angular momentum and turbines

**Goal:** Derive Euler's turbine equation

- **Derive by hand:** Torque = m_dot (r2 c_u2 - r1 c_u1)
- **Code from scratch:** Pelton wheel power vs bucket speed
- **Interactive lab:** Pelton runner animation (alpine hydro)
- **Test that proves it:** Max power at bucket speed = jet speed/2 (ideal)
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.11 Dimensional analysis in fluids

**Goal:** Use Re, Fr, Ma, We

- **Derive by hand:** Buckingham Pi for drag
- **Code from scratch:** Compute Pi groups from a variable list
- **Interactive lab:** Re slider from honey to the Rhine
- **Test that proves it:** Same Pi groups as textbook
- **Pro tool:** SymPy
- **ETH course:** Fluiddynamik

## 11.12 Similarity and model testing

**Goal:** Scale a dam spillway model correctly

- **Derive by hand:** Froude similarity scaling laws
- **Code from scratch:** Scale factors for a 1:50 spillway model
- **Interactive lab:** Model vs prototype comparison
- **Test that proves it:** Velocity scales with sqrt(length scale)
- **Pro tool:** Python
- **ETH course:** Fluiddynamik

## 11.13 Navier-Stokes equations

**Goal:** Derive the governing equations

- **Derive by hand:** Cauchy momentum + Newtonian constitutive law
- **Code from scratch:** Symbolically verify an exact solution
- **Interactive lab:** Term-by-term equation explorer
- **Test that proves it:** Poiseuille solution satisfies NS
- **Pro tool:** SymPy
- **ETH course:** Fluiddynamik

## 11.14 Laminar pipe flow

**Goal:** Solve Hagen-Poiseuille

- **Derive by hand:** Parabolic profile, Q = pi R^4 dp/(8 mu L)
- **Code from scratch:** Profile and flow rate calculator
- **Interactive lab:** Pipe profile animation
- **Test that proves it:** Mean velocity equals half max
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.15 Vorticity and circulation

**Goal:** Understand rotation in flows

- **Derive by hand:** Kelvin circulation theorem
- **Code from scratch:** Compute vorticity of discrete fields
- **Interactive lab:** Coconut trapped in an eddy behind a boulder ([The coconut that never escapes](https://andreolf.github.io/coconut-lab/))
- **Test that proves it:** Rankine core rotates like solid body
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.16 Potential flow

**Goal:** Build inviscid flows by superposition

- **Derive by hand:** Complex potential w(z)
- **Code from scratch:** Flow around a cylinder with circulation
- **Interactive lab:** Draggable circulation slider shows lift
- **Test that proves it:** Kutta-Joukowski lift = rho U Gamma
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.17 Open-channel flow basics

**Goal:** Understand rivers and irrigation canals

- **Derive by hand:** Specific energy, critical depth, Froude number
- **Code from scratch:** Critical depth and specific energy curve
- **Interactive lab:** Channel energy diagram
- **Test that proves it:** Minimum specific energy at Fr = 1
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.18 Weirs and Subak irrigation

**Goal:** Model flow over weirs in Balinese rice terraces

- **Derive by hand:** Broad/sharp-crested weir equations from critical flow
- **Code from scratch:** Weir discharge calculator and terrace cascade
- **Interactive lab:** Subak terrace cascade ([Subak rice terraces](https://andreolf.github.io/subak-lab/))
- **Test that proves it:** Discharge scales with head^(3/2)
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.19 Hydraulic jumps

**Goal:** Explain the roaring step in a channel

- **Derive by hand:** Momentum conjugate depths
- **Code from scratch:** Conjugate depth solver
- **Interactive lab:** Jump location slider
- **Test that proves it:** Conjugate depth formula satisfied; energy is lost
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik

## 11.20 Unsteady flow and water hammer

**Goal:** Explain pipe bangs and penstock surges

- **Derive by hand:** Joukowsky delta p = rho a delta v
- **Code from scratch:** Method-of-characteristics water hammer
- **Interactive lab:** Valve-closing animation in a penstock
- **Test that proves it:** Peak pressure matches Joukowsky for instant closure
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik
