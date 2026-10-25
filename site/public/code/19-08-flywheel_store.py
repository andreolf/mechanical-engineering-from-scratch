"""Steel flywheel to ride a village solar grid through 30 s cloud dips: size the disc, check the
rotating-disc stresses with a finite-difference solve against the closed form, and find the burst
margin, with and without a shaft bore. numpy only."""
import numpy as np

rho, E, nu = 7850.0, 205e9, 0.29               # 4340 steel, quenched and tempered (assumed properties)
sy, su = 860e6, 1000e6                          # yield and ultimate
P, t_ride = 10e3, 30.0                          # bridge 10 kW for 30 s
E_use = P * t_ride
print(f"usable energy {E_use/1e3:.0f} kJ")

def disc_fd(a, b, w, n=1501):
    """Radial displacement of a rotating disc in plane stress, finite differences.
    u'' + u'/r - u/r^2 = -(1 - nu^2) rho w^2 r / E, with sigma_r = 0 at free edges (and u(0) = 0 if solid)."""
    r = np.linspace(a if a > 0 else 0.0, b, n); h = r[1] - r[0]
    A = np.zeros((n, n)); rhs = -(1 - nu**2) * rho * w**2 * r / E
    for i in range(1, n - 1):
        A[i, i - 1] = 1 / h**2 - 1 / (2 * h * r[i]); A[i, i] = -2 / h**2 - 1 / r[i] ** 2; A[i, i + 1] = 1 / h**2 + 1 / (2 * h * r[i])
    def free(i, sgn):                            # sigma_r ~ u' + nu u / r = 0, second-order one-sided difference
        idx = [i, i + sgn, i + 2 * sgn]; c = np.array([-3, 4, -1]) / (2 * h) * sgn
        A[i, :] = 0; A[i, idx] = c; A[i, i] += nu / r[i]; rhs[i] = 0
    if a > 0: free(0, +1)
    else: A[0, :] = 0; A[0, 0] = 1; rhs[0] = 0
    free(n - 1, -1)
    u = np.linalg.solve(A, rhs)
    du = np.gradient(u, h, edge_order=2)
    with np.errstate(divide="ignore", invalid="ignore"):
        ur = np.where(r > 0, u / np.where(r > 0, r, 1), du)
    sr = E / (1 - nu**2) * (du + nu * ur); st = E / (1 - nu**2) * (ur + nu * du)
    return r, sr, st

def disc_exact(a, b, w, r):
    k = (3 + nu) / 8 * rho * w**2
    if a == 0:
        return k * (b**2 - r**2), k * (b**2 - (1 + 3 * nu) / (3 + nu) * r**2)
    return k * (a**2 + b**2 - a**2 * b**2 / r**2 - r**2), k * (a**2 + b**2 + a**2 * b**2 / r**2 - (1 + 3 * nu) / (3 + nu) * r**2)

# two ways to set the speed of a solid 0.6 m disc that runs between w_max and w_max/2 (75 % of the energy usable)
b = 0.30
def size(w_max, a=0.0):
    I = E_use / (0.5 * w_max**2 * 0.75)
    th = I / (0.5 * rho * np.pi * (b**4 - a**4))
    return th, rho * np.pi * (b**2 - a**2) * th, 0.5 * I * w_max**2
w_stress = np.sqrt((sy / 2) / ((3 + nu) / 8 * rho * b**2))      # centre stress at half of yield
w_rim = 150.0 / b                                                # rim speed 150 m/s: air drag, bearings, balance, a shop that can make it
for name, w in (("stress-limited", w_stress), ("rim-speed-limited", w_rim)):
    th, mass, Ef = size(w)
    print(f"{name:>18}: {w*60/2/np.pi:6.0f} rpm, rim {w*b:5.0f} m/s, {th*1e3:5.1f} mm thick, {mass:5.1f} kg, {Ef/mass/1e3:5.2f} kJ/kg")
    assert np.isclose(Ef / mass, 0.25 * (w * b) ** 2, rtol=1e-9)          # E/m = (rim speed)^2 / 4 for a flat disc
w_max = w_rim
th, mass, E_full = size(w_max)
print(f"choose the rim-speed limit: a 5.4 mm disc spinning at 11 600 rpm in air is a saw blade, not a store")

r, sr, st = disc_fd(0.0, b, w_max)
er, et = disc_exact(0.0, b, w_max, r)
print(f"\ncentre stress: finite differences {st[0]/1e6:.3f} MPa, closed form {et[0]/1e6:.3f} MPa")
assert np.max(np.abs(st - et)) / et[0] < 2e-3 and np.max(np.abs(sr - er)) / et[0] < 2e-3
burst = np.sqrt(su / st.max())                                   # stress grows as w^2
print(f"solid: peak {st.max()/1e6:.2f} MPa, yield margin {sy/st.max():.2f}, burst at {burst:.3f} x full speed ({w_max*burst*60/2/np.pi:.0f} rpm)")

# a 40 mm shaft bore: the hoop stress at the bore is about twice the solid-disc centre stress
a = 0.020
r2, sr2, st2 = disc_fd(a, b, w_max)
er2, et2 = disc_exact(a, b, w_max, r2)
assert np.max(np.abs(st2 - et2)) / et2[0] < 2e-3
burst2 = np.sqrt(su / st2.max())
th2, m2, _ = size(w_max, a)
print(f"with a {2*a*1e3:.0f} mm bore: bore hoop stress {st2[0]/1e6:.2f} MPa (closed form {et2[0]/1e6:.2f}), {st2[0]/st[0]:.3f} x the solid centre")
print(f"  {th2*1e3:.1f} mm thick, {m2:.1f} kg; burst at {burst2:.3f} x full speed ({w_max*burst2*60/2/np.pi:.0f} rpm)")
assert st2[0] / st[0] > 1.95 and burst2 > 2.0 and burst > 3.0
# overspeed: if the controller fails and the grid drives the motor, the governor must trip well below burst
trip = 1.15
print(f"overspeed trip at {trip:.2f} x: stress {st2[0]*trip**2/1e6:.1f} MPa at the bore, still {sy/(st2[0]*trip**2):.2f} x below yield")
assert sy / (st2[0] * trip**2) > 2
