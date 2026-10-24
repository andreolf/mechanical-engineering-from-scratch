"""Air-standard Otto and Diesel cycles: state points, net work by integrating p dV, and the closed-form efficiencies."""
import numpy as np

CV, R = 0.718, 0.287
K = (CV + R) / CV


def otto_eff(r):
    return 1 - r ** (1 - K)


def diesel_eff(r, rc):
    return 1 - r ** (1 - K) * (rc ** K - 1) / (K * (rc - 1))


def trap(y, x):
    return float(np.sum((y[1:] + y[:-1]) / 2 * np.diff(x)))


def cycle(r, q_in=None, rc=None, T1=300.0, p1=100.0, n=4000):
    """Integrate p dV around an Otto (q_in given, kJ/kg) or Diesel (cutoff rc given) cycle per kg of air."""
    v1 = R * T1 / p1; v2 = v1 / r
    v = np.linspace(v1, v2, n); p_c = p1 * (v1 / v) ** K                     # 1-2 isentropic compression
    T2 = T1 * r ** (K - 1); p2 = p_c[-1]
    if rc is None:                                                            # Otto: heat at constant volume
        T3 = T2 + q_in / CV; p3 = p2 * T3 / T2; v3 = v2; w_heat = 0.0; q = q_in
    else:                                                                     # Diesel: heat at constant pressure
        v3 = rc * v2; T3 = T2 * rc; p3 = p2; w_heat = p2 * (v3 - v2); q = (CV + R) * (T3 - T2)
    ve = np.linspace(v3, v1, n); p_e = p3 * (v3 / ve) ** K                    # 3-4 isentropic expansion
    w = trap(p_c, v) + w_heat + trap(p_e, ve)
    return w, q, T3, p3


if __name__ == "__main__":
    print(f"k = {K:.4f}")
    for r in (8, 10, 12):
        w, q, T3, p3 = cycle(r, q_in=1200.0)
        print(f"Otto r = {r}: efficiency {otto_eff(r):.4f} (integrated {w/q:.4f}), peak {T3:.0f} K, {p3/1000:.2f} MPa")
        assert abs(w / q - otto_eff(r)) < 1e-5
    w, q, T3, p3 = cycle(18, rc=2.0)
    print(f"Diesel r = 18, rc = 2: efficiency {diesel_eff(18, 2):.4f} (integrated {w/q:.4f}), peak {T3:.0f} K, {p3/1000:.2f} MPa")
    assert abs(w / q - diesel_eff(18, 2)) < 1e-5
    assert diesel_eff(10, 2) < otto_eff(10)          # same r: Otto wins; Diesel wins by running higher r
    print(f"same r = 10: Otto {otto_eff(10):.4f}, Diesel (rc 2) {diesel_eff(10, 2):.4f}")
