"""Small pumped storage for a village solar grid: a day of pumping and generating with an energy
ledger that closes exactly, then water hammer in the penstock by the method of characteristics,
checked against Joukowsky and the critical closure time. numpy only."""
import numpy as np

rho, g = 1000.0, 9.81
Lp, D, f = 300.0, 0.30, 0.015                      # penstock length, diameter, friction factor
Ap = np.pi * D**2 / 4
kf = f * Lp / D / (2 * g * Ap**2)                  # friction head = kf Q^2
z0, Ares, zmax = 50.0, 2000.0, 4.0                 # upper tank floor 50 m above the pond, area, depth
eta_p, eta_t = 0.78, 0.82                          # pump and turbine, each including the motor or generator

def flow_for_power(Ph, Hs, sign):
    """Hydraulic power at the machine Ph = rho g Q (Hs + sign*kf Q^2); sign +1 pumping, -1 generating."""
    Q = Ph / (rho * g * Hs)
    for _ in range(60): Q = Q - (rho * g * Q * (Hs + sign * kf * Q**2) - Ph) / (rho * g * (Hs + 3 * sign * kf * Q**2))
    return Q

dt = 60.0
t = np.arange(0, 24 * 3600, dt)
hr = t / 3600
P_surplus = np.clip(40e3 * np.sin(np.pi * (hr - 7) / 10), 0, None) * ((hr > 8) & (hr < 16))    # solar surplus, W (assumed)
P_demand = np.where((hr >= 18) & (hr < 23), 15e3, 0.0)                                         # evening load, W
z = 1.0                                                                                       # start 1 m deep
led = dict(E_in=0.0, E_out=0.0, pump_loss=0.0, turb_loss=0.0, fric=0.0, dPE=0.0, unserved=0.0, spilled=0.0)
zs = []
for k in range(len(t)):
    if P_surplus[k] > 0 and z < zmax:
        Pe = P_surplus[k]; Ph = eta_p * Pe; Q = 0.0
        for _ in range(30):                                   # head at the middle of this step's slab, so the PE ledger is exact
            dz = Q * dt / Ares; Hs = z0 + z + dz / 2; Q = flow_for_power(Ph, Hs, +1)
        dz = Q * dt / Ares; Hs = z0 + z + dz / 2
        led["E_in"] += Pe * dt; led["pump_loss"] += (Pe - Ph) * dt; led["fric"] += rho * g * kf * Q**3 * dt
        led["dPE"] += rho * g * Ares * dz * Hs; z += dz
    elif P_surplus[k] > 0: led["spilled"] += P_surplus[k] * dt
    if P_demand[k] > 0 and z > 0.05:
        Pe = P_demand[k]; Ph = Pe / eta_t; Q = 0.0
        for _ in range(30):
            dz = Q * dt / Ares; Hs = z0 + z - dz / 2; Q = flow_for_power(Ph, Hs, -1)
        dz = Q * dt / Ares; Hs = z0 + z - dz / 2
        led["E_out"] += Pe * dt; led["turb_loss"] += (Ph - Pe) * dt; led["fric"] += rho * g * kf * Q**3 * dt
        led["dPE"] -= rho * g * Ares * dz * Hs; z -= dz
    elif P_demand[k] > 0: led["unserved"] += P_demand[k] * dt
    zs.append(z)
kWh = {k: v / 3.6e6 for k, v in led.items()}
print("energy ledger, kWh: " + ", ".join(f"{k} {v:.3f}" for k, v in kWh.items()))
lhs = led["E_in"]
rhs = led["E_out"] + led["pump_loss"] + led["turb_loss"] + led["fric"] + led["dPE"]
print(f"in {lhs/3.6e6:.4f} kWh = out + losses + stored {rhs/3.6e6:.4f} kWh; relative error {abs(lhs-rhs)/lhs:.1e}")
assert abs(lhs - rhs) / lhs < 1e-9
zs = np.array(zs)
print(f"tank level: start 1.000 m, max {zs.max():.3f} m, end {zs[-1]:.3f} m; evening demand served {kWh['E_out']:.2f} of 75.00 kWh")
Q_turb = flow_for_power(15e3 / eta_t, z0 + 2.0, -1)
Q_pump = flow_for_power(eta_p * 30e3, z0 + 2.0, +1)
hp, ht = kf * Q_pump**2, kf * Q_turb**2
rt = eta_p * eta_t * (z0 + 2.0 - ht) / (z0 + 2.0 + hp)
print(f"at mid level: pumping 30 kW lifts {Q_pump*1e3:.1f} L/s with {hp:.3f} m friction; generating 15 kW takes {Q_turb*1e3:.1f} L/s with {ht:.3f} m")
print(f"round-trip efficiency {rt:.4f} (machines alone {eta_p*eta_t:.4f})")

