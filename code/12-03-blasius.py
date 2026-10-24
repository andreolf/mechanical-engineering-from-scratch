"""The Blasius boundary layer: f''' + f f''/2 = 0 solved by RK4 shooting on the unknown wall curvature f''(0)."""
import math
import numpy as np


def rhs(s):
    f, fp, fpp = s
    return np.array([fp, fpp, -0.5 * f * fpp])


def integrate(fpp0, eta_max=10.0, n=2000):
    h = eta_max / n
    s = np.array([0.0, 0.0, fpp0]); out = [s.copy()]
    for _ in range(n):
        k1 = rhs(s); k2 = rhs(s + h / 2 * k1); k3 = rhs(s + h / 2 * k2); k4 = rhs(s + h * k3)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); out.append(s.copy())
    return np.linspace(0, eta_max, n + 1), np.array(out)


def shoot(lo=0.1, hi=1.0, tol=1e-12):
    """Find f''(0) so that f'(eta_max) = 1 (bisection: f'(inf) grows with f''(0))."""
    while hi - lo > tol:
        m = (lo + hi) / 2
        _, s = integrate(m)
        lo, hi = (m, hi) if s[-1, 1] < 1 else (lo, m)
    return (lo + hi) / 2


if __name__ == "__main__":
    fpp0 = shoot()
    eta, s = integrate(fpp0)
    print(f"f''(0) = {fpp0:.6f}")
    assert abs(fpp0 - 0.332057) < 2e-6
    i99 = np.argmax(s[:, 1] >= 0.99)
    eta99 = eta[i99 - 1] + (0.99 - s[i99 - 1, 1]) * (eta[i99] - eta[i99 - 1]) / (s[i99, 1] - s[i99 - 1, 1])
    disp = eta[-1] - s[-1, 0]                                   # displacement thickness: integral of (1 - f')
    print(f"99 % thickness at eta = {eta99:.3f}; displacement thickness at eta = {disp:.4f}")
    assert abs(disp - 1.7208) < 1e-3 and abs(eta99 - 4.91) < 0.01
    # a 1 m plate in a 5 m/s air stream
    U, nu = 5.0, 1.5e-5
    for x in (0.1, 0.5, 1.0):
        Rex = U * x / nu
        print(f"x = {x:.1f} m: Re_x = {Rex:.3e}, delta99 = {eta99*math.sqrt(nu*x/U)*1000:.3f} mm, Cf = {2*fpp0/math.sqrt(Rex):.6f}")
    CD = 1.328 / math.sqrt(U * 1.0 / nu)
    print(f"friction drag on one side of the 1 m x 1 m plate: {0.5*1.2*U*U*CD:.5f} N (C_D = {CD:.6f})")
