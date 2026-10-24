PHASES = [
dict(slug="statics", title="Statics & Free-Body Diagrams", de="Mechanik 1: Kinematik und Statik",
 eth="Mechanik 1: Kinematik und Statik", eth_named=True,
 anchor="Swiss bridges, ski-lift towers and a Bali bamboo scaffold",
 summary="Forces, moments, equilibrium, trusses, frames, friction and virtual work.",
 lessons="""
Forces as vectors | Represent and add forces correctly | Force as a bound vector; resultant by vector sum | Force-vector class with resultant and components | Drag force arrows and see the resultant | Resultant equals component-wise sum | NumPy
Moments and couples | Compute the turning effect of forces | M = r x F; couple is free vector | Moment calculator about any point | Spanner with draggable force and pivot | Moment of a couple independent of reference point | NumPy
Equivalent force systems | Replace complex loads with a single force and moment | Reduction to a point, wrench | Reduce a distributed load to resultant + location | Distributed load slider showing resultant arrow | Resultant of a triangular load acts at L/3 | NumPy
Kinematics of rigid bodies | Describe velocities of points in a rigid body | v_B = v_A + omega x r_AB, instantaneous centre | Compute velocity field of a moving bike crank | Velocity arrows with instantaneous centre marked | Instantaneous centre has zero velocity | NumPy
Supports and constraints | Model how structures are held | Reaction types: pin, roller, clamp; degrees of freedom | Constraint counter: Gruebler-style DOF count for planar bodies | Snap supports onto a beam and count unknowns | Simply supported beam has 3 reactions, 0 DOF | Python
The free-body diagram | Isolate bodies and expose every force | Cut principle (Schnittprinzip) | FBD data structure with automatic equilibrium check | Interactive cut tool on a ladder | Ladder FBD balances in all three equations | Python
Equilibrium of rigid bodies | Solve 2D and 3D equilibrium problems | Sum F = 0, sum M = 0 | Solve reactions of a beam with arbitrary loads | Beam with draggable loads and live reactions | Reactions match hand calculation | NumPy
Static determinacy | Know when statics alone is enough | Count equations vs unknowns; rank of the equilibrium matrix | Rank test for determinate, indeterminate and mechanism | Add/remove supports and see classification change | Classifications match textbook cases | NumPy
Plane trusses: method of joints | Compute member forces in a truss bridge | Joint equilibrium, two-force members | Assemble and solve joint equations for any truss | Delete members and watch the load path (LAB:truss) | Warren truss forces match hand solution | NumPy
Method of sections | Find a single member force quickly | Moment about the intersection of two cut members | Section solver for a chosen cut | Draggable section line through a bridge | Matches method-of-joints result | NumPy
Space trusses and towers | Extend to 3D structures like ski-lift pylons | 3D joint equilibrium, Maxwell rule m = 3j - 6 | 3D truss solver | Rotatable 3D tower with member forces coloured | Simple tetrapod forces match hand calc | NumPy
Frames and machines | Analyse pliers, bike brakes and linkages | Multi-body FBDs with internal pins | Solve a bicycle rim-brake lever system | Squeeze slider showing pad force | Mechanical advantage equals arm ratio | Python
Internal forces in beams | Draw N, V, M diagrams | dV/dx = -q, dM/dx = V | Compute and plot shear and moment diagrams | Live V/M diagrams under moving loads (hero beam) | Maximum moment for central point load is PL/4 | NumPy
Cables and chains | Model suspension cables and power lines | Catenary y = a cosh(x/a), parabolic approximation | Solve catenary sag for given span and length | Cable sag slider on an alpine cable car | Catenary length integral equals specified length | SciPy
Friction | Model sliding, tipping and wedges | Coulomb friction F <= mu N | Tip vs slide predictor for a crate | Tilting ramp with crate | Slides exactly when tan(theta) > mu | Python
Belt friction | Understand capstans and belt drives | Euler-Eytelwein T2/T1 = e^{mu beta} | Belt tension calculator | Rope around a bollard with wrap-angle slider | Tension ratio exponential in wrap angle | NumPy
Centres of mass and gravity | Locate where weight acts | Composite bodies, Pappus-Guldinus | Composite centroid calculator | Assemble shapes and see CG move | CG of composite matches polygon algorithm | shapely
Hydrostatics | Compute forces from still water on dams and gates | p = rho g h, resultant on inclined plane | Force and centre of pressure on a dam gate | Reservoir level slider on an alpine dam | Centre of pressure at 2h/3 for a vertical rectangle from surface | NumPy
Principle of virtual work | Solve equilibrium with energy instead of FBDs | delta W = 0 for virtual displacements | Solve a scissor lift with virtual work | Scissor lift with load slider | Matches FBD result | SymPy
Stability of equilibrium | Know when equilibrium is unstable | Potential energy minimum, second variation | Classify equilibria of a hinged bar with spring | Energy landscape with ball | Stable iff d^2V/dtheta^2 > 0 | NumPy
"""),
dict(slug="deformable-solids", title="Strength of Materials (Deformable Solids)", de="Mechanik 2: Deformierbare Festkörper",
 eth="Mechanik 2 (Deformable Solids)", eth_named=True,
 anchor="Bike frames, Swiss rail tracks, bamboo beams in Bali",
 summary="Stress, strain, beams, torsion, buckling and energy methods: how parts deform and when they fail.",
 lessons="""
Stress | Understand stress as force per area on a cut | Cauchy stress vector t = sigma n | Compute traction on any plane from a stress tensor | Rotate a cutting plane and see traction | Traction equals sigma.n | NumPy
Strain | Measure deformation | Small strain epsilon = (grad u + grad u^T)/2 | Strain from a displacement field on a grid | Deforming grid with strain colouring | Rigid rotation produces zero small strain at first order | NumPy
Hooke's law | Relate stress and strain | Isotropic elasticity with E, nu; Lame constants | 3D Hooke's law in matrix (Voigt) form | Stress-strain slider for steel, aluminium, bamboo | Uniaxial test returns E and lateral contraction nu | NumPy
Axial bars | Compute stretch of rods and cables | delta = N L/(E A) | Stepped bar elongation solver | Rod with load and area sliders | Matches closed form for stepped bar | NumPy
Statically indeterminate bars | Use compatibility when statics is not enough | Equilibrium + compatibility + constitutive law | Solve a bar fixed at both ends with a midpoint load | Wall reactions as load moves | Reactions sum to applied load | NumPy
Thermal stress | Predict stress from temperature change | epsilon_th = alpha delta T | Compute stress in a constrained rail on a hot day | Rail temperature slider with buckling warning | Stress = -E alpha delta T for fully constrained bar | NumPy
Stress transformation and Mohr's circle | Find principal stresses and max shear | Rotation of 2D stress; Mohr's circle | Mohr's circle generator | Rotate element and track point on Mohr's circle | Principal stresses equal eigenvalues of sigma | NumPy
Failure criteria | Decide if a part yields | Tresca, von Mises; distortion energy derivation | von Mises and Tresca calculators | Yield surfaces in principal stress space | Pure shear yields at tau = sigma_y/sqrt(3) under von Mises | NumPy
Beam bending: Euler-Bernoulli | Derive the bending stress formula | Plane sections remain plane; sigma = M y / I | Bending stress field over a cross-section | Cantilever with draggable load and stress colours (hero beam) | Max stress equals M c / I | NumPy
Second moment of area | Pick efficient cross-sections | I = int y^2 dA; parallel axis theorem | Section property calculator for I, T, box, tube | Compare sections at equal mass | I-section beats rectangle at equal area | sectionproperties
Beam deflection | Compute how far a beam bends | EI w'''' = q, boundary conditions | Integrate the beam equation numerically and symbolically | Live deflected shape vs load position | Cantilever tip deflection equals PL^3/(3EI) | SymPy
Superposition and indeterminate beams | Solve continuous beams | Superposition of standard cases + compatibility | Propped cantilever via superposition | Support removal to see moment redistribution | Prop reaction under uniform load q equals 3qL/8 | NumPy
Shear stress in beams | Find where shear peaks | Jourawski formula tau = V Q /(I b) | Shear distribution over rectangular and I sections | Shear profile plot by section | Rectangle max shear equals 1.5 V/A | NumPy
Torsion of circular shafts | Size a drive shaft | tau = T r / J, phi = T L /(G J) | Shaft stress and twist calculator | Twisting shaft with rotating grid lines | Hollow shaft J matches pi(D^4-d^4)/32 | NumPy
Thin-walled torsion | Analyse bike frame tubes and boxes | Bredt-Batho shear flow q = T/(2A_m) | Torsional stiffness of closed vs open sections | Slit tube comparison | Open section dramatically less stiff than closed | NumPy
Combined loading | Superpose axial, bending and torsion | Superposition then von Mises | Check a crank arm under pedalling load | Pedal force slider with stress hotspot | Hotspot location matches hand analysis | NumPy
Strain energy | Use energy to compute deflections | U = int sigma epsilon /2 dV | Strain energy of bar, beam, shaft | Energy bar chart per load type | Energy equals work of external load P delta/2 | NumPy
Castigliano's theorem | Find deflections from energy derivatives | delta_i = dU/dP_i | Deflection of a curved bar (bike hook) | Load point selector | Matches direct integration | SymPy
Buckling of columns | Predict when slender members fail suddenly | Euler buckling P_cr = pi^2 E I/(K L)^2 | Eigenvalue solution of discretised column | Compress a column until it snaps sideways | Discrete critical load converges to Euler | NumPy
Imperfections and real buckling | Understand why real columns fail below Euler | Imperfect column amplification 1/(1 - P/P_cr) | Imperfect column load-deflection curve | Imperfection slider | Deflection grows without bound as P approaches P_cr | NumPy
Pressure vessels | Size a tank or pipe wall | Thin wall: sigma_hoop = p r / t, sigma_axial = p r/(2t) | Penstock wall thickness calculator for an alpine hydro plant | Pressure slider with hoop stress | Hoop stress is twice axial stress | NumPy
Stress concentrations | Understand why parts crack at holes and fillets | Kirsch solution: K_t = 3 for a hole in a plate | Plot Kirsch stress field around a hole | Plate with hole stress heat-map | Peak stress equals 3 times remote stress | NumPy
"""),
dict(slug="dynamics", title="Dynamics", de="Mechanik 3: Dynamik",
 eth="Mechanik 3: Dynamik", eth_named=True,
 anchor="Swiss rail curves, a ski jump, a Bali scooter and a spinning flywheel",
 summary="Particles, systems, rigid bodies in 2D and 3D, rotating frames and gyroscopes.",
 lessons="""
Particle kinematics | Describe trajectories, velocity and acceleration | Cartesian, polar and path coordinates | Compute v and a along a measured GPS track | Track with tangential/normal acceleration arrows | Normal acceleration equals v^2/rho on a circle | NumPy
Newton's second law | Write equations of motion for a particle | F = m a; cut-free and add forces | Simulate a ski jumper with gravity and drag | Ski-jump trajectory with drag coefficient slider | Zero drag reproduces parabola | SciPy
Work and energy | Use energy to skip integration | Work-energy theorem, conservative forces | Roller-coaster speed from energy | Draggable track profile with speed colouring | Energy-based speed matches ODE simulation | NumPy
Impulse and momentum | Analyse collisions and rockets | Linear impulse, conservation of momentum | 1D collision solver with restitution | Two-cart collision lab | Momentum conserved to 1e-12 | NumPy
The rocket equation | Derive variable-mass motion | Tsiolkovsky delta v = v_e ln(m0/m1) | Integrate rocket ascent with gravity | Mass ratio slider | Integrated delta v (no gravity) matches Tsiolkovsky | SciPy
Systems of particles | Treat many bodies at once | Centre of mass theorem, internal forces cancel | N-body simulation of a few particles | Particle system with COM tracker | COM moves uniformly without external force | NumPy
Angular momentum of particles | Explain why spinning skaters speed up | L = r x m v; dL/dt = M | Simulate a mass on a shrinking string | Radius slider showing omega increase | L conserved within integrator tolerance | NumPy
Rigid body kinematics in 2D | Relate velocities and accelerations of linkage points | v_B = v_A + omega x r, a_B with centripetal term | Four-bar linkage kinematics | Animated four-bar with velocity polygons | Grashof condition predicts crank rotation | NumPy
Planar rigid body dynamics | Simulate rolling wheels and swinging doors | M_G = I_G alpha; rolling constraint | Disk vs ring race down a ramp | Rolling race lab | Disk accelerates at 2/3 g sin(theta), ring at 1/2 | SciPy
Moment of inertia | Compute I for real parts | I = int r^2 dm, parallel axis | Inertia of a flywheel from its profile | Flywheel profile editor | Matches CAD mass properties for simple shapes | NumPy
Rotating machinery and balancing | Avoid vibration from unbalanced rotors | Static vs dynamic imbalance | Compute correction masses for a rotor | Rotor with draggable unbalance | Corrected rotor has zero net force and moment | NumPy
Relative motion and rotating frames | Compute motion seen from a moving observer | a = a_rel + 2 omega x v_rel + omega x (omega x r) + ... | Simulate a ball on a rotating carousel | Inertial vs rotating view toggle | Coriolis deflection direction correct for rotation sense | NumPy
3D rigid-body kinematics | Describe orientation in 3D | Rotation matrices, Euler angles, quaternions | Quaternion integrator for angular velocity | Gimbal lock demo vs quaternion | Quaternion stays unit norm with renormalisation | scipy.spatial.transform
Inertia tensor | Understand how mass distribution resists rotation | I tensor, principal axes | Compute inertia tensor of a point cloud body | Principal axes overlay on a 3D part | Principal moments equal eigenvalues | NumPy
Euler's equations | Simulate free 3D rotation | I omega' + omega x I omega = M | Integrate torque-free rotation | Tennis-racket (intermediate axis) instability demo | Rotation about intermediate axis is unstable | SciPy
Gyroscopes and precession | Explain why a spinning wheel doesn't fall | Precession rate Omega = m g r /(I omega) for fast top | Simulate a gyroscope on a pivot | Spinning flywheel lab: change spin, watch precession (LAB:flywheel) | Simulated precession rate approaches formula for fast spin | SciPy
Flywheel energy storage | Size a flywheel for energy storage | E = I omega^2/2, rim stress sigma = rho v^2 | Energy and stress vs speed for a rim | Spin-up slider with burst warning | Burst speed independent of radius for thin rim | NumPy
Lagrangian mechanics | Derive equations of motion with energy | Euler-Lagrange equations | SymPy Lagrangian of a double pendulum | Double pendulum chaos lab | Energy conserved in simulation within tolerance | SymPy mechanics
Rail vehicle dynamics in curves | Understand cant and lateral acceleration | Cant balances v^2/R; uncompensated acceleration | Compute cant deficiency for a train curve | Train on curve with speed slider | Zero lateral force at balance speed | NumPy
Multibody simulation | Assemble constrained systems | Constraint equations, Lagrange multipliers | Slider-crank multibody solver | Engine slider-crank animation | Constraint drift stays below tolerance with stabilisation | Project Chrono / MuJoCo
"""),
dict(slug="vibrations", title="Vibrations & Waves", de="Schwingungen und Wellen",
 eth="Mechanik 3: Dynamik (vibrations part) and structural dynamics electives (generic)", eth_named=True,
 anchor="Pedestrian bridges, ski-lift cables, and a Bali gamelan",
 summary="Single- and multi-DOF oscillators, resonance, modes, isolation and waves in elastic bodies.",
 lessons="""
The harmonic oscillator | Derive natural frequency from first principles | m x'' + k x = 0, omega_n = sqrt(k/m) | Simulate and measure period | Mass-spring lab with k and m sliders | Measured period equals 2 pi sqrt(m/k) | NumPy
Damping | Model energy loss | Viscous damping ratio zeta, logarithmic decrement | Estimate zeta from a decaying signal | Damping slider with envelope fit | Log decrement estimate recovers zeta within 2% | SciPy
Forced vibration and resonance | Predict amplitude under harmonic forcing | Frequency response H(omega), phase | Compute and plot Bode-style amplitude/phase | Shaker frequency sweep lab | Peak near omega_n sqrt(1 - 2 zeta^2) | SciPy signal
Base excitation and isolation | Isolate machines and vehicles from vibration | Transmissibility, isolation above sqrt(2) omega_n | Bike-suspension transmissibility | Road bump excitation on a bike | Transmissibility below 1 above sqrt(2) omega_n | NumPy
Rotating unbalance | Model washing machines and turbines | m e omega^2 forcing | Response of an unbalanced rotor | Spin speed slider | High-speed amplitude approaches m e/M | NumPy
Two-DOF systems | Find modes of coupled oscillators | Eigenproblem (K - omega^2 M) phi = 0 | Solve and animate modes | Coupled pendulums with beat phenomena | Modes are M-orthogonal | NumPy
Tuned mass dampers | Calm a wobbly footbridge or tower | Den Hartog tuning | Optimise a TMD for a footbridge model | TMD on/off comparison | Peak response reduced vs untuned | SciPy optimize
Multi-DOF and modal analysis | Decouple big systems into modes | Modal coordinates, modal superposition | Shear-building model of a 5-storey frame | Mode shape animator | Modal superposition equals direct integration | SciPy eigh
Vibration of strings | Connect waves and modes | Standing waves, f_n = n c/(2L) | Modal string synthesiser | Pluck and hear the harmonics | Mode frequencies are integer multiples | NumPy
Axial and torsional vibration of rods | Model shafts and drill strings | Wave equation in rods, c = sqrt(E/rho) | Natural frequencies of a fixed-free rod | Rod mode animator | f_1 = c/(4L) for fixed-free | NumPy
Beam vibration | Find bending modes of beams | EI w'''' + rho A w_tt = 0, characteristic equation | Solve cantilever frequency equation cos(bL)cosh(bL) = -1 | Cantilever mode shapes in 3D | beta_1 L = 1.875 | SciPy
Plates and bells | See modes in 2D | Chladni patterns intuition | Finite-difference modes of a square membrane | Chladni pattern generator | Membrane eigenvalues match analytic m^2 + n^2 pattern | SciPy sparse eigsh
Experimental modal analysis | Extract modes from measurements | Frequency response functions, peak picking | Identify modes from simulated hammer test data | Hammer-tap FRF lab | Identified frequencies within 1% of model | SciPy signal
Nonlinear vibrations | See what linear theory misses | Duffing oscillator, jump phenomenon | Duffing frequency sweep up and down | Hysteresis in response curve | Up and down sweeps differ in nonlinear regime | SciPy
Self-excited vibration | Understand flutter, squeal and galloping | Negative damping, limit cycles | Van der Pol oscillator | Limit cycle in phase plane | All trajectories converge to the same cycle | SciPy
Waves and impact | Understand stress waves on impact | 1D wave reflection at free and fixed ends | Simulate impact of two rods | Wave propagation animation | Free end reflects compression as tension | NumPy
"""),
dict(slug="materials", title="Materials Science", de="Werkstoffe",
 eth="Werkstoffe und Fertigung; Engineering Design and Material Selection", eth_named=True,
 anchor="Swiss watch steels, aluminium bike frames, Bali bamboo and teak",
 summary="Atoms to alloys: why materials are stiff, strong, tough, or not, and how to choose them.",
 lessons="""
Atomic bonding and stiffness | Explain where Young's modulus comes from | Lennard-Jones potential, stiffness = curvature at minimum | Derive E from a pair potential | Interatomic potential with draggable atoms | Stiffness equals second derivative at r0 | NumPy
Crystal structures | Recognise FCC, BCC, HCP | Packing factor, coordination numbers | Generate lattices and compute packing factor | 3D lattice viewer | FCC packing factor = 0.74 | ASE
Defects and dislocations | Explain why metals are ductile | Theoretical vs real shear strength | Estimate ideal shear strength G/(2 pi) | Dislocation glide animation | Ideal strength orders of magnitude above measured | NumPy
The tensile test | Read a stress-strain curve | Engineering vs true stress, necking (Considere) | Process raw tensile data: E, yield (0.2%), UTS | Interactive tensile curve | 0.2% offset yield correctly extracted | NumPy
Hardening mechanisms | Make metals stronger | Hall-Petch, solid solution, precipitation | Fit Hall-Petch to grain-size data | Grain size slider | Fitted slope recovers synthetic constant | NumPy
Phase diagrams | Read alloy phase diagrams | Lever rule | Lever-rule calculator for a binary diagram | Click a point, get phase fractions | Fractions sum to 1 | Python
Steel and heat treatment | Understand quench, temper and the iron-carbon diagram | Fe-C diagram, TTT curves qualitative | Phase fraction tool for plain carbon steel | Cooling-rate slider over TTT sketch | Eutectoid composition near 0.76% C (textbook value) | Thermo-Calc concepts (open: pycalphad)
Diffusion | Model carburising and drying | Fick's laws, erf solution | Solve carburising depth | Concentration profile over time | Depth grows with sqrt(D t) | SciPy special.erf
Polymers | Understand viscoelastic behaviour | Maxwell and Kelvin-Voigt models | Simulate creep and relaxation | Spring-dashpot builder | Maxwell relaxes exponentially with tau = eta/E | NumPy
Composites | Design with fibres | Rule of mixtures (Voigt/Reuss bounds) | Laminate stiffness for a carbon bike frame ply | Fibre angle slider | Longitudinal modulus follows Voigt bound | NumPy
Natural materials: bamboo and wood | Engineer with Bali bamboo responsibly | Anisotropy, graded fibre density | Bending stiffness of a hollow bamboo culm | Culm wall thickness slider | Hollow culm stiffness-to-weight beats solid rod | NumPy
Fracture mechanics | Predict crack growth | Griffith energy balance, K_I = Y sigma sqrt(pi a) | Critical crack size calculator | Crack length slider with fracture threshold | Fracture when K_I >= K_IC | NumPy
Fatigue | Design parts that survive millions of cycles | S-N curves, Basquin, Goodman mean-stress correction | Goodman diagram and life estimate | Load-cycle slider on a crank | Infinite life inside the Goodman line | NumPy
Corrosion | Keep alpine and tropical structures alive | Galvanic series, Faraday's law for corrosion rate | Corrosion rate from current density | Galvanic couple picker | Rate proportional to current | Python
Material selection charts | Choose materials systematically | Performance indices, e.g. E^(1/2)/rho for light stiff beams | Ashby-style chart from an open dataset you assemble | Interactive selection line | Index ranking matches derivation | Matplotlib
Sustainability and embodied energy | Compare materials by footprint | Life-cycle energy = mass * embodied energy per kg | Compare frame materials using cited data you collect | Material footprint bars | Totals reproduce input data | Python
"""),
]
