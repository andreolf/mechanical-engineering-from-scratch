"""Velocity Verlet versus explicit Euler and RK4 over long runs: bounded energy error versus drift."""
import math
import numpy as np

G_L = 9.81                       # pendulum, L = 1 m: theta'' = -(g/L) sin theta


def energy(th, w):
    return 0.5 * w * w - G_L * math.cos(th)      # per unit m L^2


def verlet(th, w, h, n):
    a = -G_L * math.sin(th); E0 = energy(th, w); dmax = 0.0
    for _ in range(n):
        w_half = w + 0.5 * h * a
        th = th + h * w_half
        a = -G_L * math.sin(th)
        w = w_half + 0.5 * h * a
        dmax = max(dmax, abs(energy(th, w) - E0))
    return th, w, dmax


def euler(th, w, h, n):
    for _ in range(n):
        th, w = th + h * w, w - h * G_L * math.sin(th)
    return th, w


def symplectic_euler(th, w, h, n):
    for _ in range(n):
        w = w - h * G_L * math.sin(th); th = th + h * w
    return th, w


def rk4(th, w, h, n):
    f = lambda t, v: (v, -G_L * math.sin(t))
    for _ in range(n):
        k1 = f(th, w); k2 = f(th + h / 2 * k1[0], w + h / 2 * k1[1]); k3 = f(th + h / 2 * k2[0], w + h / 2 * k2[1]); k4 = f(th + h * k3[0], w + h * k3[1])
        th += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); w += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    return th, w


def kepler_verlet(r, v, h, n, mu=1.0):
    """Planar orbit with velocity Verlet; returns the worst relative energy error."""
    acc = lambda r: -mu * r / np.linalg.norm(r) ** 3
    E = lambda r, v: 0.5 * v @ v - mu / np.linalg.norm(r)
    E0 = E(r, v); a = acc(r); worst = 0.0
    for i in range(n):
        v = v + 0.5 * h * a; r = r + h * v; a = acc(r); v = v + 0.5 * h * a
        if i % 100 == 0:
            worst = max(worst, abs(E(r, v) / E0 - 1))
    return worst


if __name__ == "__main__":
    th0, w0 = math.radians(60), 0.0
    E0 = energy(th0, w0)
    rel = lambda th_w: abs(energy(*th_w) - E0) / abs(E0)
    # fine step, 1000 s: everything except explicit Euler looks good
    h, n = 0.01, 100_000
    print(f"h = {h} s, {n} steps: Verlet worst {verlet(th0, w0, h, n)[2] / abs(E0):.1e}, RK4 end {rel(rk4(th0, w0, h, n)):.1e}, "
          f"explicit Euler {rel(euler(th0, w0, h, 2000)):.1e} after only 2000 steps")
    assert rel(euler(th0, w0, h, 2000)) > 0.5
    # coarse step, long run: RK4 drifts steadily, Verlet stays bounded
    h = 0.05
    for n in (10_000, 100_000):
        dv = verlet(th0, w0, h, n)[2] / abs(E0)
        print(f"h = {h} s, {n:6d} steps ({n * h:5.0f} s): Verlet worst {dv:.2e}, symplectic Euler end {rel(symplectic_euler(th0, w0, h, n)):.2e}, RK4 end {rel(rk4(th0, w0, h, n)):.2e}")
    d1, d2 = verlet(th0, w0, h, 10_000)[2], verlet(th0, w0, h, 100_000)[2]
    r1, r2 = rel(rk4(th0, w0, h, 10_000)), rel(rk4(th0, w0, h, 100_000))
    assert d2 < 1.05 * d1                 # bounded: 10x longer, same worst error
    assert 8 < r2 / r1 < 12               # RK4: error grows in proportion to the run length
    assert d2 / abs(E0) < 1e-2
    # an eccentric orbit (e = 0.5), 100 000 steps of h = 0.01: about 159 orbits
    worst = kepler_verlet(np.array([0.5, 0.0]), np.array([0.0, math.sqrt(3.0)]), 0.01, 100_000)
    print(f"Kepler orbit, e = 0.5: worst relative energy error {worst:.2e} over 159 orbits")
    assert worst < 1e-2
