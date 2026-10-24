"""Dormand-Prince RK5(4) with error control: steps shrink at an impact and grow in free flight."""
import math
import numpy as np

C = np.array([0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1])
A = [[], [1 / 5], [3 / 40, 9 / 40], [44 / 45, -56 / 15, 32 / 9],
     [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729],
     [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656],
     [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]]
B5 = np.array([35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0])
B4 = np.array([5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40])


def dopri(f, t, y, t_end, rtol=1e-6, atol=1e-9, h=1e-3):
    ts, ys, hs = [t], [y.copy()], []
    while t < t_end:
        h = min(h, t_end - t)
        k = []
        for i in range(7):
            k.append(f(t + C[i] * h, y + h * sum(a * kj for a, kj in zip(A[i], k))))
        k = np.array(k)
        y5 = y + h * B5 @ k
        err = h * (B5 - B4) @ k                         # embedded error estimate, free of extra evaluations
        sc = atol + rtol * np.maximum(np.abs(y), np.abs(y5))
        en = math.sqrt(np.mean((err / sc) ** 2))
        if en <= 1:                                     # accept
            t, y = t + h, y5
            ts.append(t); ys.append(y.copy()); hs.append(h)
        h *= min(5.0, max(0.2, 0.9 * en ** (-1 / 5))) if en > 0 else 5.0
    return np.array(ts), np.array(ys), np.array(hs)


def ball(t, y, m=0.06, k=2e5, c=8.0, g=9.81):
    """Tennis ball on a stiff penalty contact: free fall above the floor, spring-damper below it."""
    x, v = y
    F = -m * g + ((-k * x - c * v) if x < 0 else 0.0)
    return np.array([v, F / m])


if __name__ == "__main__":
    # accuracy: harmonic oscillator, exact solution cos t
    for tol in (1e-4, 1e-6, 1e-8):
        ts, ys, hs = dopri(lambda t, y: np.array([y[1], -y[0]]), 0.0, np.array([1.0, 0.0]), 10.0, rtol=tol, atol=tol * 1e-3)
        err = abs(ys[-1, 0] - math.cos(10))
        print(f"rtol {tol:.0e}: {len(hs):4d} steps, global error at t = 10: {err:.1e}")
        assert err < 100 * tol
    # step-size history for a dropped ball
    ts, ys, hs = dopri(ball, 0.0, np.array([1.0, 0.0]), 1.0)
    contact = ys[1:, 0] < 0
    print(f"ball: {len(hs)} steps; largest step in flight {hs[~contact].max() * 1e3:.2f} ms, smallest in contact {hs[contact].min() * 1e6:.1f} us")
    # big steps in flight skip over the apex, so compute it from the first state after lift-off
    i = np.nonzero((ys[:, 0] > 0) & (ys[:, 1] > 0))[0][0]
    apex = ys[i, 0] + ys[i, 1] ** 2 / (2 * 9.81)
    print(f"contact lasts about {np.sum(hs[contact]) * 1e3:.2f} ms (pi sqrt(m/k) = {math.pi * math.sqrt(0.06 / 2e5) * 1e3:.2f} ms); rebound apex {apex:.3f} m")
    assert abs(apex - 0.7946) < 2e-3
    assert hs[contact].min() < hs[~contact].max() / 20
