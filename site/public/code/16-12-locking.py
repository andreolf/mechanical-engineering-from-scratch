"""Shear locking of Q4 in bending: a slender plane-stress cantilever with full 2x2 integration, selective reduced integration of the shear term (1 point) and uniform 1-point integration (hourglass modes), against Timoshenko beam theory. Plus volumetric locking in plane strain as nu -> 0.5."""
import math
import numpy as np

G2 = [(-1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), -1 / math.sqrt(3)), (1 / math.sqrt(3), 1 / math.sqrt(3)), (-1 / math.sqrt(3), 1 / math.sqrt(3))]


def Bmat(X, xi, eta):
    dN = 0.25 * np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)], [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
    J = dN @ X; dNx = np.linalg.solve(J, dN)
    B = np.zeros((3, 8)); B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
    return B, np.linalg.det(J)


def D_mat(E, nu, kind):
    if kind == "stress":
        return E / (1 - nu**2) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    c = E / ((1 + nu) * (1 - 2 * nu))
    return c * np.array([[1 - nu, nu, 0], [nu, 1 - nu, 0], [0, 0, (1 - 2 * nu) / 2]])


def k_q4(X, D, scheme):
    """full: 2x2 for everything. sri: 2x2 for the normal part, 1 point for the shear part. uri: 1 point for everything.
    vol: (plane strain) 2x2 for the deviatoric part, 1 point for the volumetric part."""
    k = np.zeros((8, 8))
    if scheme == "vol":
        lam = D[0, 1]; Dv = lam * np.array([[1, 1, 0], [1, 1, 0], [0, 0, 0]]); Dd = D - Dv
        for g in G2:
            B, dJ = Bmat(X, *g); k += B.T @ Dd @ B * dJ
        B, dJ = Bmat(X, 0, 0); return k + B.T @ Dv @ B * dJ * 4
    Dn = D.copy(); Dn[2, 2] = 0; Ds = np.zeros((3, 3)); Ds[2, 2] = D[2, 2]
    if scheme == "uri":
        B, dJ = Bmat(X, 0, 0); return B.T @ D @ B * dJ * 4
    for g in G2:
        B, dJ = Bmat(X, *g); k += B.T @ (D if scheme == "full" else Dn) @ B * dJ
    if scheme == "sri":
        B, dJ = Bmat(X, 0, 0); k += B.T @ Ds @ B * dJ * 4
    return k


def cantilever(nx, ny, scheme, L=10.0, H=1.0, E=1000.0, nu=0.25, P=1.0, kind="stress"):
    xs, ys = np.linspace(0, L, nx + 1), np.linspace(-H / 2, H / 2, ny + 1)
    node = lambda i, j: j * (nx + 1) + i
    X = np.array([[x, y] for y in ys for x in xs]); n = len(X)
    D = D_mat(E, nu, kind); K = np.zeros((2 * n, 2 * n)); F = np.zeros(2 * n)
    for j in range(ny):
        for i in range(nx):
            e = [node(i, j), node(i + 1, j), node(i + 1, j + 1), node(i, j + 1)]
            d = np.ravel([[2 * a, 2 * a + 1] for a in e]); K[np.ix_(d, d)] += k_q4(X[e], D, scheme)
    # tip shear P with the parabolic distribution, lumped to the end nodes by the trapezoid rule
    tip = [node(nx, j) for j in range(ny + 1)]
    tau = lambda y: 1.5 * P / H * (1 - (2 * y / H) ** 2)
    for a, b in zip(tip[:-1], tip[1:]):
        ya, yb = X[a, 1], X[b, 1]; seg = (yb - ya) * (tau(ya) + 4 * tau((ya + yb) / 2) + tau(yb)) / 6
        F[2 * a + 1] -= seg / 2; F[2 * b + 1] -= seg / 2
    fixed = [2 * node(0, j) for j in range(ny + 1)] + [2 * node(0, ny // 2) + 1]   # clamp axially, pin the mid-node vertically
    if ny % 2:
        fixed = [2 * node(0, j) for j in range(ny + 1)] + [2 * node(0, 0) + 1, 2 * node(0, ny) + 1]
    free = np.setdiff1d(np.arange(2 * n), fixed)
    Kf = K[np.ix_(free, free)]
    u = np.zeros(2 * n); u[free] = np.linalg.lstsq(Kf, F[free], rcond=None)[0] if scheme == "uri" else np.linalg.solve(Kf, F[free])
    tipv = np.mean([u[2 * a + 1] for a in tip])
    return tipv, np.linalg.matrix_rank(Kf, tol=1e-9 * np.abs(Kf).max()) < len(free)


def zero_modes(scheme, D):
    X = np.array([[0, 0], [2.0, 0], [2.0, 1.0], [0, 1.0]])
    w = np.linalg.eigvalsh(k_q4(X, D, scheme)); return int(np.sum(w < 1e-9 * w.max()))


if __name__ == "__main__":
    L, H, E, nu, P = 10.0, 1.0, 1000.0, 0.25, 1.0
    I = H**3 / 12; G = E / (2 * (1 + nu))
    timo = P * L**3 / (3 * E * I) + P * L / (5 / 6 * G * H)
    print(f"beam theory tip deflection: bending {P*L**3/(3*E*I):.4f} + shear {P*L/(5/6*G*H):.4f} = {timo:.4f}")
    D = D_mat(E, nu, "stress")
    for s in ("full", "sri", "uri"):
        print(f"zero-energy modes of one element, {s}: {zero_modes(s, D)} (3 are rigid-body motions)")
    assert zero_modes("full", D) == 3 and zero_modes("sri", D) == 3 and zero_modes("uri", D) == 5
    res = {}
    for nx, ny in ((10, 1), (20, 2), (40, 4)):
        for s in ("full", "sri"):
            v, _ = cantilever(nx, ny, s)
            res[(nx, s)] = -v
            print(f"{nx} x {ny} mesh, {s:4s}: tip {-v:8.4f} = {-v/timo*100:5.1f} % of beam theory")
    for nx in (10, 20, 40):
        assert abs(res[(nx, "sri")] - timo) < abs(res[(nx, "full")] - timo)
    assert res[(10, "full")] < 0.75 * timo and abs(res[(10, "sri")] / timo - 1) < 0.08
    v, singular = cantilever(10, 1, "uri")
    print(f"10 x 1 mesh, 1-point integration: stiffness singular = {singular} (hourglass modes); the answer is meaningless")
    assert singular
    # volumetric locking: plane strain, nu close to 0.5, deviatoric/volumetric split with 1-point volumetric
    print("plane strain, 20 x 2 mesh:")
    out = {}
    for nu2 in (0.3, 0.49, 0.4999):
        Ib = H**3 / 12; Ep = E / (1 - nu2**2); Gp = E / (2 * (1 + nu2))
        ref = P * L**3 / (3 * Ep * Ib) + P * L / (5 / 6 * Gp * H)
        a = -cantilever(20, 2, "sri", nu=nu2, kind="strain")[0]; b = -cantilever(20, 2, "vol", nu=nu2, kind="strain")[0]
        c = -cantilever(20, 2, "full", nu=nu2, kind="strain")[0]
        out[nu2] = (a, b, c, ref)
        print(f"  nu = {nu2}: full {c/ref*100:5.1f} %, shear-SRI {a/ref*100:5.1f} %, volumetric split {b/ref*100:5.1f} % of beam theory")
    assert out[0.4999][2] / out[0.4999][3] < out[0.3][2] / out[0.3][3]
