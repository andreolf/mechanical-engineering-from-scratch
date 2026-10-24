"""Exact pendulum period via the AGM versus the small-angle formula."""
import math


def agm(a, b, tol=1e-15):
    while abs(a - b) > tol * a:
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a


def period_ratio(theta0):
    """T / T0 for amplitude theta0 in radians."""
    k = math.sin(theta0 / 2)
    return 1.0 / agm(1.0, math.sqrt(1 - k * k))   # (4 K(k)) / (2 pi) = (2/pi) K = 1/AGM


def simulate_period(theta0, L=1.0, g=9.81, dt=1e-4):
    """Integrate the nonlinear equation with RK4 and time a quarter swing."""
    f = lambda th, om: (om, -g / L * math.sin(th))
    th, om, t = theta0, 0.0, 0.0
    while True:
        k1 = f(th, om); k2 = f(th + dt / 2 * k1[0], om + dt / 2 * k1[1])
        k3 = f(th + dt / 2 * k2[0], om + dt / 2 * k2[1]); k4 = f(th + dt * k3[0], om + dt * k3[1])
        th_n = th + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om_n = om + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        if th_n <= 0:                                  # crossed the bottom: interpolate
            return 4 * (t + dt * th / (th - th_n))
        th, om, t = th_n, om_n, t + dt


if __name__ == "__main__":
    T0 = 2 * math.pi * math.sqrt(1 / 9.81)
    for deg in (10, 30, 60):
        r, rs = period_ratio(math.radians(deg)), simulate_period(math.radians(deg)) / T0
        print(f"{deg:3d} deg: exact {r:.6f}, simulated {rs:.6f}")
        assert abs(r - rs) < 1e-6
    # find where the linear model's error reaches 1%
    lo, hi = 1.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if period_ratio(math.radians(mid)) < 1.01 else (lo, mid)
    print(f"1% error at {lo:.2f} degrees")
    assert 22 < lo < 24                                 # the lesson's test
    assert abs((period_ratio(math.radians(10)) - 1) * 86400 - 164.8) < 0.5
