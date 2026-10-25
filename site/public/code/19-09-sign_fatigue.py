"""Wind-loaded roadside sign on a steel pole: static gust check, natural frequency and vortex lock-in,
then fatigue at the welded base from synthetic turbulent wind, rainflow counting written from
scratch and Miner's rule over a Weibull wind climate. numpy only."""
import numpy as np

rho, E, fy = 1.2, 210e9, 355e6
Bs, Hs, zc, Cd = 2.0, 1.0, 4.5, 1.2                 # sign 2 m x 1 m, centre 4.5 m up, flat plate drag
D, t = 0.1683, 0.005                                # pole CHS 168.3 x 5
Lp = zc + 0.0
I = np.pi / 64 * (D**4 - (D - 2 * t) ** 4)
W = I / (D / 2)
A_sign = Bs * Hs

def base_stress(V):
    F = 0.5 * rho * Cd * A_sign * V * np.abs(V)
    Fp = 0.5 * rho * 0.7 * D * Lp * V * np.abs(V)     # wind on the pole itself, acting at mid height
    return (F * zc + Fp * Lp / 2) / W

V_gust = 35.0                                        # assumed 3 s design gust
s_gust = base_stress(V_gust)
print(f"pole I = {I*1e8:.1f} cm^4, W = {W*1e6:.1f} cm^3; gust {V_gust} m/s gives {s_gust/1e6:.1f} MPa at the base (yield {fy/1e6:.0f}), factor {fy/1.1/(1.5*s_gust):.2f} after 1.5 on load and 1.1 on steel")
assert fy / 1.1 > 1.5 * s_gust

# natural frequency: cantilever with a 35 kg sign at the top, Rayleigh with 0.236 of the pole mass
m_sign, m_pole = 35.0, 7850 * np.pi / 4 * (D**2 - (D - 2 * t) ** 2) * Lp
k = 3 * E * I / Lp**3
fn = np.sqrt(k / (m_sign + 0.236 * m_pole)) / (2 * np.pi)
# check with a finite-element beam (cubic Hermite elements, consistent mass) of the same pole
ne = 20; le = Lp / ne; mu = m_pole / Lp
kel = E * I / le**3 * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le**2, -6 * le, 2 * le**2], [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le**2, -6 * le, 4 * le**2]])
mel = mu * le / 420 * np.array([[156, 22 * le, 54, -13 * le], [22 * le, 4 * le**2, 13 * le, -3 * le**2], [54, 13 * le, 156, -22 * le], [-13 * le, -3 * le**2, -22 * le, 4 * le**2]])
nd = 2 * (ne + 1); K = np.zeros((nd, nd)); M = np.zeros((nd, nd))
for e in range(ne):
    s = slice(2 * e, 2 * e + 4); K[s, s] += kel; M[s, s] += mel
M[-2, -2] += m_sign
Kf, Mf = K[2:, 2:], M[2:, 2:]
Lc = np.linalg.cholesky(Mf); Li = np.linalg.inv(Lc)
f_fe = np.sqrt(np.linalg.eigvalsh(Li @ Kf @ Li.T)[0]) / (2 * np.pi)
print(f"first natural frequency: Rayleigh {fn:.3f} Hz, beam FEM {f_fe:.3f} Hz")
assert abs(fn / f_fe - 1) < 0.01
V_lock = f_fe * D / 0.2
print(f"vortex lock-in on the pole at {V_lock:.2f} m/s (St 0.2); the sign plate sheds at f = 0.14 V / {Hs} m, lock-in at {f_fe*Hs/0.14:.1f} m/s")

def rainflow(x):
    """ASTM E1049 three-point rainflow. Returns (ranges, counts) with half cycles counted as 0.5."""
    x = np.asarray(x, float)
    d = np.diff(x); keep = np.r_[True, d[1:] * d[:-1] < 0, True] if len(x) > 2 else np.ones(len(x), bool)
    x = x[np.r_[True, np.diff(x) != 0]] if len(x) > 1 else x
    d = np.diff(x); tp = [x[0]] + [x[i] for i in range(1, len(x) - 1) if d[i - 1] * d[i] < 0] + [x[-1]]
    st, out = [], []
    for p in tp:
        st.append(p)
        while len(st) >= 3:
            Xr, Yr = abs(st[-1] - st[-2]), abs(st[-2] - st[-3])
            if Xr < Yr: break
            if len(st) == 3: out.append((Yr, 0.5)); st.pop(0)
            else: out.append((Yr, 1.0)); last = st.pop(); st.pop(); st.pop(); st.append(last)
    for i in range(len(st) - 1): out.append((abs(st[i + 1] - st[i]), 0.5))
    r = np.array([o[0] for o in out]); c = np.array([o[1] for o in out])
    return r, c

