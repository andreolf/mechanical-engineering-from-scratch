"""The undamped harmonic oscillator: simulate m x'' + k x = 0 and measure the period."""
import math
import numpy as np


def simulate(m, k, x0, v0, t_end, dt):
    """Velocity Verlet: second order and energy-stable for oscillators."""
    n = int(round(t_end / dt)); x = np.empty(n + 1); v = np.empty(n + 1)
    x[0], v[0] = x0, v0; a = -k / m * x0
    for i in range(n):
        x[i + 1] = x[i] + dt * v[i] + 0.5 * dt * dt * a
        a_new = -k / m * x[i + 1]
        v[i + 1] = v[i] + 0.5 * dt * (a + a_new); a = a_new
    return np.arange(n + 1) * dt, x, v


def measured_period(t, x):
    """Average spacing of upward zero crossings, with linear interpolation between samples."""
    i = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    tc = t[i] - x[i] * (t[i + 1] - t[i]) / (x[i + 1] - x[i])
    return np.mean(np.diff(tc))


if __name__ == "__main__":
    m, k = 300.0, 30e3                     # quarter of a car on its spring
    wn = math.sqrt(k / m)
    t, x, v = simulate(m, k, 0.05, 0.0, 10.0, 1e-3)
    T = measured_period(t, x)
    print(f"m = {m:.0f} kg, k = {k/1e3:.0f} kN/m: omega_n = {wn:.3f} rad/s, f_n = {wn/(2*math.pi):.4f} Hz")
    print(f"measured period {T:.6f} s, formula 2 pi sqrt(m/k) = {2*math.pi*math.sqrt(m/k):.6f} s")
    assert abs(T - 2 * math.pi * math.sqrt(m / k)) < 1e-5
    E = 0.5 * m * v**2 + 0.5 * k * x**2
    print(f"energy {E[0]:.4f} J, worst relative change {np.max(np.abs(E / E[0] - 1)):.1e}")
    assert np.max(np.abs(E / E[0] - 1)) < 1e-4
    # amplitude does not change the period (linear system)
    for x0 in (0.001, 0.2):
        assert abs(measured_period(*simulate(m, k, x0, 0, 10, 1e-3)[:2]) - T) < 1e-9
    # static deflection shortcut: f_n = sqrt(g / delta) / (2 pi)
    delta = m * 9.81 / k
    print(f"static sag {delta*1000:.1f} mm gives f_n = {math.sqrt(9.81/delta)/(2*math.pi):.4f} Hz")
    # doubling the mass lowers the frequency by sqrt 2
    T2 = measured_period(*simulate(2 * m, k, 0.05, 0, 10, 1e-3)[:2])
    print(f"double the mass: period {T2:.4f} s, ratio {T2/T:.4f}")
    assert abs(T2 / T - math.sqrt(2)) < 1e-4
