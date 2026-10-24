"""Forced vibration: frequency response H(omega) of a damped oscillator, checked against time simulation."""
import math
import numpy as np


def H(w, m, c, k):
    """Complex receptance X/F for F e^{i w t}."""
    return 1.0 / (k - m * w**2 + 1j * c * w)


def steady_amplitude_by_simulation(m, c, k, F0, w, cycles=60, per=200):
    dt = 2 * math.pi / w / per
    f = lambda t, s: np.array([s[1], (F0 * math.cos(w * t) - c * s[1] - k * s[0]) / m])
    s = np.zeros(2); t = 0.0; xs = []
    for i in range(cycles * per):
        k1 = f(t, s); k2 = f(t + dt/2, s + dt/2*k1); k3 = f(t + dt/2, s + dt/2*k2); k4 = f(t + dt, s + dt*k3)
        s = s + dt/6*(k1 + 2*k2 + 2*k3 + k4); t += dt
        if i >= (cycles - 5) * per: xs.append(s[0])
    return (max(xs) - min(xs)) / 2


if __name__ == "__main__":
    m, k, zeta, F0 = 200.0, 2e5, 0.05, 500.0     # a machine on rubber mounts, shaken by 500 N
    wn = math.sqrt(k / m); c = 2 * zeta * math.sqrt(k * m)
    print(f"omega_n = {wn:.3f} rad/s ({wn/(2*math.pi):.3f} Hz), c = {c:.1f} N s/m, static deflection {F0/k*1000:.2f} mm")
    w = np.linspace(0.01, 3 * wn, 300001)
    A = np.abs(H(w, m, c, k)) * F0
    i = np.argmax(A)
    print(f"peak at {w[i]:.3f} rad/s, theory omega_n sqrt(1 - 2 zeta^2) = {wn*math.sqrt(1-2*zeta**2):.3f}")
    assert abs(w[i] - wn * math.sqrt(1 - 2 * zeta**2)) < 1e-3
    print(f"peak amplitude {A[i]*1000:.3f} mm, dynamic amplification {A[i]/(F0/k):.4f} (theory 1/(2 zeta sqrt(1 - zeta^2)) = {1/(2*zeta*math.sqrt(1-zeta**2)):.4f})")
    for r in (0.5, 1.0, 2.0):
        h = H(r * wn, m, c, k) * F0
        xs = steady_amplitude_by_simulation(m, c, k, F0, r * wn)
        print(f"r = {r}: amplitude {abs(h)*1000:.4f} mm (simulated {xs*1000:.4f}), phase lag {-math.degrees(np.angle(h)):.2f} deg")
        assert abs(xs / abs(h) - 1) < 2e-3
