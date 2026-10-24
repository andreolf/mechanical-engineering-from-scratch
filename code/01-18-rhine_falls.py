"""Projectile from the Rhine Falls lip: closed form without and with linear drag, plus RK4 check."""
import math

G = 9.81


def no_drag(v0, theta, H, t):
    return v0 * math.cos(theta) * t, H + v0 * math.sin(theta) * t - 0.5 * G * t * t


def linear_drag(v0, theta, H, k, t):
    vx, vy = v0 * math.cos(theta), v0 * math.sin(theta)
    e = 1 - math.exp(-k * t)
    return vx / k * e, H + (vy + G / k) / k * e - G / k * t


def landing(traj, t_hi=60.0):
    """Bisection on y(t) = 0 (lesson 01.02)."""
    lo, hi = 0.0, t_hi
    for _ in range(100):
        m = 0.5 * (lo + hi)
        lo, hi = (m, hi) if traj(m)[1] > 0 else (lo, m)
    return lo, traj(lo)[0]


def rk4_drag(v0, theta, H, k, dt=1e-3):
    s = [0.0, H, v0 * math.cos(theta), v0 * math.sin(theta)]
    f = lambda s: [s[2], s[3], -k * s[2], -G - k * s[3]]
    t = 0.0
    while s[1] > 0:
        prev = s
        k1 = f(s); k2 = f([a + dt / 2 * b for a, b in zip(s, k1)])
        k3 = f([a + dt / 2 * b for a, b in zip(s, k2)]); k4 = f([a + dt * b for a, b in zip(s, k3)])
        s = [a + dt / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(s, k1, k2, k3, k4)]
        t += dt
    w = prev[1] / (prev[1] - s[1])                     # interpolate to y = 0
    return prev[0] + w * (s[0] - prev[0])


if __name__ == "__main__":
    # the lesson's test: no-drag range on flat ground matches v^2 sin(2 theta)/g
    for v0, deg in [(20, 30), (12, 45), (8, 70)]:
        th = math.radians(deg)
        _, R = landing(lambda t: no_drag(v0, th, 1e-12, t))
        assert abs(R - v0**2 * math.sin(2 * th) / G) < 1e-6
    t, x = landing(lambda t: no_drag(5.0, 0.0, 23.0, t))
    print(f"no drag: lands after {t:.3f} s, {x:.2f} m out, at {math.hypot(5, G * t):.1f} m/s")
    assert abs(t - 2.1654) < 1e-3 and abs(x - 10.827) < 1e-2
    td, xd = landing(lambda t: linear_drag(5.0, 0.0, 23.0, 0.3, t))
    print(f"linear drag k=0.3: {td:.3f} s, {xd:.2f} m out")
    assert abs(xd - 8.621) < 1e-2 and abs(rk4_drag(5.0, 0.0, 23.0, 0.3) - xd) < 1e-6
    # small k recovers the drag-free answer
    assert abs(landing(lambda t: linear_drag(5.0, 0.0, 23.0, 1e-6, t))[1] - x) < 1e-3
