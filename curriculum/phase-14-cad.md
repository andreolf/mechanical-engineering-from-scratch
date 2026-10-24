# Phase 14: CAD & Technical Drawing

*CAD und Technisches Zeichnen*

Geometry kernels from scratch, then parametric CAD in FreeCAD and Onshape.

- **ETH reference:** Engineering Design and Material Selection (sketching, technical drawing, CAD)
- **Real-world anchors:** Modelling a bike dropout, a Subak weir gate and a Swiss-style watch gear
- **Lessons:** 12

## 14.01 Technical drawing fundamentals

**Goal:** Read and produce engineering drawings

- **Derive by hand:** Orthographic projection as linear maps
- **Code from scratch:** Project a 3D wireframe to front/top/side views
- **Interactive lab:** Rotatable part with live projected views
- **Test that proves it:** Projections match hand-drawn views for a test block
- **Pro tool:** FreeCAD TechDraw
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.02 Homogeneous coordinates

**Goal:** Transform geometry like a CAD kernel

- **Derive by hand:** 4x4 matrices for rotation + translation
- **Code from scratch:** Transform library with composition
- **Interactive lab:** Transform gizmo
- **Test that proves it:** Composition order matters test
- **Pro tool:** NumPy
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.03 Curves: Bezier and B-splines

**Goal:** Understand how CAD represents curves

- **Derive by hand:** Bernstein polynomials, de Casteljau
- **Code from scratch:** de Casteljau and de Boor algorithms
- **Interactive lab:** Drag control points of a fairing curve
- **Test that proves it:** Curve passes through end control points (Bezier)
- **Pro tool:** geomdl
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.04 NURBS

**Goal:** Represent exact circles and freeform surfaces

- **Derive by hand:** Rational weights, circle as NURBS
- **Code from scratch:** Build a NURBS circle and check radius
- **Interactive lab:** Weight slider
- **Test that proves it:** All points at exact radius
- **Pro tool:** geomdl
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.05 Surfaces

**Goal:** Model freeform surfaces

- **Derive by hand:** Tensor-product patches
- **Code from scratch:** Evaluate a bicubic patch and its normals
- **Interactive lab:** Patch with draggable control net
- **Test that proves it:** Normals are unit length
- **Pro tool:** NumPy
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.06 Constructive solid geometry

**Goal:** Combine solids with booleans

- **Derive by hand:** CSG trees, signed distance functions
- **Code from scratch:** SDF-based CSG with marching cubes mesh output
- **Interactive lab:** Boolean playground (union, cut)
- **Test that proves it:** Volume of union by Monte Carlo matches inclusion-exclusion
- **Pro tool:** scikit-image marching_cubes
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.07 Meshes and STL

**Goal:** Export geometry for printing and simulation

- **Derive by hand:** Triangle meshes, normals, watertightness
- **Code from scratch:** Write an STL exporter and watertight checker
- **Interactive lab:** Mesh viewer with open-edge highlighting
- **Test that proves it:** Closed mesh has every edge shared by two faces
- **Pro tool:** trimesh
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.08 Parametric sketches and constraints

**Goal:** Understand constraint solvers

- **Derive by hand:** Geometric constraints as nonlinear equations
- **Code from scratch:** Newton-based 2D sketch solver
- **Interactive lab:** Drag a constrained sketch
- **Test that proves it:** Constraints satisfied to 1e-9 after drag
- **Pro tool:** FreeCAD Sketcher
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.09 Parametric part modelling

**Goal:** Build a real part with design intent

- **Derive by hand:** Feature tree, parameters
- **Code from scratch:** Model a bike dropout in FreeCAD driven by a spreadsheet
- **Interactive lab:** Parameter slider preview (exported meshes)
- **Test that proves it:** Rebuild succeeds for parameter sweep
- **Pro tool:** FreeCAD Part Design
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.10 Assemblies and mates

**Goal:** Assemble parts with joints

- **Derive by hand:** Kinematic constraints between bodies
- **Code from scratch:** Assemble a four-bar in Onshape or FreeCAD Assembly
- **Interactive lab:** Animated assembly
- **Test that proves it:** Mates leave intended DOF only
- **Pro tool:** Onshape (free plan) / FreeCAD Assembly
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.11 Scripting CAD

**Goal:** Generate parts from code

- **Derive by hand:** Programmatic B-rep modelling
- **Code from scratch:** Generate a gear or weir gate with CadQuery
- **Interactive lab:** Code-to-model preview
- **Test that proves it:** Exported STEP reopens with same volume
- **Pro tool:** CadQuery / build123d
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)

## 14.12 Drawings, GD&T and handoff

**Goal:** Communicate tolerances

- **Derive by hand:** GD&T basics: datums, position, flatness
- **Code from scratch:** Annotated drawing of your dropout
- **Interactive lab:** Tolerance zone visualiser
- **Test that proves it:** Drawing contains all required dimensions checklist
- **Pro tool:** FreeCAD TechDraw
- **ETH course:** Engineering Design and Material Selection (sketching, technical drawing, CAD)
