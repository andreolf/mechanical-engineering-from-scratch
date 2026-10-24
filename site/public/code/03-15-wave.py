"""Wave equation on a string: d'Alembert's solution against the mode series, and energy conservation."""
import math
import numpy as np


def pluck(x, L, a):
    """Triangle with peak 1 at x = a L."""
    return np.where(x < a * L, x / (a * L), (L - x) / (L - a * L))


def odd_periodic(f, L):
    """Extend f (defined on [0, L], zero at the ends) oddly with period 2L, as fixed ends require."""
    def g(x):
        y = np.mod(x, 2 * L)
        return np.where(y <= L, f(y), -f(2 * L - y))
    return g


def dalembert(x, t, c, L, a):
    g = odd_periodic(lambda s: pluck(s, L, a), L)
    return 0.5 * (g(x - c * t) + g(x + c * t))


def modes(x, t, c, L, a, N=4000):
    u = np.zeros_like(x)
    for n in range(1, N + 1):
        bn = 2 * math.sin(n * math.pi * a) / (n * math.pi) ** 2 / (a * (1 - a))
        u += bn * np.sin(n * math.pi * x / L) * math.cos(n * math.pi * c * t / L)
    return u


if __name__ == "__main__":
    L, mu, T = 0.65, 4e-4, 70.0
    c = math.sqrt(T / mu); f1 = c / (2 * L)
    print(f"c = {c:.1f} m/s, f1 = {f1:.1f} Hz, tension for 329.6 Hz: {T * (329.6 / f1) ** 2:.1f} N")
    assert abs(f1 - 321.79) < 0.01
    x = np.linspace(0, L, 1301)
    for t in (0.0, 0.3e-3, 1.1e-3, 2.7e-3):
        assert np.max(np.abs(dalembert(x, t, c, L, 0.25) - modes(x, t, c, L, 0.25))) < 2e-3
    # after one full period 2L/c the string is back where it started
    assert np.max(np.abs(dalembert(x, 2 * L / c, c, L, 0.25) - pluck(x, L, 0.25))) < 1e-9
    # half a period later the shape is flipped
    assert np.max(np.abs(dalembert(x, L / c, c, L, 0.25) + pluck(L - x, L, 0.25))) < 1e-9
    # harmonic content: the 4th harmonic vanishes for a pluck at L/4
    amps = [abs(math.sin(n * math.pi / 4)) / n ** 2 for n in range(1, 7)]
    print("relative harmonics:", [round(v / amps[0], 3) for v in amps])
    assert amps[3] < 1e-15
    # energy (kinetic + strain) stays constant as the shape travels and reflects
    xf = np.linspace(0, L, 20001); dt = 1e-8
    def energy(t):
        u_t = (dalembert(xf, t + dt, c, L, 0.25) - dalembert(xf, t - dt, c, L, 0.25)) / (2 * dt)
        u_x = np.gradient(dalembert(xf, t, c, L, 0.25), xf)
        return np.trapezoid(0.5 * mu * u_t ** 2 + 0.5 * T * u_x ** 2, xf)
    E = [energy(t) for t in (0.0, 0.37e-3, 1.21e-3, 2.5e-3)]
    print("energy (J per unit amplitude^2):", [round(float(e), 3) for e in E])
    assert max(E) - min(E) < 0.01 * E[0]
