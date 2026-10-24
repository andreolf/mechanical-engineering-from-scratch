"""Equilibria, Jacobians and phase-plane trajectories for the damped pendulum."""
import math
import numpy as np


def jacobian(f, y, h=1e-6):
    y = np.asarray(y, float)
    return np.column_stack([(f(y + h * e) - f(y - h * e)) / (2 * h) for e in np.eye(len(y))])


def classify(J, tol=1e-9):
    lam = np.linalg.eigvals(J)
    re, im = lam.real, lam.imag
    if np.all(np.abs(im) > tol):
        return "centre" if np.all(np.abs(re) < tol) else ("stable spiral" if np.all(re < 0) else "unstable spiral")
    if re.min() < -tol and re.max() > tol:
        return "saddle"
    return "stable node" if np.all(re < 0) else "unstable node"


def rk4_path(f, y0, h, n):
    y = np.array(y0, float); out = [y.copy()]
    for _ in range(n):
        k1 = f(y); k2 = f(y + h / 2 * k1); k3 = f(y + h / 2 * k2); k4 = f(y + h * k3)
        y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(y.copy())
    return np.array(out)


if __name__ == "__main__":
    g, L, z = 9.81, 1.0, 0.1
    w0 = math.sqrt(g / L)
    f = lambda y: np.array([y[1], -w0 ** 2 * math.sin(y[0]) - 2 * z * w0 * y[1]])
    J0, Jpi = jacobian(f, [0, 0]), jacobian(f, [math.pi, 0])
    print("bottom:", classify(J0), np.round(np.linalg.eigvals(J0), 3))
    print("top:   ", classify(Jpi), np.round(np.linalg.eigvals(Jpi), 3))
    assert classify(J0) == "stable spiral" and classify(Jpi) == "saddle"
    assert classify(jacobian(lambda y: np.array([y[1], -w0 ** 2 * math.sin(y[0])]), [0, 0])) == "centre"
    # undamped: just below the separatrix speed it swings back, just above it goes over
    fu = lambda y: np.array([y[1], -w0 ** 2 * math.sin(y[0])])
    below = rk4_path(fu, [0, 0.99 * 2 * w0], 1e-3, 6000)
    above = rk4_path(fu, [0, 1.01 * 2 * w0], 1e-3, 6000)
    assert below[:, 0].max() < math.pi and above[:, 0].max() > 2 * math.pi
    E = 0.5 * below[:, 1] ** 2 - w0 ** 2 * np.cos(below[:, 0])
    assert np.ptp(E) < 1e-8 * abs(E[0])                       # energy conserved to RK4 accuracy
    # damped: a strong kick goes over the top, then settles a whole turn away
    path = rk4_path(f, [0, 8.0], 1e-3, 40000)
    turns = round(path[-1, 0] / (2 * math.pi))
    print(f"kick of 8 rad/s with zeta = 0.1: settles {turns} turn(s) from the start")
    assert turns >= 1 and abs(path[-1, 0] - 2 * math.pi * turns) < 1e-3
