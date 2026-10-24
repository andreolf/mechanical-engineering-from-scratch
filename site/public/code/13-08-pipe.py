"""Forced convection in pipes: the laminar limits (3.66 and 4.36) derived numerically, then Dittus-Boelter and Gnielinski with their validity ranges."""
import math


def rk4(f, y, x0, x1, n):
    h = (x1 - x0) / n; x = x0
    for _ in range(n):
        k1 = f(x, y); k2 = f(x + h / 2, [a + h / 2 * b for a, b in zip(y, k1)]); k3 = f(x + h / 2, [a + h / 2 * b for a, b in zip(y, k2)]); k4 = f(x + h, [a + h * b for a, b in zip(y, k3)])
        y = [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4)]; x += h
    return y


def nu_constant_wall_temperature(n=4000):
    """Fully developed Graetz mode: (1/r)(r phi')' + lam^2 (1 - r^2) phi = 0, phi'(0) = 0, phi(1) = 0. Nu = lam^2 / 2 (based on diameter)."""
    def phi_at_wall(lam2):
        r0 = 1e-6
        f = lambda r, y: [y[1], -y[1] / r - lam2 * (1 - r * r) * y[0]]
        return rk4(f, [1.0, -lam2 * r0 / 2], r0, 1.0, n)[0]
    a, b = 5.0, 9.0
    while b - a > 1e-12:
        c = 0.5 * (a + b)
        a, b = (c, b) if (phi_at_wall(a) > 0) == (phi_at_wall(c) > 0) else (a, c)
    return 0.5 * (a + b) / 2


def nu_constant_heat_flux(n=200000):
    """Constant flux, fully developed: (1/r)(r T')' = C u(r) with u = 2(1 - r^2) and r the radius over r_w.
    Take C = 1: then r T' = 2 (r^2/2 - r^4/4), so T'(1) = 1/2. Integrate T(r) and its bulk (velocity-weighted) mean numerically.
    Nu = h D / k = 2 T'(1) / (Tw - Tm)."""
    dr = 1.0 / n
    rs = [(i + 0.5) * dr for i in range(n)]
    dT = [2 * (r * r / 2 - r ** 4 / 4) / r for r in rs]
    T, acc = [], 0.0
    for r, g in zip(rs, dT):
        T.append(acc + g * dr / 2); acc += g * dr                     # T at the cell centre, from T(0) = 0
    Tw = acc
    Tm = sum(2 * (1 - r * r) * t * r for r, t in zip(rs, T)) / sum(2 * (1 - r * r) * r for r in rs)
    return 2 * 0.5 / (Tw - Tm)


def dittus_boelter(Re, Pr, heating=True):
    ok = Re >= 1e4 and 0.6 <= Pr <= 160
    return 0.023 * Re ** 0.8 * Pr ** (0.4 if heating else 0.3), ok


def gnielinski(Re, Pr):
    f = (0.790 * math.log(Re) - 1.64) ** -2
    ok = 3000 <= Re <= 5e6 and 0.5 <= Pr <= 2000
    return (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f / 8) * (Pr ** (2 / 3) - 1)), ok


if __name__ == "__main__":
    a = nu_constant_wall_temperature()
    b = nu_constant_heat_flux()
    print(f"laminar fully developed: Nu = {a:.4f} (constant wall temperature), {b:.4f} (constant flux; exact 48/11 = {48/11:.4f})")
    assert abs(a - 3.6568) < 1e-3 and abs(b - 48 / 11) < 1e-3
    # water at 40 C heated in a 10 mm tube at 1 m/s (an e-bike motor coolant loop)
    nu, k, Pr, D, U = 0.658e-6, 0.631, 4.32, 0.010, 1.0
    Re = U * D / nu
    Nd, okd = dittus_boelter(Re, Pr)
    Ng, okg = gnielinski(Re, Pr)
    print(f"water: Re = {Re:.0f}; Dittus-Boelter Nu = {Nd:.2f} (valid: {okd}), h = {Nd*k/D:.0f}; Gnielinski Nu = {Ng:.2f} (valid: {okg}), h = {Ng*k/D:.0f}")
    assert okd and okg and abs(Nd - Ng) < 0.1 * Ng
    # in the transition range Dittus-Boelter is outside its range and overshoots Gnielinski
    Re2 = 4000
    Nd2, okd2 = dittus_boelter(Re2, Pr); Ng2, okg2 = gnielinski(Re2, Pr)
    print(f"Re = 4000: Dittus-Boelter {Nd2:.2f} (valid: {okd2}), Gnielinski {Ng2:.2f} (valid: {okg2}); DB is {100*(Nd2/Ng2-1):.0f}% high")
    assert not okd2 and okg2 and Nd2 > 1.15 * Ng2
