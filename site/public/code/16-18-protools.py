"""Mapping the from-scratch solvers to FEniCSx, CalculiX and Gmsh. FEniCSx and CalculiX are not installed here, so this file (1) writes the Gmsh geometry and the CalculiX input deck from our own meshes and checks them, and (2) runs the 'agree within discretisation error' test between two independent discretisations of the plate with a hole (Q4 and CST), using Richardson extrapolation for the error estimate."""
import math
import numpy as np

# ---------------- plate with a hole: our solver (plane stress, quarter model, as in 16.08) ----------------

def D_ps(E, nu):
    return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])


def q4_B(X, xi, eta):
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)], [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
    J = dN @ X; dNx = np.linalg.solve(J, dN)
    B = np.zeros((3, 8)); B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
    return B, np.linalg.det(J)


def cst_B(X):
    (x1, y1), (x2, y2), (x3, y3) = X
    A2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    b = np.array([y2 - y3, y3 - y1, y1 - y2]) / A2; c = np.array([x3 - x2, x1 - x3, x2 - x1]) / A2
    B = np.zeros((3, 6)); B[0, 0::2] = b; B[1, 1::2] = c; B[2, 0::2] = c; B[2, 1::2] = b
    return B, A2 / 2


def quarter_mesh(n, a=1.0, w=10.0):
    th = np.linspace(0, math.pi / 2, 2 * n + 1)
    outer = np.array([(w, w * math.tan(t)) if t <= math.pi / 4 else (w / math.tan(t) if t < math.pi / 2 else 0.0, w) for t in th])
    nodes = []
    for r in np.linspace(0, 1, n + 1) ** 1.8:
        for k, t in enumerate(th):
            inner = np.array([a * math.cos(t), a * math.sin(t)]); nodes.append(inner + r * (outer[k] - inner))
    m = 2 * n + 1
    quads = [[i * m + k, (i + 1) * m + k, (i + 1) * m + k + 1, i * m + k + 1] for i in range(n) for k in range(2 * n)]
    return np.array(nodes), np.array(quads)


def plate(n, element, E=210e3, nu=0.3, S=1.0, w=10.0):
    """Returns the mean x displacement of the loaded edge (a smooth, energy-like quantity)."""
    nodes, quads = quarter_mesh(n, w=w); D = D_ps(E, nu); nd = len(nodes)
    K = np.zeros((2 * nd, 2 * nd)); F = np.zeros(2 * nd)
    elems = quads if element == "Q4" else [t for q in quads for t in ([q[0], q[1], q[2]], [q[0], q[2], q[3]])]
    g = 1 / math.sqrt(3)
    for e in elems:
        X = nodes[e]; d = np.ravel([[2 * i, 2 * i + 1] for i in e])
        if element == "Q4":
            k = sum(q4_B(X, a, b)[0].T @ D @ q4_B(X, a, b)[0] * q4_B(X, a, b)[1] for a in (-g, g) for b in (-g, g))
        else:
            B, A = cst_B(X); k = B.T @ D @ B * A
        K[np.ix_(d, d)] += k
    edge = sorted([i for i in range(nd) if abs(nodes[i, 0] - w) < 1e-9], key=lambda i: nodes[i, 1])
    for i, j in zip(edge[:-1], edge[1:]):
        h = nodes[j, 1] - nodes[i, 1]; F[2 * i] += S * h / 2; F[2 * j] += S * h / 2
    fixed = [2 * i + 1 for i in range(nd) if abs(nodes[i, 1]) < 1e-9] + [2 * i for i in range(nd) if abs(nodes[i, 0]) < 1e-9]
    free = np.setdiff1d(np.arange(2 * nd), fixed); u = np.zeros(2 * nd)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    return F @ u / (S * w)          # compliance / applied force = load-weighted mean edge displacement


def richardson(f1, f2, f3, r=2.0):
    """Three meshes refined by r: observed order p, extrapolated value, error estimate of the finest."""
    p = math.log(abs(f1 - f2) / abs(f2 - f3)) / math.log(r)
    fx = f3 + (f3 - f2) / (r**p - 1)
    return p, fx, abs(fx - f3)

# ---------------- what you would run with the professional tools ----------------

GMSH_GEO = """// plate with a hole, quarter model (Gmsh .geo)
a = 1.0; w = 10.0; h = 0.08;
Point(1) = {a, 0, 0, h}; Point(2) = {w, 0, 0, 1.0}; Point(3) = {w, w, 0, 1.0};
Point(4) = {0, w, 0, 1.0}; Point(5) = {0, a, 0, h}; Point(6) = {0, 0, 0, h};
Line(1) = {1, 2}; Line(2) = {2, 3}; Line(3) = {3, 4}; Line(4) = {4, 5};
Circle(5) = {5, 6, 1};
Curve Loop(1) = {1, 2, 3, 4, 5}; Plane Surface(1) = {1};
Physical Curve("symmetry_y", 1) = {1}; Physical Curve("load", 2) = {2};
Physical Curve("symmetry_x", 4) = {4}; Physical Surface("plate", 10) = {1};
"""

FENICSX_PY = '''# FEniCSx (dolfinx 0.8-style API) - not run here
from mpi4py import MPI
import numpy as np, ufl
from dolfinx import fem, io
from dolfinx.fem.petsc import LinearProblem
mesh, cells, facets = io.gmshio.read_from_msh("plate.msh", MPI.COMM_WORLD, gdim=2)
V = fem.functionspace(mesh, ("Lagrange", 1, (2,)))
E, nu = 210e3, 0.3; mu = E / (2 * (1 + nu)); lam = E * nu / (1 - nu**2)   # plane stress lambda
eps = lambda u: ufl.sym(ufl.grad(u)); sig = lambda u: 2 * mu * eps(u) + lam * ufl.tr(eps(u)) * ufl.Identity(2)
u, v = ufl.TrialFunction(V), ufl.TestFunction(V)
ds = ufl.Measure("ds", domain=mesh, subdomain_data=facets)
a = ufl.inner(sig(u), eps(v)) * ufl.dx                    # the same weak form as K
L = ufl.dot(fem.Constant(mesh, (1.0, 0.0)), v) * ds(2)     # unit traction on the loaded edge
bcs = [fem.dirichletbc(np.float64(0), fem.locate_dofs_topological(V.sub(1), 1, facets.find(1)), V.sub(1)),
       fem.dirichletbc(np.float64(0), fem.locate_dofs_topological(V.sub(0), 1, facets.find(4)), V.sub(0))]
uh = LinearProblem(a, L, bcs=bcs, petsc_options={"ksp_type": "preonly", "pc_type": "lu"}).solve()
'''


def calculix_deck(nodes, tets, fixed_nodes, load_nodes, P):
    """CalculiX / Abaqus-style input deck for a C3D4 bracket. Units N, mm, MPa."""
    out = ["*HEADING", "L bracket, C3D4, from the 16.13 mesh", "*NODE"]
    out += [f"{i+1}, {x:.6g}, {y:.6g}, {z:.6g}" for i, (x, y, z) in enumerate(nodes)]
    out += ["*ELEMENT, TYPE=C3D4, ELSET=EALL"] + [f"{e+1}, " + ", ".join(str(q + 1) for q in t) for e, t in enumerate(tets)]
    out += ["*NSET, NSET=NFIX"] + [", ".join(str(q + 1) for q in fixed_nodes[k:k + 16]) for k in range(0, len(fixed_nodes), 16)]
    out += ["*MATERIAL, NAME=STEEL", "*ELASTIC", "210000., 0.3", "*SOLID SECTION, ELSET=EALL, MATERIAL=STEEL",
            "*BOUNDARY", "NFIX, 1, 3", "*STEP", "*STATIC", "*CLOAD"]
    out += [f"{q+1}, 3, {-P/len(load_nodes):.6g}" for q in load_nodes]
    out += ["*NODE FILE", "U", "*EL FILE", "S", "*END STEP"]
    return "\n".join(out)


KUHN = [(0, 1, 2, 6), (0, 2, 3, 6), (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6), (0, 5, 1, 6)]


def bracket_mesh(h=10.0):
    m = int(20 / h)
    cells = {(i, j, k) for i in range(int(80 / h)) for j in range(m) for k in range(int(40 / h), int(60 / h))} | {(i, j, k) for i in range(m) for j in range(m) for k in range(int(60 / h))}
    ids = {}; nodes = []; tets = []; cor = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
    for (i, j, k) in sorted(cells):
        c = []
        for a, b, d in cor:
            key = (i + a, j + b, k + d)
            if key not in ids: ids[key] = len(nodes); nodes.append([h * q for q in key])
            c.append(ids[key])
        for t in KUHN:
            tt = [c[q] for q in t]; X = np.array([nodes[q] for q in tt])
            if np.linalg.det(np.hstack([np.ones((4, 1)), X])) < 0: tt = [tt[0], tt[2], tt[1], tt[3]]
            tets.append(tt)
    return np.array(nodes), tets


if __name__ == "__main__":
    # 1) agreement within discretisation error: Q4 against CST on meshes n = 8, 16, 32
    vals = {el: [plate(n, el) for n in (8, 16, 32)] for el in ("Q4", "CST")}
    est = {}
    for el, (f1, f2, f3) in vals.items():
        p, fx, err = richardson(f1, f2, f3); est[el] = (fx, err, f3)
        print(f"{el:3s}: edge displacement x E / S = {f1*210e3:.5f}, {f2*210e3:.5f}, {f3*210e3:.5f}; observed order {p:.2f}; extrapolated {fx*210e3:.5f} (error estimate {err*210e3:.5f})")
    diff = abs(est["Q4"][2] - est["CST"][2]); band = est["Q4"][1] + est["CST"][1]
    xdiff = abs(est["Q4"][0] - est["CST"][0])
    print(f"finest Q4 vs finest CST differ by {diff*210e3:.5f}; sum of their error estimates {band*210e3:.5f}; extrapolated values differ by {xdiff*210e3:.6f}")
    assert diff <= band and xdiff < band and xdiff < 0.5 * diff
    # 2) the Gmsh geometry and the FEniCSx script are text; check what can be checked without the tools
    assert GMSH_GEO.count("Point(") == 6 and "Circle(5) = {5, 6, 1}" in GMSH_GEO
    compile(FENICSX_PY, "fenicsx_plate.py", "exec")          # valid Python syntax
    # 3) the CalculiX deck for the 16.13 bracket
    nodes, tets = bracket_mesh(10.0)
    fixed = [i for i, q in enumerate(nodes) if abs(q[0]) < 1e-9]; load = [i for i, q in enumerate(nodes) if abs(q[0] - 80) < 1e-9]
    deck = calculix_deck(nodes, tets, fixed, load, 1000.0)
    lines = deck.splitlines()
    print(f"CalculiX deck: {len(lines)} lines, {len(nodes)} nodes, {len(tets)} C3D4 elements, {len(fixed)} fixed nodes, total load {sum(float(l.split(',')[2]) for l in lines if l.count(',') == 2 and l.split(',')[1].strip() == '3'):.1f} N")
    assert lines.count("*NODE") == 1 and lines.index("*ELEMENT, TYPE=C3D4, ELSET=EALL") == 3 + len(nodes)
    assert abs(sum(float(l.split(",")[2]) for l in lines if l.count(",") == 2 and l.split(",")[1].strip() == "3") + 1000.0) < 1e-2      # 6 significant digits per line
    print("first lines:", " | ".join(lines[:4]))
