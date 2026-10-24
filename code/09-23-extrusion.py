"""Extrusion: ideal work, Johnson's empirical die pressure and container friction, for hot aluminium and cold steel."""
import math
import numpy as np


def mean_flow_stress(K, n, eps):
    """Average of K e^n over 0..eps (strain hardening, cold work)."""
    return K * eps**n / (n + 1)


def ram_force(D0, Lb, R, sigma_f, m=1.0):
    """Die force by Johnson's formula p = sigma (0.8 + 1.5 ln R) plus container friction m k over the billet surface."""
    A0 = math.pi * D0**2 / 4
    p_die = sigma_f * (0.8 + 1.5 * math.log(R))
    F_die = p_die * A0
    F_fric = m * sigma_f / math.sqrt(3) * math.pi * D0 * Lb
    return F_die, F_fric


if __name__ == "__main__":
    # hot extrusion of a 6063 aluminium profile from a 100 mm billet, 300 mm long, at about 480 C
    D0, Lb, sig = 0.100, 0.300, 40e6
    A0 = math.pi * D0**2 / 4
    for R in (10, 40, 80):
        Fd, Ff = ram_force(D0, Lb, R, sig)
        print(f"R = {R:3d}: ideal pressure {sig*math.log(R)/1e6:.0f} MPa, Johnson {sig*(0.8+1.5*math.log(R))/1e6:.0f} MPa; die {Fd/1e6:.2f} MN + friction {Ff/1e6:.2f} MN = {(Fd+Ff)/1e6:.2f} MN")
    Fd, Ff = ram_force(D0, Lb, 40, sig)
    print(f"  profile area at R = 40: {A0/40*1e6:.0f} mm^2; the friction falls to zero as the billet is used up")
    # cold forward extrusion of a steel slug: K = 700 MPa, n = 0.2, R = 4
    K, n, R = 700e6, 0.2, 4.0
    eps = math.log(R)
    sbar = mean_flow_stress(K, n, eps)
    e = np.linspace(0, eps, 200001); s = K * e**n
    w = float(np.sum((s[1:] + s[:-1]) / 2 * np.diff(e)))
    print(f"cold steel R = 4: strain {eps:.3f}, mean flow stress {sbar/1e6:.1f} MPa, ideal work {w/1e6:.1f} MJ/m^3")
    assert abs(w - sbar * eps) / w < 1e-4
    p = sbar * (0.8 + 1.5 * eps)
    print(f"  Johnson die pressure {p/1e6:.0f} MPa ({p/(sbar*eps):.2f} x ideal)")
    assert 0.8 + 1.5 * eps > eps
