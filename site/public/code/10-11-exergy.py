"""Exergy: flow exergy of water streams, a heat exchanger's exergy balance, and the Gouy-Stodola theorem X_dest = T0 S_gen."""
import math

C = 4.186         # kJ/(kg K)
T0 = 288.15       # dead state: 15 C


def flow_exergy(T):
    """Specific flow exergy (kJ/kg) of liquid water at T (K), ignoring pressure: (h - h0) - T0 (s - s0)."""
    return C * (T - T0) - T0 * C * math.log(T / T0)


def heat_exergy(Q, T):
    """Exergy (work potential) of heat Q delivered at constant temperature T."""
    return Q * (1 - T0 / T)


def exchanger(mh, Th_in, Th_out, mc, Tc_in):
    Q = mh * C * (Th_in - Th_out)
    Tc_out = Tc_in + Q / (mc * C)
    dXh = mh * (flow_exergy(Th_in) - flow_exergy(Th_out))
    dXc = mc * (flow_exergy(Tc_out) - flow_exergy(Tc_in))
    Sgen = mh * C * math.log(Th_out / Th_in) + mc * C * math.log(Tc_out / Tc_in)
    return Q, Tc_out, dXh, dXc, Sgen


if __name__ == "__main__":
    Q, Tc, dXh, dXc, S = exchanger(1.0, 363.15, 323.15, 1.5, 283.15)
    print(f"heat duty {Q:.2f} kW; cold stream leaves at {Tc-273.15:.2f} C")
    print(f"exergy given by hot stream {dXh:.3f} kW, gained by cold {dXc:.3f} kW")
    print(f"destroyed {dXh-dXc:.3f} kW; T0 x Sgen = {T0*S:.3f} kW; second-law efficiency {dXc/dXh:.3f}")
    assert abs((dXh - dXc) - T0 * S) < 1e-9           # Gouy-Stodola
    assert S > 0
    print(f"exergy of 1000 kJ of heat at 90 C: {heat_exergy(1000, 363.15):.1f} kJ; at 1500 C: {heat_exergy(1000, 1773.15):.1f} kJ")
    print(f"first-law efficiency of the exchanger (no heat loss): 1.000")
