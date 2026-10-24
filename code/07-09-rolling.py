"""Rolling race down a ramp: a = g sin(theta) / (1 + I / (m r^2)), checked by simulating the rigid-body equations."""
import math
import numpy as np


def race(k, theta, L, g=9.81, dt=1e-4):
    """k = I / (m r^2). Unknowns: friction F and acceleration; equations m a = m g sin - F, I alpha = F r, a = alpha r.
    Integrates x'' = a with semi-implicit Euler and returns the time to roll L metres."""
    A = np.array([[1.0, 1.0], [1.0, -1.0 / k]])           # rows: m a + F = m g sin;  a - F / (k m) = 0  (m = 1)
    a, F = np.linalg.solve(A, [g * math.sin(theta), 0.0])
    x, v, t = 0.0, 0.0, 0.0
    while x < L:
        v += a * dt; x += v * dt; t += dt
    return a, F, t


if __name__ == "__main__":
    th, L, g = math.radians(10), 2.0, 9.81
    shapes = {"sliding block (no friction)": None, "solid sphere": 2 / 5, "solid disk": 1 / 2, "thin ring": 1.0}
    for name, k in shapes.items():
        if k is None:
            a = g * math.sin(th); t = math.sqrt(2 * L / a); F = 0.0
        else:
            a, F, t = race(k, th, L)
        print(f"{name:28s} a = {a:.4f} m/s^2 = {a / (g * math.sin(th)):.4f} g sin(theta), friction {F:.4f} N per kg, time {t:.3f} s")
    a_disk, _, _ = race(0.5, th, L); a_ring, _, _ = race(1.0, th, L)
    assert abs(a_disk - 2 / 3 * g * math.sin(th)) < 1e-12 and abs(a_ring - 0.5 * g * math.sin(th)) < 1e-12
    # energy check for the disk: m g h = m v^2 / 2 + I w^2 / 2 = (3/4) m v^2
    v = math.sqrt(2 * a_disk * L)
    print(f"disk at the bottom: v = {v:.4f} m/s; energy says sqrt(4 g h / 3) = {math.sqrt(4 * g * L * math.sin(th) / 3):.4f}")
    assert abs(v - math.sqrt(4 * g * L * math.sin(th) / 3)) < 1e-12
    # the disk rolls without slipping only if friction mu >= F / N = tan(theta) / 3
    print(f"disk needs mu >= tan(theta)/3 = {math.tan(th) / 3:.4f}; ring needs tan(theta)/2 = {math.tan(th) / 2:.4f}")
