PHASES = [
dict(slug="thermodynamics", title="Thermodynamics", de="Thermodynamik 1 & 2",
 eth="Thermodynamik 1 / Thermodynamik 2", eth_named=True,
 anchor="Alpine pumped hydro, a Swiss heat pump, a Bali scooter engine",
 summary="Energy, entropy, cycles and real fluids, with property tables built by code.",
 lessons="""
Systems, states and properties | Define what you are analysing | Closed vs open systems, state postulate | Represent a thermodynamic state as an object with consistency checks | System boundary drawer | Over-specified state raises an error | CoolProp
The ideal gas | Use the simplest equation of state well | pv = RT, kinetic theory derivation | Derive pressure from molecular collisions in a box simulation | Gas particle box with temperature slider | Simulated pressure matches nRT/V within noise | NumPy
Work and heat | Compute boundary work in processes | W = int p dV | Integrate p-V work for isothermal, isobaric, polytropic | Draggable p-V path | Isothermal work equals nRT ln(V2/V1) | NumPy
The first law for closed systems | Balance energy | dU = dQ - dW | First-law solver for piston-cylinder problems | Energy flow Sankey | Energy residual zero | Python
The first law for open systems | Analyse turbines, pumps and nozzles | Steady-flow energy equation, enthalpy | SFEE solver | Turbine/nozzle selector | Nozzle exit velocity from enthalpy drop | CoolProp
Pure substances and phase change | Read steam tables like a pro | Saturation, quality, two-phase mixtures | Build a lookup + interpolation over a saturation table | T-v diagram with draggable state | Quality interpolation reproduces table values | CoolProp
Pumped-storage hydropower | Size an alpine pumped-storage plant energy budget | E = rho g h V eta | Energy and round-trip efficiency calculator | Reservoir up/down animation | Stored energy scales linearly with head and volume | Python
The second law | Know what is impossible | Kelvin-Planck, Clausius statements, Carnot efficiency | Carnot efficiency calculator and proof by contradiction notes | Heat engine with reservoir sliders | No cycle beats 1 - Tc/Th | Python
Entropy | Quantify irreversibility | dS = dQ_rev/T, entropy generation | Compute entropy change for mixing water streams | Mixing lab | Entropy generation always >= 0 | CoolProp
Isentropic efficiency | Model real turbines and compressors | eta_s definitions | Compressor exit temperature with efficiency | h-s diagram | eta = 1 recovers isentropic exit state | CoolProp
Exergy | Measure useful energy | Exergy destruction = T0 S_gen | Exergy balance of a heat exchanger | Exergy loss bars | Gouy-Stodola relation holds | CoolProp
Otto and Diesel cycles | Analyse piston engines | Air-standard cycle efficiency 1 - r^(1-k) | Simulate Otto cycle | p-V loop with compression ratio slider | Efficiency matches formula | NumPy
The Brayton cycle | Analyse gas turbines and jet engines | Pressure ratio efficiency | Brayton cycle with real component efficiencies | T-s loop | Ideal Brayton efficiency = 1 - r_p^((1-k)/k) | CoolProp
The Rankine cycle | Analyse steam power plants | Rankine with superheat and reheat | Rankine solver using property library | T-s diagram | Energy balance closes | CoolProp
Refrigeration and heat pumps | Understand Swiss heat pumps | COP, vapour-compression cycle | Heat pump cycle with R290 properties | COP vs outdoor temperature | COP below Carnot COP | CoolProp
Real gases | Go beyond ideal gas | Van der Waals, compressibility factor | Solve van der Waals cubic for v | Isotherms with Maxwell construction | Z approaches 1 at low pressure | CoolProp
Gas mixtures and psychrometrics | Model humid air for Bali and Zurich climates | Partial pressures, relative humidity, dew point | Psychrometric calculator | Psychrometric chart with Bali vs Zurich points | Dew point equals temperature at RH 100% | psychrolib
Combustion | Compute flame temperatures and emissions | Stoichiometry, adiabatic flame temperature | Adiabatic flame temperature of methane-air | Equivalence ratio slider | Peak near stoichiometric | Cantera
Chemical equilibrium | Predict composition at high temperature | Gibbs minimisation | Minimise Gibbs energy for a simple dissociation | Equilibrium vs temperature | Matches Cantera equilibrium | Cantera
Energy systems of Switzerland | Put thermodynamics in a national context | Energy balances in TWh | Model a seasonal energy balance with clearly labelled assumed data | Seasonal storage graph | Balance closes by construction | Python
"""),
dict(slug="fluid-dynamics-1", title="Fluid Dynamics 1: Foundations", de="Fluiddynamik (Teil 1)",
 eth="Fluiddynamik", eth_named=True,
 anchor="The Limmat, the Rhine Falls, a coconut in a Bali river eddy",
 summary="Fluid statics, kinematics, conservation laws, Bernoulli, momentum and dimensional analysis.",
 lessons="""
What is a fluid | Define fluids, viscosity and the continuum | Newton's law of viscosity tau = mu du/dy | Couette flow velocity profile | Shear between plates with speed slider | Linear profile for Newtonian fluid | NumPy
Fluid statics | Compute pressure in still fluids | dp/dz = -rho g | Manometer and pressure-with-depth calculator | Manometer lab | Pressure at 10 m water approx 98 kPa gauge | NumPy
Buoyancy and stability | Explain why a coconut floats and boats stay upright | Archimedes, metacentric height | Floating draft and metacentric height of a boat | Tilting hull with metacentre | Stable iff GM > 0 | NumPy
Flow kinematics | Describe flow fields | Eulerian vs Lagrangian, streamlines, pathlines, streaklines | Trace particles in an unsteady field | Streamline vs pathline toggle | Steady flow: all three coincide | NumPy
Material derivative | Follow a fluid parcel | D/Dt = d/dt + u . grad | Compute material acceleration numerically | Particle acceleration arrows | Matches analytical example | NumPy
Conservation of mass | Derive continuity | Reynolds transport theorem, div u = 0 for incompressible | Check divergence of discrete velocity fields | Pipe contraction with flow rate counter | Flow rate equal at all sections | NumPy
Bernoulli's equation | Derive it and know when it lies | Euler equation along a streamline; assumptions | Venturi meter calculator | Pipe flow lab: change diameter, watch speed and pressure (LAB:pipe) | Pressure drop matches Bernoulli in inviscid limit | NumPy
Torricelli and draining tanks | Apply Bernoulli to outflow | v = sqrt(2 g h), quasi-steady assumption | Tank draining time | Draining tank animation | Time matches analytic for constant area | SciPy
Momentum theorem | Compute forces from flows | Control-volume momentum balance | Force on a pipe bend and on a jet hitting a plate | Jet deflector lab | Force equals mass flow times velocity change | NumPy
Angular momentum and turbines | Derive Euler's turbine equation | Torque = m_dot (r2 c_u2 - r1 c_u1) | Pelton wheel power vs bucket speed | Pelton runner animation (alpine hydro) | Max power at bucket speed = jet speed/2 (ideal) | NumPy
Dimensional analysis in fluids | Use Re, Fr, Ma, We | Buckingham Pi for drag | Compute Pi groups from a variable list | Re slider from honey to the Rhine | Same Pi groups as textbook | SymPy
Similarity and model testing | Scale a dam spillway model correctly | Froude similarity scaling laws | Scale factors for a 1:50 spillway model | Model vs prototype comparison | Velocity scales with sqrt(length scale) | Python
Navier-Stokes equations | Derive the governing equations | Cauchy momentum + Newtonian constitutive law | Symbolically verify an exact solution | Term-by-term equation explorer | Poiseuille solution satisfies NS | SymPy
Laminar pipe flow | Solve Hagen-Poiseuille | Parabolic profile, Q = pi R^4 dp/(8 mu L) | Profile and flow rate calculator | Pipe profile animation | Mean velocity equals half max | NumPy
Vorticity and circulation | Understand rotation in flows | Kelvin circulation theorem | Compute vorticity of discrete fields | Coconut trapped in an eddy behind a boulder (LAB:coconut) | Rankine core rotates like solid body | NumPy
Potential flow | Build inviscid flows by superposition | Complex potential w(z) | Flow around a cylinder with circulation | Draggable circulation slider shows lift | Kutta-Joukowski lift = rho U Gamma | NumPy
Open-channel flow basics | Understand rivers and irrigation canals | Specific energy, critical depth, Froude number | Critical depth and specific energy curve | Channel energy diagram | Minimum specific energy at Fr = 1 | NumPy
Weirs and Subak irrigation | Model flow over weirs in Balinese rice terraces | Broad/sharp-crested weir equations from critical flow | Weir discharge calculator and terrace cascade | Subak terrace cascade (LAB:subak) | Discharge scales with head^(3/2) | NumPy
Hydraulic jumps | Explain the roaring step in a channel | Momentum conjugate depths | Conjugate depth solver | Jump location slider | Conjugate depth formula satisfied; energy is lost | NumPy
Unsteady flow and water hammer | Explain pipe bangs and penstock surges | Joukowsky delta p = rho a delta v | Method-of-characteristics water hammer | Valve-closing animation in a penstock | Peak pressure matches Joukowsky for instant closure | NumPy
"""),
dict(slug="fluid-dynamics-2", title="Fluid Dynamics 2: Viscous Flows, Turbulence, Aero", de="Fluiddynamik (Teil 2)",
 eth="Fluiddynamik (later chapters) and fluid-dynamics electives (generic)", eth_named=True,
 anchor="A cyclist in the Swiss wind, Rhine turbulence, a kite over Bali",
 summary="Boundary layers, drag, pipe losses, turbulence, compressible flow and aerodynamics.",
 lessons="""
Exact viscous solutions | Solve Couette, Poiseuille and Stokes problems | Reduced NS for parallel flows | Stokes first problem (impulsively started plate) | Growing diffusion layer | Layer grows as sqrt(nu t) | SciPy special
Low-Reynolds flow | Understand micro-swimmers and settling | Stokes drag F = 6 pi mu R U | Settling velocity of sediment in a river | Particle size slider | Matches Stokes law at low Re | NumPy
Boundary layers | Derive Prandtl's boundary layer idea | Scaling delta ~ x Re_x^(-1/2) | Solve the Blasius equation by shooting | Velocity profile along a plate | f''(0) approx 0.332 | SciPy solve_ivp
Separation | Explain why flow detaches behind a boulder | Adverse pressure gradient | Thwaites method for separation point | Cylinder with separation marker | Laminar separation predicted near 104-110 degrees (literature range) | NumPy
Drag | Estimate drag on bodies | Pressure vs friction drag, C_D | Drag of a cyclist using C_D A | Riding position slider | Power scales with v^3 | NumPy
Lift and airfoils | Explain how wings work without myths | Kutta condition, thin airfoil theory C_L = 2 pi alpha | Thin airfoil lift slope calculator | Airfoil with angle-of-attack slider | Slope 2 pi per radian | XFOIL
Panel methods | Compute pressure on arbitrary airfoils | Source/vortex panels | Vortex panel method from scratch | Pressure distribution plot | Matches thin airfoil theory at small angle | XFOIL
Turbulence phenomenology | Understand chaotic flow | Energy cascade, Kolmogorov scales | Generate and analyse a synthetic turbulent signal | Energy spectrum with -5/3 guide | Kolmogorov length from dissipation formula | NumPy
Reynolds averaging | Model turbulence for engineering | RANS, Reynolds stresses, closure problem | Compute Reynolds stresses from synthetic velocity data | Mean vs fluctuation decomposition | Fluctuation mean is zero | NumPy
Turbulent pipe flow | Predict pressure losses in real pipes | Darcy-Weisbach, Colebrook equation | Solve Colebrook for friction factor | Moody chart generator | Laminar limit f = 64/Re | fluids (Python package)
Pipe networks | Design water supply systems | Hardy Cross method | Solve a looped village water network | Network with flow arrows | Mass conserved at every node | EPANET / WNTR
Pumps and systems | Match pumps to pipelines | Pump curve vs system curve, affinity laws | Operating point solver | Pump speed slider | Affinity laws scale flow linearly with speed | fluids
Compressible flow basics | Understand speed of sound and Mach number | a = sqrt(k R T), stagnation properties | Isentropic relations calculator | Mach number slider | T0/T = 1 + (k-1)/2 Ma^2 | NumPy
Nozzles and choking | Design converging-diverging nozzles | Area-Mach relation | Nozzle flow solver with shock location | CD nozzle with back-pressure slider | Choked mass flow independent of back pressure | NumPy
Normal shocks | Compute jumps across shocks | Rankine-Hugoniot relations | Normal shock calculator | Shock tube animation | Entropy increases across shock | NumPy
Vortex shedding | Explain cable singing and bridge oscillations | Strouhal number St ~ 0.2 | Shedding frequency for a ski-lift cable | Karman street visual | Frequency scales with U/D | NumPy
Wind and buildings | Estimate wind loads | Dynamic pressure, gust factors (labelled simplification) | Wind load on a signboard | Wind speed slider | Load scales with v^2 | Python
Mixing and dispersion in rivers | Model pollutant spread in the Limmat | Advection-diffusion equation | Gaussian plume in a channel | Dye release lab | Total mass conserved | NumPy
"""),
dict(slug="heat-transfer", title="Heat Transfer", de="Wärmeübertragung",
 eth="Thermodynamik 3 (heat-transfer topics; check current syllabus) and heat transfer electives", eth_named=True,
 anchor="Keeping a Bali house cool, an alpine hut warm, a CPU alive",
 summary="Conduction, convection, radiation and heat exchangers derived and simulated.",
 lessons="""
Conduction and Fourier's law | Derive heat flux from temperature gradients | q = -k grad T | 1D steady conduction through a wall | Wall with thermal conductivity slider | Linear profile in homogeneous wall | NumPy
Thermal resistance networks | Analyse layered walls like circuits | R = L/(k A), series and parallel | Wall resistance network solver | Insulation layer builder for an alpine hut | Heat flow equals delta T / R_total | Python
Cylindrical and spherical conduction | Insulate pipes correctly | R = ln(r2/r1)/(2 pi k L), critical radius | Critical insulation radius calculator | Pipe insulation thickness slider | Critical radius = k/h | NumPy
Fins | Cool engines and electronics | Fin equation m^2 = h P/(k A), efficiency | Fin temperature profile solver | Fin length slider | Long fin heat rate sqrt(h P k A) theta_b | SciPy
Transient conduction: lumped | Decide when lumped models work | Biot number, exponential cooling | Lumped cooling of a coconut in a fridge (stated assumptions) | Biot slider with validity warning | Valid when Bi < 0.1 | NumPy
Transient conduction: distributed | Solve heating of thick bodies | Heat equation, Heisler-style solutions | 1D/2D transient conduction FD solver | Temperature heat-map animation | Converges to analytic series | NumPy
Convection fundamentals | Understand h and the boundary layer | Nusselt number, thermal boundary layer | Compute h from Nu correlations | Flow speed slider over a plate | Laminar plate Nu ~ Re^(1/2) Pr^(1/3) | NumPy
Forced convection correlations | Use correlations responsibly | Dittus-Boelter, Gnielinski (range of validity) | Correlation library with validity checks | Pipe flow heat-transfer calculator | Raises warning outside validity range | ht (Python package)
Natural convection | Model hot plates and room air | Grashof, Rayleigh, Boussinesq approximation | Natural convection h on a vertical plate | Rayleigh slider | Transition near Ra ~ 1e9 (typical criterion) | NumPy
Radiation | Compute radiative exchange | Stefan-Boltzmann, emissivity, view factors | View factor by Monte Carlo ray casting | Tropical roof vs reflective paint | Parallel plates view factor approaches 1 when large | NumPy
Solar energy | Model solar gain in Bali vs Zurich | Solar geometry, irradiance on tilted planes | Solar position and panel yield model with labelled inputs | Sun path visual for both locations | Noon elevation matches 90 - latitude + declination | pvlib
Heat exchangers: LMTD | Size heat exchangers | Log-mean temperature difference | LMTD design calculator | Parallel vs counterflow profiles | Counterflow needs less area for same duty | NumPy
Heat exchangers: effectiveness-NTU | Rate exchangers when outlets are unknown | epsilon-NTU relations | epsilon-NTU solver | NTU slider | Same result as LMTD when outlets known | NumPy
Electronics and battery cooling | Apply everything to a real thermal design | Thermal network + convection + radiation | Thermal model of an e-bike battery pack | Load profile with temperature trace | Steady state consistent with resistance network | Python
"""),
dict(slug="machine-design", title="Machine Elements & Design", de="Maschinenkonstruktion / Dimensionierung",
 eth="Maschinenkonstruktion (Machine Design) and Dimensionierung courses", eth_named=True,
 anchor="Bike drivetrains, ski-lift grips, Swiss watch gears, a Bali scooter",
 summary="Dimensioning shafts, bearings, gears, bolts and welds: from load to safe, buildable part.",
 lessons="""
The design process | Go from need to concept to detail | Requirements, morphological box, evaluation matrix | Weighted decision matrix tool | Concept scoring board | Ranking reproducible from weights | Python
Safety factors and reliability | Pick safety factors with reasons | Stress-strength interference, reliability index | Monte Carlo failure probability | Overlapping distributions | Analytical normal-normal result matched | SciPy stats
Tolerances and fits | Make parts that assemble | ISO fits, tolerance stack-up (worst case vs RSS) | Stack-up calculator | Stack chain visual | RSS <= worst case | Python
Shaft design | Size shafts for strength and fatigue | Combined bending-torsion, Goodman-based shaft equations | Shaft diameter calculator | Load layout editor | Larger safety factor yields larger diameter | NumPy
Keys, splines and press fits | Transmit torque from hub to shaft | Lame thick-cylinder equations for interference | Press-fit pressure and torque capacity | Interference slider | Contact pressure matches Lame solution | NumPy
Rolling bearings | Choose bearings by life | L10 = (C/P)^p with p = 3 for ball bearings | Bearing life calculator | Load vs life curve | Doubling load cuts life by factor 8 | Python
Plain bearings and lubrication | Understand hydrodynamic lubrication | Reynolds equation for thin films | 1D Reynolds equation solver for a slider bearing | Pressure build-up in a wedge | Load capacity positive only for converging wedge | NumPy
Gear geometry | Understand involute gears | Involute curve, base circle, law of gearing | Generate involute profiles | Meshing gear animation | Constant velocity ratio along line of action | NumPy
Gear strength | Size gears against bending and pitting | Lewis bending equation, Hertz contact basics | Gear stress estimates | Module/face-width sliders | Stress decreases with module | Python
Gear trains and planetary gears | Design transmissions | Willis equation for planetary sets | Planetary ratio solver | Animated planetary gearbox (e-bike hub) | Willis relation satisfied | Python
Belts and chains | Design bike and conveyor drives | Chain kinematics, polygonal effect, belt tensions | Chain speed fluctuation calculator | Chainring tooth-count slider | Fluctuation decreases with tooth count | NumPy
Bolted joints | Design joints that do not loosen | Joint diagram, preload, stiffness ratio | Bolted joint diagram tool | Preload slider | External load share follows stiffness ratio | Python
Welded joints | Size welds | Throat stress, fatigue classes concept | Fillet weld stress calculator | Weld layout editor | Stress inversely proportional to throat size | Python
Springs | Design helical springs | k = G d^4/(8 D^3 n), Wahl factor | Spring designer | Coil count slider | Stiffness matches formula | Python
Clutches and brakes | Size friction devices | Uniform wear vs uniform pressure torque | Disc brake torque for a bike | Brake lever force slider | Uniform wear torque <= uniform pressure | NumPy
Linkages and mechanisms | Synthesise motion | Freudenstein equation | Three-position linkage synthesis | Linkage designer | Synthesised linkage passes through targets | NumPy
Ski-lift grip and cable design | Integrate elements on a Swiss anchor | Friction grip force, cable tension, safety factors | Detachable grip clamp force model (educational) | Slope and load sliders | Grip holds when friction capacity > slope component times SF | Python
Design review and documentation | Ship designs others can build | Calculation reports, traceability | Auto-generate a calculation report from your Python modules | Report preview | Report reproduces all numbers from code | Jupyter / Quarto
"""),
]
