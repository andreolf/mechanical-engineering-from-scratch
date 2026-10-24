# Phase 04: Numerical Methods

*Numerische Methoden*

Root finding, integration, ODE solvers, stability and finite differences built from scratch.

- **ETH reference:** Numerical methods for engineers (generic; ETH offers several numerics courses) (generic description)
- **Real-world anchors:** Simulating Swiss rail braking and alpine snow loads without a black box
- **Lessons:** 20

## 04.01 Error analysis and convergence order

**Goal:** Measure how fast a method converges

- **Derive by hand:** Order p from e_{n+1} ~ C e_n^p
- **Code from scratch:** Estimate convergence order from data
- **Interactive lab:** Log-log error plot fitter
- **Test that proves it:** Newton gives p ~ 2, secant p ~ 1.618
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.02 Root finding toolbox

**Goal:** Pick the right root finder

- **Derive by hand:** Bisection, secant, Brent hybrids
- **Code from scratch:** Implement secant and a simplified Brent
- **Interactive lab:** Race of methods on a hard function
- **Test that proves it:** Brent never fails on bracketed roots in the test suite
- **Pro tool:** scipy.optimize.brentq
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.03 Nonlinear systems

**Goal:** Solve coupled nonlinear equations

- **Derive by hand:** Multidimensional Newton with Jacobian
- **Code from scratch:** Newton for a two-cable equilibrium problem
- **Interactive lab:** Cable net settling to equilibrium
- **Test that proves it:** Residual below 1e-10 within 10 iterations
- **Pro tool:** scipy.optimize.root
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.04 Interpolation

**Goal:** Reconstruct data between samples

- **Derive by hand:** Lagrange polynomials, Runge phenomenon
- **Code from scratch:** Lagrange vs Chebyshev nodes
- **Interactive lab:** Node selector showing Runge wiggles
- **Test that proves it:** Chebyshev max error falls as n grows
- **Pro tool:** scipy.interpolate
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.05 Splines

**Goal:** Smooth curves for CAD and data

- **Derive by hand:** Cubic spline continuity conditions
- **Code from scratch:** Natural cubic spline from scratch (tridiagonal solve)
- **Interactive lab:** Drag control points of a bike-frame tube curve
- **Test that proves it:** Second derivative continuous at knots
- **Pro tool:** scipy.interpolate.CubicSpline
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.06 Numerical differentiation of noisy data

**Goal:** Differentiate measurements safely

- **Derive by hand:** Noise amplification ~ eps/h
- **Code from scratch:** Savitzky-Golay smoothing then differentiate
- **Interactive lab:** Noisy vs filtered derivative
- **Test that proves it:** Filtered derivative error below raw
- **Pro tool:** scipy.signal.savgol_filter
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.07 Gaussian quadrature

**Goal:** Integrate with the fewest evaluations

- **Derive by hand:** Orthogonal polynomials, exactness degree 2n-1
- **Code from scratch:** Gauss-Legendre nodes via Golub-Welsch
- **Interactive lab:** Node positions on [-1, 1]
- **Test that proves it:** n-point rule exact for polynomial degree 2n-1
- **Pro tool:** numpy.polynomial.legendre
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.08 Explicit Euler and stability

**Goal:** Understand why simulations blow up

- **Derive by hand:** Stability region abs(1 + h lambda) <= 1
- **Code from scratch:** Euler on y' = -k y for varying h
- **Interactive lab:** Stability region plot with step slider
- **Test that proves it:** Diverges exactly when h > 2/k
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.09 Runge-Kutta methods

**Goal:** Integrate ODEs accurately

- **Derive by hand:** Derive RK2 from Taylor matching; RK4 tableau
- **Code from scratch:** Implement RK4 and a Butcher tableau engine
- **Interactive lab:** Pendulum trajectories with Euler vs RK4
- **Test that proves it:** RK4 error slope is 4
- **Pro tool:** scipy.integrate.solve_ivp
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.10 Adaptive step size

**Goal:** Spend effort where dynamics are fast

