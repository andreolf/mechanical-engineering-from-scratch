"""Rankine steam cycle with superheat and reheat, using small embedded steam tables (IAPWS-95 values) and interpolation."""
import bisect

# superheated steam: (T C, h kJ/kg, s kJ/(kg K))
SUP = {
    10.0: [(350, 2924.02, 5.9459), (400, 3097.45, 6.2141), (450, 3242.34, 6.4219), (500, 3375.13, 6.5995),
           (550, 3501.96, 6.7585), (600, 3625.76, 6.9045), (650, 3748.12, 7.0408)],
    2.0: [(250, 2903.24, 6.5475), (300, 3024.18, 6.7684), (350, 3137.65, 6.9583), (400, 3248.34, 7.1292),
          (450, 3358.22, 7.2866), (500, 3468.24, 7.4337), (550, 3578.97, 7.5725), (600, 3690.74, 7.7043), (650, 3803.75, 7.8302)],
}
# saturated water and steam at the 10 kPa condenser
COND = dict(T=45.81, hf=191.81, hg=2583.86, sf=0.6492, sg=8.1488, vf=0.0010103)
P_COND = 0.01   # MPa


def interp(rows, key, val, out):
    xs = [r[key] for r in rows]
    i = min(max(bisect.bisect_left(xs, val), 1), len(xs) - 1)
    a, b = rows[i - 1], rows[i]
    t = (val - a[key]) / (b[key] - a[key])
    return a[out] + t * (b[out] - a[out])


def h_at(p, T):
    return interp(SUP[p], 0, T, 1)


def s_at(p, T):
    return interp(SUP[p], 0, T, 2)


def expand_to_condenser(h_in, s_in, eta):
    x = (s_in - COND["sf"]) / (COND["sg"] - COND["sf"])
    hs = COND["hf"] + x * (COND["hg"] - COND["hf"])
    h = h_in - eta * (h_in - hs)
    return h, (h - COND["hf"]) / (COND["hg"] - COND["hf"])


def rankine(T_boiler=500, p_boiler=10.0, eta_t=1.0, reheat=None):
    wp = COND["vf"] * (p_boiler - P_COND) * 1000          # kJ/kg, v dp
    h2 = COND["hf"] + wp
    h3, s3 = h_at(p_boiler, T_boiler), s_at(p_boiler, T_boiler)
    q_in = h3 - h2
    if reheat:                                           # expand to 2 MPa, reheat to T
        p_r, T_r = reheat
        h4s = interp(SUP[p_r], 2, s3, 1)
        h4 = h3 - eta_t * (h3 - h4s)
        w_hp = h3 - h4
        h5, s5 = h_at(p_r, T_r), s_at(p_r, T_r)
        q_in += h5 - h4
        h6, x = expand_to_condenser(h5, s5, eta_t)
        wt = w_hp + h5 - h6
    else:
        h6, x = expand_to_condenser(h3, s3, eta_t)
        wt = h3 - h6
    q_out = h6 - COND["hf"]
    return dict(wp=wp, wt=wt, q_in=q_in, q_out=q_out, eta=(wt - wp) / q_in, x=x)


if __name__ == "__main__":
    for label, kw in (("ideal, 10 MPa 500 C", {}), ("turbine 85 %", dict(eta_t=0.85)),
                      ("reheat at 2 MPa to 500 C", dict(reheat=(2.0, 500))), ("reheat, turbines 85 %", dict(reheat=(2.0, 500), eta_t=0.85))):
        c = rankine(**kw)
        print(f"{label}: pump {c['wp']:.2f}, turbine {c['wt']:.1f}, heat in {c['q_in']:.1f}, out {c['q_out']:.1f} kJ/kg; "
              f"efficiency {c['eta']:.4f}, exit quality {c['x']:.4f}")
        assert abs(c['q_in'] - c['q_out'] - (c['wt'] - c['wp'])) < 1e-9          # energy balance closes
    carnot = 1 - (COND["T"] + 273.15) / (500 + 273.15)
    print(f"Carnot between 45.81 and 500 C: {carnot:.4f}")
    assert rankine()['eta'] < carnot
