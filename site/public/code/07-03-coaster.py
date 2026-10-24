"""Roller-coaster speed from energy, checked against a direct simulation of the motion along the track."""
import math
import numpy as np


def track(x):
    """Height (m) of a smooth track profile: a drop from 40 m towards 10 m, a bump near x = 80 m and a 27 m hill at x = 150 m."""
    return 40 - 30 * (1 / (1 + np.exp(-(x - 30) / 8))) + 12 * np.exp(-((x - 80) / 15) ** 2) + 17 * np.exp(-((x - 150) / 18) ** 2)


def dtrack(x, h=1e-5):
    return (track(x + h) - track(x - h)) / (2 * h)


def speed_from_energy(x, v0=1.0, g=9.81):
    return np.sqrt(np.maximum(v0**2 + 2 * g * (track(0) - track(x)), 0))


def simulate(x_end, v0=1.0, g=9.81, dt=1e-3, mu=0.0):
    """Motion along the path coordinate s: s'' = -g sin(theta) - mu g cos(theta) sign(v). Uses RK4 in (x, s')."""
    def f(state):
        x, v = state
        slope = dtrack(x); c = 1 / math.sqrt(1 + slope**2); s = slope * c
        return np.array([v * c, -g * s - mu * g * c * np.sign(v)])
    st = np.array([0.0, v0]); xs, vs = [0.0], [v0]
    while st[0] < x_end and st[1] > 0:
        k1 = f(st); k2 = f(st + dt / 2 * k1); k3 = f(st + dt / 2 * k2); k4 = f(st + dt * k3)
        st = st + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); xs.append(st[0]); vs.append(st[1])
    return np.array(xs), np.array(vs)


if __name__ == "__main__":
    xs, vs = simulate(190.0)
    ve = speed_from_energy(xs)
    print(f"max |v_sim - v_energy| = {np.max(np.abs(vs - ve)):.2e} m/s over {len(xs)} steps")
    assert np.max(np.abs(vs - ve)) < 1e-6
    for xq in (30, 80, 115, 150):
        i = int(np.argmin(np.abs(xs - xq)))
        print(f"  x = {xs[i]:6.1f} m, height {track(xs[i]):5.2f} m: {vs[i]:5.2f} m/s = {vs[i]*3.6:5.1f} km/h")
    # mass doesn't appear anywhere: every car, full or empty, has the same speed at the same height
    # with rolling friction (mu = 0.015) the car loses speed and may stall on the last hill
    xs2, vs2 = simulate(190.0, mu=0.015)
    i = int(np.argmin(np.abs(xs2 - 150))) if xs2[-1] > 150 else -1
    print(f"with mu = 0.015: reaches x = {xs2[-1]:.1f} m; speed at the last crest {vs2[i]:.2f} m/s (frictionless {vs[int(np.argmin(np.abs(xs - 150)))]:.2f})")
