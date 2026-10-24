"""Pump and system curves: the operating point, and the affinity laws for a change of speed."""
import math

RHO, G = 1000.0, 9.81


def pump_head(Q, N, H0=40.0, a=4000.0, N0=1450.0):
    """A typical centrifugal pump curve at speed N (rpm): H = H0 (N/N0)^2 - a Q^2."""
    return H0 * (N / N0) ** 2 - a * Q * Q


def pump_eff(Q, N, Qbep=0.06, N0=1450.0, eta_max=0.78):
    """Efficiency peaks at the best-efficiency flow, which moves with speed (affinity)."""
    q = Q / (Qbep * N / N0)
    return max(0.0, eta_max * (2 * q - q * q))


def system_head(Q, Hs=15.0, k=3000.0):
    """Static lift plus friction losses that grow as Q^2."""
    return Hs + k * Q * Q


def operating_point(N, **sys):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if pump_head(m, N) > system_head(m, **sys) else (lo, m)
    return (lo + hi) / 2


if __name__ == "__main__":
    for N in (1450, 1200, 1000):
        Q = operating_point(N); H = system_head(Q); eta = pump_eff(Q, N)
        P = RHO * G * Q * H / eta
        print(f"N = {N} rpm: Q = {Q*1000:.3f} L/s, H = {H:.3f} m, efficiency {eta:.3f}, shaft power {P/1000:.3f} kW")
    # affinity laws: a point (Q, H) on the curve at N maps to (Q r, H r^2) at r N, with power r^3
    r = 1200 / 1450
    for Q in (0.02, 0.05, 0.08):
        H = pump_head(Q, 1450)
        assert abs(pump_head(Q * r, 1200) - H * r * r) < 1e-12           # flow linear in speed, head quadratic
        assert abs(pump_eff(Q * r, 1200) - pump_eff(Q, 1450)) < 1e-12     # same efficiency at the similar point
    print(f"affinity check passed for r = {r:.4f}: flow x {r:.4f}, head x {r*r:.4f}, power x {r**3:.4f}")
    # with no static lift the system curve is itself a parabola through the origin, so the operating flow scales exactly
    Q1, Q2 = operating_point(1450, Hs=0.0), operating_point(1200, Hs=0.0)
    print(f"no static lift: Q ratio {Q2/Q1:.6f} = speed ratio {r:.6f}")
    assert abs(Q2 / Q1 - r) < 1e-9
