"""Heat exchangers by LMTD: march the two streams along the exchanger numerically and confirm Q = U A LMTD, for parallel flow and counterflow."""
import math


def lmtd(dT1, dT2):
    return dT1 if abs(dT1 - dT2) < 1e-12 else (dT1 - dT2) / math.log(dT1 / dT2)


def march_parallel(Th_in, Tc_in, Ch, Cc, UA, n=20000):
    """Both streams enter at x = 0. dTh = -U dA (Th - Tc)/Ch, dTc = +U dA (Th - Tc)/Cc. RK4 along the area."""
    f = lambda th, tc: (-(th - tc) / Ch, (th - tc) / Cc)
    th, tc, dA = Th_in, Tc_in, UA / n
    for _ in range(n):
        a1, b1 = f(th, tc); a2, b2 = f(th + dA / 2 * a1, tc + dA / 2 * b1); a3, b3 = f(th + dA / 2 * a2, tc + dA / 2 * b2); a4, b4 = f(th + dA * a3, tc + dA * b3)
        th += dA / 6 * (a1 + 2 * a2 + 2 * a3 + a4); tc += dA / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
    return th, tc


def march_counter(Th_in, Tc_in, Ch, Cc, UA, n=2000):
    """Cold enters at the far end. Shoot on the unknown cold outlet temperature at x = 0 so the cold stream arrives at Tc_in at x = L."""
    def cold_at_end(tc_out):
        f = lambda th, tc: (-(th - tc) / Ch, -(th - tc) / Cc)   # cold flows the other way, so it falls in +x
        th, tc, dA = Th_in, tc_out, UA / n
        for _ in range(n):
            a1, b1 = f(th, tc); a2, b2 = f(th + dA / 2 * a1, tc + dA / 2 * b1); a3, b3 = f(th + dA / 2 * a2, tc + dA / 2 * b2); a4, b4 = f(th + dA * a3, tc + dA * b3)
            th += dA / 6 * (a1 + 2 * a2 + 2 * a3 + a4); tc += dA / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        return th, tc
    lo, hi = Tc_in, Th_in
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if cold_at_end(mid)[1] < Tc_in else (lo, mid)   # arriving too cold: the guess was too low
    tc_out = 0.5 * (lo + hi)
    return cold_at_end(tc_out)[0], tc_out


if __name__ == "__main__":
    # an oil cooler: engine oil 110 -> ? C (C_h = 0.2 kg/s x 2100 = 420 W/K) cooled by water at 25 C (C_c = 0.1 kg/s x 4180 = 418 W/K), UA = 300 W/K
    Th_in, Tc_in, Ch, Cc, UA = 110.0, 25.0, 420.0, 418.0, 300.0
    for name, fn in (("parallel", march_parallel), ("counter", march_counter)):
        th, tc = fn(Th_in, Tc_in, Ch, Cc, UA)
        Q = Ch * (Th_in - th)
        dT1, dT2 = (Th_in - Tc_in, th - tc) if name == "parallel" else (Th_in - tc, th - Tc_in)
        print(f"{name}: oil out {th:.4f} C, water out {tc:.4f} C, Q = {Q:.3f} W; U A LMTD = {UA*lmtd(dT1, dT2):.3f} W (LMTD {lmtd(dT1, dT2):.4f} K)")
        assert abs(Q - Cc * (tc - Tc_in)) < 1e-6 * Q and abs(Q - UA * lmtd(dT1, dT2)) < 1e-5 * Q
    # area for a fixed duty: cool the oil to 80 C (Q = 12600 W)
    Q = Ch * 30; tco = Tc_in + Q / Cc
    UA_par = Q / lmtd(Th_in - Tc_in, 80 - tco)
    UA_cnt = Q / lmtd(Th_in - tco, 80 - Tc_in)
    print(f"duty 12.6 kW: water leaves at {tco:.4f} C; UA needed {UA_par:.2f} W/K parallel, {UA_cnt:.2f} W/K counter ({100*(1-UA_cnt/UA_par):.1f}% less area)")
    assert UA_cnt < UA_par
    th, _ = march_counter(Th_in, Tc_in, Ch, Cc, UA_cnt)
    assert abs(th - 80) < 1e-4
