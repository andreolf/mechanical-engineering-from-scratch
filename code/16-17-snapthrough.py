"""Geometrically nonlinear truss (exact kinematics, Green-Lagrange strain), Newton-Raphson with the tangent stiffness, and Crisfield's cylindrical arc-length method. The two-bar von Mises truss snaps through; arc-length traces the full equilibrium path, which is checked against the closed-form one."""
import math
import numpy as np


def internal(nodes, bars, EA, u):
    """Internal force vector and tangent stiffness. Green strain e = (l^2 - L^2) / (2 L^2), N = EA e."""
    n = len(u); f = np.zeros(n); K = np.zeros((n, n))
    for i, j in bars:
        X = nodes[j] - nodes[i]; L = np.linalg.norm(X)
        d = [2 * i, 2 * i + 1, 2 * j, 2 * j + 1]
        x = X + u[d[2:]] - u[d[:2]]                       # current bar vector
        e = (x @ x - L * L) / (2 * L * L); N = EA * e
        g = np.concatenate([-x, x])                       # d(l^2 / 2)/du
        f[d] += N * g / L                                 # virtual work: N * de/du * L, de/du = g / L^2
        Kg = N / L * np.block([[np.eye(2), -np.eye(2)], [-np.eye(2), np.eye(2)]])   # geometric (stress) stiffness
        Km = EA / L**3 * np.outer(g, g)                                             # material stiffness
        K[np.ix_(d, d)] += Km + Kg
    return f, K


def solve_free(K, r, free):
    return np.linalg.solve(K[np.ix_(free, free)], r[free])


def arc_length(nodes, bars, EA, Fref, free, dl, nsteps, tol=1e-10):
    n = len(Fref); u = np.zeros(n); lam = 0.0; path = [(0.0, u.copy())]
    du_prev = None; dlam_prev = 1.0
    for step in range(nsteps):
        f, K = internal(nodes, bars, EA, u)
        ut = np.zeros(n); ut[free] = solve_free(K, Fref, free)
        dlam = dl / math.sqrt(ut @ ut)
        if du_prev is not None and ut @ du_prev < 0: dlam = -dlam     # keep going forward along the path
        Du = dlam * ut; Dlam = dlam
        for it in range(50):
            f, K = internal(nodes, bars, EA, u + Du)
            r = (lam + Dlam) * Fref - f
            if np.linalg.norm(r[free]) < tol * max(1.0, np.linalg.norm(Fref)): break
            a = np.zeros(n); b = np.zeros(n)
            a[free] = solve_free(K, Fref, free); b[free] = solve_free(K, r, free)
            # cylindrical constraint |Du + db + dl*a|^2 = dl^2
            A = a @ a; B = 2 * a @ (Du + b); Cc = (Du + b) @ (Du + b) - dl * dl
            disc = B * B - 4 * A * Cc
            if disc < 0: raise RuntimeError("arc-length: no real root")
            roots = [(-B + s * math.sqrt(disc)) / (2 * A) for s in (1, -1)]
            # pick the root that keeps the increment pointing the same way
            dlk = max(roots, key=lambda q: (Du + b + q * a) @ Du)
            Du = Du + b + dlk * a; Dlam += dlk
        else:
            raise RuntimeError("arc-length did not converge")
        u = u + Du; lam += Dlam; du_prev = Du; path.append((lam, u.copy()))
    return path


def newton_load_control(nodes, bars, EA, Fref, free, lams, tol=1e-10):
    n = len(Fref); u = np.zeros(n); out = []
    for lam in lams:
        for it in range(100):
            f, K = internal(nodes, bars, EA, u); r = lam * Fref - f
            if np.linalg.norm(r[free]) < tol * max(1.0, np.linalg.norm(Fref)): break
            du = np.zeros(n); du[free] = solve_free(K, r, free); u = u + du
        else:
            out.append((lam, None)); continue
        out.append((lam, u.copy()))
    return out


A_HALF, H, EA = 1.0, 0.1, 1.0e6      # m, m, N
NODES = np.array([[-A_HALF, 0.0], [0.0, H], [A_HALF, 0.0]])
BARS = [(0, 1), (1, 2)]
FREE = [2, 3]                          # apex u, v


def exact_P(w):
    """Downward apex load for apex deflection w, Green strain, symmetric deformation."""
    L0 = math.hypot(A_HALF, H); l = math.hypot(A_HALF, H - w)
    N = EA * (l * l - L0 * L0) / (2 * L0 * L0)
    return -2 * N * (H - w) / L0          # the internal force uses x / L0, the reference length


if __name__ == "__main__":
    Fref = np.zeros(6); Fref[3] = -1.0                   # 1 N down at the apex, scaled by lambda
    # small-deflection check: tangent stiffness at u = 0 matches the linear truss
    f0, K0 = internal(NODES, BARS, EA, np.zeros(6))
    L0 = math.hypot(A_HALF, H); kv = 2 * EA / L0 * (H / L0) ** 2
    assert abs(K0[3, 3] - kv) < 1e-6 * kv
    # analytic limit point: dP/dw = 0
    ws = np.linspace(0, 2 * H, 200001); Ps = np.array([exact_P(w) for w in ws])
    i = np.argmax(Ps); Pmax, wmax = Ps[i], ws[i]
    print(f"apex vertical stiffness at rest {kv:.2f} N/m; analytic limit load {Pmax:.4f} N at w = {wmax*1000:.3f} mm (closed form h (1 - 1/sqrt 3) = {H*(1-1/math.sqrt(3))*1000:.3f} mm)")
    # load control: Newton converges up to the limit, then jumps to the far branch
    lams = np.linspace(0, 1.3 * Pmax, 27)
    res = newton_load_control(NODES, BARS, EA, Fref, FREE, lams)
    jumps = [(l, -u[3]) for l, u in res if u is not None]
    big = [(l, w) for l, w in jumps if w > 1.5 * H]
    print(f"load control: {len(jumps)} of {len(lams)} load levels converged; first level beyond the limit lands at w = {big[0][1]*1000:.2f} mm (snapped)")
    assert big and big[0][0] > Pmax
    # arc length: the full path, through the limit point, the unstable branch and back up
    path = arc_length(NODES, BARS, EA, Fref, FREE, dl=0.004, nsteps=80)
    lam = np.array([p[0] for p in path]); w = np.array([-p[1][3] for p in path])
    err = max(abs(l - exact_P(x)) for l, x in zip(lam, w))
    print(f"arc length: {len(path)-1} steps, w from 0 to {w.max()*1000:.1f} mm, load min {lam.min():.4f} N, max {lam.max():.4f} N; max error against the closed form {err:.2e} N")
    seg = w < 2 * H
    print(f"  on the snap (w < 2h): load from {lam[seg].max():.4f} N down to {lam[seg].min():.4f} N; analytic extremes +/- {Pmax:.4f} N")
    assert err < 1e-6 and w.max() > 2.2 * H and abs(lam[seg].max() - Pmax) < 0.01 * Pmax and abs(lam[seg].min() + Pmax) < 0.01 * Pmax
    assert abs(H * (1 - 1 / math.sqrt(3)) - wmax) < 1e-5
    assert np.all(np.diff(w) > 0)                           # moves steadily forward through the snap
