"""The eddy behind a step in a channel (a bed step in a river, in 2D and laminar): the
backward-facing step at Re = 400 in OpenFOAM's simpleFoam on three meshes, and how the
recirculation length converges as the mesh is refined.

The cases were run with OpenFOAM v1912 on the machine that built this course
(3 s, 22 s and 267 s); their results are stored below so this file runs anywhere.
With OpenFOAM installed, RUN_OPENFOAM=1 python3 riverstep.py reruns all three (about 5 min).
numpy only."""
import os, re, shutil, subprocess, tempfile
import numpy as np

# Geometry: channel height H = 1, step height S = 0.5 (expansion ratio 2), inlet over 0 < y < 0.5 with the
# parabolic profile u = 24 y (0.5 - y) (mean 1), Re = U_mean H / nu = 400, outlet 20 H downstream.
L = 20.0
def files(nx, ny, Re=400):  # ny cells across each half of the channel
    nu = 1 / Re
    yf = (np.arange(ny) + 0.5) * 0.5 / ny                      # inlet face centres, 0 < y < 0.5
    uin = 24 * yf * (0.5 - yf)
    inlet = "nonuniform List<vector> %d (%s)" % (ny, " ".join(f"({u:.8f} 0 0)" for u in uin))
    H = lambda obj, cls="dictionary": f"FoamFile {{ version 2.0; format ascii; class {cls}; object {obj}; }}\n"
    return {
"system/blockMeshDict": H("blockMeshDict") + f"""scale 1;
vertices ( (0 -0.5 0) ({L} -0.5 0) ({L} 0 0) (0 0 0) ({L} 0.5 0) (0 0.5 0)
           (0 -0.5 0.1) ({L} -0.5 0.1) ({L} 0 0.1) (0 0 0.1) ({L} 0.5 0.1) (0 0.5 0.1) );
blocks ( hex (0 1 2 3 6 7 8 9) ({nx} {ny} 1) simpleGrading (1 1 1)
         hex (3 2 4 5 9 8 10 11) ({nx} {ny} 1) simpleGrading (1 1 1) );
edges ();
boundary
(
    inlet  {{ type patch; faces ((3 9 11 5)); }}
    step   {{ type wall;  faces ((0 6 9 3)); }}
    outlet {{ type patch; faces ((1 2 8 7) (2 4 10 8)); }}
    walls  {{ type wall;  faces ((0 1 7 6) (5 11 10 4)); }}
    frontAndBack {{ type empty; faces ((0 3 2 1) (3 5 4 2) (6 7 8 9) (9 8 10 11)); }}
);
mergePatchPairs ();
""",
"system/controlDict": H("controlDict") + """application simpleFoam;
startFrom startTime; startTime 0; stopAt endTime; endTime 20000; deltaT 1;
writeControl timeStep; writeInterval 20000; purgeWrite 1; writeFormat ascii; writePrecision 8;
writeCompression off; timeFormat general; timePrecision 6; runTimeModifiable true;
""",
"system/fvSchemes": H("fvSchemes") + """ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear orthogonal; }
interpolationSchemes { default linear; }
snGradSchemes { default orthogonal; }
""",
"system/fvSolution": H("fvSolution") + """solvers
{
    p { solver GAMG; smoother GaussSeidel; tolerance 1e-10; relTol 0.05; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-10; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; residualControl { p 1e-7; U 1e-8; } }
relaxationFactors { equations { U 0.7; } fields { p 1; } }
""",
"constant/transportProperties": H("transportProperties") + f"transportModel Newtonian;\nnu {nu:.8g};\n",
"constant/turbulenceProperties": H("turbulenceProperties") + "simulationType laminar;\n",
"0/U": H("U", "volVectorField") + f"""dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 0);
boundaryField
{{
    inlet  {{ type fixedValue; value {inlet}; }}
    step   {{ type noSlip; }}
    walls  {{ type noSlip; }}
    outlet {{ type zeroGradient; }}
    frontAndBack {{ type empty; }}
}}
""",
"0/p": H("p", "volScalarField") + """dimensions [0 2 -2 0 0 0 0];
internalField uniform 0;
boundaryField
{
    inlet  { type zeroGradient; }
    step   { type zeroGradient; }
    walls  { type zeroGradient; }
    outlet { type fixedValue; value uniform 0; }
    frontAndBack { type empty; }
}
""",
    }

