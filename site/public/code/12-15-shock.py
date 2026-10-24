"""Normal shocks: the Rankine-Hugoniot jump relations, a conservation and entropy check, and the exact Sod shock tube."""
import math

K, R = 1.4, 287.05
CP = K * R / (K - 1)


def normal_shock(M1, k=K):
    M2 = math.sqrt((1 + (k - 1) / 2 * M1 ** 2) / (k * M1 ** 2 - (k - 1) / 2))
    p21 = 1 + 2 * k / (k + 1) * (M1 ** 2 - 1)
    r21 = (k + 1) * M1 ** 2 / ((k - 1) * M1 ** 2 + 2)
    T21 = p21 / r21
    return M2, p21, r21, T21


def entropy_jump(M1, k=K):
    _, p21, _, T21 = normal_shock(M1, k)
    return CP * math.log(T21) - R * math.log(p21)


def sod_exact(rhoL=1.0, pL=1.0, rhoR=0.125, pR=0.1, k=K):
    """Star-region pressure and velocity for a shock tube with gas at rest (Toro's exact Riemann solver, two-shock-or-rarefaction functions)."""
    aL, aR = math.sqrt(k * pL / rhoL), math.sqrt(k * pR / rhoR)
    def f(p, rho, pk, a):
        if p > pk:
            A, B = 2 / ((k + 1) * rho), (k - 1) / (k + 1) * pk
            return (p - pk) * math.sqrt(A / (p + B))
        return 2 * a / (k - 1) * ((p / pk) ** ((k - 1) / (2 * k)) - 1)
    lo, hi = 1e-8, 10 * max(pL, pR)
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m, rhoL, pL, aL) + f(m, rhoR, pR, aR) < 0 else (lo, m)
    p = (lo + hi) / 2
    u = 0.5 * (f(p, rhoR, pR, aR) - f(p, rhoL, pL, aL))
    g = (k - 1) / (k + 1)
    rho2 = rhoR * (p / pR + g) / (g * p / pR + 1)          # density behind the right-moving shock
    S = u * rho2 / (rho2 - rhoR)                             # shock speed from mass conservation
    return p, u, S, aR


if __name__ == "__main__":
    M1 = 2.0
    M2, p21, r21, T21 = normal_shock(M1)
    print(f"M1 = {M1}: M2 = {M2:.5f}, p2/p1 = {p21:.4f}, rho2/rho1 = {r21:.4f}, T2/T1 = {T21:.4f}")
    # conservation across the shock, per unit p1 and rho1 (shock frame)
    a1 = math.sqrt(K); u1 = M1 * a1; u2 = u1 / r21; a2 = math.sqrt(K * p21 / r21)
    mass = 1 * u1 - r21 * u2
    mom = (1 + u1 ** 2) - (p21 + r21 * u2 ** 2)
    h = lambda p, rho: K / (K - 1) * p / rho
    energy = (h(1, 1) + u1 ** 2 / 2) - (h(p21, r21) + u2 ** 2 / 2)
    print(f"residuals: mass {mass:.1e}, momentum {mom:.1e}, energy {energy:.1e}; M2 from u2/a2 = {u2/a2:.5f}")
    assert max(abs(mass), abs(mom), abs(energy)) < 1e-12 and abs(u2 / a2 - M2) < 1e-12
    for M in (1.0, 1.2, 1.5, 2.0, 3.0, 5.0):
        ds = entropy_jump(M)
        print(f"M1 = {M}: entropy rise {ds:9.4f} J/(kg K), stagnation pressure kept {math.exp(-ds/R)*100:6.2f} %")
        assert ds >= -1e-12                                       # entropy never falls across a shock
    print(f"an 'expansion shock' at M1 = 0.8 would need ds = {entropy_jump(0.8):.4f} J/(kg K) < 0: impossible")
    assert entropy_jump(0.8) < 0
    # Sod's shock tube: the shock it launches obeys the same relations
    p, u, S, aR = sod_exact()
    Ms = S / aR
    print(f"Sod: p* = {p:.5f}, u* = {u:.5f}, shock speed {S:.5f}, shock Mach {Ms:.5f}; p*/pR = {p/0.1:.5f} vs normal-shock {normal_shock(Ms)[1]:.5f}")
    assert abs(p / 0.1 - normal_shock(Ms)[1]) < 1e-9
