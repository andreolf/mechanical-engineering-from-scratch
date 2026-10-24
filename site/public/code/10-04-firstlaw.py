"""First law for a closed system: a piston-cylinder solver that tracks Q, W and the change in internal energy through a sequence of processes, checking the energy residual."""
import math

R, CV = 287.0, 718.0         # air, J/(kg K)


def process(state, kind, value, m):
    """Advance an ideal-gas state (p, V, T) through one process; return new state and (Q, W, dU) in J.
    kind: 'p' constant pressure to temperature value, 'v' constant volume to temperature value,
          'T' isothermal to volume value, 's' reversible adiabatic to volume value (k = 1.4)."""
    p, V, T = state
    if kind == "p":
        T2 = value; V2 = m * R * T2 / p; p2 = p; W = p * (V2 - V)
    elif kind == "v":
        T2 = value; V2 = V; p2 = m * R * T2 / V; W = 0.0
    elif kind == "T":
        V2 = value; T2 = T; p2 = m * R * T / V2; W = m * R * T * math.log(V2 / V)
    elif kind == "s":
        k = (CV + R) / CV; V2 = value; p2 = p * (V / V2) ** k; T2 = p2 * V2 / (m * R); W = (p2 * V2 - p * V) / (1 - k)
    dU = m * CV * (T2 - T)
    Q = dU + W                   # first law: Q - W = dU
    return (p2, V2, T2), (Q, W, dU)


if __name__ == "__main__":
    # 2 L of air at 150 kPa and 300 K under a free piston; heated at constant pressure to 500 K,
    # where the piston hits stops; then heated at constant volume to 700 K.
    p1, V1, T1 = 150e3, 2e-3, 300.0
    m = p1 * V1 / (R * T1)
    st = (p1, V1, T1); totals = [0.0, 0.0, 0.0]
    for kind, val, label in (("p", 500.0, "constant pressure to 500 K"), ("v", 700.0, "constant volume to 700 K")):
        st, (Q, W, dU) = process(st, kind, val, m)
        totals = [a + b for a, b in zip(totals, (Q, W, dU))]
        print(f"{label}: Q = {Q:.1f} J, W = {W:.1f} J, dU = {dU:.1f} J -> p = {st[0]/1e3:.1f} kPa, V = {st[1]*1e3:.3f} L")
        assert abs(Q - W - dU) < 1e-9
    print(f"mass {m*1000:.4f} g; totals Q = {totals[0]:.1f} J, W = {totals[1]:.1f} J, dU = {totals[2]:.1f} J")
    assert abs(totals[2] - m * CV * (700 - 300)) < 1e-9
    # a cycle returns to its start: net Q equals net W
    st = (p1, V1, T1); net = [0.0, 0.0, 0.0]
    for kind, val in (("s", 0.5e-3), ("v", None), ("s", 2e-3), ("v", 300.0)):
        if val is None:
            val = st[2] + 400.0      # heat addition raising T by 400 K at minimum volume
        st, (Q, W, dU) = process(st, kind, val, m)
        net = [a + b for a, b in zip(net, (Q, W, dU))]
    print(f"Otto-like cycle: net Q = {net[0]:.2f} J, net W = {net[1]:.2f} J, net dU = {net[2]:.2e} J; back to T = {st[2]:.1f} K")
    assert abs(net[2]) < 1e-9 and abs(net[0] - net[1]) < 1e-9
