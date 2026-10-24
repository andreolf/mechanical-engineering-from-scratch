"""Torricelli tank: exact solution versus explicit Euler, and Euler's first-order convergence."""
import math

G = 9.81


def exact_h(t, h0, A, a):
    k = a / A * math.sqrt(2 * G)
    return max(0.0, math.sqrt(h0) - k * t / 2) ** 2


def euler_h(T, h0, A, a, dt):
    k = a / A * math.sqrt(2 * G)
    h, t = h0, 0.0
    n = round(T / dt)
    for _ in range(n):
        h = max(0.0, h - dt * k * math.sqrt(h))
        t += dt
    return h


if __name__ == "__main__":
    h0, A, a = 2.0, 1.0, 0.002
    k = a / A * math.sqrt(2 * G)
    assert abs(2 * math.sqrt(h0) / k - 319.275) < 1e-2
    assert abs(2 * (math.sqrt(2) - 1) / k - 93.51) < 1e-2
    e = exact_h(100, h0, A, a)
    errs = []
    for dt in (10, 5, 2.5, 1.25, 0.625):
        errs.append(abs(euler_h(100, h0, A, a, dt) - e))
        print(f"dt={dt:6.3f}  error {errs[-1]:.3e}")
    ratios = [errs[i] / errs[i + 1] for i in range(len(errs) - 1)]
    assert all(1.9 < r < 2.1 for r in ratios)            # error halves with the step: first order
    assert abs(euler_h(100, h0, A, a, 10) - 0.9269) < 1e-3 and abs(e - 0.9434) < 1e-3
