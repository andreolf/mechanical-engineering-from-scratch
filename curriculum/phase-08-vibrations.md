# Phase 08: Vibrations & Waves

*Schwingungen und Wellen*

Single- and multi-DOF oscillators, resonance, modes, isolation and waves in elastic bodies.

- **ETH reference:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)
- **Real-world anchors:** Pedestrian bridges, ski-lift cables, and a Bali gamelan
- **Lessons:** 16

## 08.01 The harmonic oscillator

**Goal:** Derive natural frequency from first principles

- **Derive by hand:** m x'' + k x = 0, omega_n = sqrt(k/m)
- **Code from scratch:** Simulate and measure period
- **Interactive lab:** Mass-spring lab with k and m sliders
- **Test that proves it:** Measured period equals 2 pi sqrt(m/k)
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.02 Damping

**Goal:** Model energy loss

- **Derive by hand:** Viscous damping ratio zeta, logarithmic decrement
- **Code from scratch:** Estimate zeta from a decaying signal
- **Interactive lab:** Damping slider with envelope fit
- **Test that proves it:** Log decrement estimate recovers zeta within 2%
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.03 Forced vibration and resonance

**Goal:** Predict amplitude under harmonic forcing

- **Derive by hand:** Frequency response H(omega), phase
- **Code from scratch:** Compute and plot Bode-style amplitude/phase
- **Interactive lab:** Shaker frequency sweep lab
- **Test that proves it:** Peak near omega_n sqrt(1 - 2 zeta^2)
- **Pro tool:** SciPy signal
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.04 Base excitation and isolation

**Goal:** Isolate machines and vehicles from vibration

- **Derive by hand:** Transmissibility, isolation above sqrt(2) omega_n
- **Code from scratch:** Bike-suspension transmissibility
- **Interactive lab:** Road bump excitation on a bike
- **Test that proves it:** Transmissibility below 1 above sqrt(2) omega_n
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.05 Rotating unbalance

**Goal:** Model washing machines and turbines

- **Derive by hand:** m e omega^2 forcing
- **Code from scratch:** Response of an unbalanced rotor
- **Interactive lab:** Spin speed slider
- **Test that proves it:** High-speed amplitude approaches m e/M
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.06 Two-DOF systems

**Goal:** Find modes of coupled oscillators

- **Derive by hand:** Eigenproblem (K - omega^2 M) phi = 0
- **Code from scratch:** Solve and animate modes
- **Interactive lab:** Coupled pendulums with beat phenomena
- **Test that proves it:** Modes are M-orthogonal
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.07 Tuned mass dampers

**Goal:** Calm a wobbly footbridge or tower

- **Derive by hand:** Den Hartog tuning
- **Code from scratch:** Optimise a TMD for a footbridge model
- **Interactive lab:** TMD on/off comparison
- **Test that proves it:** Peak response reduced vs untuned
- **Pro tool:** SciPy optimize
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.08 Multi-DOF and modal analysis

**Goal:** Decouple big systems into modes

- **Derive by hand:** Modal coordinates, modal superposition
- **Code from scratch:** Shear-building model of a 5-storey frame
- **Interactive lab:** Mode shape animator
- **Test that proves it:** Modal superposition equals direct integration
- **Pro tool:** SciPy eigh
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.09 Vibration of strings

**Goal:** Connect waves and modes

- **Derive by hand:** Standing waves, f_n = n c/(2L)
- **Code from scratch:** Modal string synthesiser
- **Interactive lab:** Pluck and hear the harmonics
- **Test that proves it:** Mode frequencies are integer multiples
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.10 Axial and torsional vibration of rods

**Goal:** Model shafts and drill strings

- **Derive by hand:** Wave equation in rods, c = sqrt(E/rho)
- **Code from scratch:** Natural frequencies of a fixed-free rod
- **Interactive lab:** Rod mode animator
- **Test that proves it:** f_1 = c/(4L) for fixed-free
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.11 Beam vibration

**Goal:** Find bending modes of beams

- **Derive by hand:** EI w'''' + rho A w_tt = 0, characteristic equation
- **Code from scratch:** Solve cantilever frequency equation cos(bL)cosh(bL) = -1
- **Interactive lab:** Cantilever mode shapes in 3D
- **Test that proves it:** beta_1 L = 1.875
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.12 Plates and bells

**Goal:** See modes in 2D

- **Derive by hand:** Chladni patterns intuition
- **Code from scratch:** Finite-difference modes of a square membrane
- **Interactive lab:** Chladni pattern generator
- **Test that proves it:** Membrane eigenvalues match analytic m^2 + n^2 pattern
- **Pro tool:** SciPy sparse eigsh
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.13 Experimental modal analysis

**Goal:** Extract modes from measurements

- **Derive by hand:** Frequency response functions, peak picking
- **Code from scratch:** Identify modes from simulated hammer test data
- **Interactive lab:** Hammer-tap FRF lab
- **Test that proves it:** Identified frequencies within 1% of model
- **Pro tool:** SciPy signal
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.14 Nonlinear vibrations

**Goal:** See what linear theory misses

- **Derive by hand:** Duffing oscillator, jump phenomenon
- **Code from scratch:** Duffing frequency sweep up and down
- **Interactive lab:** Hysteresis in response curve
- **Test that proves it:** Up and down sweeps differ in nonlinear regime
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.15 Self-excited vibration

**Goal:** Understand flutter, squeal and galloping

- **Derive by hand:** Negative damping, limit cycles
- **Code from scratch:** Van der Pol oscillator
- **Interactive lab:** Limit cycle in phase plane
- **Test that proves it:** All trajectories converge to the same cycle
- **Pro tool:** SciPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)

## 08.16 Waves and impact

**Goal:** Understand stress waves on impact

- **Derive by hand:** 1D wave reflection at free and fixed ends
- **Code from scratch:** Simulate impact of two rods
- **Interactive lab:** Wave propagation animation
- **Test that proves it:** Free end reflects compression as tension
- **Pro tool:** NumPy
- **ETH course:** Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)
