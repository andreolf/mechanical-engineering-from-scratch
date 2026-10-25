"""PID cruise control of an e-bike: a non-linear speed model with drag, rolling resistance, hills,
a motor force limit and lags. P alone leaves an error on a hill, integral action removes it, a steep
hill saturates the motor and winds up the integrator, and clamping anti-windup fixes the overshoot.
Ziegler-Nichols gains come from the ultimate gain of the linearised loop. numpy only."""
import numpy as np

m, g, rho, CdA, Crr = 100.0, 9.81, 1.2, 0.5, 0.006       # rider + bike, air, drag area, rolling
Fmax, tau_a, tau_s = 80.0, 0.2, 0.3                        # motor force limit N, motor lag s, speed-filter lag s
v_ref = 25 / 3.6

def grade(t, steep):
    return (0.08 if steep else 0.03) if 20 <= t < 60 else 0.0

def simulate(Kp, Ki, Kd, steep=False, antiwindup=True, T=100.0, dt=0.002):
    v, F, vm, I, e_prev = v_ref, 0.0, v_ref, 0.0, 0.0
    F = 0.5 * rho * CdA * v_ref**2 + Crr * m * g             # start in steady cruise on the flat
    I = F / Ki if Ki else 0.0
    n = int(T / dt); out = np.empty((n, 3))
    for k in range(n):
        t = k * dt
        e = v_ref - vm
        D = (e - e_prev) / dt if k else 0.0; e_prev = e
        u = Kp * e + Ki * I + Kd * D
        u_sat = min(max(u, 0.0), Fmax)                       # the motor can only push, up to 80 N
        if not antiwindup or u == u_sat or (u > Fmax and e < 0) or (u < 0 and e > 0):
            I += e * dt                                      # clamping: freeze the integrator while it would push further into saturation
        F += dt * (u_sat - F) / tau_a
        th = np.arctan(grade(t, steep))
        a = (F - 0.5 * rho * CdA * v * abs(v) - Crr * m * g * np.cos(th) - m * g * np.sin(th)) / m
        v += a * dt
        vm += dt * (v - vm) / tau_s
        out[k] = t, v, u_sat
    return out

# linearised loop at cruise: G = 1/(m s + c) * 1/(tau_a s + 1) * 1/(tau_s s + 1), c = rho CdA v
c = rho * CdA * v_ref
den = np.polymul([m, c], np.polymul([tau_a, 1], [tau_s, 1]))
Ku = None
lo, hi = 1.0, 1e5
for _ in range(200):
    mid = np.sqrt(lo * hi)
    if np.max(np.roots(np.polyadd(den, [mid])).real) > 0: hi = mid
    else: lo = mid
Ku = lo; wu = np.max(np.abs(np.roots(np.polyadd(den, [Ku])).imag)); Tu = 2 * np.pi / wu
a1, a2, a3 = den[1] / den[0], den[2] / den[0], den[3] / den[0]
print(f"linearised plant time constant m/c = {m/c:.2f} s; ultimate gain Ku = {Ku:.3f} N/(m/s), Tu = {Tu:.4f} s (Routh: Ku = {(a1*a2-a3)*den[0]:.3f})")
assert abs(Ku - (a1 * a2 - a3) * den[0]) < 1e-6 * Ku
Kp, Ti, Td = 0.6 * Ku, Tu / 2, Tu / 8                       # classic Ziegler-Nichols PID
print(f"Ziegler-Nichols PID: Kp = {Kp:.2f}, Ti = {Ti:.4f} s, Td = {Td:.4f} s")
Kp_t, Ki_t = 0.3 * Ku, 0.3 * Ku / (4 * Tu)                  # a gentler PI for the cruise tests: Kp = 0.3 Ku, Ti = 4 Tu

err = lambda o, t0, t1: np.mean(v_ref - o[(o[:, 0] > t0) & (o[:, 0] < t1), 1]) * 3.6
P = simulate(Kp_t, 0, 0)
PI = simulate(Kp_t, Ki_t, 0)
print(f"3 % hill, P only (Kp = {Kp_t:.1f}): speed error at the end of the hill {err(P, 55, 60):.3f} km/h (linear theory: total force needed / (Kp + c) = {(0.5*rho*CdA*v_ref**2 + Crr*m*g + m*g*np.sin(np.arctan(0.03)))/(Kp_t+c)*3.6:.3f})")
print(f"3 % hill, PI (Ki = {Ki_t:.2f}): error {err(PI, 55, 60):.4f} km/h")
assert abs(err(P, 55, 60) / ((0.5*rho*CdA*v_ref**2 + Crr*m*g + m*g*np.sin(np.arctan(0.03)))/(Kp_t+c)*3.6) - 1) < 0.02
assert err(P, 55, 60) > 0.5 and abs(err(PI, 55, 60)) < 0.01         # integral action removes the steady error

ZN = simulate(Kp, Kp / Ti, Kp * Td)
print(f"ZN PID on the 3 % hill: peak speed dip {(v_ref - ZN[(ZN[:,0]>20)&(ZN[:,0]<40),1].min())*3.6:.3f} km/h, error at 55-60 s {err(ZN, 55, 60):.4f} km/h")

wind = simulate(Kp_t, Ki_t, 0, steep=True, antiwindup=False)
aw = simulate(Kp_t, Ki_t, 0, steep=True, antiwindup=True)
for name, o in (("no anti-windup", wind), ("clamping anti-windup", aw)):
    after = o[o[:, 0] > 60]
    print(f"8 % hill, {name:20s}: slowest {o[:,1].min()*3.6:.2f} km/h, overshoot after the crest {(after[:,1].max()-v_ref)*3.6:.2f} km/h")
assert (wind[wind[:, 0] > 60, 1].max() - v_ref) > 3 * (aw[aw[:, 0] > 60, 1].max() - v_ref)
