"""Numerical Hessian, classification of stationary points and Newton's method for minimisation."""
import numpy as np


def num_grad(f, x, h=1e-5):
    x = np.asarray(x, float)
    return np.array([(f(x + h * e) - f(x - h * e)) / (2 * h) for e in np.eye(len(x))])


def num_hessian(f, x, h=1e-4):
    x = np.asarray(x, float); n = len(x); H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ei, ej = h * np.eye(n)[i], h * np.eye(n)[j]
            H[i, j] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (4 * h * h)
    return 0.5 * (H + H.T)


def classify(H, tol=1e-6):
    w = np.linalg.eigvalsh(H)
    if np.all(w > tol): return "minimum"
    if np.all(w < -tol): return "maximum"
    if np.any(w > tol) and np.any(w < -tol): return "saddle"
    return "inconclusive"


def newton_min(f, x0, tol=1e-10, max_iter=50):
    x = np.asarray(x0, float); hist = [x.copy()]
    for _ in range(max_iter):
        g = num_grad(f, x)
        if np.linalg.norm(g) < tol:
            break
        x = x + np.linalg.solve(num_hessian(f, x), -g)
        hist.append(x.copy())
    return x, hist


if __name__ == "__main__":
    f = lambda p: p[0] ** 3 - 3 * p[0] + p[1] ** 2
    assert classify(num_hessian(f, [1, 0])) == "minimum" and classify(num_hessian(f, [-1, 0])) == "saddle"
    assert np.allclose(num_hessian(f, [1, 0]), [[6, 0], [0, 2]], atol=1e-5)
    q = lambda p: -2 + 3 * (p[0] - 1) ** 2 + p[1] ** 2
    print(f"at (1.1, 0.1): exact {f([1.1, 0.1]):.4f}, quadratic model {q([1.1, 0.1]):.4f}")
    assert abs(f([1.1, 0.1]) - q([1.1, 0.1])) < 2e-3
    # Rosenbrock's banana valley: Newton reaches the minimum (1, 1) in a handful of steps
    rosen = lambda p: (1 - p[0]) ** 2 + 100 * (p[1] - p[0] ** 2) ** 2
    x, hist = newton_min(rosen, [-1.2, 1.0])
    print(f"Rosenbrock: Newton reached {np.round(x, 8)} in {len(hist) - 1} steps")
    assert np.allclose(x, [1, 1], atol=1e-6) and len(hist) - 1 < 15
    assert classify(num_hessian(rosen, [1, 1])) == "minimum"
    # a monkey saddle has a zero Hessian at the origin: inconclusive
    assert classify(num_hessian(lambda p: p[0] ** 3 - 3 * p[0] * p[1] ** 2, [0, 0])) == "inconclusive"
