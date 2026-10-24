"""The rocket equation: Tsiolkovsky's delta v, then an ascent integrated with gravity."""
import math
import numpy as np


def tsiolkovsky(ve, m0, m1):
    return ve * math.log(m0 / m1)


def burn(m0, mprop, ve, mdot, g=0.0, dt=1e-3):
    """Vertical burn: m dv/dt = mdot ve - m g, with m(t) = m0 - mdot t. RK4 on (h, v)."""
    tb = mprop / mdot
    f = lambda t, s: np.array([s[1], mdot * ve / (m0 - mdot * t) - g])
    t, s = 0.0, np.zeros(2)
    n = int(round(tb / dt))
    h = tb / n
    for _ in range(n):
        k1 = f(t, s); k2 = f(t + h / 2, s + h / 2 * k1); k3 = f(t + h / 2, s + h / 2 * k2); k4 = f(t + h, s + h * k3)
        s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += h
    return s, tb


if __name__ == "__main__":
    # a small sounding rocket: 1000 kg at lift-off, 750 kg of propellant, exhaust 2500 m/s, burning 15 kg/s
    m0, mp, ve, mdot = 1000.0, 750.0, 2500.0, 15.0
    dv = tsiolkovsky(ve, m0, m0 - mp)
    (h, v), tb = burn(m0, mp, ve, mdot, g=0.0)
    print(f"Tsiolkovsky: dv = {dv:.3f} m/s; integrated without gravity: {v:.3f} m/s after {tb:.0f} s")
    assert abs(v - dv) < 1e-6
    (h, v), tb = burn(m0, mp, ve, mdot, g=9.81)
    print(f"with gravity: burnout at {h/1e3:.2f} km, {v:.1f} m/s (gravity loss g tb = {9.81*tb:.1f} m/s)")
    assert abs((dv - v) - 9.81 * tb) < 1e-6
    hmax = h + v**2 / (2 * 9.81)
    print(f"coasting (no drag, flat-earth g) to apogee {hmax/1e3:.1f} km")
    print(f"lift-off acceleration {mdot*ve/m0 - 9.81:.2f} m/s^2, thrust/weight {mdot*ve/(m0*9.81):.2f}")
    # staging: the same propellant split into two stages beats one stage
    s1 = tsiolkovsky(ve, 1000, 1000 - 500)                 # stage 1 burns 500 kg, then drops a 60 kg tank
    s2 = tsiolkovsky(ve, 1000 - 500 - 60, 1000 - 500 - 60 - 250)
    one = tsiolkovsky(ve, 1000, 250)
    print(f"single stage {one:.0f} m/s; two stages (dropping 60 kg of empty tank) {s1 + s2:.0f} m/s")
