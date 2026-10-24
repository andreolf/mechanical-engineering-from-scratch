"""Effectiveness-NTU: closed-form effectiveness for parallel and counterflow, checked against marching the two streams numerically, and against LMTD."""
import math


def eff_parallel(ntu, cr):
    return (1 - math.exp(-ntu * (1 + cr))) / (1 + cr)


def eff_counter(ntu, cr):
    if abs(1 - cr) < 1e-12:
        return ntu / (1 + ntu)
    e = math.exp(-ntu * (1 - cr))
    return (1 - e) / (1 - cr * e)


def march(Ch, Cc, UA, counter, n=4000):
    """Q from marching both streams with RK4, inlets 1 (hot) and 0 (cold). Counterflow shoots on the cold outlet."""
    def run(tc0, sign):
        f = lambda th, tc: (-(th - tc) / Ch, sign * (th - tc) / Cc)
        th, tc, dA = 1.0, tc0, UA / n
        for _ in range(n):
            a1, b1 = f(th, tc); a2, b2 = f(th + dA / 2 * a1, tc + dA / 2 * b1); a3, b3 = f(th + dA / 2 * a2, tc + dA / 2 * b2); a4, b4 = f(th + dA * a3, tc + dA * b3)
            th += dA / 6 * (a1 + 2 * a2 + 2 * a3 + a4); tc += dA / 6 * (b1 + 2 * b2 + 2 * b3 + b4)
        return th, tc
    if not counter:
        th, _ = run(0.0, +1)
    else:
        lo, hi = 0.0, 1.0
        for _ in range(55):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if run(mid, -1)[1] < 0 else (lo, mid)
        th, _ = run(0.5 * (lo + hi), -1)
    return Ch * (1 - th)


if __name__ == "__main__":
    worst = 0.0
    for Ch, Cc, UA in ((420, 418, 300), (1000, 250, 400), (200, 900, 1500), (500, 500, 800)):
        Cmin, Cmax = min(Ch, Cc), max(Ch, Cc)
        ntu, cr = UA / Cmin, Cmin / Cmax
        for counter, eff in ((False, eff_parallel), (True, eff_counter)):
            q_num, q_ntu = march(Ch, Cc, UA, counter), eff(ntu, cr) * Cmin
            worst = max(worst, abs(q_num - q_ntu) / q_ntu)
    print(f"closed-form effectiveness vs RK4 marching, 8 cases: worst relative error {worst:.1e}")
    assert worst < 1e-7
    # the oil cooler from 13.12: oil 110 C (C_h = 420 W/K), water 25 C (C_c = 418 W/K), UA = 300 W/K
    Ch, Cc, UA, Thi, Tci = 420.0, 418.0, 300.0, 110.0, 25.0
    ntu, cr = UA / Cc, Cc / Ch
    for name, eff in (("parallel", eff_parallel), ("counter", eff_counter)):
        e = eff(ntu, cr); Q = e * Cc * (Thi - Tci)
        tho, tco = Thi - Q / Ch, Tci + Q / Cc
        dT1, dT2 = (Thi - Tci, tho - tco) if name == "parallel" else (Thi - tco, tho - Tci)
        lm = (dT1 - dT2) / math.log(dT1 / dT2)
        print(f"{name}: NTU = {ntu:.4f}, Cr = {cr:.4f}, effectiveness {e:.5f}, Q = {Q:.3f} W; UA LMTD = {UA*lm:.3f} W")
        assert abs(Q - UA * lm) < 1e-6 * Q
    # diminishing returns: counterflow, Cr = 1
    for n_ in (0.5, 1, 2, 4, 8):
        print(f"  NTU {n_}: counterflow effectiveness (Cr = 1) {eff_counter(n_, 1.0):.4f}, parallel {eff_parallel(n_, 1.0):.4f}")
    assert eff_parallel(50, 1.0) < 0.5 + 1e-12 and eff_counter(50, 1.0) > 0.98
    # a condenser (Cr = 0): every arrangement gives 1 - exp(-NTU)
    assert abs(eff_counter(2, 0) - eff_parallel(2, 0)) < 1e-15 and abs(eff_counter(2, 0) - (1 - math.exp(-2))) < 1e-15
