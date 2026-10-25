"""The lid-driven cavity at Re = 100 in OpenFOAM (icoFoam) and in this course's own
MAC projection solver, compared on the centrelines with each other and with Ghia et al.

The OpenFOAM case is written out in full below. icoFoam (OpenFOAM v1912, Debian package)
was run on the box that built this course: 64 x 64 cells, dt = 0.004, to t = 30, 28 s.
Its centreline velocities are stored here, so this file runs without OpenFOAM. With
OpenFOAM installed, RUN_OPENFOAM=1 python3 openfoam_cavity.py reruns the case. numpy only."""
import os, re, shutil, subprocess, tempfile
import numpy as np

CASE = {
    "system/blockMeshDict": """FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
scale 1;
vertices ( (0 0 0) (1 0 0) (1 1 0) (0 1 0) (0 0 0.1) (1 0 0.1) (1 1 0.1) (0 1 0.1) );
blocks ( hex (0 1 2 3 4 5 6 7) (64 64 1) simpleGrading (1 1 1) );
edges ();
boundary
(
    movingWall { type wall; faces ((3 7 6 2)); }
    fixedWalls { type wall; faces ((0 4 7 3) (2 6 5 1) (1 5 4 0)); }
    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }
);
mergePatchPairs ();
""",
    "system/controlDict": """FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     icoFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         30;
deltaT          0.004;
writeControl    timeStep;
writeInterval   2500;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
""",
    "system/fvSchemes": """FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; grad(p) Gauss linear; }
divSchemes      { default none; div(phi,U) Gauss linear; }
laplacianSchemes { default Gauss linear orthogonal; }
interpolationSchemes { default linear; }
snGradSchemes   { default orthogonal; }
""",
    "system/fvSolution": """FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers
{
    p { solver PCG; preconditioner DIC; tolerance 1e-08; relTol 0.05; }
    pFinal { $p; relTol 0; }
    U { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-08; relTol 0; }
}
PISO { nCorrectors 2; nNonOrthogonalCorrectors 0; pRefCell 0; pRefValue 0; }
""",
    "constant/transportProperties": """FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }
nu              0.01;
""",
    "0/U": """FoamFile { version 2.0; format ascii; class volVectorField; object U; }
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    movingWall { type fixedValue; value uniform (1 0 0); }
    fixedWalls { type noSlip; }
    frontAndBack { type empty; }
}
""",
    "0/p": """FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    movingWall { type zeroGradient; }
    fixedWalls { type zeroGradient; }
    frontAndBack { type empty; }
}
""",
}

# icoFoam result at t = 30: u on x = 0.5 (cell centres y = (j + 1/2)/64, the two cells either side averaged)
U_OF = np.array([
    -0.005946, -0.017023, -0.027428, -0.037276, -0.046664, -0.055679, -0.064398, -0.072886,
    -0.081201, -0.089390, -0.097491, -0.105536, -0.113543, -0.121523, -0.129477, -0.137394,
    -0.145253, -0.153021, -0.160652, -0.168091, -0.175269, -0.182107, -0.188517, -0.194400,
    -0.199649, -0.204156, -0.207805, -0.210483, -0.212080, -0.212491, -0.211622, -0.209390,
    -0.205727, -0.200585, -0.193934, -0.185763, -0.176083, -0.164924, -0.152334, -0.138372,
    -0.123111, -0.106626, -0.088991, -0.070271, -0.050510, -0.029724, -0.007886, 0.015085,
    0.039348, 0.065152, 0.092858, 0.122960, 0.156099, 0.193071, 0.234822, 0.282412,
    0.336957, 0.399519, 0.470947, 0.551674, 0.641471, 0.739205, 0.842632, 0.948304,
])
# and v on y = 0.5 at x = (i + 1/2)/64
V_OF = np.array([
    0.014647, 0.040948, 0.064360, 0.085016, 0.103073, 0.118699, 0.132076, 0.143384,
    0.152801, 0.160497, 0.166631, 0.171348, 0.174777, 0.177029, 0.178201, 0.178371,
    0.177603, 0.175946, 0.173433, 0.170090, 0.165930, 0.160957, 0.155171, 0.148565,
    0.141127, 0.132846, 0.123706, 0.113695, 0.102799, 0.091009, 0.078320, 0.064733,
    0.050255, 0.034903, 0.018706, 0.001704, -0.016044, -0.034464, -0.053458, -0.072904,
    -0.092651, -0.112518, -0.132289, -0.151709, -0.170489, -0.188295, -0.204763, -0.219492,
    -0.232061, -0.242037, -0.248993, -0.252529, -0.252298, -0.248031, -0.239565, -0.226863,
    -0.210037, -0.189351, -0.165223, -0.138204, -0.108956, -0.078213, -0.046736, -0.015302,
])

def run_openfoam():
    d = tempfile.mkdtemp(prefix="cavity_")
    for name, text in CASE.items():
        os.makedirs(os.path.join(d, os.path.dirname(name)), exist_ok=True)
        open(os.path.join(d, name), "w").write(text)
    env = dict(os.environ, FOAM_ETC=os.environ.get("FOAM_ETC", "/usr/share/openfoam/etc"))
    for app in ("blockMesh", "icoFoam"):
        subprocess.run([app], cwd=d, env=env, check=True, stdout=subprocess.DEVNULL)
    s = open(os.path.join(d, "30", "U")).read()
    i = s.index("internalField")
    vals = re.findall(r"\(([^()]+)\)", s[i:].split("(", 1)[1])[:4096]
    U = np.array([[float(x) for x in v.split()] for v in vals]).reshape(64, 64, 3)   # [j, i]
    shutil.rmtree(d)
    return 0.5 * (U[:, 31, 0] + U[:, 32, 0]), 0.5 * (U[31, :, 1] + U[32, :, 1])

