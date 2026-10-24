"""Froude similarity: scale factors for a 1:50 spillway model, and why the Reynolds number can't match at the same time."""
import math

EXPONENTS = {"length": 1.0, "velocity": 0.5, "time": 0.5, "discharge": 2.5, "force": 3.0, "pressure": 1.0, "power": 3.5}


def scale(quantity, lam):
    """Prototype/model ratio for Froude similarity with the same fluid and gravity; lam = prototype/model length ratio."""
    return lam ** EXPONENTS[quantity]


if __name__ == "__main__":
    lam = 50.0
    for q in EXPONENTS:
        print(f"{q:9s}: prototype = model x {scale(q, lam):,.2f}")
    # a prototype spillway passing 1500 m^3/s, water 8 m/s, a 30 s surge
    Qp, Vp, tp = 1500.0, 8.0, 30.0
    Qm, Vm, tm = Qp / scale("discharge", lam), Vp / scale("velocity", lam), tp / scale("time", lam)
    print(f"model: {Qm*1000:.2f} L/s, {Vm:.4f} m/s, surge lasts {tm:.3f} s")
    g = 9.81; Lp = 10.0; Lm = Lp / lam
    Fr_p, Fr_m = Vp / math.sqrt(g * Lp), Vm / math.sqrt(g * Lm)
    assert abs(Fr_p - Fr_m) < 1e-12                                     # Froude matched
    assert abs(Vp / Vm - math.sqrt(lam)) < 1e-12                        # velocity scales with sqrt(length scale)
    nu = 1.0e-6
    Re_p, Re_m = Vp * Lp / nu, Vm * Lm / nu
    print(f"Froude number {Fr_p:.4f} in both; Reynolds {Re_p:.2e} prototype vs {Re_m:.2e} model (ratio {Re_p/Re_m:.1f} = lambda^1.5)")
    print(f"matching Re too would need a model fluid with nu = {nu/lam**1.5:.2e} m^2/s, which doesn't exist")