- **Derive by hand:** Embedded RK pairs, error estimate
- **Code from scratch:** Implement RK45 (Dormand-Prince) step control
- **Interactive lab:** Step size plot during a bouncing-ball impact
- **Test that proves it:** Global error stays near tolerance
- **Pro tool:** SciPy RK45
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.11 Stiff equations and implicit methods

**Goal:** Simulate stiff systems like contact or chemistry

- **Derive by hand:** Implicit Euler, A-stability
- **Code from scratch:** Implicit Euler with Newton for a stiff spring
- **Interactive lab:** Explicit vs implicit with large steps
- **Test that proves it:** Implicit stays stable at h = 100/k
- **Pro tool:** SciPy BDF/Radau
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.12 Symplectic integrators

**Goal:** Conserve energy over long simulations

- **Derive by hand:** Hamiltonian structure, leapfrog/Verlet
- **Code from scratch:** Velocity Verlet for orbits and pendulums
- **Interactive lab:** Energy drift plot Euler vs Verlet
- **Test that proves it:** Verlet energy error bounded over 10^5 steps
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.13 Finite differences in 1D

**Goal:** Discretise derivatives on a grid

- **Derive by hand:** Stencils from Taylor expansion
- **Code from scratch:** Build second-derivative matrix and solve -u'' = f
- **Interactive lab:** Grid refinement viewer
- **Test that proves it:** Error O(h^2)
- **Pro tool:** scipy.sparse.diags
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.14 Heat equation: explicit and implicit

**Goal:** Solve parabolic PDEs safely

- **Derive by hand:** FTCS stability r = alpha dt/dx^2 <= 1/2; Crank-Nicolson
- **Code from scratch:** Implement FTCS and Crank-Nicolson
- **Interactive lab:** Rod cooling animation with stability slider
- **Test that proves it:** FTCS blows up for r > 0.5
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.15 Wave equation and CFL

**Goal:** Solve hyperbolic PDEs

- **Derive by hand:** CFL condition c dt/dx <= 1
- **Code from scratch:** Leapfrog wave solver for a guitar string
- **Interactive lab:** String with CFL number slider
- **Test that proves it:** Stable and accurate for CFL = 1
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.16 Advection and upwinding

**Goal:** Transport quantities without wiggles

- **Derive by hand:** Upwind scheme, numerical diffusion via modified equation
- **Code from scratch:** Upwind vs central for a pollutant pulse in a river
- **Interactive lab:** Pulse travelling down a channel
- **Test that proves it:** Upwind stays monotone; central oscillates
- **Pro tool:** NumPy
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.17 2D Poisson solvers

**Goal:** Solve steady 2D fields

- **Derive by hand:** 5-point stencil, Jacobi/Gauss-Seidel/SOR
- **Code from scratch:** SOR solver with optimal omega
- **Interactive lab:** Convergence race of Jacobi vs SOR
- **Test that proves it:** SOR converges in fewer iterations by an order of magnitude
- **Pro tool:** scipy.sparse.linalg.spsolve
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.18 Multigrid intuition

**Goal:** Understand why the fastest solvers are fast

- **Derive by hand:** Smoothing high frequencies, coarse-grid correction
- **Code from scratch:** Two-grid V-cycle for 1D Poisson
- **Interactive lab:** Error frequency content per cycle
- **Test that proves it:** Residual reduction per cycle independent of n
- **Pro tool:** PyAMG
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.19 Optimisation algorithms

**Goal:** Optimise designs numerically

- **Derive by hand:** Gradient descent, BFGS, line search
- **Code from scratch:** Implement BFGS with Armijo line search
- **Interactive lab:** Path on the Rosenbrock valley
- **Test that proves it:** Reaches minimum (1,1) within 1e-6
- **Pro tool:** scipy.optimize.minimize
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)

## 04.20 Verification and validation

**Goal:** Prove your solver is right

- **Derive by hand:** Method of manufactured solutions
- **Code from scratch:** MMS test for your Poisson solver
- **Interactive lab:** Observed order vs refinement plot
- **Test that proves it:** Observed order equals 2
- **Pro tool:** pytest
- **ETH course:** Numerical methods for engineers (generic; ETH offers several numerics courses)
