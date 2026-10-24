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
