"""Micro-hydro with a Pelton turbine: penstock sizing (Swamee-Jain friction, cost of pipe against
the energy it loses), net head, jet and nozzle, Euler turbine equation with an energy balance that
closes exactly, and runner sizing against a 50 Hz generator. numpy only."""
import numpy as np

rho, g, nu = 1000.0, 9.81, 1.0e-6
Hg, Q, Lp, eps = 40.0, 0.020, 150.0, 0.007e-3           # gross head, design flow, penstock length, HDPE roughness (assumed site)
K_minor = 1.5                                            # intake, bends, valve

def friction(Re, rel):
    return 0.25 / np.log10(rel / 3.7 + 5.74 / Re**0.9) ** 2      # Swamee-Jain, turbulent

def head_loss(D):
    V = Q / (np.pi * D**2 / 4); Re = V * D / nu
    return (friction(Re, eps / D) * Lp / D + K_minor) * V**2 / (2 * g), V, Re

# Swamee-Jain against a Colebrook solve at one point
D0 = 0.125; _, V0, Re0 = head_loss(D0)
f = 0.02
for _ in range(50): f = (-2 * np.log10(eps / D0 / 3.7 + 2.51 / (Re0 * np.sqrt(f)))) ** -2
assert abs(friction(Re0, eps / D0) / f - 1) < 0.02

eta_set = 0.97**2 * 0.935 * 0.95 * 0.90                  # nozzle (Cv^2), runner peak, bearings and belt, generator
print("penstock   V m/s    Re      loss m   net head   power kW   pipe cost   lost energy 10 y")
best = None
for Dmm in (90, 110, 125, 160, 200):
    D = Dmm / 1000; hf, V, Re = head_loss(D)
    P = eta_set * rho * g * Q * (Hg - hf)
    cost = 18.0 * (D / 0.1) ** 1.6 * Lp                  # installed HDPE, EUR (assumed scaling)
    lost = eta_set * rho * g * Q * hf / 1e3 * 8760 * 0.7 * 10 * 0.10   # kWh at 70 % capacity factor, 0.10 EUR/kWh
    total = cost + lost
    print(f"  {Dmm:4d} mm  {V:5.2f}  {Re:8.0f}  {hf:7.2f}   {Hg-hf:7.2f}   {P/1e3:7.3f}   {cost:8.0f}   {lost:8.0f}")
    if best is None or total < best[1]: best = (Dmm, total, hf)
Dmm, _, hf = best
Hn = Hg - hf
print(f"cheapest over 10 years: {Dmm} mm, loss {hf:.2f} m = {hf/Hg*100:.1f} % of the gross head")
assert hf / Hg < 0.10                                    # the usual rule of thumb: lose under 10 %

# jet
Cv = 0.97
Vj = Cv * np.sqrt(2 * g * Hn)
print(f"\njet velocity {Vj:.3f} m/s")

# Euler turbine equation for a bucket moving at u, deflection 165 deg, relative speed kept by k = 0.9
beta, k = np.radians(165), 0.9
def bucket(u, V=Vj):
    w1 = V - u; w2 = k * w1
    c2 = np.array([u + w2 * np.cos(beta), w2 * np.sin(beta)])            # absolute exit velocity
    P = rho * Q * u * (w1 - w2 * np.cos(beta))                         # force on bucket times its speed
    return P, 0.5 * rho * Q * (c2 @ c2), 0.5 * rho * Q * (w1**2 - w2**2)
for u in np.linspace(0.1, 0.9, 5) * Vj:                                   # energy: jet = shaft + leaving + bucket friction
    P, KEout, loss = bucket(u)
    assert np.isclose(0.5 * rho * Q * Vj**2, P + KEout + loss, rtol=1e-12)
us = np.linspace(0, 1, 100001) * Vj
Pu = np.array([bucket(u)[0] for u in us[::100]])
ratio = us[::100][np.argmax(Pu)] / Vj
eta_r = Pu.max() / (0.5 * rho * Q * Vj**2)
print(f"runner power peaks at u/V = {ratio:.3f} with hydraulic efficiency {eta_r:.4f}; (1 + k cos 15)/2 = {(1 + k*np.cos(np.radians(15)))/2:.4f}")
assert abs(ratio - 0.5) < 1e-3 and np.isclose(eta_r, (1 + k * np.cos(np.radians(15))) / 2, rtol=1e-6)

# runner sizing: real runners run at u/V about 0.46 because of bucket geometry and windage
u = 0.46 * Vj
print("\njets  runner rpm   pitch D m   jet d mm   D/d   (want D/d of at least about 10)")
choice = None
for jets in (1, 2):
    d = np.sqrt(4 * Q / jets / (np.pi * Vj))
    for N in (1500, 1000, 750):
        Dp = 60 * u / (np.pi * N)
        ok = Dp / d >= 10
        print(f"  {jets}     {N:5d}      {Dp:.3f}      {d*1e3:5.1f}   {Dp/d:4.1f} {'ok' if ok else ''}")
        if ok and choice is None: choice = (jets, N, Dp, d)
jets, N, Dp, d = choice
P_e = eta_set * rho * g * Q * Hn
print(f"choice: {jets} jets, runner {N} rpm on a 1500 rpm 4-pole generator by belt, pitch diameter {Dp*1e3:.0f} mm, {P_e/1e3:.2f} kW electric")
assert jets == 2 and N == 1000
