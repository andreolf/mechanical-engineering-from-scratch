"""Two-grid and multigrid V-cycles for -u'' = f in 1D: weighted Jacobi smooths, the coarse grid fixes the smooth error."""
import math
import numpy as np


def apply_A(u, h):
    """-u'' on interior nodes; u includes the zero boundary values."""
    r = np.zeros_like(u)
    r[1:-1] = (2 * u[1:-1] - u[:-2] - u[2:]) / h**2
    return r


def smooth(u, f, h, sweeps, w=2 / 3):
    for _ in range(sweeps):
        u[1:-1] = (1 - w) * u[1:-1] + w * 0.5 * (u[:-2] + u[2:] + h * h * f[1:-1])
    return u


def restrict(r):
    """Full weighting: coarse value = (1/4, 1/2, 1/4) of the fine neighbours."""
    rc = np.zeros((len(r) - 1) // 2 + 1)
    rc[1:-1] = 0.25 * r[1:-2:2] + 0.5 * r[2:-1:2] + 0.25 * r[3::2]
    return rc


def prolong(ec):
    """Linear interpolation back to the fine grid."""
    e = np.zeros(2 * (len(ec) - 1) + 1)
    e[::2] = ec; e[1::2] = 0.5 * (ec[:-1] + ec[1:])
    return e


def v_cycle(u, f, h, pre=2, post=2, two_grid=False):
    n = len(u) - 1
    if n <= 2:
        u[1] = 0.5 * (u[0] + u[2] + h * h * f[1]); return u
    u = smooth(u, f, h, pre)
    rc = restrict(f - apply_A(u, h))
    if two_grid:                                       # solve the coarse problem exactly
        m = len(rc) - 2; H = 2 * h
        Ac = (2 * np.eye(m) - np.eye(m, k=1) - np.eye(m, k=-1)) / H**2
        ec = np.zeros(len(rc)); ec[1:-1] = np.linalg.solve(Ac, rc[1:-1])
    else:                                              # or recurse: a full multigrid V-cycle
        ec = v_cycle(np.zeros(len(rc)), rc, 2 * h)
    u = u + prolong(ec)
    return smooth(u, f, h, post)


def reduction_factor(n, cycles=8, two_grid=False):
    h = 1.0 / n
    rng = np.random.default_rng(0)
    f = rng.standard_normal(n + 1); f[0] = f[-1] = 0           # rough right-hand side: every frequency present
    u = np.zeros(n + 1); r = [np.linalg.norm(f - apply_A(u, h))]
    for _ in range(cycles):
        u = v_cycle(u, f, h, two_grid=two_grid); r.append(np.linalg.norm((f - apply_A(u, h))[1:-1]))
    return (r[-1] / r[2]) ** (1 / (cycles - 2)), r


if __name__ == "__main__":
    # why smoothing alone fails: weighted Jacobi damps mode k by |1 - 2w sin^2(k pi h / 2)|
    n = 64; h = 1 / n; w = 2 / 3
    g = lambda k: abs(1 - 2 * w * math.sin(k * math.pi * h / 2) ** 2)
    print(f"weighted Jacobi damping per sweep, n = {n}: smoothest mode {g(1):.4f}, high modes (k >= n/2) at most {max(g(k) for k in range(n // 2, n)):.4f}")
    assert max(g(k) for k in range(n // 2, n)) <= 1 / 3 + 1e-12
    print("   n   two-grid factor   V-cycle factor")
    facs = []
    for n in (32, 64, 128, 256, 512, 1024):
        tg, _ = reduction_factor(n, two_grid=True); vc, _ = reduction_factor(n)
        facs.append(vc)
        print(f"{n:5d} {tg:16.4f} {vc:16.4f}")
    assert max(facs) < 0.15 and max(facs) - min(facs) < 0.03      # independent of n
