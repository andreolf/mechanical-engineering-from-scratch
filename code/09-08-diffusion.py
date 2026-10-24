"""Diffusion: Arrhenius diffusivity, the erf solution for carburising, checked against a finite-difference solution of Fick's second law."""
import math
import numpy as np

R = 8.314
D0, Q = 2.3e-5, 148e3        # carbon in austenite (FCC iron): m^2/s, J/mol


def D(T):
    return D0 * math.exp(-Q / (R * T))


def erfinv(y):
    """Inverse error function by Newton's method on math.erf."""
    x = 0.0
    for _ in range(50):
        x -= (math.erf(x) - y) / (2 / math.sqrt(math.pi) * math.exp(-x * x))
    return x


def profile(x, t, T, Cs, C0):
    """Carbon content at depth x (m) after time t (s), surface held at Cs, initial C0."""
    return Cs - (Cs - C0) * math.erf(x / (2 * math.sqrt(D(T) * t)))


def case_depth(t, T, Cs, C0, Cx):
    """Depth where the carbon content has fallen to Cx."""
    z = erfinv((Cs - Cx) / (Cs - C0))
    return 2 * z * math.sqrt(D(T) * t)


def fdm(t, T, Cs, C0, L=3e-3, n=301):
    """Explicit finite differences for dC/dt = D d2C/dx2 on [0, L]; returns grid and profile."""
    x = np.linspace(0, L, n); dx = x[1] - x[0]; d = D(T)
    dt = 0.4 * dx * dx / d; steps = int(math.ceil(t / dt)); dt = t / steps
    c = np.full(n, C0); c[0] = Cs
    for _ in range(steps):
        c[1:-1] += d * dt / dx**2 * (c[2:] - 2 * c[1:-1] + c[:-2])
    return x, c


if __name__ == "__main__":
    T = 927 + 273.15
    print(f"D at 927 C: {D(T):.3e} m^2/s; at 1027 C: {D(1300.15):.3e} m^2/s")
    t = 4 * 3600
    xc = case_depth(t, T, 1.0, 0.2, 0.4)
    print(f"case depth to 0.4 %C after 4 h at 927 C: {xc*1e3:.3f} mm")
    assert abs(profile(xc, t, T, 1.0, 0.2) - 0.4) < 1e-9
    # depth grows with sqrt(time): 4x the time, 2x the depth
    assert abs(case_depth(4 * t, T, 1.0, 0.2, 0.4) / xc - 2) < 1e-12
    hours_hot = (xc / (2 * erfinv(0.75))) ** 2 / D(1300.15) / 3600
    print(f"same depth at 1027 C takes {hours_hot:.2f} h")
    x, c = fdm(t, T, 1.0, 0.2)
    exact = np.array([profile(xi, t, T, 1.0, 0.2) for xi in x])
    err = np.max(np.abs(c - exact))
    print(f"finite differences vs erf: max difference {err:.2e} wt% C")
    assert err < 2e-3
    for xm in (0.25, 0.5, 1.0, 1.5):
        print(f"  {xm} mm: {profile(xm*1e-3, t, T, 1.0, 0.2):.3f} %C")
