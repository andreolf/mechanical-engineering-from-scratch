"""Implicit (backward) Euler with Newton iterations: stable at steps 100 times beyond the explicit limit."""
import numpy as np

M, C, K, D, F = 0.01, 20.0, 1e4, 1e-3, 10.0     # kg, N s/m, N/m, m, N: a small mass on a stiffening rubber bushing


def f(y):
    x, v = y
    return np.array([v, (F - C * v - K * x * (1 + (x / D) ** 2)) / M])


def jac(y):
    x, v = y
    return np.array([[0.0, 1.0], [-K * (1 + 3 * (x / D) ** 2) / M, -C / M]])


def implicit_euler(y0, h, n, tol=1e-12):
    """Solve y_{n+1} - y_n - h f(y_{n+1}) = 0 for y_{n+1} by Newton at every step."""
    y = np.array(y0, float); out = [y.copy()]; newton_its = []
    for _ in range(n):
        z = y.copy()
        for it in range(1, 30):
            G = z - y - h * f(z)
            dz = np.linalg.solve(np.eye(2) - h * jac(z), -G)
            z += dz
            if np.linalg.norm(dz) < tol * (1 + np.linalg.norm(z)):
                break
        newton_its.append(it); y = z; out.append(y.copy())
    return np.array(out), newton_its


def explicit_euler(y0, h, n):
    y = np.array(y0, float); out = [y.copy()]
    for _ in range(n):
        y = y + h * f(y); out.append(y.copy())
        if not np.all(np.isfinite(y)) or abs(y[0]) > 1e3:
            break
    return np.array(out)


if __name__ == "__main__":
    lam = np.linalg.eigvals(jac([0.0, 0.0]))
    print(f"eigenvalues at rest: {lam.real.round(1)} 1/s (critically damped); explicit Euler needs h < {2 / 1000:.3f} s")
    # scalar check: amplification 1/(1 + h k) for y' = -k y, even at h = 100/k
    k = 1000.0; h = 100 / k
    assert abs(1 / (1 + h * k) - 1 / 101) < 1e-15
    # the bushing under a 10 N step: static deflection solves s + s^3 = 1 with s = x / D
    s = np.roots([1, 0, 1, -1]); s = s[np.isreal(s)].real[0]
    print(f"static deflection {s * D * 1e3:.4f} mm")
    y_imp, its = implicit_euler([0, 0], 0.1, 20)
    y_exp = explicit_euler([0, 0], 0.1, 20)
    print(f"implicit Euler, h = 0.1 s (h|lambda| = 100): x = {y_imp[-1, 0] * 1e3:.4f} mm after 2 s, Newton iterations per step {min(its)}-{max(its)}")
    print(f"explicit Euler, same step: |x| = {abs(y_exp[-1, 0]):.1e} m after {len(y_exp) - 1} steps (blown up)")
    assert abs(y_imp[-1, 0] - s * D) < 1e-9 and abs(y_exp[-1, 0]) > 1
    # accuracy needs small steps only while things change fast: compare the transient at t = 2 ms
    ref, _ = implicit_euler([0, 0], 1e-6, 2000)
    errs = []
    for hh in (1e-4, 5e-5):
        yy, _ = implicit_euler([0, 0], hh, int(round(2e-3 / hh)))
        errs.append(abs(yy[-1, 0] - ref[-1, 0]))
        print(f"h = {hh:.0e} s: x(2 ms) error {errs[-1] * 1e6:.2f} um")
    assert 1.8 < errs[0] / errs[1] < 2.2          # first order: stable is not the same as accurate
