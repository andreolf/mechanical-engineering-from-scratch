"""Streamlines, pathlines and streaklines in the unsteady field u = U0, v = V0 sin(omega t), traced with RK4."""
import numpy as np

U0, V0 = 1.0, 0.5


def oscillating(omega):
    return lambda x, y, t: np.array([U0, V0 * np.sin(omega * t)])


def rk4(f, s, t0, t1, n):
    """Integrate ds/dt = f(s, t) from t0 to t1 in n steps; returns all states."""
    h = (t1 - t0) / n; out = [s.copy()]; t = t0
    for _ in range(n):
        k1 = f(s, t); k2 = f(s + h / 2 * k1, t + h / 2); k3 = f(s + h / 2 * k2, t + h / 2); k4 = f(s + h * k3, t + h)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += h; out.append(s.copy())
    return np.array(out)


def pathline(field, x0, t0, T, n=400):
    """Track one particle released at x0 at time t0."""
    return rk4(lambda s, t: field(*s, t), np.array(x0, float), t0, t0 + T, n)


def streamline(field, x0, t_frozen, L, n=400):
    """Curve tangent to the velocity field frozen at one instant."""
    return rk4(lambda s, _: field(*s, t_frozen), np.array(x0, float), 0, L, n)


def streakline(field, x0, t_now, n_release=60, n=200):
    """Positions at t_now of all particles released from x0 at earlier times."""
    return np.array([pathline(field, x0, t0, t_now - t0, n)[-1] for t0 in np.linspace(0, t_now, n_release, endpoint=False)])


if __name__ == "__main__":
    T = 2 * np.pi
    f = oscillating(1.0)
    p = pathline(f, [0, 0], 0, T); s = streamline(f, [0, 0], np.pi / 2, T); k = streakline(f, [0, 0], T)
    print(f"unsteady: pathline from the origin ends at ({p[-1,0]:.4f}, {p[-1,1]:.4f}); peak y {p[:,1].max():.4f} (exact 2 V0/omega = {2*V0:.4f})")
    print(f"  streamline at t = pi/2: straight, slope {s[-1,1]/s[-1,0]:.4f} (= V0/U0)")
    print(f"  streakline at t = 2 pi: y from {k[:,1].min():.4f} to {k[:,1].max():.4f}, a mirror image of the pathline")
    assert abs(p[:, 1].max() - 2 * V0) < 1e-4                     # y(t) = V0 (1 - cos t) / omega
    assert abs(s[-1, 1] / s[-1, 0] - V0 / U0) < 1e-12
    steady = lambda x, y, t: np.array([U0, 0.3])                  # steady field: all three coincide
    for pts in (pathline(steady, [0, 0], 0, 3), streamline(steady, [0, 0], 0, 3), streakline(steady, [0, 0], 3)):
        assert np.max(np.abs(pts[:, 1] - 0.3 * pts[:, 0])) < 1e-12
    print("steady field: pathline, streamline and streakline all lie on y = 0.3 x")
