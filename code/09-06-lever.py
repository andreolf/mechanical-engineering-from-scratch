"""Phase diagrams: an ideal-solution Cu-Ni diagram from melting data, and the lever rule."""
import math
import numpy as np

R = 8.314
TA, HA = 1358.0, 13.05e3       # copper: melting point (K), heat of fusion (J/mol)
TB, HB = 1728.0, 17.48e3       # nickel


def solidus_liquidus(T):
    """Ideal liquid and solid solutions: x_l / x_s = exp(H / R (1/Tm - 1/T)) for each component. Returns Ni fractions (x_s, x_l)."""
    kA = math.exp(HA / R * (1 / TA - 1 / T)); kB = math.exp(HB / R * (1 / TB - 1 / T))
    xs = (1 - kA) / (kB - kA); xl = kB * xs
    return xs, xl


def lever(x0, xs, xl):
    """Fractions of liquid and solid for overall composition x0 between the two phase boundaries."""
    fl = (xs - x0) / (xs - xl); return fl, 1 - fl


if __name__ == "__main__":
    for Tc in (1100, 1200, 1250, 1300, 1400):
        xs, xl = solidus_liquidus(Tc + 273.15)
        print(f"{Tc} C: liquid has {xl*100:.1f} % Ni, solid has {xs*100:.1f} % Ni")
    x0, T = 0.40, 1235 + 273.15
    xs, xl = solidus_liquidus(T)
    fl, fs = lever(x0, xs, xl)
    print(f"alloy with 40 % Ni at 1235 C: {fl*100:.1f} % liquid ({xl*100:.1f} % Ni) and {fs*100:.1f} % solid ({xs*100:.1f} % Ni)")
    assert abs(fl + fs - 1) < 1e-15 and abs(fl * xl + fs * xs - x0) < 1e-12
    # temperatures where the 40 % alloy starts and finishes solidifying (bisection on each boundary)
    def bisect(f, lo, hi):
        for _ in range(60):
            m = 0.5 * (lo + hi)
            if f(lo) * f(m) <= 0: hi = m
            else: lo = m
        return 0.5 * (lo + hi)
    T_liq = bisect(lambda T: solidus_liquidus(T)[1] - x0, TA + 1e-6, TB - 1e-6)
    T_sol = bisect(lambda T: solidus_liquidus(T)[0] - x0, TA + 1e-6, TB - 1e-6)
    print(f"40 % Ni alloy: starts to freeze at {T_liq-273.15:.1f} C, fully solid at {T_sol-273.15:.1f} C")
    # pure ends melt at their melting points
    assert abs(solidus_liquidus(TA + 1e-3)[0]) < 1e-3 and abs(solidus_liquidus(TB - 1e-3)[1] - 1) < 1e-3
    for T in np.linspace(T_sol + 1, T_liq - 1, 5):
        xs, xl = solidus_liquidus(T); fl, fs = lever(x0, xs, xl)
        assert 0 <= fl <= 1 and abs(fl + fs - 1) < 1e-15
