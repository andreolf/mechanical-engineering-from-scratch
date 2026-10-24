"""Chemical equilibrium by Gibbs-energy minimisation: dissociation of CO2 into CO and O2 at 1 atm, checked against the Kp method."""
import math

RU = 8.314462618
P0 = 1e5
NASA = {
    "CO2": (1000, [3.85746029, 0.00441437026, -2.21481404e-06, 5.23490188e-10, -4.72084164e-14, -48759.166, 2.27163806],
            [2.35677352, 0.00898459677, -7.12356269e-06, 2.45919022e-09, -1.43699548e-13, -48371.9697, 9.90105222]),
    "CO": (1000, [2.71518561, 0.00206252743, -9.98825771e-07, 2.30053008e-10, -2.03647716e-14, -14151.8724, 7.81868772],
           [3.57953347, -0.00061035368, 1.01681433e-06, 9.07005884e-10, -9.04424499e-13, -14344.086, 3.50840928]),
    "O2": (1000, [3.28253784, 0.00148308754, -7.57966669e-07, 2.09470555e-10, -2.16717794e-14, -1088.45772, 5.45323129],
           [3.78245636, -0.00299673416, 9.84730201e-06, -9.68129509e-09, 3.24372837e-12, -1063.94356, 3.65767573]),
}


def g0(sp, T):
    """Standard molar Gibbs energy g = h - T s (J/mol) at 1 bar, from NASA polynomials."""
    Tm, hi, lo = NASA[sp]
    a = hi if T > Tm else lo
    h = RU * T * (a[0] + a[1] * T / 2 + a[2] * T ** 2 / 3 + a[3] * T ** 3 / 4 + a[4] * T ** 4 / 5 + a[5] / T)
    s = RU * (a[0] * math.log(T) + a[1] * T + a[2] * T ** 2 / 2 + a[3] * T ** 3 / 3 + a[4] * T ** 4 / 4 + a[6])
    return h - T * s


def G(xi, T, p):
    """Total Gibbs energy of 1 mol CO2 dissociated to extent xi: (1-xi) CO2 + xi CO + xi/2 O2."""
    n = {"CO2": 1 - xi, "CO": xi, "O2": xi / 2}
    N = sum(n.values())
    return sum(ni * (g0(sp, T) + RU * T * math.log(ni / N * p / P0)) for sp, ni in n.items() if ni > 0)


def minimise(T, p=101325.0):
    a, b = 1e-12, 1 - 1e-12                 # golden-section search: G is convex in xi
    r = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        c, d = b - r * (b - a), a + r * (b - a)
        if G(c, T, p) < G(d, T, p): b = d
        else: a = c
    return (a + b) / 2


def kp_solution(T, p=101325.0):
    dG = g0("CO", T) + 0.5 * g0("O2", T) - g0("CO2", T)
    Kp = math.exp(-dG / (RU * T))
    lo, hi = 1e-15, 1 - 1e-15                 # Kp = xi (xi/2)^0.5 / (1 - xi) * (p/P0 / (1 + xi/2))^0.5
    for _ in range(200):
        x = (lo + hi) / 2
        if x * math.sqrt(x / 2) / (1 - x) * math.sqrt(p / P0 / (1 + x / 2)) > Kp: hi = x
        else: lo = x
    return x, Kp


if __name__ == "__main__":
    for T in (1500, 2000, 2500, 3000, 3500):
        xi = minimise(T); xk, Kp = kp_solution(T)
        print(f"{T} K: dissociated fraction {xi:.5f} (Kp method {xk:.5f}, Kp = {Kp:.4e}); mole fraction CO {xi/(1+xi/2):.4f}")
        assert abs(xi - xk) < 1e-6
    xi10 = minimise(2500, 10 * 101325.0)
    print(f"2500 K at 10 atm: {xi10:.5f}; higher pressure suppresses dissociation (Le Chatelier)")
    assert xi10 < minimise(2500)