# water hammer: reservoir upstream, valve at the powerhouse, steel pipe 6 mm wall
K, Es, e = 2.2e9, 200e9, 0.006
a = np.sqrt(K / rho / (1 + K * D / (Es * e)))
Tcrit = 2 * Lp / a
print(f"\nwave speed {a:.1f} m/s, 2L/a = {Tcrit:.3f} s")

def moc(Q0, Tc, H0=z0 + 2.0, T=8.0, nx=60):
    """Method of characteristics. Valve: Q = Cv tau sqrt(H), tau falls linearly to 0 over Tc."""
    dx = Lp / nx; dtm = dx / a; B = a / (g * Ap); R = f * dx / (2 * g * D * Ap**2)
    H = H0 - kf * Q0**2 * np.linspace(0, 1, nx + 1); Q = np.full(nx + 1, Q0)
    Cv = Q0 / np.sqrt(H[-1]); Hmax = H[-1]; tt = 0.0; Hv = []
    while tt < T:
        tt += dtm
        CP = H[:-1] + B * Q[:-1] - R * Q[:-1] * np.abs(Q[:-1]); CM = H[1:] - B * Q[1:] + R * Q[1:] * np.abs(Q[1:])
        Hn = np.empty_like(H); Qn = np.empty_like(Q)
        Hn[1:-1] = (CP[:-1] + CM[1:]) / 2; Qn[1:-1] = (CP[:-1] - CM[1:]) / (2 * B)
        Hn[0] = H0; Qn[0] = (H0 - CM[0]) / B                                   # reservoir
        tau = max(0.0, 1 - tt / Tc) if Tc > 0 else 0.0
        cv = Cv * tau
        if cv == 0: Qn[-1] = 0.0; Hn[-1] = CP[-1]
        else:                                                                 # Q = cv sqrt(H) with H = CP - B Q
            s = (-B * cv**2 + np.sqrt((B * cv**2) ** 2 + 4 * cv**2 * CP[-1])) / 2; Qn[-1] = s; Hn[-1] = CP[-1] - B * s
        H, Q = Hn, Qn; Hmax = max(Hmax, H[-1]); Hv.append(H[-1])
    return Hmax, np.array(Hv)

V0 = Q_turb / Ap
dHj = a * V0 / g
H_inst, _ = moc(Q_turb, 0.0)
H_valve0 = z0 + 2.0 - kf * Q_turb**2
print(f"pipe velocity {V0:.3f} m/s; Joukowsky rise aV/g = {dHj:.2f} m; MOC instant closure rise {H_inst - H_valve0:.2f} m")
assert abs((H_inst - H_valve0) / dHj - 1) < 0.03
print("closure time s   peak head m   rise m   Michaud 2LV/(g Tc) m")
for Tc in (0.2, Tcrit, 2.0, 5.0, 10.0, 20.0):
    Hm, _ = moc(Q_turb, Tc, T=Tc + 6)
    mich = 2 * Lp * V0 / (g * Tc)
    print(f"   {Tc:6.3f}       {Hm:7.2f}    {Hm-H_valve0:6.2f}    {min(mich, dHj):6.2f}")
    if Tc <= Tcrit: assert abs((Hm - H_valve0) / dHj - 1) < 0.03                # closing faster than 2L/a gives the full Joukowsky rise
    if Tc == 10.0: H10 = Hm - H_valve0
assert H10 < 0.3 * dHj
print(f"a 10 s closure keeps the rise to {H10:.2f} m, {H10/dHj*100:.0f} % of the instant-closure surge")
