"""Vortex shedding: Strouhal frequency for a ski-lift cable, a van der Pol wake oscillator, and lock-in with the cable's own modes."""
import math
import numpy as np

ST = 0.2


def shedding_freq(U, D, St=ST):
    return St * U / D


def wake_oscillator(U, D, eps=0.3, t_end=None, St=ST):
    """Van der Pol model of the fluctuating lift: q'' + eps W (q^2 - 1) q' + W^2 q = 0 with W = 2 pi St U / D.
    Integrates with RK4 and returns the measured frequency from upward zero crossings."""
    W = 2 * math.pi * St * U / D
    T = 2 * math.pi / W; t_end = t_end or 400 * T; dt = T / 200
    def f(s): return np.array([s[1], -eps * W * (s[0] ** 2 - 1) * s[1] - W * W * s[0]])
    s = np.array([0.1, 0.0]); t = 0.0; crossings = []
    while t < t_end:
        k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
        s_new = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if s[0] < 0 <= s_new[0] and t > t_end / 2:
            crossings.append(t + dt * (-s[0]) / (s_new[0] - s[0]))
        s, t = s_new, t + dt
    return (len(crossings) - 1) / (crossings[-1] - crossings[0])


def cable_modes(L, T, mu, n):
    return [m / (2 * L) * math.sqrt(T / mu) for m in range(1, n + 1)]


if __name__ == "__main__":
    D = 0.040                                                     # a 40 mm haul rope
    for U in (2.0, 5.0, 10.0, 20.0):
        print(f"wind {U:4.1f} m/s: Re = {U*D/1.5e-5:9.0f}, shedding at {shedding_freq(U, D):6.1f} Hz")
    f1 = wake_oscillator(5.0, D); f2 = wake_oscillator(10.0, D); f3 = wake_oscillator(10.0, 2 * D)
    print(f"wake oscillator: {f1:.4f} Hz at 5 m/s, {f2:.4f} Hz at 10 m/s, {f3:.4f} Hz at 10 m/s with D doubled")
    print(f"ratio for doubled U: {f2/f1:.6f}; for doubled U and D: {f3/f1:.6f}")
    assert abs(f2 / f1 - 2) < 1e-3 and abs(f3 / f1 - 1) < 1e-3       # frequency scales with U/D
    print(f"van der Pol at eps = 0.3 runs {100*(1 - f1/shedding_freq(5.0, D)):.2f} % below St U/D")
    # a 60 m span, 150 kN tension, 5.5 kg/m: modes are spaced only f1 apart, so some mode is always near the shedding frequency
    f1c = cable_modes(60.0, 150e3, 5.5, 1)[0]
    print(f"cable fundamental {f1c:.4f} Hz; modes every {f1c:.4f} Hz")
    for U in (5.0, 10.0, 20.0):
        fs = shedding_freq(U, D); m = round(fs / f1c)
        print(f"  {U:4.1f} m/s: shedding {fs:.1f} Hz is closest to mode {m} at {m*f1c:.3f} Hz ({100*abs(m*f1c-fs)/fs:.2f} % away)")
        assert abs(m * f1c - fs) <= f1c / 2
