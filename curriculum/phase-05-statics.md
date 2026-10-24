# Phase 05: Statics & Free-Body Diagrams

*Mechanik 1: Kinematik und Statik*

Forces, moments, equilibrium, trusses, frames, friction and virtual work.

- **ETH reference:** Mechanik 1: Kinematik und Statik
- **Real-world anchors:** Swiss bridges, ski-lift towers and a Bali bamboo scaffold
- **Lessons:** 20

## 05.01 Forces as vectors

**Goal:** Represent and add forces correctly

- **Derive by hand:** Force as a bound vector; resultant by vector sum
- **Code from scratch:** Force-vector class with resultant and components
- **Interactive lab:** Drag force arrows and see the resultant
- **Test that proves it:** Resultant equals component-wise sum
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.02 Moments and couples

**Goal:** Compute the turning effect of forces

- **Derive by hand:** M = r x F; couple is free vector
- **Code from scratch:** Moment calculator about any point
- **Interactive lab:** Spanner with draggable force and pivot
- **Test that proves it:** Moment of a couple independent of reference point
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.03 Equivalent force systems

**Goal:** Replace complex loads with a single force and moment

- **Derive by hand:** Reduction to a point, wrench
- **Code from scratch:** Reduce a distributed load to resultant + location
- **Interactive lab:** Distributed load slider showing resultant arrow
- **Test that proves it:** Resultant of a triangular load acts at L/3
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.04 Kinematics of rigid bodies

**Goal:** Describe velocities of points in a rigid body

- **Derive by hand:** v_B = v_A + omega x r_AB, instantaneous centre
- **Code from scratch:** Compute velocity field of a moving bike crank
- **Interactive lab:** Velocity arrows with instantaneous centre marked
- **Test that proves it:** Instantaneous centre has zero velocity
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.05 Supports and constraints

**Goal:** Model how structures are held

- **Derive by hand:** Reaction types: pin, roller, clamp; degrees of freedom
- **Code from scratch:** Constraint counter: Gruebler-style DOF count for planar bodies
- **Interactive lab:** Snap supports onto a beam and count unknowns
- **Test that proves it:** Simply supported beam has 3 reactions, 0 DOF
- **Pro tool:** Python
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.06 The free-body diagram

**Goal:** Isolate bodies and expose every force

- **Derive by hand:** Cut principle (Schnittprinzip)
- **Code from scratch:** FBD data structure with automatic equilibrium check
- **Interactive lab:** Interactive cut tool on a ladder
- **Test that proves it:** Ladder FBD balances in all three equations
- **Pro tool:** Python
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.07 Equilibrium of rigid bodies

**Goal:** Solve 2D and 3D equilibrium problems

- **Derive by hand:** Sum F = 0, sum M = 0
- **Code from scratch:** Solve reactions of a beam with arbitrary loads
- **Interactive lab:** Beam with draggable loads and live reactions
- **Test that proves it:** Reactions match hand calculation
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.08 Static determinacy

**Goal:** Know when statics alone is enough

- **Derive by hand:** Count equations vs unknowns; rank of the equilibrium matrix
- **Code from scratch:** Rank test for determinate, indeterminate and mechanism
- **Interactive lab:** Add/remove supports and see classification change
- **Test that proves it:** Classifications match textbook cases
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.09 Plane trusses: method of joints

**Goal:** Compute member forces in a truss bridge

- **Derive by hand:** Joint equilibrium, two-force members
- **Code from scratch:** Assemble and solve joint equations for any truss
- **Interactive lab:** Delete members and watch the load path ([Break the bridge](#lab-truss))
- **Test that proves it:** Warren truss forces match hand solution
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.10 Method of sections

**Goal:** Find a single member force quickly

- **Derive by hand:** Moment about the intersection of two cut members
- **Code from scratch:** Section solver for a chosen cut
- **Interactive lab:** Draggable section line through a bridge
- **Test that proves it:** Matches method-of-joints result
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.11 Space trusses and towers

**Goal:** Extend to 3D structures like ski-lift pylons

- **Derive by hand:** 3D joint equilibrium, Maxwell rule m = 3j - 6
- **Code from scratch:** 3D truss solver
- **Interactive lab:** Rotatable 3D tower with member forces coloured
- **Test that proves it:** Simple tetrapod forces match hand calc
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.12 Frames and machines

**Goal:** Analyse pliers, bike brakes and linkages

- **Derive by hand:** Multi-body FBDs with internal pins
- **Code from scratch:** Solve a bicycle rim-brake lever system
- **Interactive lab:** Squeeze slider showing pad force
- **Test that proves it:** Mechanical advantage equals arm ratio
- **Pro tool:** Python
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.13 Internal forces in beams

**Goal:** Draw N, V, M diagrams

- **Derive by hand:** dV/dx = -q, dM/dx = V
- **Code from scratch:** Compute and plot shear and moment diagrams
- **Interactive lab:** Live V/M diagrams under moving loads ([Cantilever beam (hero)](#hero))
- **Test that proves it:** Maximum moment for central point load is PL/4
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.14 Cables and chains

**Goal:** Model suspension cables and power lines

- **Derive by hand:** Catenary y = a cosh(x/a), parabolic approximation
- **Code from scratch:** Solve catenary sag for given span and length
- **Interactive lab:** Cable sag slider on an alpine cable car
- **Test that proves it:** Catenary length integral equals specified length
- **Pro tool:** SciPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.15 Friction

**Goal:** Model sliding, tipping and wedges

- **Derive by hand:** Coulomb friction F <= mu N
- **Code from scratch:** Tip vs slide predictor for a crate
- **Interactive lab:** Tilting ramp with crate
- **Test that proves it:** Slides exactly when tan(theta) > mu
- **Pro tool:** Python
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.16 Belt friction

**Goal:** Understand capstans and belt drives

- **Derive by hand:** Euler-Eytelwein T2/T1 = e^{mu beta}
- **Code from scratch:** Belt tension calculator
- **Interactive lab:** Rope around a bollard with wrap-angle slider
- **Test that proves it:** Tension ratio exponential in wrap angle
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.17 Centres of mass and gravity

**Goal:** Locate where weight acts

- **Derive by hand:** Composite bodies, Pappus-Guldinus
- **Code from scratch:** Composite centroid calculator
- **Interactive lab:** Assemble shapes and see CG move
- **Test that proves it:** CG of composite matches polygon algorithm
- **Pro tool:** shapely
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.18 Hydrostatics

**Goal:** Compute forces from still water on dams and gates

- **Derive by hand:** p = rho g h, resultant on inclined plane
- **Code from scratch:** Force and centre of pressure on a dam gate
- **Interactive lab:** Reservoir level slider on an alpine dam
- **Test that proves it:** Centre of pressure at 2h/3 for a vertical rectangle from surface
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.19 Principle of virtual work

**Goal:** Solve equilibrium with energy instead of FBDs

- **Derive by hand:** delta W = 0 for virtual displacements
- **Code from scratch:** Solve a scissor lift with virtual work
- **Interactive lab:** Scissor lift with load slider
- **Test that proves it:** Matches FBD result
- **Pro tool:** SymPy
- **ETH course:** Mechanik 1: Kinematik und Statik

## 05.20 Stability of equilibrium

**Goal:** Know when equilibrium is unstable

- **Derive by hand:** Potential energy minimum, second variation
- **Code from scratch:** Classify equilibria of a hinged bar with spring
- **Interactive lab:** Energy landscape with ball
- **Test that proves it:** Stable iff d^2V/dtheta^2 > 0
- **Pro tool:** NumPy
- **ETH course:** Mechanik 1: Kinematik und Statik