r, c = rainflow([-2, 1, -3, 5, -1, 3, -4, 4, -2])          # the ASTM E1049 example
tally = {int(k): float(c[r == k].sum()) for k in np.unique(r)}
print("ASTM example:", tally)
assert tally == {3: 0.5, 4: 1.5, 6: 0.5, 8: 1.0, 9: 0.5}

# turbulent wind: Kaimal-like first-order filtered noise, turbulence intensity 0.18, length scale 100 m
rng = np.random.default_rng(9)
fs, T_bin = 4.0, 3600.0
def wind(U, n):
    tau = 100.0 / U; a = np.exp(-1 / (fs * tau)); s = 0.18 * U
    e = rng.standard_normal(n) * s * np.sqrt(1 - a**2); u = np.empty(n); u[0] = 0
    for i in range(1, n): u[i] = a * u[i - 1] + e[i]
    return U + u

# S-N curve, Eurocode 3 style, welded base plate detail category 71: m = 3 down to 5e6 cycles,
# m = 5 down to the cut-off at 1e8 cycles, no damage below the cut-off
dsc, gMf = 71e6, 1.35
def cycles_to_fail(ds, dsc_=None):
    dsc_ = dsc if dsc_ is None else dsc_
    ds = np.asarray(ds, float) * gMf
    dsD, dsL = 0.737 * dsc_, 0.737 * 0.549 * dsc_
    with np.errstate(divide="ignore"):
        N = np.where(ds >= dsD, 2e6 * (dsc_ / ds) ** 3, 5e6 * (dsD / ds) ** 5)
    return np.where(ds < dsL, np.inf, N)

kW, cW = 2.0, 5.5                                          # Weibull wind climate at 4.5 m (assumed)
bins = np.arange(1, 26, 1.0)
p_bin = np.exp(-((bins - 0.5) / cW) ** kW) - np.exp(-((bins + 0.5) / cW) ** kW)
hours = p_bin * 8760
D_year = 0.0
print("\nmean wind  hours/yr  stress cycles/h  largest range MPa  damage/yr")
for U, h in zip(bins, hours):
    s = base_stress(wind(U, int(fs * T_bin)))
    rr, cc = rainflow(s)
    dmg = np.sum(cc / cycles_to_fail(rr)) * h
    D_year += dmg
    if U in (3, 6, 10, 14, 18, 22): print(f"   {U:4.0f}     {h:7.1f}     {cc.sum():7.0f}         {rr.max()/1e6:6.2f}        {dmg:.2e}")
life = 1 / D_year
print(f"buffeting along the wind: Miner damage {D_year:.3e} per year, fatigue life {life:.0f} years")
assert life > 1000

# vortex shedding across the wind (Eurocode 1 style, simplified: the pole sheds, the sign adds no damping)
L_phi = 0.236 * Lp                                         # integral of the squared mode shape, tip = 1
m_e = (m_sign + 0.236 * m_pole) / L_phi                    # equivalent mass per metre
def viv(delta):
    Sc = 2 * delta * m_e / (rho * D**2)
    y = D * 0.13 * 0.6 * 0.7 / (0.2**2 * Sc)               # K = 0.13 cantilever, K_w = 0.6, c_lat = 0.7
    ds = 2 * 3 * E * y * (D / 2) / Lp**2                   # stress range at the base from the tip amplitude
    band = (np.exp(-((0.9 * V_lock) / cW) ** kW) - np.exp(-((1.1 * V_lock) / cW) ** kW)) * 8760   # hours a year within 10 % of lock-in
    n_year = band * 3600 * f_fe
    return Sc, y, ds, band, n_year, n_year / cycles_to_fail(ds)
for name, delta in (("bare welded steel, log decrement 0.012", 0.012), ("with a chain or tuned damper, 0.15", 0.15)):
    Sc, y, ds, band, n_year, Dv = viv(delta)
    print(f"{name}: Scruton {Sc:.1f}, tip amplitude {y*1e3:.2f} mm, stress range {ds/1e6:.2f} MPa, {band:.0f} h/yr near lock-in, {n_year:.2e} cycles/yr, life {('%.1f years' % (1/Dv)) if Dv > 0 else 'unlimited (below the cut-off)'}")
    if delta == 0.012: assert 1 / Dv < 5
    else: assert Dv == 0 or 1 / Dv > 100
