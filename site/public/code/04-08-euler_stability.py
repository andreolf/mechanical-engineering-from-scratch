"""Explicit Euler on y' = -k y: amplification factor 1 - h k, stable exactly when h <= 2/k."""
import numpy as np


def euler(f, y0, h, n):
    y = np.empty(n + 1); y[0] = y0
    for i in range(n):
        y[i + 1] = y[i] + h * f(y[i])
    return y


if __name__ == "__main__":
    # a thermocouple bead: time constant tau = 0.5 s, so k = 2 1/s
    k = 2.0; f = lambda y: -k * y
    print("  h (s)   h k   amplification   |y| after 50 steps")
    for h in (0.1, 0.5, 0.9, 1.0, 1.1):
        y = euler(f, 1.0, h, 50)
        print(f"{h:6.2f} {h * k:6.2f} {1 - h * k:14.2f} {abs(y[-1]):20.3e}")
    # the stability limit is exactly h = 2 / k
    for h in np.linspace(0.05, 1.5, 59):
        grows = abs(euler(f, 1.0, h, 200)[-1]) > 1.0
        assert grows == (h > 2 / k + 1e-12), h
    print(f"diverges exactly when h > 2/k = {2 / k} s")
    # stiff pair: a fast mode (k = 1000) forces a tiny step even after it has died out
    lam = np.array([-1.0, -1000.0])
    h_max = 2 / 1000
    print(f"system with eigenvalues {lam}: explicit Euler needs h < {h_max} s, i.e. {int(10 / h_max)} steps to reach t = 10 s")
    assert np.all(np.abs(1 + 0.0019 * lam) < 1) and not np.all(np.abs(1 + 0.0021 * lam) < 1)
