# Mechanical Engineering from Scratch: Curriculum

20 phases, 356 lessons. Every lesson: derive by hand, code from scratch, prove with a test, then meet the pro tool.

ETH course names refer to the ETH Zurich D-MAVT BSc (Programme Regulations 2022) where marked; others are generic descriptions. Not affiliated with or endorsed by ETH Zurich.

| # | Phase | ETH reference | Lessons |
|---|---|---|---|
| 00 | [Engineering Toolkit & Setup](phase-00-setup.md) | Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice | 12 |
| 01 | [Analysis 1: Single-Variable Calculus](phase-01-analysis-1.md) | Analysis 1 | 18 |
| 02 | [Linear Algebra](phase-02-linear-algebra.md) | Lineare Algebra 1 / Lineare Algebra 2 | 16 |
| 03 | [Analysis 2 & 3: Multivariable, Vector Calculus, PDEs](phase-03-analysis-2-3.md) | Analysis 2 / Analysis 3 | 20 |
| 04 | [Numerical Methods](phase-04-numerical-methods.md) | Numerical methods for engineers (generic; ETH offers several numerics courses) (generic) | 20 |
| 05 | [Statics & Free-Body Diagrams](phase-05-statics.md) | Mechanik 1: Kinematik und Statik | 20 |
| 06 | [Strength of Materials (Deformable Solids)](phase-06-deformable-solids.md) | Mechanik 2 (Deformable Solids) | 22 |
| 07 | [Dynamics](phase-07-dynamics.md) | Mechanik 3: Dynamik | 20 |
| 08 | [Vibrations & Waves](phase-08-vibrations.md) | Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic) | 16 |
| 09 | [Materials & Manufacturing](phase-09-materials-manufacturing.md) | Werkstoffe und Fertigung; Engineering Design and Material Selection | 30 |
| 10 | [Thermodynamics](phase-10-thermodynamics.md) | Thermodynamik 1 / Thermodynamik 2 | 20 |
| 11 | [Fluid Dynamics 1: Foundations](phase-11-fluid-dynamics-1.md) | Fluiddynamik | 20 |
| 12 | [Fluid Dynamics 2: Viscous Flows, Turbulence, Aero](phase-12-fluid-dynamics-2.md) | Fluiddynamik (later chapters) and fluid-dynamics electives (generic) | 18 |
| 13 | [Heat Transfer](phase-13-heat-transfer.md) | Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives | 14 |
| 14 | [CAD & Technical Drawing](phase-14-cad.md) | Engineering Design and Material Selection (sketching, technical drawing, CAD) | 12 |
| 15 | [Machine Elements & Design](phase-15-machine-design.md) | Maschinenkonstruktion (Machine Design) and Dimensionierung courses | 18 |
| 16 | [Finite Element Method from Scratch](phase-16-fem.md) | Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives (generic) | 18 |
| 17 | [Computational Fluid Dynamics from Scratch](phase-17-cfd.md) | Computational fluid dynamics electives (generic) (generic) | 18 |
| 18 | [Measurement, Signals & Control](phase-18-measurement-control.md) | Regelungstechnik 1; Praktikum / lab courses (generic for measurement) | 14 |
| 19 | [Capstone Projects](phase-19-capstone.md) | Fokus-Projekt / Bachelor-Arbeit (project format, not course content) | 10 |
# Phase 00: Engineering Toolkit & Setup

*Werkzeugkasten*

Python, NumPy, plotting, units and dimensional analysis: the bench you will build every machine on.

- **ETH reference:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice
- **Real-world anchors:** Measuring a Bali river and a Zurich tram with the same units discipline
- **Lessons:** 12

## 00.01 Your engineering notebook

**Goal:** Set up Python, NumPy, Matplotlib and a lesson repo you will keep for the whole course

- **Derive by hand:** No math yet: define the derive-code-test-keep loop and what counts as a passing artifact
- **Code from scratch:** Create a venv, a `lessons/` package and a `pytest` smoke test that imports numpy
- **Interactive lab:** Terminal checklist that turns green as each tool is detected
- **Test that proves it:** `pytest -q` passes and prints the NumPy version
- **Pro tool:** Python, NumPy, pytest, JupyterLab
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.02 SI units and why rockets crash

**Goal:** Never mix units again by carrying them through every calculation

- **Derive by hand:** Base units, derived units, unit algebra as exponent vectors over (m, kg, s, A, K, mol, cd)
- **Code from scratch:** Write a tiny `Quantity` class that stores value plus exponent vector and refuses to add incompatible units
- **Interactive lab:** Unit-calculator widget: type 3 kN*m/(2 s) and see the derived unit
- **Test that proves it:** Adding metres to seconds raises; N*m/s simplifies to W
- **Pro tool:** pint (Python units library)
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.03 Dimensional analysis and Buckingham Pi

**Goal:** Reduce a messy physical problem to a few dimensionless groups

- **Derive by hand:** Buckingham Pi theorem as the null space of the dimension matrix
- **Code from scratch:** Compute Pi groups with an SVD null-space of the dimension matrix
- **Interactive lab:** Pick variables of a pendulum or pipe flow and watch the Pi groups appear
- **Test that proves it:** Pendulum yields T*sqrt(g/L) = f(theta0); drag yields Re and drag coefficient
- **Pro tool:** SymPy
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.04 Estimation and Fermi problems

**Goal:** Get the order of magnitude right before computing anything

- **Derive by hand:** Product of bounded factors, log-normal error propagation
- **Code from scratch:** Monte Carlo a Fermi estimate (water flowing through a Subak canal per day) with log-uniform inputs
- **Interactive lab:** Slider histogram of the estimate distribution
- **Test that proves it:** Median estimate lies within one decade of a hand calculation
- **Pro tool:** NumPy random
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.05 Vectors, arrays and broadcasting

**Goal:** Think in arrays instead of loops

- **Derive by hand:** Vector spaces in R^n, element-wise vs matrix operations
- **Code from scratch:** Vectorise a loop that computes forces on 10^5 particles; compare timing
- **Interactive lab:** Loop vs vectorised race bar
- **Test that proves it:** Vectorised result equals loop result to 1e-12 and is at least 20x faster
- **Pro tool:** NumPy
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.06 Plotting like an engineer

**Goal:** Make plots that answer a question: axes, units, log scales

- **Derive by hand:** Log scales turn power laws into straight lines: log y = log a + b log x
- **Code from scratch:** Build a `plot_eng()` helper with units in labels and log-log fitting
- **Interactive lab:** Toggle linear/log axes on a power-law dataset
- **Test that proves it:** Fitted exponent on synthetic y = 3x^1.5 data recovers 1.5 +- 0.01
- **Pro tool:** Matplotlib
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.07 Error, precision and floating point

**Goal:** Know when your computer is lying to you

- **Derive by hand:** IEEE 754 doubles, machine epsilon, catastrophic cancellation
- **Code from scratch:** Compute (1 - cos x)/x^2 naively and stably for small x
- **Interactive lab:** Slider of x showing the naive formula collapse
- **Test that proves it:** Stable version stays within 1e-10 of 0.5 for x = 1e-8
- **Pro tool:** NumPy finfo
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.08 Reading data from sensors

**Goal:** Load, clean and resample a real time series

- **Derive by hand:** Sampling, aliasing intuition, linear interpolation
- **Code from scratch:** Parse a CSV of Limmat river levels (sample data you record or download), resample to hourly
- **Interactive lab:** Interactive time-series zoom
- **Test that proves it:** Resampled series has no NaNs and preserves the mean within 1%
- **Pro tool:** pandas
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.09 Version control for engineers

**Goal:** Keep every artifact reproducible

- **Derive by hand:** Content hashing: a commit is a hash of a tree of hashes
- **Code from scratch:** Write a 30-line content-addressed store that hashes files like git does
- **Interactive lab:** Visual DAG of your lesson commits
- **Test that proves it:** Same file content gives the same hash; changed byte changes it
- **Pro tool:** git
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.10 Free-body thinking before formulas

**Goal:** Learn the one habit that solves most mechanics problems: isolate, draw, balance

- **Derive by hand:** Newton's laws as balance statements over a cut-out system
- **Code from scratch:** Encode a free-body diagram as a list of force vectors and check if it balances
- **Interactive lab:** Drag-a-cut tool on a bicycle: cut anywhere and see the internal forces you must add
- **Test that proves it:** Sum of forces on a static bike frame cut equals zero within 1e-9
- **Pro tool:** Paper, then Python
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.11 Symbolic math as a checker

**Goal:** Use computer algebra to verify hand derivations, not replace them

