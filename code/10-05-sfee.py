"""Steady-flow energy equation for nozzles, turbines, compressors and throttles with air as an ideal gas."""
import math

CP, R = 1005.0, 287.0
K = CP / (CP - R)


def sfee_power(mdot, h1, h2, V1=0.0, V2=0.0, z1=0.0, z2=0.0, Q=0.0):
    """Shaft power out (W) from Q - W = mdot [(h2 - h1) + (V2^2 - V1^2)/2 + g (z2 - z1)]."""
    return Q - mdot * ((h2 - h1) + (V2**2 - V1**2) / 2 + 9.81 * (z2 - z1))


def isentropic_T(T1, p1, p2):
    return T1 * (p2 / p1) ** ((K - 1) / K)


if __name__ == "__main__":
    # nozzle: air enters at 500 K, 300 kPa, 30 m/s; expands isentropically to 100 kPa
    T1, p1, V1 = 500.0, 300e3, 30.0
    T2 = isentropic_T(T1, p1, 100e3)
    V2 = math.sqrt(V1**2 + 2 * CP * (T1 - T2))
    print(f"nozzle: exit T = {T2:.2f} K, exit velocity {V2:.1f} m/s")
    assert abs(sfee_power(1.0, CP * T1, CP * T2, V1, V2)) < 1e-6       # no work, no heat: residual zero
    # turbine: 2 kg/s from 1200 K, 1 MPa to 100 kPa, isentropic
    T2t = isentropic_T(1200.0, 1e6, 100e3)
    Wt = sfee_power(2.0, CP * 1200, CP * T2t)
    print(f"turbine: exit {T2t:.1f} K, power {Wt/1e3:.1f} kW")
    # compressor: 2 kg/s from 300 K, 100 kPa to 1 MPa, isentropic (power is negative: absorbed)
    T2c = isentropic_T(300.0, 100e3, 1e6)
    Wc = sfee_power(2.0, CP * 300, CP * T2c)
    print(f"compressor: exit {T2c:.1f} K, power {Wc/1e3:.1f} kW")
    print(f"net from this ideal pair: {(Wt + Wc)/1e3:.1f} kW")
    # throttle valve: h2 = h1, so an ideal gas leaves at the same temperature
    assert sfee_power(1.0, CP * 400, CP * 400) == 0.0
    # 1 m of height vs 1 K of temperature for water flowing through a pump
    print(f"water: g x 1 m = {9.81:.2f} J/kg, c x 1 K = {4186:.0f} J/kg")
