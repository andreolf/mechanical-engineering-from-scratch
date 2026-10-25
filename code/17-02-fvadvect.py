"""1D finite-volume advection in conservation form: cell averages updated by face fluxes. Periodic domain; the total amount is conserved to round-off because every face flux leaves one cell and enters its neighbour. Also a non-conservative update for contrast."""
import numpy as np


def upwind_flux(q, a):
    """Flux through the right face of each cell, i+1/2, for speed a > 0."""
    return a * q


def step_fv(q, a, dx, dt):
    F = upwind_flux(q, a)                    # F[i] = flux at face i+1/2
    return q - dt / dx * (F - np.roll(F, 1))  # F[i-1/2] = F[i-1]


def run(N=200, a=1.0, cfl=0.8, T=1.0):
    dx = 1.0 / N; x = (np.arange(N) + 0.5) * dx
    q = np.exp(-200 * (x - 0.3) ** 2) + (np.abs(x - 0.7) < 0.1)       # a bump and a block of dye
    dt = cfl * dx / a; n = int(round(T / dt)); dt = T / n
    m0 = q.sum() * dx; drift = 0.0
    for _ in range(n):
        q = step_fv(q, a, dx, dt); drift = max(drift, abs(q.sum() * dx - m0))
    return x, q, m0, drift, n


if __name__ == "__main__":
    x, q, m0, drift, n = run()
    print(f"{n} steps once around the periodic domain: total {m0:.15f}, largest drift {drift:.2e}")
    assert drift < 1e-13
    assert q.min() >= -1e-15 and q.max() <= 1 + 1e-12       # upwind with CFL <= 1: no new extremes
    # stability: CFL above 1 blows up
    x, q2, _, _, _ = run(cfl=1.2, T=0.5)
    print(f"CFL 1.2: max |q| after half a period {np.abs(q2).max():.2e} (unstable)")
    assert np.abs(q2).max() > 1e3
    # a non-conservative form for a variable speed a(x) q_x: amount is not conserved
    N = 200; dx = 1 / N; xc = (np.arange(N) + 0.5) * dx; ax = 1 + 0.5 * np.sin(2 * np.pi * xc)
    qa = np.exp(-200 * (xc - 0.3) ** 2); qb = qa.copy(); dt = 0.5 * dx / ax.max()
    af = 1 + 0.5 * np.sin(2 * np.pi * (xc + dx / 2))          # speed at the right faces
    for _ in range(400):
        Fa = af * qa; qa = qa - dt / dx * (Fa - np.roll(Fa, 1))                 # conservative: (a q)_x
        qb = qb - dt / dx * ax * (qb - np.roll(qb, 1))                           # non-conservative: a q_x
    m = np.exp(-200 * (xc - 0.3) ** 2).sum() * dx
    print(f"variable speed, 400 steps: conservative total {qa.sum()*dx:.12f}, non-conservative {qb.sum()*dx:.6f}, start {m:.12f}")
    assert abs(qa.sum() * dx - m) < 1e-13 and abs(qb.sum() * dx - m) > 1e-3
