# Phase 01: Analysis 1: Single-Variable Calculus

*Analysis 1*

Limits, derivatives, integrals and series, each built as code you can trust.

- **ETH reference:** Analysis 1
- **Real-world anchors:** The slope of a Bali rice terrace and the curve of the Rhine Falls
- **Lessons:** 18

## 01.01 Numbers, sequences and limits

**Goal:** Understand convergence well enough to trust an iteration

- **Derive by hand:** Epsilon-N definition, monotone bounded sequences converge
- **Code from scratch:** Iterate a_{n+1} = (a_n + 2/a_n)/2 and find the N for a given epsilon
- **Interactive lab:** Sequence plot with an epsilon band you can drag
- **Test that proves it:** Iteration hits sqrt(2) within 1e-12 in fewer than 7 steps
- **Pro tool:** NumPy
- **ETH course:** Analysis 1

## 01.02 Continuity and the intermediate value theorem

**Goal:** Prove a root exists, then find it

- **Derive by hand:** IVT, sign change implies root
- **Code from scratch:** Implement bisection with guaranteed error bound (b-a)/2^n
- **Interactive lab:** Bisection animator on a terrace-height function
- **Test that proves it:** Bisection error never exceeds the theoretical bound
- **Pro tool:** SciPy optimize.bisect
- **ETH course:** Analysis 1

## 01.03 The derivative from first principles

**Goal:** Derive the derivative as a limit and measure it numerically

- **Derive by hand:** f'(x) = lim (f(x+h)-f(x))/h; Taylor shows O(h) error
- **Code from scratch:** Forward, backward and central differences; plot error vs h on log-log
- **Interactive lab:** Error-vs-h plot showing truncation vs round-off V-shape
- **Test that proves it:** Central difference error slope is 2 on the log-log plot
- **Pro tool:** NumPy
- **ETH course:** Analysis 1

## 01.04 Differentiation rules

**Goal:** Derive product, quotient and chain rules and apply them to engineering formulas

- **Derive by hand:** Chain rule from the limit definition
- **Code from scratch:** Build forward-mode automatic differentiation with dual numbers
- **Interactive lab:** Dual-number calculator showing value and derivative together
- **Test that proves it:** Dual-number derivative of sin(x^2) matches 2x cos(x^2) to machine precision
- **Pro tool:** JAX
- **ETH course:** Analysis 1

## 01.05 Newton's method

**Goal:** Solve nonlinear equations fast

- **Derive by hand:** Linearise f around x_n: x_{n+1} = x_n - f/f'; quadratic convergence
- **Code from scratch:** Newton solver with your dual-number derivatives
- **Interactive lab:** Tangent-line animation converging on a root
- **Test that proves it:** Digits of accuracy roughly double per step near a simple root
- **Pro tool:** SciPy optimize.newton
- **ETH course:** Analysis 1

## 01.06 Optimisation in one variable

**Goal:** Find the cheapest or strongest design

- **Derive by hand:** f'=0, second-derivative test
- **Code from scratch:** Maximise the volume of an open box folded from sheet metal
- **Interactive lab:** Drag the cut size and see volume vs size
- **Test that proves it:** Optimum cut equals side/6 analytically
- **Pro tool:** SciPy optimize.minimize_scalar
- **ETH course:** Analysis 1

## 01.07 Taylor series

**Goal:** Approximate any smooth function and know the error

- **Derive by hand:** Taylor's theorem with Lagrange remainder
- **Code from scratch:** Build Taylor polynomials of sin and exp; plot remainder vs bound
- **Interactive lab:** Add terms one by one and watch the fit spread
- **Test that proves it:** Actual error is always below the Lagrange bound
- **Pro tool:** SymPy series
- **ETH course:** Analysis 1

## 01.08 Small-angle physics

**Goal:** Justify sin(theta) ~ theta with numbers, not faith

- **Derive by hand:** Remainder of sin Taylor series
- **Code from scratch:** Compare exact and linearised pendulum periods vs amplitude
- **Interactive lab:** Pendulum period vs amplitude chart
- **Test that proves it:** Linear model error is below 1% for amplitude under about 23 degrees
- **Pro tool:** NumPy
- **ETH course:** Analysis 1

## 01.09 The Riemann integral

**Goal:** Build the integral as a limit of sums

