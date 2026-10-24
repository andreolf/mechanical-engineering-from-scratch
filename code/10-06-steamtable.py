"""Steam tables in code: a saturation table for water (values from IAPWS-95), interpolation that respects the physics, and two-phase mixtures by quality."""
import math

# T (C), p_sat (kPa), v_f, v_g (m^3/kg), h_f, h_g (kJ/kg), s_f, s_g (kJ/(kg K))
SAT = [
    (10, 1.2282, 0.001000, 106.3032, 42.02, 2519.21, 0.1511, 8.8998),
    (20, 2.3393, 0.001002, 57.7567, 83.91, 2537.43, 0.2965, 8.6660),
    (30, 4.2470, 0.001004, 32.8783, 125.73, 2555.55, 0.4368, 8.4520),
    (40, 7.3849, 0.001008, 19.5151, 167.53, 2573.51, 0.5724, 8.2555),
    (50, 12.3519, 0.001012, 12.0269, 209.34, 2591.29, 0.7038, 8.0748),
    (60, 19.9464, 0.001017, 7.6672, 251.18, 2608.83, 0.8313, 7.9081),
    (70, 31.2009, 0.001023, 5.0395, 293.07, 2626.10, 0.9551, 7.7540),
    (80, 47.4145, 0.001029, 3.4052, 335.01, 2643.02, 1.0756, 7.6111),
    (90, 70.1818, 0.001036, 2.3591, 377.04, 2659.53, 1.1929, 7.4781),
    (100, 101.4180, 0.001043, 1.6718, 419.17, 2675.57, 1.3072, 7.3541),
    (120, 198.6744, 0.001060, 0.8912, 503.81, 2705.93, 1.5279, 7.1291),
    (140, 361.5391, 0.001080, 0.5085, 589.16, 2733.44, 1.7392, 6.9293),
    (160, 618.2346, 0.001102, 0.3068, 675.47, 2757.44, 1.9426, 6.7491),
    (180, 1002.8105, 0.001127, 0.1938, 763.05, 2777.21, 2.1392, 6.5840),
    (200, 1554.9279, 0.001157, 0.1272, 852.27, 2792.01, 2.3305, 6.4302),
    (250, 3976.1749, 0.001252, 0.0501, 1085.77, 2800.93, 2.7935, 6.0721),
    (300, 8587.9049, 0.001404, 0.0217, 1345.01, 2749.64, 3.2552, 5.7059),
]
COLS = ["T", "p", "vf", "vg", "hf", "hg", "sf", "sg"]
LOGCOLS = {"p", "vg"}          # these vary exponentially: interpolate ln(value) against 1/T


def sat(T):
    """Saturation properties at T (C) by interpolation between table rows."""
    for lo, hi in zip(SAT[:-1], SAT[1:]):
        if lo[0] <= T <= hi[0]:
            out = {}
            for i, c in enumerate(COLS):
                if c in LOGCOLS:
                    x0, x1, x = 1 / (lo[0] + 273.15), 1 / (hi[0] + 273.15), 1 / (T + 273.15)
                    out[c] = math.exp(math.log(lo[i]) + (x - x0) / (x1 - x0) * (math.log(hi[i]) - math.log(lo[i])))
                else:
                    out[c] = lo[i] + (T - lo[0]) / (hi[0] - lo[0]) * (hi[i] - lo[i])
            return out
    raise ValueError("temperature outside the table")


def mixture(T, x):
    s = sat(T)
    return {c: s[c + "f"] + x * (s[c + "g"] - s[c + "f"]) for c in ("v", "h", "s")}


def quality_from(T, prop, value):
    s = sat(T)
    return (value - s[prop + "f"]) / (s[prop + "g"] - s[prop + "f"])


if __name__ == "__main__":
    # interpolation reproduces the tabulated rows exactly...
    for row in SAT[1:-1]:
        s = sat(row[0])
        assert all(abs(s[c] - row[i]) < 1e-9 * max(1, abs(row[i])) for i, c in enumerate(COLS))
    # ...and matches IAPWS-95 at temperatures between rows
    ref = {25: (3.16993, 104.829, 2546.505, 43.3373), 45: (9.59500, 188.435, 2582.426, 15.2521), 150: (476.165, 632.179, 2745.925, 0.392453)}
    for T, (p, hf, hg, vg) in ref.items():
        s = sat(T)
        print(f"{T} C: p = {s['p']:.4f} kPa ({p}), hf = {s['hf']:.2f} ({hf}), hg = {s['hg']:.2f} ({hg}), vg = {s['vg']:.4f} ({vg})")
        assert abs(s["p"] / p - 1) < 0.005 and abs(s["hf"] - hf) < 0.3 and abs(s["vg"] / vg - 1) < 0.01
    m = mixture(100, 0.9)
    print(f"wet steam at 100 C, x = 0.9: v = {m['v']:.4f} m^3/kg, h = {m['h']:.2f} kJ/kg, s = {m['s']:.4f} kJ/(kg K)")
    x = quality_from(100, "h", m["h"])
    assert abs(x - 0.9) < 1e-12
    print(f"latent heat at 100 C: {sat(100)['hg'] - sat(100)['hf']:.2f} kJ/kg")
