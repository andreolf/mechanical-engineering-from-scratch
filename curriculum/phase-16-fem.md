# Phase 16: Finite Element Method from Scratch

*Finite-Elemente-Methode*

From spring chains to 2D/3D solids, dynamics and nonlinearity, then CalculiX and FEniCSx.

- **ETH reference:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives (generic description)
- **Real-world anchors:** A bike frame, a Swiss footbridge and an alpine dam wall
- **Lessons:** 18

## 16.01 Springs to stiffness matrices

**Goal:** See FEM as assembling springs

- **Derive by hand:** Element stiffness k [[1,-1],[-1,1]], assembly
- **Code from scratch:** Assemble a spring chain and solve
- **Interactive lab:** Spring chain with node displacements
- **Test that proves it:** Matches series-spring formula
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.02 Direct stiffness method for trusses

**Goal:** Solve any 2D truss

- **Derive by hand:** Transformation of bar stiffness to global axes
- **Code from scratch:** 2D truss FEM solver
- **Interactive lab:** Break-the-bridge truss lab ([Break the bridge](#lab-truss))
- **Test that proves it:** Matches statics solution for determinate trusses
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.03 Weak form

**Goal:** Derive FEM from a differential equation

- **Derive by hand:** Multiply by test function, integrate by parts
- **Code from scratch:** Weak form of -(EA u')' = f symbolically
- **Interactive lab:** Test-function visualiser
- **Test that proves it:** Galerkin system equals stiffness method for bars
- **Pro tool:** SymPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.04 Shape functions and the 1D element

**Goal:** Build elements from interpolation

- **Derive by hand:** Linear and quadratic Lagrange shape functions
- **Code from scratch:** 1D FEM with linear and quadratic elements
- **Interactive lab:** Element order toggle with error plot
- **Test that proves it:** Quadratic converges faster
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.05 Beam elements

**Goal:** Model frames

- **Derive by hand:** Hermite cubic shape functions, 4x4 beam stiffness
- **Code from scratch:** Euler-Bernoulli beam FEM
- **Interactive lab:** Frame with loads and deformed shape
- **Test that proves it:** Cantilever tip deflection exact with one element (point load)
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.06 2D frames

**Goal:** Analyse a bike frame as a planar frame

- **Derive by hand:** Frame element = bar + beam with transformation
- **Code from scratch:** Planar frame solver
- **Interactive lab:** Bike frame under rider load (educational model)
- **Test that proves it:** Equilibrium of reactions
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.07 Isoparametric mapping

**Goal:** Handle arbitrary element shapes

- **Derive by hand:** Jacobian of mapping, Gauss quadrature
- **Code from scratch:** Map and integrate on a distorted quad
- **Interactive lab:** Distorted element with Jacobian warning
- **Test that proves it:** Area computed equals polygon area
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.08 Plane stress and plane strain

**Goal:** Model 2D solids

- **Derive by hand:** Constitutive matrices D
- **Code from scratch:** CST and Q4 elements
- **Interactive lab:** Plate with hole stress map
- **Test that proves it:** Peak stress approaches 3x with mesh refinement
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.09 Meshing

**Goal:** Generate meshes from geometry

- **Derive by hand:** Delaunay triangulation, quality metrics
- **Code from scratch:** Simple Delaunay meshing pipeline
- **Interactive lab:** Mesh quality colouring
- **Test that proves it:** No inverted elements
- **Pro tool:** Gmsh
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.10 Assembly and sparse solvers at scale

**Goal:** Solve 100k-DOF problems

- **Derive by hand:** Sparse assembly, bandwidth, reordering
- **Code from scratch:** COO-to-CSR assembly and sparse solve
- **Interactive lab:** Sparsity before/after reordering
- **Test that proves it:** Same answer as dense on small problem
- **Pro tool:** SciPy sparse
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.11 Patch test and convergence

**Goal:** Verify your element formulation

- **Derive by hand:** Patch test, a priori error estimates
- **Code from scratch:** Patch test and convergence study
- **Interactive lab:** Error vs h plot
- **Test that proves it:** Patch test passes to machine precision
- **Pro tool:** pytest
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.12 Locking and remedies

**Goal:** Understand shear and volumetric locking

- **Derive by hand:** Why linear elements are too stiff in bending
- **Code from scratch:** Compare Q4 vs reduced integration on a bending beam
- **Interactive lab:** Locking demo
- **Test that proves it:** Reduced integration closer to beam theory
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.13 3D solids

**Goal:** Extend to tetrahedra and hexahedra

- **Derive by hand:** Tet4 stiffness
- **Code from scratch:** 3D tet FEM for a bracket
- **Interactive lab:** 3D stress viewer (three.js)
- **Test that proves it:** Uniform tension patch exact
- **Pro tool:** NumPy + meshio
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.14 Heat conduction FEM

**Goal:** Reuse the machinery for heat

- **Derive by hand:** Same weak form, conductivity matrix
- **Code from scratch:** Steady and transient 2D heat FEM
- **Interactive lab:** Heat map on a heatsink
- **Test that proves it:** Matches 1D analytic in slab test
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.15 Modal analysis with FEM

**Goal:** Find natural frequencies of structures

- **Derive by hand:** Consistent mass matrix, generalised eigenproblem
- **Code from scratch:** Modal analysis of a footbridge model
- **Interactive lab:** Mode shape animation
- **Test that proves it:** Cantilever frequencies converge to beam theory
- **Pro tool:** SciPy eigsh
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.16 Transient dynamics

**Goal:** Simulate impacts and earthquakes

- **Derive by hand:** Newmark-beta method
- **Code from scratch:** Newmark integrator on a frame
- **Interactive lab:** Ground shake slider
- **Test that proves it:** Average acceleration scheme is unconditionally stable
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.17 Nonlinear FEM

**Goal:** Handle large deformations and plasticity

- **Derive by hand:** Newton-Raphson, tangent stiffness
- **Code from scratch:** Geometrically nonlinear truss (snap-through) with arc-length
- **Interactive lab:** Snap-through animation
- **Test that proves it:** Arc-length traces the full equilibrium path
- **Pro tool:** NumPy
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives

## 16.18 Pro tools: CalculiX and FEniCSx

**Goal:** Map your solver to industrial open-source tools

- **Derive by hand:** Same weak forms in a DSL
- **Code from scratch:** Recreate your plate-with-hole in FEniCSx and a bracket in CalculiX
- **Interactive lab:** Side-by-side comparison
- **Test that proves it:** Results agree within discretisation error
- **Pro tool:** FEniCSx, CalculiX, Gmsh, ParaView
- **ETH course:** Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives
