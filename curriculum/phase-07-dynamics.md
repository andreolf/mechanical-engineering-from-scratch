# Phase 07: Dynamics

*Mechanik 3: Dynamik*

Particles, systems, rigid bodies in 2D and 3D, rotating frames and gyroscopes.

- **ETH reference:** Mechanik 3: Dynamik
- **Real-world anchors:** Swiss rail curves, a ski jump, a Bali scooter and a spinning flywheel
- **Lessons:** 20

## 07.01 Particle kinematics

**Goal:** Describe trajectories, velocity and acceleration

- **Derive by hand:** Cartesian, polar and path coordinates
- **Code from scratch:** Compute v and a along a measured GPS track
- **Interactive lab:** Track with tangential/normal acceleration arrows
- **Test that proves it:** Normal acceleration equals v^2/rho on a circle
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.02 Newton's second law

**Goal:** Write equations of motion for a particle

- **Derive by hand:** F = m a; cut-free and add forces
- **Code from scratch:** Simulate a ski jumper with gravity and drag
- **Interactive lab:** Ski-jump trajectory with drag coefficient slider
- **Test that proves it:** Zero drag reproduces parabola
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik

## 07.03 Work and energy

**Goal:** Use energy to skip integration

- **Derive by hand:** Work-energy theorem, conservative forces
- **Code from scratch:** Roller-coaster speed from energy
- **Interactive lab:** Draggable track profile with speed colouring
- **Test that proves it:** Energy-based speed matches ODE simulation
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.04 Impulse and momentum

**Goal:** Analyse collisions and rockets

- **Derive by hand:** Linear impulse, conservation of momentum
- **Code from scratch:** 1D collision solver with restitution
- **Interactive lab:** Two-cart collision lab
- **Test that proves it:** Momentum conserved to 1e-12
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.05 The rocket equation

**Goal:** Derive variable-mass motion

- **Derive by hand:** Tsiolkovsky delta v = v_e ln(m0/m1)
- **Code from scratch:** Integrate rocket ascent with gravity
- **Interactive lab:** Mass ratio slider
- **Test that proves it:** Integrated delta v (no gravity) matches Tsiolkovsky
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik

## 07.06 Systems of particles

**Goal:** Treat many bodies at once

- **Derive by hand:** Centre of mass theorem, internal forces cancel
- **Code from scratch:** N-body simulation of a few particles
- **Interactive lab:** Particle system with COM tracker
- **Test that proves it:** COM moves uniformly without external force
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.07 Angular momentum of particles

**Goal:** Explain why spinning skaters speed up

- **Derive by hand:** L = r x m v; dL/dt = M
- **Code from scratch:** Simulate a mass on a shrinking string
- **Interactive lab:** Radius slider showing omega increase
- **Test that proves it:** L conserved within integrator tolerance
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.08 Rigid body kinematics in 2D

**Goal:** Relate velocities and accelerations of linkage points

- **Derive by hand:** v_B = v_A + omega x r, a_B with centripetal term
- **Code from scratch:** Four-bar linkage kinematics
- **Interactive lab:** Animated four-bar with velocity polygons
- **Test that proves it:** Grashof condition predicts crank rotation
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.09 Planar rigid body dynamics

**Goal:** Simulate rolling wheels and swinging doors

- **Derive by hand:** M_G = I_G alpha; rolling constraint
- **Code from scratch:** Disk vs ring race down a ramp
- **Interactive lab:** Rolling race lab
- **Test that proves it:** Disk accelerates at 2/3 g sin(theta), ring at 1/2
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik

## 07.10 Moment of inertia

**Goal:** Compute I for real parts

- **Derive by hand:** I = int r^2 dm, parallel axis
- **Code from scratch:** Inertia of a flywheel from its profile
- **Interactive lab:** Flywheel profile editor
- **Test that proves it:** Matches CAD mass properties for simple shapes
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.11 Rotating machinery and balancing

**Goal:** Avoid vibration from unbalanced rotors

- **Derive by hand:** Static vs dynamic imbalance
- **Code from scratch:** Compute correction masses for a rotor
- **Interactive lab:** Rotor with draggable unbalance
- **Test that proves it:** Corrected rotor has zero net force and moment
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.12 Relative motion and rotating frames

**Goal:** Compute motion seen from a moving observer

- **Derive by hand:** a = a_rel + 2 omega x v_rel + omega x (omega x r) + ...
- **Code from scratch:** Simulate a ball on a rotating carousel
- **Interactive lab:** Inertial vs rotating view toggle
- **Test that proves it:** Coriolis deflection direction correct for rotation sense
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.13 3D rigid-body kinematics

**Goal:** Describe orientation in 3D

- **Derive by hand:** Rotation matrices, Euler angles, quaternions
- **Code from scratch:** Quaternion integrator for angular velocity
- **Interactive lab:** Gimbal lock demo vs quaternion
- **Test that proves it:** Quaternion stays unit norm with renormalisation
- **Pro tool:** scipy.spatial.transform
- **ETH course:** Mechanik 3: Dynamik

## 07.14 Inertia tensor

**Goal:** Understand how mass distribution resists rotation

- **Derive by hand:** I tensor, principal axes
- **Code from scratch:** Compute inertia tensor of a point cloud body
- **Interactive lab:** Principal axes overlay on a 3D part
- **Test that proves it:** Principal moments equal eigenvalues
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.15 Euler's equations

**Goal:** Simulate free 3D rotation

- **Derive by hand:** I omega' + omega x I omega = M
- **Code from scratch:** Integrate torque-free rotation
- **Interactive lab:** Tennis-racket (intermediate axis) instability demo
- **Test that proves it:** Rotation about intermediate axis is unstable
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik

## 07.16 Gyroscopes and precession

**Goal:** Explain why a spinning wheel doesn't fall

- **Derive by hand:** Precession rate Omega = m g r /(I omega) for fast top
- **Code from scratch:** Simulate a gyroscope on a pivot
- **Interactive lab:** Spinning flywheel lab: change spin, watch precession ([Gyroscope & flywheel](#lab-flywheel))
- **Test that proves it:** Simulated precession rate approaches formula for fast spin
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik

## 07.17 Flywheel energy storage

**Goal:** Size a flywheel for energy storage

- **Derive by hand:** E = I omega^2/2, rim stress sigma = rho v^2
- **Code from scratch:** Energy and stress vs speed for a rim
- **Interactive lab:** Spin-up slider with burst warning
- **Test that proves it:** Burst speed independent of radius for thin rim
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.18 Lagrangian mechanics

**Goal:** Derive equations of motion with energy

- **Derive by hand:** Euler-Lagrange equations
- **Code from scratch:** SymPy Lagrangian of a double pendulum
- **Interactive lab:** Double pendulum chaos lab
- **Test that proves it:** Energy conserved in simulation within tolerance
- **Pro tool:** SymPy mechanics
- **ETH course:** Mechanik 3: Dynamik

## 07.19 Rail vehicle dynamics in curves

**Goal:** Understand cant and lateral acceleration

- **Derive by hand:** Cant balances v^2/R; uncompensated acceleration
- **Code from scratch:** Compute cant deficiency for a train curve
- **Interactive lab:** Train on curve with speed slider
- **Test that proves it:** Zero lateral force at balance speed
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik

## 07.20 Multibody simulation

**Goal:** Assemble constrained systems

- **Derive by hand:** Constraint equations, Lagrange multipliers
- **Code from scratch:** Slider-crank multibody solver
- **Interactive lab:** Engine slider-crank animation
- **Test that proves it:** Constraint drift stays below tolerance with stabilisation
- **Pro tool:** Project Chrono / MuJoCo
- **ETH course:** Mechanik 3: Dynamik
