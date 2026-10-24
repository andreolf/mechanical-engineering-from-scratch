"""Injection moulding: cooling time of a plastic wall from the one-term slab solution, checked with finite differences, and why it grows with thickness squared."""
import math
import numpy as np

K, RHO, CP = 0.17, 1050.0, 2000.0      # ABS
ALPHA = K / (RHO * CP)
TM, TW, TE = 240.0, 60.0, 90.0         # melt, mould wall and ejection (centre) temperatures, C


def cooling_time(s, a=ALPHA, Tm=TM, Tw=TW, Te=TE):
    """Time for the centre of a wall of thickness s to cool to Te (one-term Fourier series)."""
    return s * s / (math.pi**2 * a) * math.log(4 / math.pi * (Tm - Tw) / (Te - Tw))


def fdm_cooling_time(s, n=81):
    x = np.linspace(0, s, n); dx = x[1] - x[0]; dt = 0.4 * dx * dx / ALPHA
    T = np.full(n, TM); T[0] = T[-1] = TW; t = 0.0
    while T[n // 2] > TE:
        T[1:-1] += ALPHA * dt / dx**2 * (T[2:] - 2 * T[1:-1] + T[:-2]); t += dt
    return t


if __name__ == "__main__":
    print(f"ABS thermal diffusivity {ALPHA:.3e} m^2/s")
    for s_mm in (1.0, 2.0, 3.0, 4.0):
        tc = cooling_time(s_mm / 1000); tf = fdm_cooling_time(s_mm / 1000)
        print(f"  wall {s_mm:.0f} mm: formula {tc:.2f} s, finite differences {tf:.2f} s")
        assert abs(tc - tf) / tc < 0.01
    assert abs(cooling_time(0.004) / cooling_time(0.002) - 4) < 1e-12
    # cycle: fill 1 s, hold included in cooling, open/eject/close 4 s
    cyc = 1 + cooling_time(0.002) + 4
    print(f"2 mm part cycle about {cyc:.1f} s: {3600/cyc:.0f} shots per hour; with a 4 mm wall {3600/(5+cooling_time(0.004)):.0f}")
    # colder mould: faster but more stress and worse surface
    print(f"mould at 40 C: {cooling_time(0.002, Tw=40.0):.2f} s for the 2 mm wall")
