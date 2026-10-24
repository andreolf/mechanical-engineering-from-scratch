"""Particle kinematics along a sampled track: velocity, tangential and normal acceleration."""
import math
import numpy as np


def derivatives(t, x, y):
    """Central differences (second order) for velocity and acceleration."""
    vx, vy = np.gradient(x, t, edge_order=2), np.gradient(y, t, edge_order=2)
    ax, ay = np.gradient(vx, t, edge_order=2), np.gradient(vy, t, edge_order=2)
    return vx, vy, ax, ay


def path_components(vx, vy, ax, ay):
    """Split acceleration into tangential (speed change) and normal (direction change) parts."""
    v = np.hypot(vx, vy)
    at = (vx * ax + vy * ay) / v
    an = (vx * ay - vy * ax) / v           # signed: positive when turning left
    rho = v**2 / np.maximum(np.abs(an), 1e-12)   # straight stretches: radius effectively infinite
    return v, at, an, rho


if __name__ == "__main__":
    # 1. a car on a 50 m radius roundabout at a steady 10 m/s, logged at 10 Hz
    R, V = 50.0, 10.0
    t = np.arange(0, 20, 0.1)
    x, y = R * np.cos(V * t / R), R * np.sin(V * t / R)
    v, at, an, rho = path_components(*derivatives(t, x, y))
    print(f"roundabout: speed {v[100]:.4f} m/s, a_t {at[100]:+.2e}, a_n {an[100]:.4f} m/s^2 (v^2/R = {V**2/R:.4f}), radius {rho[100]:.3f} m")
    assert abs(an[100] - V**2 / R) < 1e-3 and abs(at[100]) < 1e-3
    # 2. a cyclist's GPS track: a straight, a 30 m bend while braking, then a straight, with 0.5 m GPS noise
    dt = 1.0
    s_of_t = lambda tt: 12 * tt - 0.15 * tt**2         # braking at 0.3 m/s^2
    tt = np.arange(0, 30, dt)
    s = s_of_t(tt)
    def place(s):
        L1, Rb = 100.0, 30.0
        if s < L1: return s, 0.0
        if s < L1 + math.pi / 2 * Rb:
            ph = (s - L1) / Rb; return L1 + Rb * math.sin(ph), Rb * (1 - math.cos(ph))
        return L1 + Rb, Rb + (s - L1 - math.pi / 2 * Rb)
    xy = np.array([place(si) for si in s])
    rng = np.random.default_rng(1)
    noisy = xy + rng.normal(0, 0.5, xy.shape)
    for name, P in (("clean", xy), ("noisy", noisy)):
        v, at, an, rho = path_components(*derivatives(tt, P[:, 0], P[:, 1]))
        i = 12                                           # mid-bend (s = 122 m)
        print(f"GPS {name}: at t = {tt[i]:.0f} s speed {v[i]:.2f} m/s (true {12 - 0.3*tt[i]:.2f}), a_t {at[i]:+.2f} (true -0.30), a_n {an[i]:.2f} (true {(12-0.3*tt[i])**2/30:.2f})")
    # smoothing helps: a 5-point moving average before differencing
    k = np.ones(5) / 5
    sm = np.column_stack([np.convolve(noisy[:, j], k, mode="same") for j in range(2)])
    v, at, an, rho = path_components(*derivatives(tt, sm[:, 0], sm[:, 1]))
    print(f"smoothed noisy: speed {v[12]:.2f} m/s, a_n {an[12]:.2f} m/s^2 (differentiating noise amplifies it; smoothing trades noise for lag)")
    # 3. polar coordinates: a_r = r'' - r th'^2, a_th = r th'' + 2 r' th'
    r = lambda t: 2 + 0.5 * t; th = lambda t: 0.8 * t
    tq, h = 1.3, 1e-4
    X = lambda t: np.array([r(t) * math.cos(th(t)), r(t) * math.sin(th(t))])
    a = (X(tq + h) - 2 * X(tq) + X(tq - h)) / h**2
    er = np.array([math.cos(th(tq)), math.sin(th(tq))]); et = np.array([-er[1], er[0]])
    ar, ath = 0 - r(tq) * 0.8**2, 0 + 2 * 0.5 * 0.8
    print(f"polar: a_r numeric {a @ er:.4f} vs formula {ar:.4f}; a_theta numeric {a @ et:.4f} vs formula {ath:.4f}")
    assert abs(a @ er - ar) < 1e-5 and abs(a @ et - ath) < 1e-5
