# Phase 03: Analysis 2 & 3: Multivariable, Vector Calculus, PDEs

*Analysis 2 / Analysis 3*

Fields, gradients, divergence, curl and the PDEs every later phase solves.

- **ETH reference:** Analysis 2 / Analysis 3
- **Real-world anchors:** Pressure fields in the Limmat, temperature in an alpine dam
- **Lessons:** 20

## 03.01 Functions of several variables

**Goal:** Visualise and reason about fields

- **Derive by hand:** Level sets, partial derivatives
- **Code from scratch:** Evaluate and plot a terrain height field
- **Interactive lab:** 3D terrain with contour lines
- **Test that proves it:** Partial derivatives match finite differences
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.02 The gradient

**Goal:** Find the direction of steepest change

- **Derive by hand:** grad f, directional derivative = grad f . n
- **Code from scratch:** Gradient descent down a terrain
- **Interactive lab:** Ball rolling down a draggable terrain
- **Test that proves it:** Gradient is orthogonal to level curves numerically
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.03 Multivariable Taylor and the Hessian

**Goal:** Classify minima and saddles

- **Derive by hand:** Second-order Taylor, Hessian eigenvalues
- **Code from scratch:** Newton's method in 2D
- **Interactive lab:** Saddle vs bowl surface
- **Test that proves it:** Hessian eigenvalue signs classify test points correctly
- **Pro tool:** SciPy optimize
- **ETH course:** Analysis 2 / Analysis 3

## 03.04 Constrained optimisation

**Goal:** Optimise designs under constraints

- **Derive by hand:** Lagrange multipliers
- **Code from scratch:** Lightest cylindrical tank for a given volume
- **Interactive lab:** Constraint curve tangent to level sets
- **Test that proves it:** Optimum has height = diameter
- **Pro tool:** scipy.optimize.minimize
- **ETH course:** Analysis 2 / Analysis 3

## 03.05 Double and triple integrals

**Goal:** Compute mass, centroid and inertia of real parts

- **Derive by hand:** Fubini, change of variables, Jacobian determinant
- **Code from scratch:** Monte Carlo and quadrature for second moment of area
- **Interactive lab:** Area moment of an I-beam computed live
- **Test that proves it:** I-beam I_y matches hand formula
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.06 Polar, cylindrical and spherical coordinates

**Goal:** Pick the coordinates that make the problem easy

- **Derive by hand:** Jacobians r, r^2 sin theta
- **Code from scratch:** Integrate the mass of a flywheel rim
- **Interactive lab:** Coordinate grid morphing
- **Test that proves it:** Disk inertia equals m r^2/2
- **Pro tool:** SymPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.07 Line integrals and work

**Goal:** Compute work along paths and spot conservative fields

- **Derive by hand:** int F . dr, path independence iff curl F = 0
- **Code from scratch:** Integrate work on a ski-lift path in a gravity field
- **Interactive lab:** Path drag tool showing path independence
- **Test that proves it:** Gravity work depends only on height change
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.08 Divergence and flux

**Goal:** Measure sources and sinks in a flow

- **Derive by hand:** Divergence theorem
- **Code from scratch:** Compute flux of a velocity field through a closed curve
- **Interactive lab:** Flux arrows through a draggable circle
- **Test that proves it:** Discrete flux equals area integral of divergence
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.09 Curl and circulation

**Goal:** Measure rotation in a flow, the heart of eddies

