"""Rolling bearing life: L10 = (C/P)^a, equivalent load, life at other reliabilities from a Weibull model, and a Monte Carlo fleet of bearings."""
import math
import numpy as np

B_WEIBULL = 1.5  # typical Weibull slope for ball bearing fatigue


def L10(C, P, roller=False):
    """Basic rating life in millions of revolutions."""
    a = 10 / 3 if roller else 3
    return (C / P) ** a


def equivalent_load(Fr, Fa, X=1.0, Y=0.0):
    return X * Fr + Y * Fa


def life_at_reliability(L10_life, R, b=B_WEIBULL):
    """Two-parameter Weibull through the L10 point: fraction surviving is exp(-(L/eta)^b)."""
    return L10_life * (math.log(1 / R) / math.log(1 / 0.9)) ** (1 / b)


def required_C(P, life_mrev, roller=False):
    a = 10 / 3 if roller else 3
    return P * life_mrev ** (1 / a)


if __name__ == "__main__":
    C = 8060.0  # deep groove ball bearing 6202, dynamic rating (N)
    P = 1500.0
    L = L10(C, P)
    wheel = math.pi * 0.45  # scooter wheel circumference, m
    print(f"L10 = {L:.1f} million revolutions = {L*1e6*wheel/1000:,.0f} km")
    assert abs(L10(C, 2 * P) - L / 8) < 1e-9  # doubling the load cuts ball bearing life 8 times
    assert abs(L10(C, 2 * P, True) / L10(C, P, True) - 2 ** (-10 / 3)) < 1e-12
    # combined load with catalogue factors
    Pc = equivalent_load(1200, 400, X=0.56, Y=1.8)
    print(f"Fr 1200 N + Fa 400 N -> P = {Pc:.0f} N, L10 = {L10(C, Pc):.1f} Mrev")
    # reliability: 95% and 99% lives, and the median
    for R in (0.95, 0.99, 0.5):
        print(f"life at {100*R:.0f}% reliability: {life_at_reliability(L, R):.1f} Mrev ({life_at_reliability(L, R)/L:.3f} x L10)")
    # Monte Carlo fleet: Weibull lives scaled so 10% fail before L10
    eta = L / (math.log(1 / 0.9)) ** (1 / B_WEIBULL)
    rng = np.random.default_rng(5)
    lives = eta * rng.weibull(B_WEIBULL, 200_000)
    frac = np.mean(lives < L)
    print(f"fleet of 200000: {100*frac:.2f}% fail before L10, median life {np.median(lives)/L:.3f} x L10")
    assert abs(frac - 0.10) < 0.003
    assert abs(np.median(lives) / life_at_reliability(L, 0.5) - 1) < 0.01
    # selection: required rating for 20000 km of scooter riding at 1500 N
    need = required_C(P, 20000e3 / wheel / 1e6)
    print(f"for 20000 km: C >= {need:.0f} N")
