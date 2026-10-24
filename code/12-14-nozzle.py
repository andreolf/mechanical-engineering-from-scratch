"""Converging-diverging nozzle: the area-Mach relation, choked mass flow, and where a normal shock sits for a given back pressure."""
import math

K, R = 1.4, 287.05


def area_ratio(M, k=K):
    """A/A* for isentropic flow at Mach M."""
    return (1 / M) * ((2 / (k + 1)) * (1 + (k - 1) / 2 * M * M)) ** ((k + 1) / (2 * (k - 1)))


def mach_from_area(Ar, supersonic, k=K):
    lo, hi = (1.0, 50.0) if supersonic else (1e-9, 1.0)
    for _ in range(200):
        m = (lo + hi) / 2
        too_big = area_ratio(m, k) > Ar
        if supersonic: lo, hi = (lo, m) if too_big else (m, hi)
        else: lo, hi = (m, hi) if too_big else (lo, m)
    return (lo + hi) / 2


def p_ratio(M, k=K):
    return (1 + (k - 1) / 2 * M * M) ** (-k / (k - 1))


def shock(M1, k=K):
    M2 = math.sqrt((1 + (k - 1) / 2 * M1 ** 2) / (k * M1 ** 2 - (k - 1) / 2))
    p21 = 1 + 2 * k / (k + 1) * (M1 ** 2 - 1)
    p0r = p21 * p_ratio(M1, k) / p_ratio(M2, k)          # p02/p01 = (p2/p1) (p1/p01) / (p2/p02)
    return M2, p21, p0r


def nozzle(p0, T0, At, Ae, pb, k=K):
    """Mass flow and exit state for back pressure pb. Returns (mdot, regime, shock area or None, exit pressure)."""
    Are = Ae / At
    Me_sub, Me_sup = mach_from_area(Are, False), mach_from_area(Are, True)
    p_crit1 = p0 * p_ratio(Me_sub)                       # subsonic everywhere, just sonic at the throat
    M2s, p21, _ = shock(Me_sup); p_crit2 = p0 * p_ratio(Me_sup) * p21   # normal shock standing at the exit
    mdot_choked = At * p0 / math.sqrt(T0) * math.sqrt(k / R) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
    if pb >= p0: return 0.0, "no flow", None, pb
    if pb >= p_crit1:                                     # unchoked: subsonic throughout, exit pressure = pb
        Me = math.sqrt(2 / (k - 1) * ((p0 / pb) ** ((k - 1) / k) - 1))
        Astar = Ae / area_ratio(Me)
        return Astar / At * mdot_choked, "subsonic, not choked", None, pb
    if pb >= p_crit2:                                     # shock in the diverging part: find its area by bisection
        lo, hi = At * 1.0000001, Ae
        def exit_p(As):
            M1 = mach_from_area(As / At, True); _, _, p0r = shock(M1)
            Astar2 = At / p0r                             # throat area that the post-shock flow would need
            Me = mach_from_area(Ae / Astar2, False)
            return p0 * p0r * p_ratio(Me)
        for _ in range(100):
            m = (lo + hi) / 2
            lo, hi = (m, hi) if exit_p(m) > pb else (lo, m)
        return mdot_choked, "normal shock inside the nozzle", (lo + hi) / 2, pb
    return mdot_choked, "supersonic exit (over- or under-expanded outside)", None, p0 * p_ratio(Me_sup)


if __name__ == "__main__":
    p0, T0, At, Ae = 700e3, 300.0, 1.0e-4, 2.0e-4          # a 7 bar air supply, 1 cm^2 throat, exit twice as big
    Me_sub, Me_sup = mach_from_area(2.0, False), mach_from_area(2.0, True)
    print(f"A/A* = 2: subsonic M = {Me_sub:.5f}, supersonic M = {Me_sup:.5f}")
    assert abs(area_ratio(Me_sub) - 2) < 1e-9 and abs(area_ratio(Me_sup) - 2) < 1e-9
    flows = []
    for pb_bar in (6.9, 6.6, 6.5, 5.5, 4.0, 2.0, 0.6, 0.0):
        md, regime, As, pe = nozzle(p0, T0, At, Ae, pb_bar * 1e5)
        flows.append((pb_bar, md))
        print(f"pb = {pb_bar:4.1f} bar: mdot = {md*1000:.5f} g/s, {regime}" + (f", shock at A/At = {As/At:.4f}" if As else ""))
    choked = [md for pb, md in flows if pb <= 6.5]
    assert max(choked) - min(choked) < 1e-15                # choked flow doesn't depend on back pressure
    c = math.sqrt(K / R) * (2 / (K + 1)) ** ((K + 1) / (2 * (K - 1)))
    print(f"choked mass flow = {c:.6f} A* p0 / sqrt(T0) = {c*At*p0/math.sqrt(T0)*1000:.5f} g/s")
    print(f"critical back pressures: choking at {p0*p_ratio(Me_sub)/1e5:.4f} bar, shock at the exit at {p0*p_ratio(Me_sup)*shock(Me_sup)[1]/1e5:.4f} bar, design exit {p0*p_ratio(Me_sup)/1e5:.4f} bar")
