"""Van der Waals gas: solve the cubic for molar volume, compressibility, and the Maxwell equal-area construction for CO2."""
import numpy as np

R = 8.314462618
A, B = 0.3640, 4.267e-5          # CO2: Pa m^6/mol^2, m^3/mol


def p_vdw(v, T):
    return R * T / (v - B) - A / v ** 2


def volumes(p, T):
    """Real roots v > b of p v^3 - (p b + R T) v^2 + a v - a b = 0, sorted."""
    r = np.roots([p, -(p * B + R * T), A, -A * B])
    return sorted(x.real for x in r if abs(x.imag) < 1e-9 * abs(x) and x.real > B)


def area_mismatch(p, T):
    """Integral of (p_vdw - p) dv between the liquid and vapour roots; zero at the saturation pressure."""
    vl, _, vg = volumes(p, T)
    integral = R * T * np.log((vg - B) / (vl - B)) + A * (1 / vg - 1 / vl)
    return integral - p * (vg - vl)


def p_sat(T, lo, hi):
    for _ in range(100):                         # bisection on the equal-area condition
        mid = (lo + hi) / 2
        if area_mismatch(mid, T) > 0: lo = mid
        else: hi = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    Tc, pc, vc = 8 * A / (27 * R * B), A / (27 * B * B), 3 * B
    print(f"vdW critical point of CO2: {Tc:.2f} K, {pc/1e6:.3f} MPa, Zc = {pc*vc/(R*Tc):.4f} (real CO2: 304.13 K, 7.377 MPa, 0.274)")
    for p in (1e3, 1e5, 1e6, 5e6):
        v = volumes(p, 350.0)[-1]
        print(f"350 K, {p/1e6:8.3f} MPa: v = {v*1e3:.5f} L/mol, Z = {p*v/(R*350):.5f}")
    assert abs(p_vdw(volumes(5e6, 350.0)[-1], 350.0) - 5e6) < 1e-3
    assert abs(1e3 * volumes(1e3, 350.0)[-1] / (R * 350) - 1) < 1e-4                  # Z -> 1 at low pressure
    T = 280.0
    # bracket: the spinodal pressures (local min and max of the isotherm)
    vs = np.linspace(1.05 * B, 30 * B, 50000); ps = p_vdw(vs, T)
    turn = np.where(np.diff(np.sign(np.diff(ps))) != 0)[0] + 1        # local minimum, then local maximum
    lo, hi = max(ps[turn[0]], 1.0) * 1.0001, ps[turn[1]] * 0.9999
    ps_ = p_sat(T, lo, hi)
    vl, _, vg = volumes(ps_, T)
    print(f"Maxwell construction at {T:.0f} K: p_sat = {ps_/1e6:.4f} MPa (real CO2: 4.160 MPa); liquid {vl*1e6:.2f}, vapour {vg*1e6:.1f} cm^3/mol")
    assert abs(area_mismatch(ps_, T)) < 1e-6
