"""Stress-strength interference: probability of failure from two normal distributions, analytic against Monte Carlo, and why the same safety factor can hide very different risks."""
import math
import numpy as np


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def Phi_inv(p, lo=-12.0, hi=12.0):
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if Phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pf_normal(muR, sR, muS, sS):
    """Strength R and stress S independent normals: failure when R - S < 0."""
    z = (muR - muS) / math.hypot(sR, sS)
    return z, Phi(-z)


def pf_monte_carlo(muR, sR, muS, sS, n=2_000_000, seed=1):
    rng = np.random.default_rng(seed)
    R = rng.normal(muR, sR, n)
    S = rng.normal(muS, sS, n)
    p = np.mean(R < S)
    return p, math.sqrt(p * (1 - p) / n)


def strength_needed(pf, sR_cov, muS, sS):
    """Mean strength giving failure probability pf when strength scatter is a fixed fraction of its mean."""
    z = -Phi_inv(pf)
    lo, hi = muS, 20 * muS
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if (mid - muS) / math.hypot(sR_cov * mid, sS) < z:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


if __name__ == "__main__":
    # aluminium handlebar clamp: strength 300 MPa, 8% scatter; peak stress 180 MPa, 15% scatter
    muR, sR, muS, sS = 300.0, 24.0, 180.0, 27.0
    z, pf = pf_normal(muR, sR, muS, sS)
    pmc, se = pf_monte_carlo(muR, sR, muS, sS)
    print(f"central safety factor {muR/muS:.3f}, reliability index z = {z:.4f}")
    print(f"analytic P_f = {pf:.3e}, Monte Carlo {pmc:.3e} +- {se:.1e}")
    assert abs(pmc - pf) < 4 * se
    # same central safety factor, twice the scatter: the risk explodes
    z2, pf2 = pf_normal(muR, 2 * sR, muS, 2 * sS)
    p2, se2 = pf_monte_carlo(muR, 2 * sR, muS, 2 * sS, seed=2)
    print(f"double scatter, same factor: z = {z2:.4f}, P_f = {pf2:.4f} (Monte Carlo {p2:.4f})")
    assert abs(p2 - pf2) < 4 * se2 and pf2 > 50 * pf
    # design target: one failure in a million clamps
    m = strength_needed(1e-6, 0.08, muS, sS)
    z6, pf6 = pf_normal(m, 0.08 * m, muS, sS)
    print(f"strength for P_f = 1e-6: {m:.1f} MPa (safety factor {m/muS:.3f}, z = {z6:.4f})")
    assert abs(pf6 - 1e-6) < 1e-9
