"""Psychrometrics: humidity ratio, dew point and enthalpy of moist air, Bali against Zurich, and the water an air conditioner condenses."""
import math

A_, B_, C_ = 610.94, 17.625, 243.04       # Magnus formula (Alduchov and Eskridge), Pa and C


def p_sat(T):
    return A_ * math.exp(B_ * T / (T + C_))


def dew_point(T, RH):
    g = math.log(RH * p_sat(T) / A_)          # exact inverse of the Magnus formula
    return C_ * g / (B_ - g)


def humidity_ratio(T, RH, p):
    pv = RH * p_sat(T)
    return 0.622 * pv / (p - pv)


def enthalpy(T, w):
    """kJ per kg of dry air, relative to dry air and liquid water at 0 C."""
    return 1.006 * T + w * (2501 + 1.86 * T)


if __name__ == "__main__":
    places = {"Bali, Denpasar (sea level, 101.3 kPa), afternoon": (31.0, 0.75, 101.3e3),
              "Zurich (408 m, 96.6 kPa), July afternoon": (25.0, 0.50, 96.6e3),
              "Zurich, January morning": (0.0, 0.85, 96.6e3)}
    for name, (T, RH, p) in places.items():
        w = humidity_ratio(T, RH, p)
        print(f"{name}: {T} C, RH {RH:.0%}: w = {w*1000:.2f} g/kg, dew point {dew_point(T, RH):.2f} C, h = {enthalpy(T, w):.2f} kJ/kg")
    for T in (-10, 0, 15, 31, 45):
        assert abs(dew_point(T, 1.0) - T) < 1e-9          # at saturation the dew point is the air temperature
    # air conditioning in Bali: 31 C 75 % -> 24 C 50 %: cool to the target's dew point, condense, reheat
    p = 101.3e3
    w1, w2 = humidity_ratio(31, 0.75, p), humidity_ratio(24, 0.50, p)
    Td = dew_point(24, 0.50)
    h1, h_cold, h2 = enthalpy(31, w1), enthalpy(Td, w2), enthalpy(24, w2)
    water = w1 - w2; q_cool = h1 - h_cold - water * 4.186 * Td
    print(f"AC: cool to {Td:.2f} C, condense {water*1000:.2f} g of water per kg of air; cooling {q_cool:.2f} kJ/kg, reheat {h2-h_cold:.2f} kJ/kg")
    print(f"  sensible part only (31 -> 24 C dry): {1.006*7:.2f} kJ/kg, so most of the load is the humidity")
