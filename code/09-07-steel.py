"""Steel: the Fe-C eutectoid, lever-rule microstructure fractions, and how fast a quenched bar cools."""
import math

C_ALPHA, C_EUT, C_CEM = 0.022, 0.76, 6.70   # wt% C: ferrite at 727 C, eutectoid, cementite (Fe3C)


def microstructure(c):
    """Room-temperature fractions after slow cooling: (proeutectoid phase, pearlite, total ferrite, total cementite)."""
    if c <= C_EUT:
        pro = (C_EUT - c) / (C_EUT - C_ALPHA)          # proeutectoid ferrite, lever rule just above 727 C
    else:
        pro = (c - C_EUT) / (C_CEM - C_EUT)            # proeutectoid cementite
    pearlite = 1 - pro
    fe3c = (c - C_ALPHA) / (C_CEM - C_ALPHA)            # lever rule just below 727 C, all phases
    return pro, pearlite, 1 - fe3c, fe3c


def t85(D, h, rho=7850.0, cp=600.0, Tf=20.0):
    """Lumped cooling time from 800 to 500 C for a long bar of diameter D (m) in a fluid with film coefficient h."""
    return rho * cp * D / (4 * h) * math.log((800 - Tf) / (500 - Tf))


def hardness_brinell(c):
    """Rough rule for slowly cooled carbon steel: ferrite about 80 HB, pearlite about 250 HB, mixed by fraction."""
    pro, pearl, _, _ = microstructure(c)
    return 80 * pro + 250 * pearl if c <= C_EUT else 250 * pearl + 650 * pro


if __name__ == "__main__":
    for c in (0.1, 0.2, 0.45, 0.76, 1.0):
        pro, pearl, fa, fc = microstructure(c)
        kind = "ferrite" if c <= C_EUT else "cementite"
        print(f"{c:.2f} %C: proeutectoid {kind} {pro*100:.1f} %, pearlite {pearl*100:.1f} %, overall {fc*100:.2f} % Fe3C, about {hardness_brinell(c):.0f} HB")
    # pearlite itself: lever rule at the eutectoid
    fc_p = (C_EUT - C_ALPHA) / (C_CEM - C_ALPHA)
    print(f"pearlite is {fc_p*100:.1f} % cementite plates in ferrite")
    assert abs(fc_p - 0.1105) < 1e-3
    # carbon balance check for every composition
    for c in (0.05, 0.3, 0.76, 1.2):
        pro, pearl, fa, fc = microstructure(c)
        assert abs(fa * C_ALPHA + fc * C_CEM - c) < 1e-12 and abs(pro + pearl - 1) < 1e-15
    for name, h in (("still air", 50), ("oil", 1500), ("water", 5000)):
        print(f"25 mm bar in {name} (h = {h}): 800 to 500 C in {t85(0.025, h):.1f} s")
    assert abs(t85(0.025, 50) / t85(0.025, 5000) - 100) < 1e-9
    print(f"Biot number of the 25 mm bar in water (k = 40): {5000*0.025/4/40:.2f} (above 0.1, so the core lags the surface)")
