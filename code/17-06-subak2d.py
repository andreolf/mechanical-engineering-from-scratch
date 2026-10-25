"""2D shallow water over Subak-style rice terraces: a first-order finite-volume scheme with
hydrostatic reconstruction (Audusse et al. 2004) and the HLL flux. It is well balanced (a
lake at rest stays at rest), keeps depths non-negative on wet/dry fronts, and conserves
water to round-off. numpy only."""
import numpy as np

g, n_man = 9.81, 0.03        # gravity, Manning roughness of a flooded paddy

# Terrain: 5 terraces of 8 m stepping down 0.4 m each, with 6 cm bunds (dikes) at the downhill edges,
# a 0.5 % cross slope, 40 m x 12 m, 0.5 m cells.
dx = 0.5
Nx, Ny = 80, 24
xc = (np.arange(Nx) + 0.5) * dx
yc = (np.arange(Ny) + 0.5) * dx
X, Y = np.meshgrid(xc, yc)
k = np.minimum((X // 8).astype(int), 4)
Z = -0.4 * k + 0.005 * Y
bund = (X % 8 > 7.5) & (k < 4)
Z = Z + 0.06 * bund

def hll(hL, qnL, qtL, hR, qnR, qtR):
    dry = 1e-6
    uL = np.where(hL > dry, qnL / np.maximum(hL, dry), 0); vL = np.where(hL > dry, qtL / np.maximum(hL, dry), 0)
    uR = np.where(hR > dry, qnR / np.maximum(hR, dry), 0); vR = np.where(hR > dry, qtR / np.maximum(hR, dry), 0)
    cL, cR = np.sqrt(g * hL), np.sqrt(g * hR)
    sL = np.minimum(uL - cL, uR - cR); sR = np.maximum(uL + cL, uR + cR)
    FL = np.array([hL * uL, hL * uL**2 + 0.5 * g * hL**2, hL * uL * vL])
    FR = np.array([hR * uR, hR * uR**2 + 0.5 * g * hR**2, hR * uR * vR])
    UL = np.array([hL, hL * uL, hL * vL]); UR = np.array([hR, hR * uR, hR * vR])
    den = np.where(sR - sL > 1e-12, sR - sL, 1.0)
    Fs = (sR * FL - sL * FR + sL * sR * (UR - UL)) / den
    F = np.where(sL >= 0, FL, np.where(sR <= 0, FR, Fs))
    return np.where((sR - sL > 1e-12), F, 0.0), sL, sR

def face_fluxes(h, qn, qt, z, axis):
    """Fluxes through the faces along one axis, with reflective walls.
    Returns the flux seen by the left cell and by the right cell of every face."""
    def ext(a, sign=1):
        a = np.moveaxis(a, axis, -1)
        return np.concatenate([sign * a[..., :1], a, sign * a[..., -1:]], axis=-1)
    he, qne, qte, ze = ext(h), ext(qn, -1), ext(qt), ext(z)
    hL, hR = he[..., :-1], he[..., 1:]
    zf = np.maximum(ze[..., :-1], ze[..., 1:])
    hLs = np.maximum(0, hL + ze[..., :-1] - zf); hRs = np.maximum(0, hR + ze[..., 1:] - zf)
    rL = np.where(hL > 1e-6, hLs / np.maximum(hL, 1e-6), 0); rR = np.where(hR > 1e-6, hRs / np.maximum(hR, 1e-6), 0)
    F, sL, sR = hll(hLs, qne[..., :-1] * rL, qte[..., :-1] * rL, hRs, qne[..., 1:] * rR, qte[..., 1:] * rR)
    FlL = F.copy(); FlL[1] += 0.5 * g * (hL**2 - hLs**2)   # as seen from the left cell
    FlR = F.copy(); FlR[1] += 0.5 * g * (hR**2 - hRs**2)   # as seen from the right cell
    smax = np.max(np.maximum(abs(sL), abs(sR)))
    mv = lambda A: np.moveaxis(A, -1, axis + 1)
    return mv(FlL), mv(FlR), smax

def step(h, qx, qy, dt_max, src=None, cfl=0.4):
    FxL, FxR, sx = face_fluxes(h, qx, qy, Z, 1)
    FyL, FyR, sy = face_fluxes(h, qy, qx, Z, 0)
    dt = min(dt_max, 0.2, cfl * dx / max(sx, sy, 1e-9))   # 0.2 s cap while the domain is still dry
    dh = -(FxL[0][:, 1:] - FxR[0][:, :-1] + FyL[0][1:, :] - FyR[0][:-1, :]) / dx
    dqx = -(FxL[1][:, 1:] - FxR[1][:, :-1] + FyL[2][1:, :] - FyR[2][:-1, :]) / dx
    dqy = -(FxL[2][:, 1:] - FxR[2][:, :-1] + FyL[1][1:, :] - FyR[1][:-1, :]) / dx
    h = h + dt * dh
    qx, qy = qx + dt * dqx, qy + dt * dqy
    if src is not None:
        h = h + dt * src
    h = np.maximum(h, 0.0)          # only round-off negatives; the scheme is positive at this CFL
    # implicit Manning friction, then zero the momentum of (near) dry cells
    hs = np.maximum(h, 1e-6)
    sp = np.sqrt(qx**2 + qy**2) / hs
    fr = 1 + dt * g * n_man**2 * sp / hs ** (4 / 3)
    qx, qy = qx / fr, qy / fr
    qx[h < 1e-6] = 0; qy[h < 1e-6] = 0
    return h, qx, qy, dt

# 1) Lake at rest: still water on every terrace, with a wet/dry shoreline on the cross slope
eta0 = -0.4 * k + 0.05          # flat surface per terrace, 1 cm below the lowest bund top: a dry strip uphill
h = np.maximum(0, eta0 - Z)
qx = np.zeros_like(h); qy = np.zeros_like(h)
m0 = h.sum() * dx * dx
t = 0
while t < 60:
    h, qx, qy, dt = step(h, qx, qy, 60 - t); t += dt
vmax = np.max(np.sqrt(qx**2 + qy**2))
print(f"lake at rest, 60 s: max |q| = {vmax:.2e} m^2/s, mass change {abs(h.sum()*dx*dx - m0):.2e} m^3, wet cells {np.sum(h > 1e-6)} of {h.size}")
assert vmax < 1e-12

# 2) Irrigation: the terraces start dry; an inlet canal pours 20 L/s into the top corner for 10 min
h = np.zeros((Ny, Nx)); qx = np.zeros_like(h); qy = np.zeros_like(h)
Q = 0.02
src = np.zeros_like(h); src[-2:, :2] = Q / (4 * dx * dx)
t, nstep, worst = 0.0, 0, 0.0
marks, arrive = {}, [None] * 5
for T in (60, 180, 300, 600, 900):
    while t < T - 1e-9:
        h, qx, qy, dt = step(h, qx, qy, T - t, src); t += dt; nstep += 1
        worst = max(worst, abs(h.sum() * dx * dx - Q * t))
        for j in range(5):
            if arrive[j] is None and h[k == j].sum() * dx * dx > 1e-3:
                arrive[j] = t
    vol = [h[k == j].sum() * dx * dx for j in range(5)]
    marks[T] = vol
    print(f"t = {T:3d} s: water {h.sum()*dx*dx:.6f} m^3 (inflow {Q*t:.6f}), per terrace " + " ".join(f"{v:6.3f}" for v in vol)
          + f", wet {np.mean(h > 1e-3)*100:4.1f} % of the area")
print(f"{nstep} steps; worst mass error {worst:.2e} m^3; min depth {h.min():.2e}")
print("first litre on each terrace at t =", ", ".join("never" if a is None else f"{a:.0f} s" for a in arrive))
assert worst < 1e-9 and h.min() >= 0
# The cascade: each terrace receives water only after the one above has filled to its bund
got = [a for a in arrive if a is not None]
assert len(got) >= 3 and got == sorted(got)
np.save("/tmp/p17/subak_h.npy", h)