- **Derive by hand:** Riemann sums, refinement, fundamental theorem of calculus
- **Code from scratch:** Left, right, midpoint sums; convergence plot
- **Interactive lab:** Rectangles refining under a curve
- **Test that proves it:** Midpoint error decreases as O(1/n^2)
- **Pro tool:** NumPy
- **ETH course:** Analysis 1

## 01.10 Trapezoid and Simpson rules

**Goal:** Integrate measured data accurately

- **Derive by hand:** Derive error terms from Taylor expansion
- **Code from scratch:** Implement composite trapezoid and Simpson
- **Interactive lab:** Rule comparison on an irrigation-channel cross-section profile
- **Test that proves it:** Simpson integrates cubics exactly
- **Pro tool:** scipy.integrate
- **ETH course:** Analysis 1

## 01.11 Work, area and centroids

**Goal:** Use integrals for real geometric quantities

- **Derive by hand:** Centroid x_c = int x dA / int dA
- **Code from scratch:** Compute centroid of an arbitrary 2D profile from polyline points
- **Interactive lab:** Drag polygon vertices, watch the centroid move
- **Test that proves it:** Centroid of a semicircle lands at 4r/(3 pi)
- **Pro tool:** shapely
- **ETH course:** Analysis 1

## 01.12 Exponentials and logarithms

**Goal:** Model growth, decay and cooling

- **Derive by hand:** e^x as the solution of y' = y; ln as its inverse
- **Code from scratch:** Fit an exponential cooling curve of a coffee cup by linear regression on ln
- **Interactive lab:** Cooling curve with live fit
- **Test that proves it:** Fitted time constant recovers the synthetic value within 2%
- **Pro tool:** NumPy polyfit
- **ETH course:** Analysis 1

## 01.13 Improper integrals

**Goal:** Handle infinite domains and singularities

- **Derive by hand:** Convergence of int 1/x^p
- **Code from scratch:** Numerically integrate with variable substitution to remove singularities
- **Interactive lab:** Tail-area visualiser
- **Test that proves it:** int_1^inf 1/x^2 = 1 to 1e-8
- **Pro tool:** scipy.integrate.quad
- **ETH course:** Analysis 1

## 01.14 Series and convergence tests

**Goal:** Know when a sum converges

- **Derive by hand:** Ratio, root and comparison tests
- **Code from scratch:** Sum series with Kahan compensated summation
- **Interactive lab:** Partial sum plot for several series
- **Test that proves it:** Kahan sum of 10^7 terms beats naive sum in accuracy
- **Pro tool:** math.fsum
- **ETH course:** Analysis 1

## 01.15 First-order ODEs

**Goal:** Solve the simplest dynamic models

- **Derive by hand:** Separation of variables, integrating factors
- **Code from scratch:** Solve tank draining (Torricelli) analytically and by explicit Euler
- **Interactive lab:** Draining tank animation vs analytical curve
- **Test that proves it:** Euler error shrinks linearly with step size
- **Pro tool:** scipy.integrate.solve_ivp
- **ETH course:** Analysis 1

## 01.16 Second-order linear ODEs

**Goal:** Solve the mass-spring-damper by hand

- **Derive by hand:** Characteristic equation, under/critically/over-damped cases
- **Code from scratch:** Closed-form solution plus numeric check
- **Interactive lab:** Damping slider sweeps through the three regimes
- **Test that proves it:** Numeric and analytical responses agree to 1e-6
- **Pro tool:** SciPy
- **ETH course:** Analysis 1

## 01.17 Complex numbers for engineers

**Goal:** Use e^{i omega t} to make oscillations easy

- **Derive by hand:** Euler's formula, phasors
- **Code from scratch:** Phasor calculator for summing oscillations
- **Interactive lab:** Rotating phasor diagram
- **Test that proves it:** Sum of two phasors equals sum of time signals at every sample
- **Pro tool:** NumPy complex
- **ETH course:** Analysis 1

## 01.18 The Rhine Falls trajectory

**Goal:** Combine kinematics and calculus on a real anchor

- **Derive by hand:** Projectile motion, ignoring air drag as a stated simplification
- **Code from scratch:** Estimate where a water parcel leaving the falls lip lands; add linear drag later
- **Interactive lab:** Trajectory with drag on/off toggle
- **Test that proves it:** No-drag range matches v^2 sin(2 theta)/g for flat ground
- **Pro tool:** NumPy
- **ETH course:** Analysis 1
