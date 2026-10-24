"""A Hess-Smith panel method from scratch: constant-strength source panels plus one uniform vortex strength,
closed by the Kutta condition. Gives the pressure distribution and lift of any airfoil shape."""
import math
import numpy as np


def naca4(m, p, t, n=80):
    """Closed NACA 4-digit outline, cosine spacing, ordered TE -> lower surface -> LE -> upper surface -> TE (clockwise)."""
    beta = np.linspace(0, math.pi, n + 1); x = (1 - np.cos(beta)) / 2
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.126 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3 - 0.1036 * x ** 4)
    if m > 0:
        yc = np.where(x < p, m / p ** 2 * (2 * p * x - x * x), m / (1 - p) ** 2 * (1 - 2 * p + 2 * p * x - x * x))
        dyc = np.where(x < p, 2 * m / p ** 2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
    else:
        yc = np.zeros_like(x); dyc = np.zeros_like(x)
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    X = np.concatenate([xl[::-1], xu[1:]]); Y = np.concatenate([yl[::-1], yu[1:]])
    Y[0] = Y[-1] = (Y[0] + Y[-1]) / 2                    # close the trailing edge
    return X, Y


def influence(xc, yc, X, Y):
    """Velocities at points (xc, yc) induced by unit-strength source panels j, in global axes."""
    x1, y1, x2, y2 = X[:-1], Y[:-1], X[1:], Y[1:]
    L = np.hypot(x2 - x1, y2 - y1); th = np.arctan2(y2 - y1, x2 - x1)
    dx = xc[:, None] - x1[None, :]; dy = yc[:, None] - y1[None, :]
    xp = dx * np.cos(th) + dy * np.sin(th); yp = -dx * np.sin(th) + dy * np.cos(th)
    r1 = np.hypot(xp, yp); r2 = np.hypot(xp - L, yp)
    beta = np.arctan2(yp, xp - L) - np.arctan2(yp, xp)
    beta = np.where(np.abs(beta) < 1e-12, 0.0, beta)
    us = np.log(r1 / r2) / (2 * math.pi); vs = beta / (2 * math.pi)
    n = len(xc)
    if n == len(L):                                      # self-influence on each panel's own midpoint, from the outside
        idx = np.arange(n); us[idx, idx] = 0.0; vs[idx, idx] = 0.5
    ug = us * np.cos(th) - vs * np.sin(th); vg = us * np.sin(th) + vs * np.cos(th)
    # a unit vortex panel induces the source field rotated by -90 degrees
    uv, vv = vs, -us
    ugv = uv * np.cos(th) - vv * np.sin(th); vgv = uv * np.sin(th) + vv * np.cos(th)
    return ug, vg, ugv, vgv, L, th


def solve(X, Y, alpha):
    xc = (X[:-1] + X[1:]) / 2; yc = (Y[:-1] + Y[1:]) / 2
    ug, vg, ugv, vgv, L, th = influence(xc, yc, X, Y)
    nx, ny = -np.sin(th), np.cos(th); tx, ty = np.cos(th), np.sin(th)
    N = len(xc); A = np.zeros((N + 1, N + 1)); b = np.zeros(N + 1)
    U, V = math.cos(alpha), math.sin(alpha)
    A[:N, :N] = ug * nx[:, None] + vg * ny[:, None]
    A[:N, N] = np.sum(ugv * nx[:, None] + vgv * ny[:, None], axis=1)
    b[:N] = -(U * nx + V * ny)
    At = ug * tx[:, None] + vg * ty[:, None]; Atv = np.sum(ugv * tx[:, None] + vgv * ty[:, None], axis=1)
    A[N, :N] = At[0] + At[-1]; A[N, N] = Atv[0] + Atv[-1]; b[N] = -(U * (tx[0] + tx[-1]) + V * (ty[0] + ty[-1]))
    sol = np.linalg.solve(A, b); q, gam = sol[:N], sol[N]
    Vt = At @ q + gam * Atv + U * tx + V * ty
    Cp = 1 - Vt ** 2
    chord = X.max() - X.min()
    CL_circ = 2 * gam * L.sum() / chord
    # pressure integration: force = -sum Cp n L, lift perpendicular to the free stream
    Fx = -np.sum(Cp * nx * L); Fy = -np.sum(Cp * ny * L)
    CL_p = (Fy * math.cos(alpha) - Fx * math.sin(alpha)) / chord
    return xc, Cp, CL_circ, CL_p, np.sum(q * L)


if __name__ == "__main__":
    a = math.radians(4)
    for name, (m, p, t) in {"NACA 0001": (0, 0.4, 0.01), "NACA 0012": (0, 0.4, 0.12), "NACA 2412": (0.02, 0.4, 0.12)}.items():
        X, Y = naca4(m, p, t, 120)
        _, _, c0, _, _ = solve(X, Y, 0.0)
        _, Cp, c4, c4p, net = solve(X, Y, a)
        slope = (c4 - c0) / a
        print(f"{name}: C_L(4 deg) = {c4:.4f} (pressure integral {c4p:.4f}), slope {slope:.4f}/rad = {slope/(2*math.pi):.4f} x 2 pi, "
              f"zero-lift angle {math.degrees(-c0/slope):.3f} deg, net source {net:.1e}")
        assert abs(c4 - c4p) < 0.01 * abs(c4) and abs(net) < 1e-3         # two lift estimates agree; net source ~ 0 (a closed body)
        if t == 0.01: assert abs(slope / (2 * math.pi) - 1) < 0.02         # a thin section matches thin airfoil theory
    # thickness raises the slope roughly as 1 + 0.77 t/c
    print(f"1 + 0.77 t/c for 12 %: {1 + 0.77*0.12:.4f}")