- **Derive by hand:** Differentiation rules, simplification, substitution
- **Code from scratch:** Derive a result by hand, then assert equality with SymPy `simplify(a-b)==0`
- **Interactive lab:** Side-by-side hand/CAS derivation viewer
- **Test that proves it:** Your hand derivative of x^x matches SymPy
- **Pro tool:** SymPy
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice

## 00.12 The Swiss rail timetable problem

**Goal:** Practise turning a real system into a model with stated assumptions

- **Derive by hand:** Kinematics of constant acceleration: s = v t - v^2/(2a) phases
- **Code from scratch:** Model an SBB-style train run between two stations with accel/cruise/brake phases
- **Interactive lab:** Speed-time plot with sliders for max speed and acceleration
- **Test that proves it:** Travel time matches the analytical trapezoid profile to 1e-6
- **Pro tool:** Python
- **ETH course:** Informatik 1 / Informatik 2 (programming foundations); generic engineering-computing practice
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
# Phase 02: Linear Algebra

*Lineare Algebra*

Systems of equations, matrices and eigenvalues, the machinery behind every solver in this course.

- **ETH reference:** Lineare Algebra 1 / Lineare Algebra 2
- **Real-world anchors:** Every truss, every FEM mesh, every Swiss bridge is a matrix
- **Lessons:** 16

## 02.01 Vectors and geometry

**Goal:** Represent forces and positions as vectors

- **Derive by hand:** Dot product, cross product, projections
- **Code from scratch:** Vector toolkit: projection, angle, area via cross product
- **Interactive lab:** 3D vector playground with draggable arrows
- **Test that proves it:** Cross product is orthogonal to both inputs within 1e-12
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.02 Systems of linear equations

**Goal:** Turn equilibrium into Ax = b

- **Derive by hand:** Row picture vs column picture
- **Code from scratch:** Write a truss joint equilibrium system by hand for 3 joints
- **Interactive lab:** Two-line intersection and column combination views
- **Test that proves it:** Your system reproduces hand-solved forces
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.03 Gaussian elimination

**Goal:** Solve Ax = b from scratch

- **Derive by hand:** Elimination as a sequence of elementary matrices
- **Code from scratch:** Implement Gaussian elimination with partial pivoting
- **Interactive lab:** Step-through elimination animation
- **Test that proves it:** Matches numpy.linalg.solve to 1e-10 on random 50x50 systems
- **Pro tool:** LAPACK via NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.04 LU decomposition

**Goal:** Factor once, solve many load cases

- **Derive by hand:** A = PLU
- **Code from scratch:** Implement LU and forward/back substitution
- **Interactive lab:** Multiple load cases on one bridge reuse the factorisation
- **Test that proves it:** Reconstruct PA = LU within 1e-12
- **Pro tool:** scipy.linalg.lu
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.05 Determinants and invertibility

**Goal:** Know when a structure is a mechanism

