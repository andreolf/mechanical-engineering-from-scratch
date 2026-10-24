"""A system of particles: internal forces cancel, so the centre of mass moves uniformly."""
import numpy as np


def accelerations(x, m, G=1.0, soft=0.05):
    """Pairwise gravity-like attraction (softened). Each pair pushes equally and oppositely."""
    d = x[None, :, :] - x[:, None, :]                       # d[i, j] = x_j - x_i
    r2 = (d**2).sum(-1) + soft**2
    np.fill_diagonal(r2, np.inf)
    return G * (m[None, :, None] * d / r2[..., None] ** 1.5).sum(1)


def simulate(x, v, m, dt, steps):
    """Velocity Verlet."""
    a = accelerations(x, m); com = []
    for _ in range(steps):
        v = v + 0.5 * dt * a; x = x + dt * v; a = accelerations(x, m); v = v + 0.5 * dt * a
        com.append((m[:, None] * x).sum(0) / m.sum())
    return x, v, np.array(com)


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    n = 5
    m = rng.uniform(0.5, 2.0, n)
    x = rng.uniform(-1, 1, (n, 2))
    v = rng.normal(0, 0.3, (n, 2))
    P0 = (m[:, None] * v).sum(0); M = m.sum()
    vcom = P0 / M; com0 = (m[:, None] * x).sum(0) / M
    dt, steps = 1e-3, 5000
    x1, v1, com = simulate(x, v, m, dt, steps)
    t = dt * np.arange(1, steps + 1)
    drift = np.max(np.linalg.norm(com - (com0 + np.outer(t, vcom)), axis=1))
    P1 = (m[:, None] * v1).sum(0)
    print(f"{n} bodies, total mass {M:.3f}; COM velocity {vcom.round(4)}")
    print(f"momentum before {P0.round(6)}, after {P1.round(6)}; COM departs from a straight line by at most {drift:.1e}")
    assert np.allclose(P0, P1, atol=1e-12) and drift < 1e-10
    # the internal forces sum to zero at every instant
    a = accelerations(x, m)
    print(f"sum of m a over all particles: {(m[:, None] * a).sum(0)}")
    assert np.allclose((m[:, None] * a).sum(0), 0, atol=1e-12)
    # add an external force (uniform gravity -1 in y): the COM then falls like a single particle
    g = np.array([0.0, -1.0])
    xg, vg = x.copy(), v.copy(); ag = accelerations(xg, m) + g
    for _ in range(steps):
        vg = vg + 0.5 * dt * ag; xg = xg + dt * vg; ag = accelerations(xg, m) + g; vg = vg + 0.5 * dt * ag
    T = dt * steps
    comg = (m[:, None] * xg).sum(0) / M
    print(f"with gravity: COM at {comg.round(6)}, single-particle prediction {(com0 + vcom * T + 0.5 * g * T**2).round(6)}")
    assert np.allclose(comg, com0 + vcom * T + 0.5 * g * T**2, atol=1e-9)
