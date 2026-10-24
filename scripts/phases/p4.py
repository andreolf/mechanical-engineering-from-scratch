PHASES = [
dict(slug="cad", title="CAD & Technical Drawing", de="CAD und Technisches Zeichnen",
 eth="Engineering Design and Material Selection (sketching, technical drawing, CAD)", eth_named=True,
 anchor="Modelling a bike dropout, a Subak weir gate and a Swiss-style watch gear",
 summary="Geometry kernels from scratch, then parametric CAD in FreeCAD and Onshape.",
 lessons="""
Technical drawing fundamentals | Read and produce engineering drawings | Orthographic projection as linear maps | Project a 3D wireframe to front/top/side views | Rotatable part with live projected views | Projections match hand-drawn views for a test block | FreeCAD TechDraw
Homogeneous coordinates | Transform geometry like a CAD kernel | 4x4 matrices for rotation + translation | Transform library with composition | Transform gizmo | Composition order matters test | NumPy
Curves: Bezier and B-splines | Understand how CAD represents curves | Bernstein polynomials, de Casteljau | de Casteljau and de Boor algorithms | Drag control points of a fairing curve | Curve passes through end control points (Bezier) | geomdl
NURBS | Represent exact circles and freeform surfaces | Rational weights, circle as NURBS | Build a NURBS circle and check radius | Weight slider | All points at exact radius | geomdl
Surfaces | Model freeform surfaces | Tensor-product patches | Evaluate a bicubic patch and its normals | Patch with draggable control net | Normals are unit length | NumPy
Constructive solid geometry | Combine solids with booleans | CSG trees, signed distance functions | SDF-based CSG with marching cubes mesh output | Boolean playground (union, cut) | Volume of union by Monte Carlo matches inclusion-exclusion | scikit-image marching_cubes
Meshes and STL | Export geometry for printing and simulation | Triangle meshes, normals, watertightness | Write an STL exporter and watertight checker | Mesh viewer with open-edge highlighting | Closed mesh has every edge shared by two faces | trimesh
Parametric sketches and constraints | Understand constraint solvers | Geometric constraints as nonlinear equations | Newton-based 2D sketch solver | Drag a constrained sketch | Constraints satisfied to 1e-9 after drag | FreeCAD Sketcher
Parametric part modelling | Build a real part with design intent | Feature tree, parameters | Model a bike dropout in FreeCAD driven by a spreadsheet | Parameter slider preview (exported meshes) | Rebuild succeeds for parameter sweep | FreeCAD Part Design
Assemblies and mates | Assemble parts with joints | Kinematic constraints between bodies | Assemble a four-bar in Onshape or FreeCAD Assembly | Animated assembly | Mates leave intended DOF only | Onshape (free plan) / FreeCAD Assembly
Scripting CAD | Generate parts from code | Programmatic B-rep modelling | Generate a gear or weir gate with CadQuery | Code-to-model preview | Exported STEP reopens with same volume | CadQuery / build123d
Drawings, GD&T and handoff | Communicate tolerances | GD&T basics: datums, position, flatness | Annotated drawing of your dropout | Tolerance zone visualiser | Drawing contains all required dimensions checklist | FreeCAD TechDraw
"""),
dict(slug="fem", title="Finite Element Method from Scratch", de="Finite-Elemente-Methode",
 eth="Method of Finite Elements I (D-MAVT MSc course; check current catalogue) and computational mechanics electives", eth_named=False,
 anchor="A bike frame, a Swiss footbridge and an alpine dam wall",
 summary="From spring chains to 2D/3D solids, dynamics and nonlinearity, then CalculiX and FEniCSx.",
 lessons="""
Springs to stiffness matrices | See FEM as assembling springs | Element stiffness k [[1,-1],[-1,1]], assembly | Assemble a spring chain and solve | Spring chain with node displacements | Matches series-spring formula | NumPy
Direct stiffness method for trusses | Solve any 2D truss | Transformation of bar stiffness to global axes | 2D truss FEM solver | Break-the-bridge truss lab (LAB:truss) | Matches statics solution for determinate trusses | NumPy
Weak form | Derive FEM from a differential equation | Multiply by test function, integrate by parts | Weak form of -(EA u')' = f symbolically | Test-function visualiser | Galerkin system equals stiffness method for bars | SymPy
Shape functions and the 1D element | Build elements from interpolation | Linear and quadratic Lagrange shape functions | 1D FEM with linear and quadratic elements | Element order toggle with error plot | Quadratic converges faster | NumPy
Beam elements | Model frames | Hermite cubic shape functions, 4x4 beam stiffness | Euler-Bernoulli beam FEM | Frame with loads and deformed shape | Cantilever tip deflection exact with one element (point load) | NumPy
2D frames | Analyse a bike frame as a planar frame | Frame element = bar + beam with transformation | Planar frame solver | Bike frame under rider load (educational model) | Equilibrium of reactions | NumPy
Isoparametric mapping | Handle arbitrary element shapes | Jacobian of mapping, Gauss quadrature | Map and integrate on a distorted quad | Distorted element with Jacobian warning | Area computed equals polygon area | NumPy
Plane stress and plane strain | Model 2D solids | Constitutive matrices D | CST and Q4 elements | Plate with hole stress map | Peak stress approaches 3x with mesh refinement | NumPy
Meshing | Generate meshes from geometry | Delaunay triangulation, quality metrics | Simple Delaunay meshing pipeline | Mesh quality colouring | No inverted elements | Gmsh
Assembly and sparse solvers at scale | Solve 100k-DOF problems | Sparse assembly, bandwidth, reordering | COO-to-CSR assembly and sparse solve | Sparsity before/after reordering | Same answer as dense on small problem | SciPy sparse
Patch test and convergence | Verify your element formulation | Patch test, a priori error estimates | Patch test and convergence study | Error vs h plot | Patch test passes to machine precision | pytest
Locking and remedies | Understand shear and volumetric locking | Why linear elements are too stiff in bending | Compare Q4 vs reduced integration on a bending beam | Locking demo | Reduced integration closer to beam theory | NumPy
3D solids | Extend to tetrahedra and hexahedra | Tet4 stiffness | 3D tet FEM for a bracket | 3D stress viewer (three.js) | Uniform tension patch exact | NumPy + meshio
Heat conduction FEM | Reuse the machinery for heat | Same weak form, conductivity matrix | Steady and transient 2D heat FEM | Heat map on a heatsink | Matches 1D analytic in slab test | NumPy
Modal analysis with FEM | Find natural frequencies of structures | Consistent mass matrix, generalised eigenproblem | Modal analysis of a footbridge model | Mode shape animation | Cantilever frequencies converge to beam theory | SciPy eigsh
Transient dynamics | Simulate impacts and earthquakes | Newmark-beta method | Newmark integrator on a frame | Ground shake slider | Average acceleration scheme is unconditionally stable | NumPy
Nonlinear FEM | Handle large deformations and plasticity | Newton-Raphson, tangent stiffness | Geometrically nonlinear truss (snap-through) with arc-length | Snap-through animation | Arc-length traces the full equilibrium path | NumPy
Pro tools: CalculiX and FEniCSx | Map your solver to industrial open-source tools | Same weak forms in a DSL | Recreate your plate-with-hole in FEniCSx and a bracket in CalculiX | Side-by-side comparison | Results agree within discretisation error | FEniCSx, CalculiX, Gmsh, ParaView
"""),
dict(slug="cfd", title="Computational Fluid Dynamics from Scratch", de="Numerische Strömungsmechanik",
 eth="Computational fluid dynamics electives (generic)", eth_named=False,
 anchor="The coconut eddy, the Rhine Falls plunge pool, wind around a Zurich tower",
 summary="Finite differences and finite volumes, lid-driven cavity, lattice Boltzmann, then OpenFOAM.",
 lessons="""
Why CFD and what it can't do | Set honest expectations | Discretisation, modelling and round-off errors | Error budget worksheet | Error source explorer | Budget sums to observed error in a toy case | Python
Conservation form and finite volumes | Write conservation laws as fluxes | Integral form, cell averages, face fluxes | 1D finite-volume advection | Cells with flux arrows | Total quantity conserved to machine precision | NumPy
Flux schemes | Choose stable, accurate fluxes | Upwind, Lax-Wendroff, TVD limiters | Implement minmod and superbee limiters | Square-pulse advection comparison | TVD scheme creates no new extrema | NumPy
Burgers' equation and shocks | Meet nonlinearity | Characteristics, Rusanov flux | Burgers solver forming a shock | Wave steepening animation | Shock speed matches Rankine-Hugoniot | NumPy
Shallow water equations | Model rivers, floods and canals | Saint-Venant equations | 1D dam-break solver | Dam break in an alpine valley | Matches Ritter analytical solution | NumPy
2D shallow water and Subak terraces | Simulate terrace overflow | 2D finite volume with wetting/drying (simplified) | 2D shallow-water terrace cascade | Water spilling down terraces (LAB:subak) | Mass conserved | NumPy
Streamfunction-vorticity method | Solve 2D incompressible flow | psi-omega formulation | Lid-driven cavity at Re = 100 | Streamline animation | Primary vortex centre near published benchmark (Ghia et al. 1982) | NumPy
Pressure-velocity coupling | Handle incompressibility in primitive variables | Projection method (Chorin) | Fractional-step NS solver on a staggered grid | Pressure and velocity panels | Divergence below 1e-8 after projection | NumPy
Flow past a cylinder | Reproduce vortex shedding | Immersed boundary / masked cells | Cylinder in channel at Re ~ 100 | Karman street animation | Strouhal number close to 0.16-0.2 (literature range) | NumPy
The coconut eddy | Simulate recirculation behind a boulder | Separated flow, recirculation length | Particle tracking in your cylinder/boulder solution | Coconut trapped behind the boulder (LAB:coconut) | Particle released in the wake stays trapped for many shedding cycles in the model | NumPy
Lattice Boltzmann: theory | Derive fluid flow from particle distributions | BGK collision, D2Q9 lattice, Chapman-Enskog sketch | D2Q9 streaming and collision kernels | Distribution function viewer | Equilibrium recovers density and momentum | NumPy
Lattice Boltzmann: flows | Run real flows with LBM | Bounce-back boundaries, viscosity nu = (tau - 1/2)/3 | LBM channel and cylinder flow; JS port in the browser | Live LBM in canvas | Poiseuille profile within 1% | NumPy / JS
Turbulence modelling | Use RANS and LES appropriately | k-epsilon, k-omega SST, Smagorinsky | Mixing-length model for channel flow | Model selector | Log-law region reproduced | Python
Meshes for CFD | Build meshes that converge | Orthogonality, skewness, y+ | Mesh quality checker | Mesh quality heat-map | Flags skewed cells | Gmsh / snappyHexMesh
OpenFOAM: first case | Run a professional solver | Case structure: 0, constant, system | Run icoFoam lid-driven cavity and compare to your solver | Side-by-side streamlines | Results agree within mesh error | OpenFOAM, ParaView
OpenFOAM: river eddy | Model the Bali boulder eddy in 2D | Turbulent incompressible solver setup | simpleFoam/pimpleFoam case behind a boulder | Velocity field render | Recirculation length vs mesh study | OpenFOAM
Verification and validation in CFD | Trust your results | Grid convergence index (GCI) | GCI study script | Convergence plot | GCI reported with observed order | Python
Postprocessing and visualisation | Communicate flows clearly | Q-criterion, streamlines, line integral convolution | Compute Q-criterion and render with three.js | Interactive 3D flow viewer | Q > 0 in vortex cores of test field | ParaView, three.js
"""),
dict(slug="manufacturing", title="Manufacturing", de="Fertigung",
 eth="Werkstoffe und Fertigung (manufacturing part)", eth_named=True,
 anchor="Swiss precision machining, Bali bamboo workshops, a maker space 3D printer",
 summary="How things are made: cutting, forming, casting, joining, additive, and the physics behind each.",
 lessons="""
Manufacturing process map | Pick the right process family | Process selection by volume, material, tolerance | Process selector rule engine | Interactive process map | Selector reproduces textbook examples | Python
Metal cutting mechanics | Understand chip formation | Merchant's circle, shear angle | Cutting force model | Rake angle slider | Force decreases with rake angle in the model | NumPy
Tool life and economics | Choose cutting speeds | Taylor tool life V T^n = C, cost minimisation | Optimal cutting speed calculator | Cost vs speed curve | Optimum where derivative is zero | SciPy
CNC and G-code | Turn geometry into toolpaths | Toolpath offsets, interpolation | Write a G-code generator for a 2D pocket | G-code toolpath simulator | Toolpath stays inside boundary with tool radius offset | FreeCAD Path / CAM
Turning and milling | Compute feeds, speeds and surface finish | Ra ~ f^2/(32 r) | Surface roughness estimator | Feed slider with surface profile | Roughness scales with feed squared | Python
Sheet metal forming | Bend sheet without cracking | Bend allowance, springback | Flat pattern calculator | Bend angle slider | Bend allowance formula satisfied | FreeCAD SheetMetal
Bulk forming | Understand forging and extrusion | Slab method, flow stress | Extrusion force estimate | Ram speed and ratio sliders | Force increases with extrusion ratio | NumPy
Casting | Design castings that solidify soundly | Chvorinov's rule t = B (V/A)^n | Riser sizing tool | Solidification order animation | Riser solidifies after casting | Python
Injection moulding | Understand plastic part design | Fill pressure, cooling time ~ thickness^2 | Cooling time estimator | Wall thickness slider | Time scales with thickness squared | Python
Welding and joining physics | Control heat input | Rosenthal moving heat source (simplified) | Weld pool temperature field | Torch speed slider | Peak temperature decreases with speed | NumPy
Additive manufacturing | Print functional parts | Layer adhesion, anisotropy, overhang angles | Slicer from scratch: slice an STL into layers and perimeters | Layer-by-layer preview | Sliced area matches cross-section area | PrusaSlicer / CuraEngine
Metrology on the shop floor | Measure what you make | Measurement uncertainty, Abbe principle | Uncertainty budget for a caliper measurement | Abbe error visual | Combined uncertainty via root sum of squares | Python
Quality and statistical process control | Keep processes in control | Control charts, Cp and Cpk | SPC chart generator | Process drift simulation | Cpk computed correctly on synthetic data | Python
Building with bamboo | Apply manufacturing thinking to natural materials | Joint strength, treatment, variability | Statistical design value from bamboo test data you gather | Joint type comparison | 5th-percentile design value computed | Python
"""),
dict(slug="measurement-control", title="Measurement, Signals & Control", de="Messtechnik und Regelungstechnik",
 eth="Regelungstechnik 1; Praktikum / lab courses (generic for measurement)", eth_named=True,
 anchor="Measuring the Limmat flow, stabilising a bike, a Bali sensor buoy",
 summary="Sensors, uncertainty, signal processing, system identification and feedback control.",
 lessons="""
Measurement uncertainty | Report results honestly | GUM: type A/B, propagation | Uncertainty propagation by linearisation and Monte Carlo | Input uncertainty sliders | Both methods agree for near-linear models | uncertainties (Python)
Sensors and transducers | Know how sensors really work | Strain gauge bridge equations | Wheatstone bridge output model | Bridge with strain slider | Quarter bridge output ~ V GF epsilon/4 | Python
Sampling and aliasing | Sample without lying | Nyquist theorem | Demonstrate aliasing on a rotating wheel | Wagon-wheel effect lab | Aliased frequency formula verified | NumPy
Filters | Clean noisy signals | Low-pass RC, Butterworth design | Implement IIR filter from difference equation | Filter cutoff slider | Matches scipy.signal.lfilter | SciPy signal
Data acquisition with microcontrollers | Log real data | ADC resolution, quantisation noise q/sqrt(12) | Read an accelerometer via serial and log | Live plot | Quantisation noise matches theory | Arduino / MicroPython
River flow measurement | Measure the Limmat or a Bali canal | Velocity-area method, float method corrections | Discharge from float measurements | Cross-section integrator | Discharge equals sum of v_i A_i | Python
Strain and force measurement | Build a load cell | Bending beam load cell design | Calibrate a load cell with least squares | Calibration curve | Linearity error reported | NumPy
Temperature measurement | Measure temperature with known lag | First-order sensor dynamics | Thermocouple time-constant identification | Step response fit | Fitted tau within 5% of synthetic | SciPy
System identification | Build models from data | ARX least squares | Identify a motor model from step data | Model vs data overlay | Identified parameters match synthetic | SysIdentPy / python-control
Transfer functions and block diagrams | Model dynamic systems for control | Laplace domain, poles and zeros | Transfer function algebra class | Pole-zero map | Step response from TF matches ODE | python-control
Feedback and stability | Understand why feedback works | Closed-loop poles, Routh-Hurwitz | Root locus from scratch | Gain slider moving poles | Unstable when poles cross into RHP | python-control
PID control | Tune a controller | P, I, D effects, Ziegler-Nichols | PID controller simulation with anti-windup | Cruise control of an e-bike | Integral action removes steady-state error | python-control
Frequency response and robustness | Design robust controllers | Bode, Nyquist, gain and phase margins | Compute margins numerically | Bode plot with margin markers | Margins match python-control | python-control
State space and LQR | Control multi-variable systems | x' = A x + B u, Riccati equation | LQR for an inverted pendulum | Balance the pendulum lab | Closed-loop eigenvalues all negative real part | python-control
"""),
dict(slug="capstone", title="Capstone Projects", de="Fokus-Projekt / Bachelor-Arbeit style capstone",
 eth="Fokus-Projekt / Bachelor-Arbeit (project format, not course content)", eth_named=True,
 anchor="Real projects in Bali and Switzerland, each with a public artifact",
 summary="Integrate everything: derive, simulate, build, measure and publish a working machine or study.",
 lessons="""
Capstone method | Plan a project that ends with evidence | Requirements, risk, verification matrix | Project template repo with verification matrix | Gantt and risk board | Every requirement has a test | git, Quarto
Coconut eddy: from field video to CFD | Reproduce the Bali boulder eddy | Strouhal, recirculation, particle residence time | Combine video particle tracking with your CFD solver | Coconut lab extended (LAB:coconut) | Model residence time compared with your measurement, discrepancy explained | OpenFOAM, OpenCV
Subak weir network | Model a full terrace water-sharing network | Weir equations + network mass balance | Network simulator with seasonal inflow assumptions | Subak lab extended (LAB:subak) | Mass balance closes at every terrace | NumPy, EPANET concepts
Bamboo footbridge | Design and analyse a small bamboo footbridge | Truss/frame FEM, vibration comfort checks (educational) | Full design calculation in your FEM | Break-the-bridge lab with bamboo properties (LAB:truss) | Safety factors computed and documented; not a substitute for a licensed engineer | FEniCSx / CalculiX
Micro-hydro turbine for a village | Size a Pelton or crossflow turbine | Euler turbine equation, penstock losses | Turbine sizing tool | Head and flow sliders | Power within efficiency bounds | Python, FreeCAD
Alpine pumped-storage study | Evaluate a pumped-storage scheme | Energy, hydraulics, water hammer | Integrated model with stated assumptions | Reservoir operation animation | Energy balance closes | Python
E-bike drivetrain | Design a hub gearbox and its thermal limits | Planetary gears, bearing life, heat transfer | Integrated drivetrain calculation | Drivetrain configurator | All elements pass life/strength checks in the model | CadQuery, Python
Flywheel energy store | Design a safe small flywheel | Rotor stress, bearings, containment | Flywheel design report | Flywheel lab (LAB:flywheel) | Burst margin documented | FreeCAD, CalculiX
Wind-loaded structure | Analyse a sign or small tower | Wind load, vortex shedding, fatigue | Coupled analysis pipeline | Wind lab | Fatigue life estimate reported with assumptions | Python
Publish your artifact | Ship it like open source | Licensing, reproducibility, documentation | Publish repo, README, and an interactive web lab | Your own Break-the-machine page | Fresh clone reproduces all figures | GitHub Pages, three.js
"""),
]
