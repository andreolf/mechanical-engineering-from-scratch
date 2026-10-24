"""Brayton cycle: ideal efficiency, and a real cycle with component efficiencies, net work and the best pressure ratio."""
CP, R = 1.005, 0.287
K = CP / (CP - R)


def ideal_eff(rp):
    return 1 - rp ** ((1 - K) / K)


def real_cycle(rp, T1=300.0, T3=1400.0, eta_c=0.85, eta_t=0.90):
    e = rp ** ((K - 1) / K)
    T2 = T1 + T1 * (e - 1) / eta_c
    T4 = T3 - eta_t * (T3 - T3 / e)
    wc, wt, q = CP * (T2 - T1), CP * (T3 - T4), CP * (T3 - T2)
    return dict(T2=T2, T4=T4, wc=wc, wt=wt, w=wt - wc, q=q, eta=(wt - wc) / q, bwr=wc / wt)


if __name__ == "__main__":
    c = real_cycle(8)
    print(f"ideal rp 8: {ideal_eff(8):.4f}")
    print(f"real rp 8: T2 {c['T2']:.2f} K, T4 {c['T4']:.2f} K, net {c['w']:.2f} kJ/kg, efficiency {c['eta']:.4f}, back-work ratio {c['bwr']:.3f}")
    assert abs(real_cycle(8, eta_c=1, eta_t=1)['eta'] - ideal_eff(8)) < 1e-12        # perfect parts give the ideal
    assert abs(c['q'] - c['w'] - CP * (c['T4'] - 300.0)) < 1e-9                      # energy balance closes
    rps = [1.5 + 0.1 * i for i in range(600)]
    best_w = max(rps, key=lambda r: real_cycle(r)['w']); best_e = max(rps, key=lambda r: real_cycle(r)['eta'])
    print(f"max net work at rp {best_w:.1f} ({real_cycle(best_w)['w']:.1f} kJ/kg); max efficiency at rp {best_e:.1f} ({real_cycle(best_e)['eta']:.4f})")
    print(f"ideal cycle, rp for max work: (T3/T1)^(k/(2(k-1))) = {(1400/300)**(K/(2*(K-1))):.2f}")