- **Derive by hand:** Stokes theorem, vorticity omega = curl u
- **Code from scratch:** Vorticity of a Rankine vortex field
- **Interactive lab:** Paddle wheel spinning in a flow field ([The coconut that never escapes](https://andreolf.github.io/coconut-lab/))
- **Test that proves it:** Circulation around loop equals enclosed vorticity integral
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.10 Potential flow fields

**Goal:** Build flows from sources, sinks and vortices

- **Derive by hand:** Velocity potential, Laplace equation
- **Code from scratch:** Superpose uniform flow + doublet = flow around a cylinder (boulder)
- **Interactive lab:** Streamlines around a boulder in a river
- **Test that proves it:** Stagnation points at theta = 0, pi on the cylinder
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.11 Fourier series

**Goal:** Decompose periodic signals into sinusoids

- **Derive by hand:** Orthogonality of sin/cos, coefficient integrals
- **Code from scratch:** Compute Fourier coefficients of a square wave
- **Interactive lab:** Add harmonics, watch Gibbs overshoot
- **Test that proves it:** Overshoot approaches about 9% of the jump
- **Pro tool:** numpy.fft
- **ETH course:** Analysis 2 / Analysis 3

## 03.12 The Fourier transform and FFT

**Goal:** Analyse vibration spectra

- **Derive by hand:** DFT as a matrix, Cooley-Tukey
- **Code from scratch:** Implement radix-2 FFT
- **Interactive lab:** Spectrum of a recorded bike-frame vibration
- **Test that proves it:** Matches numpy.fft.fft to 1e-10
- **Pro tool:** numpy.fft
- **ETH course:** Analysis 2 / Analysis 3

## 03.13 Classifying PDEs

**Goal:** Recognise elliptic, parabolic and hyperbolic problems

- **Derive by hand:** Characteristics of second-order PDEs
- **Code from scratch:** Classifier for a u_xx + b u_xy + c u_yy
- **Interactive lab:** Table of PDEs mapped to physical systems
- **Test that proves it:** Laplace elliptic, heat parabolic, wave hyperbolic
- **Pro tool:** SymPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.14 The heat equation

**Goal:** Model diffusion of heat

- **Derive by hand:** Derive u_t = alpha u_xx from conservation + Fourier's law
- **Code from scratch:** Separation of variables solution on a rod
- **Interactive lab:** Rod temperature animation
- **Test that proves it:** Series solution satisfies boundary conditions
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.15 The wave equation

**Goal:** Model strings, rods and sound

- **Derive by hand:** Derive u_tt = c^2 u_xx from Newton on a string element
- **Code from scratch:** d'Alembert solution, plucked string
- **Interactive lab:** String animation with draggable pluck
- **Test that proves it:** Energy constant to 1e-6 in exact solution sampling
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.16 The Laplace equation

**Goal:** Model steady fields: potential flow, steady heat

- **Derive by hand:** Mean value property
- **Code from scratch:** Solve on a square by series and by relaxation
- **Interactive lab:** Relaxation heat-map converging
- **Test that proves it:** Interior value equals neighbour average at convergence
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.17 Boundary conditions

**Goal:** Set up well-posed problems

- **Derive by hand:** Dirichlet, Neumann, Robin
- **Code from scratch:** Implement each BC type on a 1D heat problem
- **Interactive lab:** BC type selector
- **Test that proves it:** Neumann zero-flux conserves total heat
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.18 Laplace transform

**Goal:** Solve linear ODEs with forcing

- **Derive by hand:** Transform pairs, convolution
- **Code from scratch:** Step response of a damped oscillator via partial fractions
- **Interactive lab:** Pole map and time response side by side
- **Test that proves it:** Inverse transform matches numerical integration
- **Pro tool:** SymPy laplace_transform
- **ETH course:** Analysis 2 / Analysis 3

## 03.19 Systems of ODEs and phase planes

**Goal:** Visualise nonlinear dynamics

- **Derive by hand:** Linearisation, Jacobian eigenvalues, stability
- **Code from scratch:** Phase portrait of a nonlinear pendulum
- **Interactive lab:** Draggable initial condition in the phase plane
- **Test that proves it:** Separatrix energy equals 2mgL
- **Pro tool:** SciPy
- **ETH course:** Analysis 2 / Analysis 3

## 03.20 Green's functions intuition

**Goal:** See solutions as superposition of impulse responses

- **Derive by hand:** Delta function, convolution
- **Code from scratch:** Beam deflection by superposing point loads
- **Interactive lab:** Add point loads to a beam and watch deflection sum
- **Test that proves it:** Superposed deflection equals direct solve
- **Pro tool:** NumPy
- **ETH course:** Analysis 2 / Analysis 3
