"""E-bike mid-drive: DC motor model, gear ratio choice against top speed and hill climbing, an
energy ledger from battery to road, and winding temperature on a long tropical climb. numpy only."""
import numpy as np

g, rho_air = 9.81, 1.18
m, Crr, CdA, rw = 100.0, 0.008, 0.55, 0.35          # rider and bike, rolling, drag area, wheel radius
Vb, R, Kt = 36.0, 0.25, 0.08                        # battery, winding resistance, torque constant (= back-EMF constant)
I_max, eta_g = 15.0, 0.92                           # controller current limit, gearbox and chain
P_rider, v_cut = 100.0, 25 / 3.6                    # the rider's own pedalling, EU assist cut-off speed
Cth, Rth, T_amb, T_lim = 400.0, 1.8, 30.0, 120.0    # winding heat capacity J/K, to ambient K/W, Bali afternoon, insulation limit

def road(v, grade):
    th = np.arctan(grade)
    return m * g * (Crr * np.cos(th) + np.sin(th)) + 0.5 * rho_air * CdA * v * abs(v)

def motor_current(v, G):
    """Full throttle below the cut-off: current limited by the controller and by the back-EMF."""
    if v >= v_cut: return 0.0
    wm = G * v / rw
    return float(np.clip((Vb - Kt * wm) / R, 0, I_max))

def wheel_force(v, G):
    I = motor_current(v, G)
    return eta_g * G * Kt * I / rw + P_rider / max(v, 1.0), I

def ride(G, grade, dist, dt=0.01, v0=0.5):
    v, x, T, t = v0, 0.0, T_amb, 0.0
    L = dict(batt=0.0, rider=0.0, copper=0.0, gear=0.0, roll_aero=0.0, PE=0.0, KE=-0.5 * m * v0**2)
    Tmax = T
    while x < dist:
        Fw, I = wheel_force(v, G)
        Fr = road(v, grade)
        v1 = max(v + (Fw - Fr) / m * dt, 0.05)
        vm = 0.5 * (v + v1)
        wm = G * v / rw
        L["batt"] += (Kt * wm + I * R) * I * dt                 # ideal PWM: the battery supplies back-EMF plus IR at the motor current
        L["copper"] += I**2 * R * dt
        L["gear"] += (1 - eta_g) * Kt * I * wm * dt
        L["rider"] += P_rider / max(v, 1.0) * vm * dt
        th = np.arctan(grade)
        L["PE"] += m * g * np.sin(th) * vm * dt
        L["roll_aero"] += (Fr - m * g * np.sin(th)) * vm * dt
        T += ((I**2 * R) - (T - T_amb) / Rth) / Cth * dt; Tmax = max(Tmax, T)
        x += vm * dt; v = v1; t += dt
    L["KE"] += 0.5 * m * v**2
    return t, v, Tmax, L

def top_speed(G, grade):
    vs = np.linspace(0.5, 15, 14501)
    net = np.array([wheel_force(v, G)[0] - road(v, grade) for v in vs])
    return vs[np.argmax(net < 0)] if np.any(net < 0) else np.nan

def max_grade(G):
    gr = np.linspace(0, 0.4, 4001)
    v = 2.0                                                          # walking pace with full current
    F = wheel_force(v, G)[0]
    return gr[np.argmax(np.array([road(v, s) for s in gr]) > F)]

print("ratio  flat speed km/h  8 % speed km/h  max grade at 7 km/h   3 km at 8 %: time  winding peak C  battery Wh")
res = {}
for G in (10, 16, 22, 26):
    vf, vh = top_speed(G, 0) * 3.6, top_speed(G, 0.08) * 3.6
    gmax = max_grade(G)
    t, vend, Tmax, L = ride(G, 0.08, 3000)
    res[G] = (vf, vh, gmax, t, Tmax, L)
    print(f"  {G:3d}       {vf:5.1f}            {vh:5.1f}         {gmax*100:5.1f} %              {t/60:5.1f} min     {Tmax:6.1f}      {L['batt']/3600:6.1f}")
G = 22
t, vend, Tmax, L = ride(G, 0.08, 3000)
ins = L["batt"] + L["rider"]
outs = L["copper"] + L["gear"] + L["roll_aero"] + L["PE"] + L["KE"]
print("\nledger for G = 22, Wh: " + ", ".join(f"{k} {v/3600:.2f}" for k, v in L.items()))
print(f"in {ins/3600:.3f} Wh, out {outs/3600:.3f} Wh, relative mismatch {abs(ins-outs)/ins:.1e} (time-step error)")
assert abs(ins - outs) / ins < 2e-3
assert np.isclose(L["PE"], m * g * np.sin(np.arctan(0.08)) * 3000, rtol=2e-3)
# the choices
assert res[10][4] > T_lim                       # tall gear: the motor stalls into its current limit on the hill and cooks
assert res[22][0] >= 24.9 and res[22][4] < T_lim
assert res[26][0] < 24.0                             # too low a gear spins the motor out before the cut-off speed
print(f"G = 22: reaches {res[22][0]:.1f} km/h on the flat, climbs 8 % at {res[22][1]:.1f} km/h, winding peaks at {res[22][4]:.1f} C")
Wh_km = (res[22][5]["batt"] / 3600) / 3.0
print(f"battery use on the climb {Wh_km:.1f} Wh/km; a 500 Wh pack covers {500/Wh_km:.0f} km of such climbing")
