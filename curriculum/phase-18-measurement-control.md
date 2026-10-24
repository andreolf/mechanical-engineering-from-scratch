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
