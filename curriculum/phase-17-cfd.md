# Phase 17: Computational Fluid Dynamics from Scratch

*Numerische Strömungsmechanik*

Finite differences and finite volumes, lid-driven cavity, lattice Boltzmann, then OpenFOAM.

- **ETH reference:** Computational fluid dynamics electives (generic) (generic description)
- **Real-world anchors:** The coconut eddy, the Rhine Falls plunge pool, wind around a Zurich tower
- **Lessons:** 18

## 17.01 Why CFD and what it can't do

**Goal:** Set honest expectations

- **Derive by hand:** Discretisation, modelling and round-off errors
- **Code from scratch:** Error budget worksheet
- **Interactive lab:** Error source explorer
- **Test that proves it:** Budget sums to observed error in a toy case
- **Pro tool:** Python
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.02 Conservation form and finite volumes

**Goal:** Write conservation laws as fluxes

- **Derive by hand:** Integral form, cell averages, face fluxes
- **Code from scratch:** 1D finite-volume advection
- **Interactive lab:** Cells with flux arrows
- **Test that proves it:** Total quantity conserved to machine precision
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.03 Flux schemes

**Goal:** Choose stable, accurate fluxes

- **Derive by hand:** Upwind, Lax-Wendroff, TVD limiters
- **Code from scratch:** Implement minmod and superbee limiters
- **Interactive lab:** Square-pulse advection comparison
- **Test that proves it:** TVD scheme creates no new extrema
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.04 Burgers' equation and shocks

**Goal:** Meet nonlinearity

- **Derive by hand:** Characteristics, Rusanov flux
- **Code from scratch:** Burgers solver forming a shock
- **Interactive lab:** Wave steepening animation
- **Test that proves it:** Shock speed matches Rankine-Hugoniot
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.05 Shallow water equations

**Goal:** Model rivers, floods and canals

- **Derive by hand:** Saint-Venant equations
- **Code from scratch:** 1D dam-break solver
- **Interactive lab:** Dam break in an alpine valley
- **Test that proves it:** Matches Ritter analytical solution
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.06 2D shallow water and Subak terraces

**Goal:** Simulate terrace overflow

- **Derive by hand:** 2D finite volume with wetting/drying (simplified)
- **Code from scratch:** 2D shallow-water terrace cascade
- **Interactive lab:** Water spilling down terraces ([Subak rice terraces](https://andreolf.github.io/subak-lab/))
- **Test that proves it:** Mass conserved
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.07 Streamfunction-vorticity method

**Goal:** Solve 2D incompressible flow

- **Derive by hand:** psi-omega formulation
- **Code from scratch:** Lid-driven cavity at Re = 100
- **Interactive lab:** Streamline animation
- **Test that proves it:** Primary vortex centre near published benchmark (Ghia et al. 1982)
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.08 Pressure-velocity coupling

**Goal:** Handle incompressibility in primitive variables

- **Derive by hand:** Projection method (Chorin)
- **Code from scratch:** Fractional-step NS solver on a staggered grid
- **Interactive lab:** Pressure and velocity panels
- **Test that proves it:** Divergence below 1e-8 after projection
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.09 Flow past a cylinder

**Goal:** Reproduce vortex shedding

- **Derive by hand:** Immersed boundary / masked cells
- **Code from scratch:** Cylinder in channel at Re ~ 100
- **Interactive lab:** Karman street animation
- **Test that proves it:** Strouhal number close to 0.16-0.2 (literature range)
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.10 The coconut eddy

**Goal:** Simulate recirculation behind a boulder

- **Derive by hand:** Separated flow, recirculation length
- **Code from scratch:** Particle tracking in your cylinder/boulder solution
- **Interactive lab:** Coconut trapped behind the boulder ([The coconut that never escapes](https://andreolf.github.io/coconut-lab/))
- **Test that proves it:** Particle released in the wake stays trapped for many shedding cycles in the model
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.11 Lattice Boltzmann: theory

**Goal:** Derive fluid flow from particle distributions

- **Derive by hand:** BGK collision, D2Q9 lattice, Chapman-Enskog sketch
- **Code from scratch:** D2Q9 streaming and collision kernels
- **Interactive lab:** Distribution function viewer
- **Test that proves it:** Equilibrium recovers density and momentum
- **Pro tool:** NumPy
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.12 Lattice Boltzmann: flows

**Goal:** Run real flows with LBM

- **Derive by hand:** Bounce-back boundaries, viscosity nu = (tau - 1/2)/3
- **Code from scratch:** LBM channel and cylinder flow; JS port in the browser
- **Interactive lab:** Live LBM in canvas
- **Test that proves it:** Poiseuille profile within 1%
- **Pro tool:** NumPy / JS
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.13 Turbulence modelling

**Goal:** Use RANS and LES appropriately

- **Derive by hand:** k-epsilon, k-omega SST, Smagorinsky
- **Code from scratch:** Mixing-length model for channel flow
- **Interactive lab:** Model selector
- **Test that proves it:** Log-law region reproduced
- **Pro tool:** Python
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.14 Meshes for CFD

**Goal:** Build meshes that converge

- **Derive by hand:** Orthogonality, skewness, y+
- **Code from scratch:** Mesh quality checker
- **Interactive lab:** Mesh quality heat-map
- **Test that proves it:** Flags skewed cells
- **Pro tool:** Gmsh / snappyHexMesh
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.15 OpenFOAM: first case

**Goal:** Run a professional solver

- **Derive by hand:** Case structure: 0, constant, system
- **Code from scratch:** Run icoFoam lid-driven cavity and compare to your solver
- **Interactive lab:** Side-by-side streamlines
- **Test that proves it:** Results agree within mesh error
- **Pro tool:** OpenFOAM, ParaView
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.16 OpenFOAM: river eddy

**Goal:** Model the Bali boulder eddy in 2D

- **Derive by hand:** Turbulent incompressible solver setup
- **Code from scratch:** simpleFoam/pimpleFoam case behind a boulder
- **Interactive lab:** Velocity field render
- **Test that proves it:** Recirculation length vs mesh study
- **Pro tool:** OpenFOAM
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.17 Verification and validation in CFD

**Goal:** Trust your results

- **Derive by hand:** Grid convergence index (GCI)
- **Code from scratch:** GCI study script
- **Interactive lab:** Convergence plot
- **Test that proves it:** GCI reported with observed order
- **Pro tool:** Python
- **ETH course:** Computational fluid dynamics electives (generic)

## 17.18 Postprocessing and visualisation

**Goal:** Communicate flows clearly

- **Derive by hand:** Q-criterion, streamlines, line integral convolution
- **Code from scratch:** Compute Q-criterion and render with three.js
- **Interactive lab:** Interactive 3D flow viewer
- **Test that proves it:** Q > 0 in vortex cores of test field
- **Pro tool:** ParaView, three.js
- **ETH course:** Computational fluid dynamics electives (generic)
