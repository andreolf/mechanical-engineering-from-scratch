"""A gyroscope on a pivot: full rigid-body simulation against the fast-top precession rate m g r / (I omega)."""
import math
import numpy as np




def simulate(I1, I3, m, g, l, theta0, spin, t_end, dt=1e-4):
    """Lagrangian of the heavy symmetric top: L = I1/2 (th'^2 + ph'^2 sin^2 th) + I3/2 (ps' + ph' cos th)^2 - m g l cos th.
    Conserved: w3 = ps' + ph' cos th (spin) and p_phi = I1 ph' sin^2 th + I3 w3 cos th.
    Start with th' = 0, ph' = 0 (released from rest in precession): the top nutates and precesses on average."""
    w3 = spin
    p_phi = I3 * w3 * math.cos(theta0)                     # ph'(0) = 0
    def f(st):
        th, thd, ph = st
        phd = (p_phi - I3 * w3 * math.cos(th)) / (I1 * math.sin(th) ** 2)
        thdd = (phd**2 * math.sin(th) * math.cos(th) * I1 - I3 * w3 * phd * math.sin(th) + m * g * l * math.sin(th)) / I1
        return np.array([thd, thdd, phd])
    st = np.array([theta0, 0.0, 0.0]); t = 0.0; ths = [theta0]
    n = int(round(t_end / dt))
    for _ in range(n):
        k1 = f(st); k2 = f(st + dt/2*k1); k3 = f(st + dt/2*k2); k4 = f(st + dt*k3)
        st = st + dt/6*(k1 + 2*k2 + 2*k3 + k4); ths.append(st[0])
    return st, np.array(ths)


if __name__ == "__main__":
    # a toy gyroscope: 0.15 kg rotor, I3 = 6e-5 kg m^2 (spin axis), I1 = 4e-5 about the pivot, centre of mass 0.04 m out, horizontal
    m, g, l, I1, I3 = 0.15, 9.81, 0.04, 4.0e-5, 6.0e-5
    theta0 = math.pi / 2
    print("spin (rad/s)  simulated precession  formula m g l/(I3 w)  ratio   nutation amplitude (deg)")
    for spin in (100.0, 200.0, 500.0, 1000.0, 2000.0):
        T = 2.0
        st, ths = simulate(I1, I3, m, g, l, theta0, spin, T)
        Om_sim = st[2] / T
        Om_fast = m * g * l / (I3 * spin)
        print(f"{spin:10.0f}  {Om_sim:18.5f}  {Om_fast:20.5f}  {Om_sim / Om_fast:6.4f}   {math.degrees(ths.max() - ths.min()):.4f}")
    st, _ = simulate(I1, I3, m, g, l, theta0, 2000.0, 2.0)
    assert abs(st[2] / 2.0 / (m * g * l / (I3 * 2000.0)) - 1) < 0.01
    # the precession formula is the angular momentum law: torque m g l turns H = I3 w at rate Omega, so m g l = Omega I3 w
    print(f"at 2000 rad/s (19,100 rpm) the gyroscope precesses once every {2 * math.pi / (m * g * l / (I3 * 2000)):.2f} s")