if os.environ.get("RUN_OPENFOAM") == "1" and shutil.which("icoFoam"):
    U_OF, V_OF = run_openfoam()
    print("icoFoam rerun")
else:
    print("using the stored icoFoam centrelines (set RUN_OPENFOAM=1 to rerun)")

def mac_cavity(N=64, Re=100.0, tmax=60.0, tol=1e-6):
    """Chorin projection on a MAC grid (as in the projection lesson)."""
    h = 1.0 / N
    dt = min(0.2 * h * h * Re, 0.5 * h)
    L = (np.diag(-2.0 * np.ones(N)) + np.diag(np.ones(N - 1), 1) + np.diag(np.ones(N - 1), -1)) / h**2
    L[0, 0] = L[-1, -1] = -1 / h**2
    lam, V = np.linalg.eigh(L)
    den = lam[:, None] + lam[None, :]
    k0 = np.argmin(abs(lam)); den[k0, k0] = np.inf
    U = np.zeros((N + 1, N + 2)); W = np.zeros((N + 2, N + 1))
    def ghosts():
        U[:, 0] = -U[:, 1]; U[:, -1] = 2 - U[:, -2]; W[0, :] = -W[1, :]; W[-1, :] = -W[-2, :]
    t, it = 0.0, 0
    while t < tmax:
        ghosts()
        uc = 0.5 * (U[1:, 1:-1] + U[:-1, 1:-1]); vc = 0.5 * (W[1:-1, 1:] + W[1:-1, :-1])
        uv = 0.5 * (U[:, 1:] + U[:, :-1]) * 0.5 * (W[1:, :] + W[:-1, :])
        lu = (U[2:, 1:-1] + U[:-2, 1:-1] + U[1:-1, 2:] + U[1:-1, :-2] - 4 * U[1:-1, 1:-1]) / h**2
        lv = (W[2:, 1:-1] + W[:-2, 1:-1] + W[1:-1, 2:] + W[1:-1, :-2] - 4 * W[1:-1, 1:-1]) / h**2
        Fu = -(uc[1:] ** 2 - uc[:-1] ** 2) / h - (uv[1:-1, 1:] - uv[1:-1, :-1]) / h + lu / Re
        Fv = -(vc[:, 1:] ** 2 - vc[:, :-1] ** 2) / h - (uv[1:, 1:-1] - uv[:-1, 1:-1]) / h + lv / Re
        U[1:-1, 1:-1] += dt * Fu; W[1:-1, 1:-1] += dt * Fv
        div = (U[1:, 1:-1] - U[:-1, 1:-1] + W[1:-1, 1:] - W[1:-1, :-1]) / h
        p = V @ ((V.T @ (div / dt) @ V) / den) @ V.T
        U[1:-1, 1:-1] -= dt * (p[1:] - p[:-1]) / h; W[1:-1, 1:-1] -= dt * (p[:, 1:] - p[:, :-1]) / h
        t += dt; it += 1
        if it % 200 == 0 and max(np.max(abs(Fu - (p[1:] - p[:-1]) / h)), np.max(abs(Fv - (p[:, 1:] - p[:, :-1]) / h))) < tol:
            break
    return U[N // 2, 1:-1], W[1:-1, N // 2], it

u_own, v_own, it = mac_cavity()
y = (np.arange(64) + 0.5) / 64
ghia_y = np.array([0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813, 0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609, 0.9688, 0.9766])
ghia_u = np.array([-0.03717, -0.04192, -0.04775, -0.06434, -0.10150, -0.15662, -0.21090, -0.20581, -0.13641, 0.00332, 0.23151, 0.68717, 0.73722, 0.78871, 0.84123])
ghia_x = np.array([0.0625, 0.0703, 0.0781, 0.0938, 0.1563, 0.2266, 0.2344, 0.5000, 0.8047, 0.8594, 0.9063, 0.9453, 0.9531, 0.9609, 0.9688])
ghia_v = np.array([0.09233, 0.10091, 0.10890, 0.12317, 0.16077, 0.17507, 0.17527, 0.05454, -0.24533, -0.22445, -0.16914, -0.10313, -0.08864, -0.07391, -0.05906])

du = np.max(abs(u_own - U_OF)); dv = np.max(abs(v_own - V_OF))
gu_of = np.max(abs(np.interp(ghia_y, y, U_OF) - ghia_u)); gu_own = np.max(abs(np.interp(ghia_y, y, u_own) - ghia_u))
gv_of = np.max(abs(np.interp(ghia_x, y, V_OF) - ghia_v)); gv_own = np.max(abs(np.interp(ghia_x, y, v_own) - ghia_v))
print(f"own MAC solver: steady after {it} steps")
print(f"u on x = 0.5: min {U_OF.min():.4f} (icoFoam), {u_own.min():.4f} (own), -0.2109 (Ghia); max |own - icoFoam| = {du:.4f}")
print(f"v on y = 0.5: max {V_OF.max():.4f} / min {V_OF.min():.4f} (icoFoam), {v_own.max():.4f} / {v_own.min():.4f} (own), 0.1753 / -0.2453 (Ghia); max |own - icoFoam| = {dv:.4f}")
print(f"max deviation from Ghia: icoFoam u {gu_of:.4f}, v {gv_of:.4f}; own u {gu_own:.4f}, v {gv_own:.4f}")
assert du < 0.01 and dv < 0.01
assert max(gu_of, gv_of, gu_own, gv_own) < 0.02
