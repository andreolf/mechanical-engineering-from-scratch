"""Vapour-compression heat pump with propane (R290): COP from an embedded saturation table, compared with the Carnot COP."""
import math

# saturated propane (CoolProp reference values): T C, p kPa, hf, hg kJ/kg, sf, sg kJ/(kg K), cp of saturated vapour
SAT = [(-25, 203.4, 139.60, 546.28, 0.7701, 2.4090, 1.546), (-20, 244.5, 151.36, 552.13, 0.8168, 2.3999, 1.580),
       (-15, 291.6, 163.28, 557.93, 0.8630, 2.3918, 1.616), (-10, 345.3, 175.35, 563.65, 0.9090, 2.3846, 1.655),
       (-5, 406.0, 187.59, 569.30, 0.9546, 2.3781, 1.695), (0, 474.5, 200.00, 574.87, 1.0000, 2.3724, 1.739),
       (5, 551.1, 212.60, 580.33, 1.0452, 2.3672, 1.785), (10, 636.6, 225.40, 585.67, 1.0902, 2.3626, 1.835),
       (15, 731.5, 238.40, 590.89, 1.1351, 2.3583, 1.890), (20, 836.5, 251.64, 595.95, 1.1799, 2.3544, 1.949),
       (25, 952.1, 265.11, 600.84, 1.2247, 2.3507, 2.015), (30, 1079.0, 278.83, 605.54, 1.2695, 2.3471, 2.088),
       (35, 1217.9, 292.84, 610.01, 1.3143, 2.3436, 2.170), (40, 1369.4, 307.15, 614.21, 1.3594, 2.3399, 2.263),
       (45, 1534.3, 321.79, 618.12, 1.4046, 2.3360, 2.371), (50, 1713.3, 336.80, 621.66, 1.4502, 2.3317, 2.499),
       (55, 1907.2, 352.23, 624.77, 1.4962, 2.3268, 2.652), (60, 2116.8, 368.14, 627.36, 1.5429, 2.3210, 2.841),
       (65, 2343.0, 384.60, 629.29, 1.5903, 2.3139, 3.086)]


def sat(T):
    """Linearly interpolated saturation row at T (C)."""
    i = min(max(int((T + 25) // 5), 0), len(SAT) - 2)
    a, b = SAT[i], SAT[i + 1]; t = (T - a[0]) / 5
    return [a[j] + t * (b[j] - a[j]) for j in range(7)]


def cycle(Te, Tc, eta_c=0.70):
    """Heating COP for evaporation at Te and condensation at Tc (C). Compressor exit modelled as superheated vapour
    with constant cp along the condensing isobar: s = sg(Tc) + cp ln(T/Tc)."""
    _, pe, _, h1, _, s1, _ = sat(Te)
    _, pc, h3, hg, _, sg, cp = sat(Tc)
    T2s = (Tc + 273.15) * math.exp(max(s1 - sg, 0) / cp)
    h2s = hg + cp * (T2s - Tc - 273.15)
    h2 = h1 + (h2s - h1) / eta_c
    return dict(h1=h1, h2s=h2s, h2=h2, h3=h3, T2s=T2s - 273.15, rp=pc / pe, cop=(h2 - h3) / (h2 - h1), cop_s=(h2s - h3) / (h2s - h1))


def carnot_cop(Te, Tc):
    return (Tc + 273.15) / (Tc - Te)


if __name__ == "__main__":
    c = cycle(-5, 40)
    print(f"evaporate -5 C, condense 40 C: h1 {c['h1']:.2f}, h2s {c['h2s']:.2f} (T2s {c['T2s']:.2f} C), h3 {c['h3']:.2f} kJ/kg")
    print(f"  pressure ratio {c['rp']:.2f}; COP isentropic {c['cop_s']:.3f}, with eta_c 0.70 {c['cop']:.3f}; Carnot {carnot_cop(-5, 40):.3f}")
    # CoolProp reference for the same cycle: h2s 626.28, COP 4.221
    assert abs(c['h2s'] - 626.28) < 0.2 and abs(c['cop'] - 4.221) < 0.01
    print("outdoor C | COP floor heating (35 C) | COP radiators (55 C)")
    for To in (-15, -5, 2, 7, 15):
        a, b = cycle(To - 5, 40)['cop'], cycle(To - 5, 60)['cop']
        assert a < carnot_cop(To - 5, 40) and b < carnot_cop(To - 5, 60)
        print(f"  {To:4d} | {a:.2f} | {b:.2f}")