- **Derive by hand:** det as signed volume; det = 0 means singular
- **Code from scratch:** Detect a missing truss member via near-zero determinant
- **Interactive lab:** Delete a member, watch det go to zero ([Break the bridge](#lab-truss))
- **Test that proves it:** Mechanism truss yields condition number above 1e12
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.06 Vector spaces and rank

**Goal:** Count independent equations and unknowns

- **Derive by hand:** Rank-nullity theorem
- **Code from scratch:** Compute rank via elimination; find null space
- **Interactive lab:** Null-space visualiser: rigid-body modes of an unsupported truss
- **Test that proves it:** Free 2D truss has a 3-dimensional null space
- **Pro tool:** SciPy null_space
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.07 Orthogonality and least squares

**Goal:** Fit models to noisy measurements

- **Derive by hand:** Normal equations A^T A x = A^T b, projection
- **Code from scratch:** Fit a calibration line to strain-gauge data
- **Interactive lab:** Residuals shown as vertical bars
- **Test that proves it:** Matches numpy.linalg.lstsq
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.08 QR and Gram-Schmidt

**Goal:** Solve least squares stably

- **Derive by hand:** Gram-Schmidt orthogonalisation, A = QR
- **Code from scratch:** Implement modified Gram-Schmidt and solve least squares
- **Interactive lab:** Orthogonalisation animation in 3D
- **Test that proves it:** Q^T Q = I within 1e-12
- **Pro tool:** numpy.linalg.qr
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.09 Eigenvalues and eigenvectors

**Goal:** Find the natural directions of a linear map

- **Derive by hand:** det(A - lambda I) = 0
- **Code from scratch:** Power iteration and inverse iteration
- **Interactive lab:** Unit circle mapped to an ellipse with eigenvectors highlighted
- **Test that proves it:** Power iteration finds the dominant eigenvalue within 1e-8
- **Pro tool:** numpy.linalg.eig
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.10 Symmetric matrices and the spectral theorem

**Goal:** Understand why stiffness matrices behave nicely

- **Derive by hand:** Real eigenvalues, orthogonal eigenvectors
- **Code from scratch:** Jacobi eigenvalue algorithm for symmetric matrices
- **Interactive lab:** Rotation sweeps zeroing off-diagonals
- **Test that proves it:** Eigenvalues match numpy.linalg.eigh
- **Pro tool:** SciPy eigh
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.11 Positive definiteness and energy

**Goal:** Connect matrices to strain energy

- **Derive by hand:** x^T K x > 0 for a stable structure
- **Code from scratch:** Cholesky factorisation from scratch
- **Interactive lab:** Energy bowl surface for a 2-DOF spring system
- **Test that proves it:** Cholesky fails exactly when matrix is indefinite
- **Pro tool:** scipy.linalg.cholesky
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.12 Singular value decomposition

**Goal:** Find the most important modes of any data

- **Derive by hand:** A = U Sigma V^T
- **Code from scratch:** SVD via eigen-decomposition of A^T A; low-rank image of a Swiss landscape
- **Interactive lab:** Rank slider reconstructing an image
- **Test that proves it:** Rank-k error equals the (k+1)th singular value in 2-norm
- **Pro tool:** numpy.linalg.svd
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.13 Coordinate transformations

**Goal:** Rotate frames without mistakes

- **Derive by hand:** Rotation matrices, orthogonality, composition
- **Code from scratch:** Rotate a stress tensor and a force between frames
- **Interactive lab:** Rotating frame gizmo
- **Test that proves it:** R^T R = I and det R = 1
- **Pro tool:** scipy.spatial.transform
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.14 Sparse matrices

**Goal:** Solve systems with millions of unknowns

- **Derive by hand:** Sparsity patterns, fill-in
- **Code from scratch:** CSR storage and sparse matrix-vector product
- **Interactive lab:** Sparsity spy plot of a 2D mesh Laplacian
- **Test that proves it:** CSR matvec equals dense matvec
- **Pro tool:** scipy.sparse
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.15 Iterative solvers

**Goal:** Solve huge systems without factorising

- **Derive by hand:** Jacobi, Gauss-Seidel convergence via spectral radius
- **Code from scratch:** Implement conjugate gradient
- **Interactive lab:** Residual history plot
- **Test that proves it:** CG converges in at most n steps in exact arithmetic on SPD systems (check small n)
- **Pro tool:** scipy.sparse.linalg.cg
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2

## 02.16 Linear maps in mechanics

**Goal:** See statics, FEM and vibration as the same algebra

- **Derive by hand:** K u = f, M u'' + K u = 0
- **Code from scratch:** Unify a spring chain as K u = f and as an eigenproblem
- **Interactive lab:** Spring chain with static and modal views
- **Test that proves it:** Static solution satisfies equilibrium at every node
- **Pro tool:** NumPy
- **ETH course:** Lineare Algebra 1 / Lineare Algebra 2
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
# Phase 06: Strength of Materials (Deformable Solids)

*Mechanik 2: Deformierbare Festkörper*

Stress, strain, beams, torsion, buckling and energy methods: how parts deform and when they fail.

- **ETH reference:** Mechanik 2 (Deformable Solids)
- **Real-world anchors:** Bike frames, Swiss rail tracks, bamboo beams in Bali
- **Lessons:** 22

## 06.01 Stress

**Goal:** Understand stress as force per area on a cut

- **Derive by hand:** Cauchy stress vector t = sigma n
- **Code from scratch:** Compute traction on any plane from a stress tensor
- **Interactive lab:** Rotate a cutting plane and see traction
- **Test that proves it:** Traction equals sigma.n
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.02 Strain

**Goal:** Measure deformation

- **Derive by hand:** Small strain epsilon = (grad u + grad u^T)/2
- **Code from scratch:** Strain from a displacement field on a grid
- **Interactive lab:** Deforming grid with strain colouring
- **Test that proves it:** Rigid rotation produces zero small strain at first order
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.03 Hooke's law

**Goal:** Relate stress and strain

- **Derive by hand:** Isotropic elasticity with E, nu; Lame constants
- **Code from scratch:** 3D Hooke's law in matrix (Voigt) form
- **Interactive lab:** Stress-strain slider for steel, aluminium, bamboo
- **Test that proves it:** Uniaxial test returns E and lateral contraction nu
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.04 Axial bars

**Goal:** Compute stretch of rods and cables

- **Derive by hand:** delta = N L/(E A)
- **Code from scratch:** Stepped bar elongation solver
- **Interactive lab:** Rod with load and area sliders
- **Test that proves it:** Matches closed form for stepped bar
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.05 Statically indeterminate bars

**Goal:** Use compatibility when statics is not enough

- **Derive by hand:** Equilibrium + compatibility + constitutive law
- **Code from scratch:** Solve a bar fixed at both ends with a midpoint load
- **Interactive lab:** Wall reactions as load moves
- **Test that proves it:** Reactions sum to applied load
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.06 Thermal stress

**Goal:** Predict stress from temperature change

- **Derive by hand:** epsilon_th = alpha delta T
- **Code from scratch:** Compute stress in a constrained rail on a hot day
- **Interactive lab:** Rail temperature slider with buckling warning
- **Test that proves it:** Stress = -E alpha delta T for fully constrained bar
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.07 Stress transformation and Mohr's circle

**Goal:** Find principal stresses and max shear

- **Derive by hand:** Rotation of 2D stress; Mohr's circle
- **Code from scratch:** Mohr's circle generator
- **Interactive lab:** Rotate element and track point on Mohr's circle
- **Test that proves it:** Principal stresses equal eigenvalues of sigma
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.08 Failure criteria

**Goal:** Decide if a part yields

- **Derive by hand:** Tresca, von Mises; distortion energy derivation
- **Code from scratch:** von Mises and Tresca calculators
- **Interactive lab:** Yield surfaces in principal stress space
- **Test that proves it:** Pure shear yields at tau = sigma_y/sqrt(3) under von Mises
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.09 Beam bending: Euler-Bernoulli

**Goal:** Derive the bending stress formula

- **Derive by hand:** Plane sections remain plane; sigma = M y / I
- **Code from scratch:** Bending stress field over a cross-section
- **Interactive lab:** Cantilever with draggable load and stress colours ([Cantilever beam (hero)](#hero))
- **Test that proves it:** Max stress equals M c / I
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.10 Second moment of area

**Goal:** Pick efficient cross-sections

- **Derive by hand:** I = int y^2 dA; parallel axis theorem
- **Code from scratch:** Section property calculator for I, T, box, tube
- **Interactive lab:** Compare sections at equal mass
- **Test that proves it:** I-section beats rectangle at equal area
- **Pro tool:** sectionproperties
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.11 Beam deflection

**Goal:** Compute how far a beam bends

- **Derive by hand:** EI w'''' = q, boundary conditions
- **Code from scratch:** Integrate the beam equation numerically and symbolically
- **Interactive lab:** Live deflected shape vs load position
- **Test that proves it:** Cantilever tip deflection equals PL^3/(3EI)
- **Pro tool:** SymPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.12 Superposition and indeterminate beams

**Goal:** Solve continuous beams

- **Derive by hand:** Superposition of standard cases + compatibility
- **Code from scratch:** Propped cantilever via superposition
- **Interactive lab:** Support removal to see moment redistribution
- **Test that proves it:** Prop reaction under uniform load q equals 3qL/8
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.13 Shear stress in beams

**Goal:** Find where shear peaks

- **Derive by hand:** Jourawski formula tau = V Q /(I b)
- **Code from scratch:** Shear distribution over rectangular and I sections
- **Interactive lab:** Shear profile plot by section
- **Test that proves it:** Rectangle max shear equals 1.5 V/A
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.14 Torsion of circular shafts

**Goal:** Size a drive shaft

- **Derive by hand:** tau = T r / J, phi = T L /(G J)
- **Code from scratch:** Shaft stress and twist calculator
- **Interactive lab:** Twisting shaft with rotating grid lines
- **Test that proves it:** Hollow shaft J matches pi(D^4-d^4)/32
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.15 Thin-walled torsion

**Goal:** Analyse bike frame tubes and boxes

- **Derive by hand:** Bredt-Batho shear flow q = T/(2A_m)
- **Code from scratch:** Torsional stiffness of closed vs open sections
- **Interactive lab:** Slit tube comparison
- **Test that proves it:** Open section dramatically less stiff than closed
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.16 Combined loading

**Goal:** Superpose axial, bending and torsion

- **Derive by hand:** Superposition then von Mises
- **Code from scratch:** Check a crank arm under pedalling load
- **Interactive lab:** Pedal force slider with stress hotspot
- **Test that proves it:** Hotspot location matches hand analysis
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.17 Strain energy

**Goal:** Use energy to compute deflections

- **Derive by hand:** U = int sigma epsilon /2 dV
- **Code from scratch:** Strain energy of bar, beam, shaft
- **Interactive lab:** Energy bar chart per load type
- **Test that proves it:** Energy equals work of external load P delta/2
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.18 Castigliano's theorem

**Goal:** Find deflections from energy derivatives

- **Derive by hand:** delta_i = dU/dP_i
- **Code from scratch:** Deflection of a curved bar (bike hook)
- **Interactive lab:** Load point selector
- **Test that proves it:** Matches direct integration
- **Pro tool:** SymPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.19 Buckling of columns

**Goal:** Predict when slender members fail suddenly

- **Derive by hand:** Euler buckling P_cr = pi^2 E I/(K L)^2
- **Code from scratch:** Eigenvalue solution of discretised column
- **Interactive lab:** Compress a column until it snaps sideways
- **Test that proves it:** Discrete critical load converges to Euler
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.20 Imperfections and real buckling

**Goal:** Understand why real columns fail below Euler

- **Derive by hand:** Imperfect column amplification 1/(1 - P/P_cr)
- **Code from scratch:** Imperfect column load-deflection curve
- **Interactive lab:** Imperfection slider
- **Test that proves it:** Deflection grows without bound as P approaches P_cr
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.21 Pressure vessels

**Goal:** Size a tank or pipe wall

- **Derive by hand:** Thin wall: sigma_hoop = p r / t, sigma_axial = p r/(2t)
- **Code from scratch:** Penstock wall thickness calculator for an alpine hydro plant
- **Interactive lab:** Pressure slider with hoop stress
- **Test that proves it:** Hoop stress is twice axial stress
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)

## 06.22 Stress concentrations

**Goal:** Understand why parts crack at holes and fillets

- **Derive by hand:** Kirsch solution: K_t = 3 for a hole in a plate
- **Code from scratch:** Plot Kirsch stress field around a hole
- **Interactive lab:** Plate with hole stress heat-map
- **Test that proves it:** Peak stress equals 3 times remote stress
- **Pro tool:** NumPy
- **ETH course:** Mechanik 2 (Deformable Solids)
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
# Phase 09: Materials & Manufacturing

*Werkstoffe und Fertigung*

Atoms to alloys to finished parts: why materials behave as they do and how things are made.

- **ETH reference:** Werkstoffe und Fertigung; Engineering Design and Material Selection
- **Real-world anchors:** Swiss watch steels, aluminium bike frames, Bali bamboo and teak; Swiss precision machining, Bali bamboo workshops, a maker space 3D printer
- **Lessons:** 30

## 09.01 Atomic bonding and stiffness

**Goal:** Explain where Young's modulus comes from

- **Derive by hand:** Lennard-Jones potential, stiffness = curvature at minimum
- **Code from scratch:** Derive E from a pair potential
- **Interactive lab:** Interatomic potential with draggable atoms
- **Test that proves it:** Stiffness equals second derivative at r0
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.02 Crystal structures

**Goal:** Recognise FCC, BCC, HCP

- **Derive by hand:** Packing factor, coordination numbers
- **Code from scratch:** Generate lattices and compute packing factor
- **Interactive lab:** 3D lattice viewer
- **Test that proves it:** FCC packing factor = 0.74
- **Pro tool:** ASE
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.03 Defects and dislocations

**Goal:** Explain why metals are ductile

- **Derive by hand:** Theoretical vs real shear strength
- **Code from scratch:** Estimate ideal shear strength G/(2 pi)
- **Interactive lab:** Dislocation glide animation
- **Test that proves it:** Ideal strength orders of magnitude above measured
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.04 The tensile test

**Goal:** Read a stress-strain curve

- **Derive by hand:** Engineering vs true stress, necking (Considere)
- **Code from scratch:** Process raw tensile data: E, yield (0.2%), UTS
- **Interactive lab:** Interactive tensile curve
- **Test that proves it:** 0.2% offset yield correctly extracted
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.05 Hardening mechanisms

**Goal:** Make metals stronger

- **Derive by hand:** Hall-Petch, solid solution, precipitation
- **Code from scratch:** Fit Hall-Petch to grain-size data
- **Interactive lab:** Grain size slider
- **Test that proves it:** Fitted slope recovers synthetic constant
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.06 Phase diagrams

**Goal:** Read alloy phase diagrams

- **Derive by hand:** Lever rule
- **Code from scratch:** Lever-rule calculator for a binary diagram
- **Interactive lab:** Click a point, get phase fractions
- **Test that proves it:** Fractions sum to 1
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.07 Steel and heat treatment

**Goal:** Understand quench, temper and the iron-carbon diagram

- **Derive by hand:** Fe-C diagram, TTT curves qualitative
- **Code from scratch:** Phase fraction tool for plain carbon steel
- **Interactive lab:** Cooling-rate slider over TTT sketch
- **Test that proves it:** Eutectoid composition near 0.76% C (textbook value)
- **Pro tool:** Thermo-Calc concepts (open: pycalphad)
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.08 Diffusion

**Goal:** Model carburising and drying

- **Derive by hand:** Fick's laws, erf solution
- **Code from scratch:** Solve carburising depth
- **Interactive lab:** Concentration profile over time
- **Test that proves it:** Depth grows with sqrt(D t)
- **Pro tool:** SciPy special.erf
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.09 Polymers

**Goal:** Understand viscoelastic behaviour

- **Derive by hand:** Maxwell and Kelvin-Voigt models
- **Code from scratch:** Simulate creep and relaxation
- **Interactive lab:** Spring-dashpot builder
- **Test that proves it:** Maxwell relaxes exponentially with tau = eta/E
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.10 Composites

**Goal:** Design with fibres

- **Derive by hand:** Rule of mixtures (Voigt/Reuss bounds)
- **Code from scratch:** Laminate stiffness for a carbon bike frame ply
- **Interactive lab:** Fibre angle slider
- **Test that proves it:** Longitudinal modulus follows Voigt bound
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.11 Natural materials: bamboo and wood

**Goal:** Engineer with Bali bamboo responsibly

- **Derive by hand:** Anisotropy, graded fibre density
- **Code from scratch:** Bending stiffness of a hollow bamboo culm
- **Interactive lab:** Culm wall thickness slider
- **Test that proves it:** Hollow culm stiffness-to-weight beats solid rod
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.12 Fracture mechanics

**Goal:** Predict crack growth

- **Derive by hand:** Griffith energy balance, K_I = Y sigma sqrt(pi a)
- **Code from scratch:** Critical crack size calculator
- **Interactive lab:** Crack length slider with fracture threshold
- **Test that proves it:** Fracture when K_I >= K_IC
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.13 Fatigue

**Goal:** Design parts that survive millions of cycles

- **Derive by hand:** S-N curves, Basquin, Goodman mean-stress correction
- **Code from scratch:** Goodman diagram and life estimate
- **Interactive lab:** Load-cycle slider on a crank
- **Test that proves it:** Infinite life inside the Goodman line
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.14 Corrosion

**Goal:** Keep alpine and tropical structures alive

- **Derive by hand:** Galvanic series, Faraday's law for corrosion rate
- **Code from scratch:** Corrosion rate from current density
- **Interactive lab:** Galvanic couple picker
- **Test that proves it:** Rate proportional to current
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.15 Material selection charts

**Goal:** Choose materials systematically

- **Derive by hand:** Performance indices, e.g. E^(1/2)/rho for light stiff beams
- **Code from scratch:** Ashby-style chart from an open dataset you assemble
- **Interactive lab:** Interactive selection line
- **Test that proves it:** Index ranking matches derivation
- **Pro tool:** Matplotlib
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.16 Sustainability and embodied energy

**Goal:** Compare materials by footprint

- **Derive by hand:** Life-cycle energy = mass * embodied energy per kg
- **Code from scratch:** Compare frame materials using cited data you collect
- **Interactive lab:** Material footprint bars
- **Test that proves it:** Totals reproduce input data
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.17 Manufacturing process map

**Goal:** Pick the right process family

- **Derive by hand:** Process selection by volume, material, tolerance
- **Code from scratch:** Process selector rule engine
- **Interactive lab:** Interactive process map
- **Test that proves it:** Selector reproduces textbook examples
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.18 Metal cutting mechanics

**Goal:** Understand chip formation

- **Derive by hand:** Merchant's circle, shear angle
- **Code from scratch:** Cutting force model
- **Interactive lab:** Rake angle slider
- **Test that proves it:** Force decreases with rake angle in the model
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.19 Tool life and economics

**Goal:** Choose cutting speeds

- **Derive by hand:** Taylor tool life V T^n = C, cost minimisation
- **Code from scratch:** Optimal cutting speed calculator
- **Interactive lab:** Cost vs speed curve
- **Test that proves it:** Optimum where derivative is zero
- **Pro tool:** SciPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.20 CNC and G-code

**Goal:** Turn geometry into toolpaths

- **Derive by hand:** Toolpath offsets, interpolation
- **Code from scratch:** Write a G-code generator for a 2D pocket
- **Interactive lab:** G-code toolpath simulator
- **Test that proves it:** Toolpath stays inside boundary with tool radius offset
- **Pro tool:** FreeCAD Path / CAM
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.21 Turning and milling

**Goal:** Compute feeds, speeds and surface finish

- **Derive by hand:** Ra ~ f^2/(32 r)
- **Code from scratch:** Surface roughness estimator
- **Interactive lab:** Feed slider with surface profile
- **Test that proves it:** Roughness scales with feed squared
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.22 Sheet metal forming

**Goal:** Bend sheet without cracking

- **Derive by hand:** Bend allowance, springback
- **Code from scratch:** Flat pattern calculator
- **Interactive lab:** Bend angle slider
- **Test that proves it:** Bend allowance formula satisfied
- **Pro tool:** FreeCAD SheetMetal
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.23 Bulk forming

**Goal:** Understand forging and extrusion

- **Derive by hand:** Slab method, flow stress
- **Code from scratch:** Extrusion force estimate
- **Interactive lab:** Ram speed and ratio sliders
- **Test that proves it:** Force increases with extrusion ratio
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.24 Casting

**Goal:** Design castings that solidify soundly

- **Derive by hand:** Chvorinov's rule t = B (V/A)^n
- **Code from scratch:** Riser sizing tool
- **Interactive lab:** Solidification order animation
- **Test that proves it:** Riser solidifies after casting
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.25 Injection moulding

**Goal:** Understand plastic part design

- **Derive by hand:** Fill pressure, cooling time ~ thickness^2
- **Code from scratch:** Cooling time estimator
- **Interactive lab:** Wall thickness slider
- **Test that proves it:** Time scales with thickness squared
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.26 Welding and joining physics

**Goal:** Control heat input

- **Derive by hand:** Rosenthal moving heat source (simplified)
- **Code from scratch:** Weld pool temperature field
- **Interactive lab:** Torch speed slider
- **Test that proves it:** Peak temperature decreases with speed
- **Pro tool:** NumPy
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.27 Additive manufacturing

**Goal:** Print functional parts

- **Derive by hand:** Layer adhesion, anisotropy, overhang angles
- **Code from scratch:** Slicer from scratch: slice an STL into layers and perimeters
- **Interactive lab:** Layer-by-layer preview
- **Test that proves it:** Sliced area matches cross-section area
- **Pro tool:** PrusaSlicer / CuraEngine
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.28 Metrology on the shop floor

**Goal:** Measure what you make

- **Derive by hand:** Measurement uncertainty, Abbe principle
- **Code from scratch:** Uncertainty budget for a caliper measurement
- **Interactive lab:** Abbe error visual
- **Test that proves it:** Combined uncertainty via root sum of squares
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.29 Quality and statistical process control

**Goal:** Keep processes in control

- **Derive by hand:** Control charts, Cp and Cpk
- **Code from scratch:** SPC chart generator
- **Interactive lab:** Process drift simulation
- **Test that proves it:** Cpk computed correctly on synthetic data
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection

## 09.30 Building with bamboo

**Goal:** Apply manufacturing thinking to natural materials

- **Derive by hand:** Joint strength, treatment, variability
- **Code from scratch:** Statistical design value from bamboo test data you gather
- **Interactive lab:** Joint type comparison
- **Test that proves it:** 5th-percentile design value computed
- **Pro tool:** Python
- **ETH course:** Werkstoffe und Fertigung; Engineering Design and Material Selection
# Phase 10: Thermodynamics

*Thermodynamik 1 & 2*

Energy, entropy, cycles and real fluids, with property tables built by code.

- **ETH reference:** Thermodynamik 1 / Thermodynamik 2
- **Real-world anchors:** Alpine pumped hydro, a Swiss heat pump, a Bali scooter engine
- **Lessons:** 20

## 10.01 Systems, states and properties

**Goal:** Define what you are analysing

- **Derive by hand:** Closed vs open systems, state postulate
- **Code from scratch:** Represent a thermodynamic state as an object with consistency checks
- **Interactive lab:** System boundary drawer
- **Test that proves it:** Over-specified state raises an error
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.02 The ideal gas

**Goal:** Use the simplest equation of state well

- **Derive by hand:** pv = RT, kinetic theory derivation
- **Code from scratch:** Derive pressure from molecular collisions in a box simulation
- **Interactive lab:** Gas particle box with temperature slider
- **Test that proves it:** Simulated pressure matches nRT/V within noise
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.03 Work and heat

**Goal:** Compute boundary work in processes

- **Derive by hand:** W = int p dV
- **Code from scratch:** Integrate p-V work for isothermal, isobaric, polytropic
- **Interactive lab:** Draggable p-V path
- **Test that proves it:** Isothermal work equals nRT ln(V2/V1)
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.04 The first law for closed systems

**Goal:** Balance energy

- **Derive by hand:** dU = dQ - dW
- **Code from scratch:** First-law solver for piston-cylinder problems
- **Interactive lab:** Energy flow Sankey
- **Test that proves it:** Energy residual zero
- **Pro tool:** Python
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.05 The first law for open systems

**Goal:** Analyse turbines, pumps and nozzles

- **Derive by hand:** Steady-flow energy equation, enthalpy
- **Code from scratch:** SFEE solver
- **Interactive lab:** Turbine/nozzle selector
- **Test that proves it:** Nozzle exit velocity from enthalpy drop
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.06 Pure substances and phase change

**Goal:** Read steam tables like a pro

- **Derive by hand:** Saturation, quality, two-phase mixtures
- **Code from scratch:** Build a lookup + interpolation over a saturation table
- **Interactive lab:** T-v diagram with draggable state
- **Test that proves it:** Quality interpolation reproduces table values
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.07 Pumped-storage hydropower

**Goal:** Size an alpine pumped-storage plant energy budget

- **Derive by hand:** E = rho g h V eta
- **Code from scratch:** Energy and round-trip efficiency calculator
- **Interactive lab:** Reservoir up/down animation
- **Test that proves it:** Stored energy scales linearly with head and volume
- **Pro tool:** Python
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.08 The second law

**Goal:** Know what is impossible

- **Derive by hand:** Kelvin-Planck, Clausius statements, Carnot efficiency
- **Code from scratch:** Carnot efficiency calculator and proof by contradiction notes
- **Interactive lab:** Heat engine with reservoir sliders
- **Test that proves it:** No cycle beats 1 - Tc/Th
- **Pro tool:** Python
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.09 Entropy

**Goal:** Quantify irreversibility

- **Derive by hand:** dS = dQ_rev/T, entropy generation
- **Code from scratch:** Compute entropy change for mixing water streams
- **Interactive lab:** Mixing lab
- **Test that proves it:** Entropy generation always >= 0
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.10 Isentropic efficiency

**Goal:** Model real turbines and compressors

- **Derive by hand:** eta_s definitions
- **Code from scratch:** Compressor exit temperature with efficiency
- **Interactive lab:** h-s diagram
- **Test that proves it:** eta = 1 recovers isentropic exit state
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.11 Exergy

**Goal:** Measure useful energy

- **Derive by hand:** Exergy destruction = T0 S_gen
- **Code from scratch:** Exergy balance of a heat exchanger
- **Interactive lab:** Exergy loss bars
- **Test that proves it:** Gouy-Stodola relation holds
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.12 Otto and Diesel cycles

**Goal:** Analyse piston engines

- **Derive by hand:** Air-standard cycle efficiency 1 - r^(1-k)
- **Code from scratch:** Simulate Otto cycle
- **Interactive lab:** p-V loop with compression ratio slider
- **Test that proves it:** Efficiency matches formula
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.13 The Brayton cycle

**Goal:** Analyse gas turbines and jet engines

- **Derive by hand:** Pressure ratio efficiency
- **Code from scratch:** Brayton cycle with real component efficiencies
- **Interactive lab:** T-s loop
- **Test that proves it:** Ideal Brayton efficiency = 1 - r_p^((1-k)/k)
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.14 The Rankine cycle

**Goal:** Analyse steam power plants

- **Derive by hand:** Rankine with superheat and reheat
- **Code from scratch:** Rankine solver using property library
- **Interactive lab:** T-s diagram
- **Test that proves it:** Energy balance closes
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.15 Refrigeration and heat pumps

**Goal:** Understand Swiss heat pumps

- **Derive by hand:** COP, vapour-compression cycle
- **Code from scratch:** Heat pump cycle with R290 properties
- **Interactive lab:** COP vs outdoor temperature
- **Test that proves it:** COP below Carnot COP
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.16 Real gases

**Goal:** Go beyond ideal gas

- **Derive by hand:** Van der Waals, compressibility factor
- **Code from scratch:** Solve van der Waals cubic for v
- **Interactive lab:** Isotherms with Maxwell construction
- **Test that proves it:** Z approaches 1 at low pressure
- **Pro tool:** CoolProp
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.17 Gas mixtures and psychrometrics

**Goal:** Model humid air for Bali and Zurich climates

- **Derive by hand:** Partial pressures, relative humidity, dew point
- **Code from scratch:** Psychrometric calculator
- **Interactive lab:** Psychrometric chart with Bali vs Zurich points
- **Test that proves it:** Dew point equals temperature at RH 100%
- **Pro tool:** psychrolib
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.18 Combustion

**Goal:** Compute flame temperatures and emissions

- **Derive by hand:** Stoichiometry, adiabatic flame temperature
- **Code from scratch:** Adiabatic flame temperature of methane-air
- **Interactive lab:** Equivalence ratio slider
- **Test that proves it:** Peak near stoichiometric
- **Pro tool:** Cantera
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.19 Chemical equilibrium

**Goal:** Predict composition at high temperature

- **Derive by hand:** Gibbs minimisation
- **Code from scratch:** Minimise Gibbs energy for a simple dissociation
- **Interactive lab:** Equilibrium vs temperature
- **Test that proves it:** Matches Cantera equilibrium
- **Pro tool:** Cantera
- **ETH course:** Thermodynamik 1 / Thermodynamik 2

## 10.20 Energy systems of Switzerland

**Goal:** Put thermodynamics in a national context

- **Derive by hand:** Energy balances in TWh
- **Code from scratch:** Model a seasonal energy balance with clearly labelled assumed data
- **Interactive lab:** Seasonal storage graph
- **Test that proves it:** Balance closes by construction
- **Pro tool:** Python
- **ETH course:** Thermodynamik 1 / Thermodynamik 2
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
# Phase 12: Fluid Dynamics 2: Viscous Flows, Turbulence, Aero

*Fluiddynamik (Teil 2)*

Boundary layers, drag, pipe losses, turbulence, compressible flow and aerodynamics.

- **ETH reference:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)
- **Real-world anchors:** A cyclist in the Swiss wind, Rhine turbulence, a kite over Bali
- **Lessons:** 18

## 12.01 Exact viscous solutions

**Goal:** Solve Couette, Poiseuille and Stokes problems

- **Derive by hand:** Reduced NS for parallel flows
- **Code from scratch:** Stokes first problem (impulsively started plate)
- **Interactive lab:** Growing diffusion layer
- **Test that proves it:** Layer grows as sqrt(nu t)
- **Pro tool:** SciPy special
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.02 Low-Reynolds flow

**Goal:** Understand micro-swimmers and settling

- **Derive by hand:** Stokes drag F = 6 pi mu R U
- **Code from scratch:** Settling velocity of sediment in a river
- **Interactive lab:** Particle size slider
- **Test that proves it:** Matches Stokes law at low Re
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.03 Boundary layers

**Goal:** Derive Prandtl's boundary layer idea

- **Derive by hand:** Scaling delta ~ x Re_x^(-1/2)
- **Code from scratch:** Solve the Blasius equation by shooting
- **Interactive lab:** Velocity profile along a plate
- **Test that proves it:** f''(0) approx 0.332
- **Pro tool:** SciPy solve_ivp
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.04 Separation

**Goal:** Explain why flow detaches behind a boulder

- **Derive by hand:** Adverse pressure gradient
- **Code from scratch:** Thwaites method for separation point
- **Interactive lab:** Cylinder with separation marker
- **Test that proves it:** Laminar separation predicted near 104-110 degrees (literature range)
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.05 Drag

**Goal:** Estimate drag on bodies

- **Derive by hand:** Pressure vs friction drag, C_D
- **Code from scratch:** Drag of a cyclist using C_D A
- **Interactive lab:** Riding position slider
- **Test that proves it:** Power scales with v^3
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.06 Lift and airfoils

**Goal:** Explain how wings work without myths

- **Derive by hand:** Kutta condition, thin airfoil theory C_L = 2 pi alpha
- **Code from scratch:** Thin airfoil lift slope calculator
- **Interactive lab:** Airfoil with angle-of-attack slider
- **Test that proves it:** Slope 2 pi per radian
- **Pro tool:** XFOIL
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.07 Panel methods

**Goal:** Compute pressure on arbitrary airfoils

- **Derive by hand:** Source/vortex panels
- **Code from scratch:** Vortex panel method from scratch
- **Interactive lab:** Pressure distribution plot
- **Test that proves it:** Matches thin airfoil theory at small angle
- **Pro tool:** XFOIL
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.08 Turbulence phenomenology

**Goal:** Understand chaotic flow

- **Derive by hand:** Energy cascade, Kolmogorov scales
- **Code from scratch:** Generate and analyse a synthetic turbulent signal
- **Interactive lab:** Energy spectrum with -5/3 guide
- **Test that proves it:** Kolmogorov length from dissipation formula
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.09 Reynolds averaging

**Goal:** Model turbulence for engineering

- **Derive by hand:** RANS, Reynolds stresses, closure problem
- **Code from scratch:** Compute Reynolds stresses from synthetic velocity data
- **Interactive lab:** Mean vs fluctuation decomposition
- **Test that proves it:** Fluctuation mean is zero
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.10 Turbulent pipe flow

**Goal:** Predict pressure losses in real pipes

- **Derive by hand:** Darcy-Weisbach, Colebrook equation
- **Code from scratch:** Solve Colebrook for friction factor
- **Interactive lab:** Moody chart generator
- **Test that proves it:** Laminar limit f = 64/Re
- **Pro tool:** fluids (Python package)
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.11 Pipe networks

**Goal:** Design water supply systems

- **Derive by hand:** Hardy Cross method
- **Code from scratch:** Solve a looped village water network
- **Interactive lab:** Network with flow arrows
- **Test that proves it:** Mass conserved at every node
- **Pro tool:** EPANET / WNTR
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.12 Pumps and systems

**Goal:** Match pumps to pipelines

- **Derive by hand:** Pump curve vs system curve, affinity laws
- **Code from scratch:** Operating point solver
- **Interactive lab:** Pump speed slider
- **Test that proves it:** Affinity laws scale flow linearly with speed
- **Pro tool:** fluids
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.13 Compressible flow basics

**Goal:** Understand speed of sound and Mach number

- **Derive by hand:** a = sqrt(k R T), stagnation properties
- **Code from scratch:** Isentropic relations calculator
- **Interactive lab:** Mach number slider
- **Test that proves it:** T0/T = 1 + (k-1)/2 Ma^2
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.14 Nozzles and choking

**Goal:** Design converging-diverging nozzles

- **Derive by hand:** Area-Mach relation
- **Code from scratch:** Nozzle flow solver with shock location
- **Interactive lab:** CD nozzle with back-pressure slider
- **Test that proves it:** Choked mass flow independent of back pressure
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.15 Normal shocks

**Goal:** Compute jumps across shocks

- **Derive by hand:** Rankine-Hugoniot relations
- **Code from scratch:** Normal shock calculator
- **Interactive lab:** Shock tube animation
- **Test that proves it:** Entropy increases across shock
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.16 Vortex shedding

**Goal:** Explain cable singing and bridge oscillations

- **Derive by hand:** Strouhal number St ~ 0.2
- **Code from scratch:** Shedding frequency for a ski-lift cable
- **Interactive lab:** Karman street visual
- **Test that proves it:** Frequency scales with U/D
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.17 Wind and buildings

**Goal:** Estimate wind loads

- **Derive by hand:** Dynamic pressure, gust factors (labelled simplification)
- **Code from scratch:** Wind load on a signboard
- **Interactive lab:** Wind speed slider
- **Test that proves it:** Load scales with v^2
- **Pro tool:** Python
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)

## 12.18 Mixing and dispersion in rivers

**Goal:** Model pollutant spread in the Limmat

- **Derive by hand:** Advection-diffusion equation
- **Code from scratch:** Gaussian plume in a channel
- **Interactive lab:** Dye release lab
- **Test that proves it:** Total mass conserved
- **Pro tool:** NumPy
- **ETH course:** Fluiddynamik (later chapters) and fluid-dynamics electives (generic)
# Phase 13: Heat Transfer

*Wärmeübertragung*

Conduction, convection, radiation and heat exchangers derived and simulated.

- **ETH reference:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives
- **Real-world anchors:** Keeping a Bali house cool, an alpine hut warm, a CPU alive
- **Lessons:** 14

## 13.01 Conduction and Fourier's law

**Goal:** Derive heat flux from temperature gradients

- **Derive by hand:** q = -k grad T
- **Code from scratch:** 1D steady conduction through a wall
- **Interactive lab:** Wall with thermal conductivity slider
- **Test that proves it:** Linear profile in homogeneous wall
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.02 Thermal resistance networks

**Goal:** Analyse layered walls like circuits

- **Derive by hand:** R = L/(k A), series and parallel
- **Code from scratch:** Wall resistance network solver
- **Interactive lab:** Insulation layer builder for an alpine hut
- **Test that proves it:** Heat flow equals delta T / R_total
- **Pro tool:** Python
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.03 Cylindrical and spherical conduction

**Goal:** Insulate pipes correctly

- **Derive by hand:** R = ln(r2/r1)/(2 pi k L), critical radius
- **Code from scratch:** Critical insulation radius calculator
- **Interactive lab:** Pipe insulation thickness slider
- **Test that proves it:** Critical radius = k/h
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.04 Fins

**Goal:** Cool engines and electronics

- **Derive by hand:** Fin equation m^2 = h P/(k A), efficiency
- **Code from scratch:** Fin temperature profile solver
- **Interactive lab:** Fin length slider
- **Test that proves it:** Long fin heat rate sqrt(h P k A) theta_b
- **Pro tool:** SciPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.05 Transient conduction: lumped

**Goal:** Decide when lumped models work

- **Derive by hand:** Biot number, exponential cooling
- **Code from scratch:** Lumped cooling of a coconut in a fridge (stated assumptions)
- **Interactive lab:** Biot slider with validity warning
- **Test that proves it:** Valid when Bi < 0.1
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.06 Transient conduction: distributed

**Goal:** Solve heating of thick bodies

- **Derive by hand:** Heat equation, Heisler-style solutions
- **Code from scratch:** 1D/2D transient conduction FD solver
- **Interactive lab:** Temperature heat-map animation
- **Test that proves it:** Converges to analytic series
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.07 Convection fundamentals

**Goal:** Understand h and the boundary layer

- **Derive by hand:** Nusselt number, thermal boundary layer
- **Code from scratch:** Compute h from Nu correlations
- **Interactive lab:** Flow speed slider over a plate
- **Test that proves it:** Laminar plate Nu ~ Re^(1/2) Pr^(1/3)
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.08 Forced convection correlations

**Goal:** Use correlations responsibly

- **Derive by hand:** Dittus-Boelter, Gnielinski (range of validity)
- **Code from scratch:** Correlation library with validity checks
- **Interactive lab:** Pipe flow heat-transfer calculator
- **Test that proves it:** Raises warning outside validity range
- **Pro tool:** ht (Python package)
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.09 Natural convection

**Goal:** Model hot plates and room air

- **Derive by hand:** Grashof, Rayleigh, Boussinesq approximation
- **Code from scratch:** Natural convection h on a vertical plate
- **Interactive lab:** Rayleigh slider
- **Test that proves it:** Transition near Ra ~ 1e9 (typical criterion)
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.10 Radiation

**Goal:** Compute radiative exchange

- **Derive by hand:** Stefan-Boltzmann, emissivity, view factors
- **Code from scratch:** View factor by Monte Carlo ray casting
- **Interactive lab:** Tropical roof vs reflective paint
- **Test that proves it:** Parallel plates view factor approaches 1 when large
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.11 Solar energy

**Goal:** Model solar gain in Bali vs Zurich

- **Derive by hand:** Solar geometry, irradiance on tilted planes
- **Code from scratch:** Solar position and panel yield model with labelled inputs
- **Interactive lab:** Sun path visual for both locations
- **Test that proves it:** Noon elevation matches 90 - latitude + declination
- **Pro tool:** pvlib
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.12 Heat exchangers: LMTD

**Goal:** Size heat exchangers

- **Derive by hand:** Log-mean temperature difference
- **Code from scratch:** LMTD design calculator
- **Interactive lab:** Parallel vs counterflow profiles
- **Test that proves it:** Counterflow needs less area for same duty
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.13 Heat exchangers: effectiveness-NTU

**Goal:** Rate exchangers when outlets are unknown

- **Derive by hand:** epsilon-NTU relations
- **Code from scratch:** epsilon-NTU solver
- **Interactive lab:** NTU slider
- **Test that proves it:** Same result as LMTD when outlets known
- **Pro tool:** NumPy
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives

## 13.14 Electronics and battery cooling

**Goal:** Apply everything to a real thermal design

- **Derive by hand:** Thermal network + convection + radiation
- **Code from scratch:** Thermal model of an e-bike battery pack
- **Interactive lab:** Load profile with temperature trace
- **Test that proves it:** Steady state consistent with resistance network
- **Pro tool:** Python
- **ETH course:** Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives
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
# Phase 15: Machine Elements & Design

*Maschinenkonstruktion / Dimensionierung*

Dimensioning shafts, bearings, gears, bolts and welds: from load to safe, buildable part.

- **ETH reference:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses
- **Real-world anchors:** Bike drivetrains, ski-lift grips, Swiss watch gears, a Bali scooter
- **Lessons:** 18

## 15.01 The design process

**Goal:** Go from need to concept to detail

- **Derive by hand:** Requirements, morphological box, evaluation matrix
- **Code from scratch:** Weighted decision matrix tool
- **Interactive lab:** Concept scoring board
- **Test that proves it:** Ranking reproducible from weights
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.02 Safety factors and reliability

**Goal:** Pick safety factors with reasons

- **Derive by hand:** Stress-strength interference, reliability index
- **Code from scratch:** Monte Carlo failure probability
- **Interactive lab:** Overlapping distributions
- **Test that proves it:** Analytical normal-normal result matched
- **Pro tool:** SciPy stats
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.03 Tolerances and fits

**Goal:** Make parts that assemble

- **Derive by hand:** ISO fits, tolerance stack-up (worst case vs RSS)
- **Code from scratch:** Stack-up calculator
- **Interactive lab:** Stack chain visual
- **Test that proves it:** RSS <= worst case
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.04 Shaft design

**Goal:** Size shafts for strength and fatigue

- **Derive by hand:** Combined bending-torsion, Goodman-based shaft equations
- **Code from scratch:** Shaft diameter calculator
- **Interactive lab:** Load layout editor
- **Test that proves it:** Larger safety factor yields larger diameter
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.05 Keys, splines and press fits

**Goal:** Transmit torque from hub to shaft

- **Derive by hand:** Lame thick-cylinder equations for interference
- **Code from scratch:** Press-fit pressure and torque capacity
- **Interactive lab:** Interference slider
- **Test that proves it:** Contact pressure matches Lame solution
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.06 Rolling bearings

**Goal:** Choose bearings by life

- **Derive by hand:** L10 = (C/P)^p with p = 3 for ball bearings
- **Code from scratch:** Bearing life calculator
- **Interactive lab:** Load vs life curve
- **Test that proves it:** Doubling load cuts life by factor 8
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.07 Plain bearings and lubrication

**Goal:** Understand hydrodynamic lubrication

- **Derive by hand:** Reynolds equation for thin films
- **Code from scratch:** 1D Reynolds equation solver for a slider bearing
- **Interactive lab:** Pressure build-up in a wedge
- **Test that proves it:** Load capacity positive only for converging wedge
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.08 Gear geometry

**Goal:** Understand involute gears

- **Derive by hand:** Involute curve, base circle, law of gearing
- **Code from scratch:** Generate involute profiles
- **Interactive lab:** Meshing gear animation
- **Test that proves it:** Constant velocity ratio along line of action
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.09 Gear strength

**Goal:** Size gears against bending and pitting

- **Derive by hand:** Lewis bending equation, Hertz contact basics
- **Code from scratch:** Gear stress estimates
- **Interactive lab:** Module/face-width sliders
- **Test that proves it:** Stress decreases with module
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.10 Gear trains and planetary gears

**Goal:** Design transmissions

- **Derive by hand:** Willis equation for planetary sets
- **Code from scratch:** Planetary ratio solver
- **Interactive lab:** Animated planetary gearbox (e-bike hub)
- **Test that proves it:** Willis relation satisfied
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.11 Belts and chains

**Goal:** Design bike and conveyor drives

- **Derive by hand:** Chain kinematics, polygonal effect, belt tensions
- **Code from scratch:** Chain speed fluctuation calculator
- **Interactive lab:** Chainring tooth-count slider
- **Test that proves it:** Fluctuation decreases with tooth count
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.12 Bolted joints

**Goal:** Design joints that do not loosen

- **Derive by hand:** Joint diagram, preload, stiffness ratio
- **Code from scratch:** Bolted joint diagram tool
- **Interactive lab:** Preload slider
- **Test that proves it:** External load share follows stiffness ratio
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.13 Welded joints

**Goal:** Size welds

- **Derive by hand:** Throat stress, fatigue classes concept
- **Code from scratch:** Fillet weld stress calculator
- **Interactive lab:** Weld layout editor
- **Test that proves it:** Stress inversely proportional to throat size
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.14 Springs

**Goal:** Design helical springs

- **Derive by hand:** k = G d^4/(8 D^3 n), Wahl factor
- **Code from scratch:** Spring designer
- **Interactive lab:** Coil count slider
- **Test that proves it:** Stiffness matches formula
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.15 Clutches and brakes

**Goal:** Size friction devices

- **Derive by hand:** Uniform wear vs uniform pressure torque
- **Code from scratch:** Disc brake torque for a bike
- **Interactive lab:** Brake lever force slider
- **Test that proves it:** Uniform wear torque <= uniform pressure
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.16 Linkages and mechanisms

**Goal:** Synthesise motion

- **Derive by hand:** Freudenstein equation
- **Code from scratch:** Three-position linkage synthesis
- **Interactive lab:** Linkage designer
- **Test that proves it:** Synthesised linkage passes through targets
- **Pro tool:** NumPy
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.17 Ski-lift grip and cable design

**Goal:** Integrate elements on a Swiss anchor

- **Derive by hand:** Friction grip force, cable tension, safety factors
- **Code from scratch:** Detachable grip clamp force model (educational)
- **Interactive lab:** Slope and load sliders
- **Test that proves it:** Grip holds when friction capacity > slope component times SF
- **Pro tool:** Python
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses

## 15.18 Design review and documentation

**Goal:** Ship designs others can build

- **Derive by hand:** Calculation reports, traceability
- **Code from scratch:** Auto-generate a calculation report from your Python modules
- **Interactive lab:** Report preview
- **Test that proves it:** Report reproduces all numbers from code
- **Pro tool:** Jupyter / Quarto
- **ETH course:** Maschinenkonstruktion (Machine Design) and Dimensionierung courses
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
# Phase 18: Measurement, Signals & Control

*Messtechnik und Regelungstechnik*

Sensors, uncertainty, signal processing, system identification and feedback control.

- **ETH reference:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)
- **Real-world anchors:** Measuring the Limmat flow, stabilising a bike, a Bali sensor buoy
- **Lessons:** 14

## 18.01 Measurement uncertainty

**Goal:** Report results honestly

- **Derive by hand:** GUM: type A/B, propagation
- **Code from scratch:** Uncertainty propagation by linearisation and Monte Carlo
- **Interactive lab:** Input uncertainty sliders
- **Test that proves it:** Both methods agree for near-linear models
- **Pro tool:** uncertainties (Python)
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.02 Sensors and transducers

**Goal:** Know how sensors really work

- **Derive by hand:** Strain gauge bridge equations
- **Code from scratch:** Wheatstone bridge output model
- **Interactive lab:** Bridge with strain slider
- **Test that proves it:** Quarter bridge output ~ V GF epsilon/4
- **Pro tool:** Python
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.03 Sampling and aliasing

**Goal:** Sample without lying

- **Derive by hand:** Nyquist theorem
- **Code from scratch:** Demonstrate aliasing on a rotating wheel
- **Interactive lab:** Wagon-wheel effect lab
- **Test that proves it:** Aliased frequency formula verified
- **Pro tool:** NumPy
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.04 Filters

**Goal:** Clean noisy signals

- **Derive by hand:** Low-pass RC, Butterworth design
- **Code from scratch:** Implement IIR filter from difference equation
- **Interactive lab:** Filter cutoff slider
- **Test that proves it:** Matches scipy.signal.lfilter
- **Pro tool:** SciPy signal
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.05 Data acquisition with microcontrollers

**Goal:** Log real data

- **Derive by hand:** ADC resolution, quantisation noise q/sqrt(12)
- **Code from scratch:** Read an accelerometer via serial and log
- **Interactive lab:** Live plot
- **Test that proves it:** Quantisation noise matches theory
- **Pro tool:** Arduino / MicroPython
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.06 River flow measurement

**Goal:** Measure the Limmat or a Bali canal

- **Derive by hand:** Velocity-area method, float method corrections
- **Code from scratch:** Discharge from float measurements
- **Interactive lab:** Cross-section integrator
- **Test that proves it:** Discharge equals sum of v_i A_i
- **Pro tool:** Python
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.07 Strain and force measurement

**Goal:** Build a load cell

- **Derive by hand:** Bending beam load cell design
- **Code from scratch:** Calibrate a load cell with least squares
- **Interactive lab:** Calibration curve
- **Test that proves it:** Linearity error reported
- **Pro tool:** NumPy
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.08 Temperature measurement

**Goal:** Measure temperature with known lag

- **Derive by hand:** First-order sensor dynamics
- **Code from scratch:** Thermocouple time-constant identification
- **Interactive lab:** Step response fit
- **Test that proves it:** Fitted tau within 5% of synthetic
- **Pro tool:** SciPy
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.09 System identification

**Goal:** Build models from data

- **Derive by hand:** ARX least squares
- **Code from scratch:** Identify a motor model from step data
- **Interactive lab:** Model vs data overlay
- **Test that proves it:** Identified parameters match synthetic
- **Pro tool:** SysIdentPy / python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.10 Transfer functions and block diagrams

**Goal:** Model dynamic systems for control

- **Derive by hand:** Laplace domain, poles and zeros
- **Code from scratch:** Transfer function algebra class
- **Interactive lab:** Pole-zero map
- **Test that proves it:** Step response from TF matches ODE
- **Pro tool:** python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.11 Feedback and stability

**Goal:** Understand why feedback works

- **Derive by hand:** Closed-loop poles, Routh-Hurwitz
- **Code from scratch:** Root locus from scratch
- **Interactive lab:** Gain slider moving poles
- **Test that proves it:** Unstable when poles cross into RHP
- **Pro tool:** python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.12 PID control

**Goal:** Tune a controller

- **Derive by hand:** P, I, D effects, Ziegler-Nichols
- **Code from scratch:** PID controller simulation with anti-windup
- **Interactive lab:** Cruise control of an e-bike
- **Test that proves it:** Integral action removes steady-state error
- **Pro tool:** python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.13 Frequency response and robustness

**Goal:** Design robust controllers

- **Derive by hand:** Bode, Nyquist, gain and phase margins
- **Code from scratch:** Compute margins numerically
- **Interactive lab:** Bode plot with margin markers
- **Test that proves it:** Margins match python-control
- **Pro tool:** python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)

## 18.14 State space and LQR

**Goal:** Control multi-variable systems

- **Derive by hand:** x' = A x + B u, Riccati equation
- **Code from scratch:** LQR for an inverted pendulum
- **Interactive lab:** Balance the pendulum lab
- **Test that proves it:** Closed-loop eigenvalues all negative real part
- **Pro tool:** python-control
- **ETH course:** Regelungstechnik 1; Praktikum / lab courses (generic for measurement)
# Phase 19: Capstone Projects

*Fokus-Projekt / Bachelor-Arbeit style capstone*

Integrate everything: derive, simulate, build, measure and publish a working machine or study.

- **ETH reference:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)
- **Real-world anchors:** Real projects in Bali and Switzerland, each with a public artifact
- **Lessons:** 10

## 19.01 Capstone method

**Goal:** Plan a project that ends with evidence

- **Derive by hand:** Requirements, risk, verification matrix
- **Code from scratch:** Project template repo with verification matrix
- **Interactive lab:** Gantt and risk board
- **Test that proves it:** Every requirement has a test
- **Pro tool:** git, Quarto
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.02 Coconut eddy: from field video to CFD

**Goal:** Reproduce the Bali boulder eddy

- **Derive by hand:** Strouhal, recirculation, particle residence time
- **Code from scratch:** Combine video particle tracking with your CFD solver
- **Interactive lab:** Coconut lab extended ([The coconut that never escapes](https://andreolf.github.io/coconut-lab/))
- **Test that proves it:** Model residence time compared with your measurement, discrepancy explained
- **Pro tool:** OpenFOAM, OpenCV
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.03 Subak weir network

**Goal:** Model a full terrace water-sharing network

- **Derive by hand:** Weir equations + network mass balance
- **Code from scratch:** Network simulator with seasonal inflow assumptions
- **Interactive lab:** Subak lab extended ([Subak rice terraces](https://andreolf.github.io/subak-lab/))
- **Test that proves it:** Mass balance closes at every terrace
- **Pro tool:** NumPy, EPANET concepts
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.04 Bamboo footbridge

**Goal:** Design and analyse a small bamboo footbridge

- **Derive by hand:** Truss/frame FEM, vibration comfort checks (educational)
- **Code from scratch:** Full design calculation in your FEM
- **Interactive lab:** Break-the-bridge lab with bamboo properties ([Break the bridge](#lab-truss))
- **Test that proves it:** Safety factors computed and documented; not a substitute for a licensed engineer
- **Pro tool:** FEniCSx / CalculiX
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.05 Micro-hydro turbine for a village

**Goal:** Size a Pelton or crossflow turbine

- **Derive by hand:** Euler turbine equation, penstock losses
- **Code from scratch:** Turbine sizing tool
- **Interactive lab:** Head and flow sliders
- **Test that proves it:** Power within efficiency bounds
- **Pro tool:** Python, FreeCAD
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.06 Alpine pumped-storage study

**Goal:** Evaluate a pumped-storage scheme

- **Derive by hand:** Energy, hydraulics, water hammer
- **Code from scratch:** Integrated model with stated assumptions
- **Interactive lab:** Reservoir operation animation
- **Test that proves it:** Energy balance closes
- **Pro tool:** Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.07 E-bike drivetrain

**Goal:** Design a hub gearbox and its thermal limits

- **Derive by hand:** Planetary gears, bearing life, heat transfer
- **Code from scratch:** Integrated drivetrain calculation
- **Interactive lab:** Drivetrain configurator
- **Test that proves it:** All elements pass life/strength checks in the model
- **Pro tool:** CadQuery, Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.08 Flywheel energy store

**Goal:** Design a safe small flywheel

- **Derive by hand:** Rotor stress, bearings, containment
- **Code from scratch:** Flywheel design report
- **Interactive lab:** Flywheel lab ([Gyroscope & flywheel](#lab-flywheel))
- **Test that proves it:** Burst margin documented
- **Pro tool:** FreeCAD, CalculiX
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.09 Wind-loaded structure

**Goal:** Analyse a sign or small tower

- **Derive by hand:** Wind load, vortex shedding, fatigue
- **Code from scratch:** Coupled analysis pipeline
- **Interactive lab:** Wind lab
- **Test that proves it:** Fatigue life estimate reported with assumptions
- **Pro tool:** Python
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)

## 19.10 Publish your artifact

**Goal:** Ship it like open source

- **Derive by hand:** Licensing, reproducibility, documentation
- **Code from scratch:** Publish repo, README, and an interactive web lab
- **Interactive lab:** Your own Break-the-machine page
- **Test that proves it:** Fresh clone reproduces all figures
- **Pro tool:** GitHub Pages, three.js
- **ETH course:** Fokus-Projekt / Bachelor-Arbeit (project format, not course content)
