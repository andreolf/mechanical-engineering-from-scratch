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
