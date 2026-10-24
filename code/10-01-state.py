"""A thermodynamic state as an object: give exactly two independent properties of an ideal gas and it works out the rest, refusing inconsistent or over-specified input."""
import math

R_AIR, CP_AIR = 287.0, 1005.0           # J/(kg K)
CV_AIR = CP_AIR - R_AIR
T_REF, P_REF = 298.15, 101325.0         # reference state for entropy (s = 0)


class StateError(ValueError):
    pass


class State:
    """Simple compressible ideal gas. Accepts any two of p (Pa), T (K), v (m^3/kg); a third must agree."""

    def __init__(self, p=None, T=None, v=None, R=R_AIR, cp=CP_AIR, rtol=1e-9):
        given = {k: x for k, x in (("p", p), ("T", T), ("v", v)) if x is not None}
        if len(given) < 2:
            raise StateError("state postulate: need two independent intensive properties")
        if any(x <= 0 for x in given.values()):
            raise StateError("p, T and v must be positive")
        self.R, self.cp, self.cv = R, cp, cp - R
        if p is None: p = R * T / v
        if T is None: T = p * v / R
        if v is None: v = R * T / p
        if abs(p * v - R * T) > rtol * R * T:
            raise StateError(f"over-specified and inconsistent: pv = {p*v:.6g} but RT = {R*T:.6g}")
        self.p, self.T, self.v = p, T, v

    @property
    def rho(self): return 1 / self.v
    @property
    def u(self): return self.cv * (self.T - T_REF)
    @property
    def h(self): return self.cp * (self.T - T_REF)
    @property
    def s(self): return self.cp * math.log(self.T / T_REF) - self.R * math.log(self.p / P_REF)

    def __repr__(self):
        return f"State(p={self.p/1e3:.2f} kPa, T={self.T:.2f} K, v={self.v:.5f} m3/kg)"


if __name__ == "__main__":
    a = State(p=101325, T=288.15)
    print(a, f"rho = {a.rho:.4f} kg/m^3")
    assert abs(a.rho - 1.2252) < 1e-3
    b = State(T=288.15, v=a.v)            # any two give the same state
    assert abs(b.p - a.p) < 1e-6
    c = State(p=2e6, T=700.0)
    print(c, f"h = {c.h/1e3:.2f} kJ/kg, s = {c.s:.2f} J/(kg K)")
    assert abs(c.h - c.u - c.R * (c.T - T_REF)) < 1e-9     # h = u + pv up to the reference constant
    try:
        State(p=101325, T=288.15, v=0.9)
    except StateError as e:
        print("rejected:", e)
    else:
        raise AssertionError("inconsistent state accepted")
    try:
        State(T=300.0)
    except StateError as e:
        print("rejected:", e)
    State(p=101325, T=288.15, v=a.v)       # consistent over-specification is accepted
