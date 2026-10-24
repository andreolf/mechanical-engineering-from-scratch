"""Radiation: a Monte Carlo view factor checked against the exact formula, grey two-surface exchange, and a tropical roof heat balance."""
import math
import numpy as np

SIGMA = 5.670374e-8


def view_factor_mc(a, b, c, n=1_000_000, seed=1):
    """Fraction of diffuse radiation leaving an a x b plate that hits an identical plate a distance c above it."""
    rng = np.random.default_rng(seed)
    x, y = rng.uniform(0, a, n), rng.uniform(0, b, n)
    # cosine-weighted directions: sin^2(theta) uniform
    u, phi = rng.uniform(0, 1, n), rng.uniform(0, 2 * math.pi, n)
    st, ct = np.sqrt(u), np.sqrt(1 - u)
    t = c / ct
    xh, yh = x + t * st * np.cos(phi), y + t * st * np.sin(phi)
    return np.mean((xh >= 0) & (xh <= a) & (yh >= 0) & (yh <= b))


def view_factor_exact(a, b, c):
    X, Y = a / c, b / c
    return 2 / (math.pi * X * Y) * (0.5 * math.log((1 + X * X) * (1 + Y * Y) / (1 + X * X + Y * Y))
                                    + X * math.sqrt(1 + Y * Y) * math.atan(X / math.sqrt(1 + Y * Y))
                                    + Y * math.sqrt(1 + X * X) * math.atan(Y / math.sqrt(1 + X * X))
                                    - X * math.atan(X) - Y * math.atan(Y))


def roof_temperature(a_sol, eps, G=1000.0, T_air=304.15, T_sky=294.15, h=10.0):
    """Steady roof: absorbed sun = emitted to the sky minus sky back-radiation + convection (underside insulated)."""
    f = lambda T: a_sol * G - eps * SIGMA * (T ** 4 - T_sky ** 4) - h * (T - T_air)
    lo, hi = 250.0, 450.0
    while hi - lo > 1e-9:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    for c in (1.0, 0.1, 0.01):
        mc, ex = view_factor_mc(1, 1, c), view_factor_exact(1, 1, c)
        sd = math.sqrt(ex * (1 - ex) / 1_000_000)
        print(f"unit squares {c} m apart: Monte Carlo F = {mc:.4f}, exact {ex:.4f} (MC standard error {sd:.1e})")
        assert abs(mc - ex) < 4 * sd + 1e-9
    assert view_factor_exact(1, 1, 0.001) > 0.998   # large parallel plates: F -> 1
    # grey parallel plates: a steel roof sheet at 70 C over a ceiling at 35 C
    T1, T2 = 343.15, 308.15
    for e1, e2, name in ((0.9, 0.9, "both painted"), (0.05, 0.9, "foil under the roof")):
        q = SIGMA * (T1 ** 4 - T2 ** 4) / (1 / e1 + 1 / e2 - 1)
        print(f"  {name}: {q:.2f} W/m^2 radiated down to the ceiling")
    # a roof in Bali at noon: G = 1000 W/m^2, air 31 C, effective sky 21 C, h = 10
    for name, a_s, e in (("galvanised steel", 0.65, 0.25), ("dark paint", 0.90, 0.90), ("white cool-roof paint", 0.20, 0.90)):
        T = roof_temperature(a_s, e)
        print(f"  {name}: absorptivity {a_s}, emissivity {e}: roof at {T-273.15:.2f} C")
    Tg, Tw = roof_temperature(0.65, 0.25), roof_temperature(0.20, 0.90)
    assert Tg - Tw > 30