def crossings(x, u):
    """Zero crossings of the wall velocity, linearly interpolated: separation and reattachment points."""
    out = []
    for k in range(len(u) - 1):
        if u[k] * u[k + 1] < 0:
            out.append(x[k] - u[k] * (x[k + 1] - x[k]) / (u[k + 1] - u[k]))
    return out

def run(nx, ny):
    d = tempfile.mkdtemp(prefix="step_")
    for name, text in files(nx, ny).items():
        os.makedirs(os.path.join(d, os.path.dirname(name)), exist_ok=True)
        open(os.path.join(d, name), "w").write(text)
    env = dict(os.environ, FOAM_ETC=os.environ.get("FOAM_ETC", "/usr/share/openfoam/etc"))
    for app in ("blockMesh", "simpleFoam"):
        subprocess.run([app], cwd=d, env=env, check=True, stdout=subprocess.DEVNULL)
    t = max((s for s in os.listdir(d) if s.isdigit() and s != "0"), key=int)
    body = open(os.path.join(d, t, "U")).read().split("internalField", 1)[1]
    n = int(re.search(r"List<vector>\s*(\d+)", body).group(1))
    U = np.array([[float(q) for q in v.split()] for v in re.findall(r"\(([^()]+)\)", body.split("(", 1)[1])[:n]])
    shutil.rmtree(d)
    lower, upper = U[:nx * ny].reshape(ny, nx, 3)[0, :, 0], U[nx * ny:].reshape(ny, nx, 3)[-1, :, 0]
    x = (np.arange(nx) + 0.5) * L / nx
    return dict(iters=int(t), lower=crossings(x, lower), upper=crossings(x, upper))

MESHES = [(200, 10), (400, 20), (800, 40)]           # cells along x, cells across each half: 200 x 20, 400 x 40, 800 x 80
STORED = {                                            # OpenFOAM v1912 results, positions in units of H
    200: dict(iters=1075, lower=[4.0679], upper=[3.5779, 5.3881]),
    400: dict(iters=2342, lower=[0.0504, 4.2615], upper=[3.8815, 5.2708]),
    800: dict(iters=6238, lower=[0.0686, 4.3089], upper=[3.9724, 5.2194]),
}
if os.environ.get("RUN_OPENFOAM") == "1" and shutil.which("simpleFoam"):
    res = {nx: run(nx, ny) for nx, ny in MESHES}
    print("simpleFoam rerun")
else:
    res = STORED
    print("using the stored simpleFoam results (set RUN_OPENFOAM=1 to rerun)")

# the inlet profile really has mean 1, so Re = U H / nu = 400
f = files(800, 40)
inlet_line = [l for l in f["0/U"].splitlines() if "inlet" in l][0]
vals = [float(v) for v in re.findall(r"\(([-0-9.e]+) 0 0\)", inlet_line)]
print(f"inlet: {len(vals)} faces, mean velocity {np.mean(vals):.6f}, nu = {1/400}")
assert abs(np.mean(vals) - 1) < 1e-3

xr = np.array([res[nx]["lower"][-1] for nx, _ in MESHES])     # main reattachment point
for (nx, ny), r in zip(MESHES, (res[m] for m, _ in MESHES)):
    corner = [x for x in r["lower"] if x < 0.5]
    print(f"{nx} x {2*ny} cells, {r['iters']} SIMPLE iterations: reattachment x = {r['lower'][-1]:.4f} H = {r['lower'][-1]/0.5:.3f} S;"
          f" upper-wall bubble {r['upper'][0]:.4f} to {r['upper'][1]:.4f} H;" + (f" corner eddy to x = {corner[0]:.4f} H" if corner else " no corner eddy resolved"))
e21, e32 = xr[1] - xr[0], xr[2] - xr[1]
p = np.log(e21 / e32) / np.log(2)
x_ext = xr[2] + e32 / (2**p - 1)
print(f"changes on refinement: {e21:.4f}, {e32:.4f} (ratio {e21/e32:.2f}); observed order p = {p:.3f}")
print(f"Richardson extrapolation: x_r = {x_ext:.4f} H = {x_ext/0.5:.3f} S; the fine mesh is {abs(x_ext-xr[2])/x_ext*100:.2f} % short")
assert xr[0] < xr[1] < xr[2] and e32 < e21 / 3      # monotone and converging
assert 1.5 < p < 2.5 and abs(x_ext - xr[2]) / x_ext < 0.01
