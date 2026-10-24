"""Adiabatic flame temperature of methane-air against equivalence ratio, from NASA 7-coefficient polynomials (GRI-Mech 3.0 data),
with complete combustion when lean and water-gas shift equilibrium when rich (no dissociation)."""
import math

RU = 8.314462618
# species: (Tmid, high-T coefficients a1..a7, low-T coefficients a1..a7)
NASA = {
    "CH4": (1000, [0.074851495, 0.0133909467, -5.73285809e-06, 1.22292535e-09, -1.0181523e-13, -9468.34459, 18.437318],
            [5.14987613, -0.0136709788, 4.91800599e-05, -4.84743026e-08, 1.66693956e-11, -10246.6476, -4.64130376]),
    "O2": (1000, [3.28253784, 0.00148308754, -7.57966669e-07, 2.09470555e-10, -2.16717794e-14, -1088.45772, 5.45323129],
           [3.78245636, -0.00299673416, 9.84730201e-06, -9.68129509e-09, 3.24372837e-12, -1063.94356, 3.65767573]),
    "N2": (1000, [2.92664, 0.0014879768, -5.68476e-07, 1.0097038e-10, -6.753351e-15, -922.7977, 5.980528],
           [3.298677, 0.0014082404, -3.963222e-06, 5.641515e-09, -2.444854e-12, -1020.8999, 3.950372]),
    "CO2": (1000, [3.85746029, 0.00441437026, -2.21481404e-06, 5.23490188e-10, -4.72084164e-14, -48759.166, 2.27163806],
            [2.35677352, 0.00898459677, -7.12356269e-06, 2.45919022e-09, -1.43699548e-13, -48371.9697, 9.90105222]),
    "H2O": (1000, [3.03399249, 0.00217691804, -1.64072518e-07, -9.7041987e-11, 1.68200992e-14, -30004.2971, 4.9667701],
            [4.19864056, -0.0020364341, 6.52040211e-06, -5.48797062e-09, 1.77197817e-12, -30293.7267, -0.849032208]),
    "CO": (1000, [2.71518561, 0.00206252743, -9.98825771e-07, 2.30053008e-10, -2.03647716e-14, -14151.8724, 7.81868772],
           [3.57953347, -0.00061035368, 1.01681433e-06, 9.07005884e-10, -9.04424499e-13, -14344.086, 3.50840928]),
    "H2": (1000, [3.3372792, -4.94024731e-05, 4.99456778e-07, -1.79566394e-10, 2.00255376e-14, -950.158922, -3.20502331],
           [2.34433112, 0.00798052075, -1.9478151e-05, 2.01572094e-08, -7.37611761e-12, -917.935173, 0.683010238]),
}


def _a(sp, T):
    Tm, hi, lo = NASA[sp]
    return hi if T > Tm else lo


def h(sp, T):
    """Molar enthalpy (J/mol) including the enthalpy of formation."""
    a = _a(sp, T)
    return RU * T * (a[0] + a[1] * T / 2 + a[2] * T ** 2 / 3 + a[3] * T ** 3 / 4 + a[4] * T ** 4 / 5 + a[5] / T)


def s(sp, T):
    """Standard molar entropy (J/(mol K)) at 1 bar."""
    a = _a(sp, T)
    return RU * (a[0] * math.log(T) + a[1] * T + a[2] * T ** 2 / 2 + a[3] * T ** 3 / 3 + a[4] * T ** 4 / 4 + a[6])


def products(phi, T):
    """Moles of products per mole of CH4 burned with (2/phi)(O2 + 3.76 N2)."""
    o2 = 2 / phi
    if phi <= 1:
        return {"CO2": 1, "H2O": 2, "O2": o2 - 2, "N2": 3.76 * o2}
    # rich: CO2 + H2 <-> CO + H2O in equilibrium; atom balances leave one unknown, x = moles of CO
    g = h("CO", T) + h("H2O", T) - h("CO2", T) - h("H2", T) - T * (s("CO", T) + s("H2O", T) - s("CO2", T) - s("H2", T))
    K = math.exp(-g / (RU * T))
    O = 2 * o2                                  # O atoms: 2 CO2 + CO + H2O = O, carbon: CO2 + CO = 1, hydrogen: 2 H2O + 2 H2 = 4
    # with CO2 = 1 - x, CO = x, H2O = O - 2(1 - x) - x = O - 2 + x, H2 = 2 - H2O = 4 - O - x
    lo, hi = max(0.0, 2 - O + 1e-12), min(1.0, 4 - O)
    for _ in range(200):
        x = (lo + hi) / 2
        r = x * (O - 2 + x) - K * (1 - x) * (4 - O - x)
        if r > 0: hi = x
        else: lo = x
    return {"CO2": 1 - x, "CO": x, "H2O": O - 2 + x, "H2": 4 - O - x, "N2": 3.76 * o2}


def flame_T(phi, T0=298.15):
    H_react = h("CH4", T0) + 2 / phi * (h("O2", T0) + 3.76 * h("N2", T0))
    lo, hi = 300.0, 3500.0
    for _ in range(100):
        T = (lo + hi) / 2
        H_prod = sum(n * h(sp, T) for sp, n in products(phi, T).items())
        if H_prod > H_react: hi = T
        else: lo = T
    return T


if __name__ == "__main__":
    lhv = -(h("CO2", 298.15) + 2 * h("H2O", 298.15) - h("CH4", 298.15) - 2 * h("O2", 298.15)) / 0.016043 / 1e6
    print(f"lower heating value of methane: {lhv:.2f} MJ/kg")
    phis = [0.5 + 0.01 * i for i in range(101)]
    Ts = [flame_T(p) for p in phis]
    peak = phis[Ts.index(max(Ts))]
    for p in (0.6, 0.8, 1.0, 1.1, 1.2, 1.4):
        pr = products(p, flame_T(p))
        print(f"phi {p:.1f}: T_ad = {flame_T(p):.1f} K   products " + ", ".join(f"{k} {v:.3f}" for k, v in pr.items()))
    print(f"peak {max(Ts):.1f} K at phi = {peak:.2f}")
    assert 0.98 <= peak <= 1.06
    # atom balance check in a rich case
    pr = products(1.3, 2000.0); o2 = 2 / 1.3
    assert abs(pr["CO2"] + pr["CO"] - 1) < 1e-12 and abs(2 * pr["H2O"] + 2 * pr["H2"] - 4) < 1e-9
    assert abs(2 * pr["CO2"] + pr["CO"] + pr["H2O"] - 2 * o2) < 1e-9
