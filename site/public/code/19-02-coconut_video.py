"""Coconut eddy, from video to model. A synthetic 'field video' (no real footage was available to
build this lesson) shows a coconut circling behind a 1 m boulder. The pipeline is the one you would
run on real frames: background subtraction, thresholding, centroid tracking, pixels to metres, then
orbit period and residence time. These are compared with a kinematic wake model (Foppl vortices
behind a cylinder, lesson 17.10): steady, and with shedding. numpy only."""
import numpy as np

a, U = 0.5, 0.4                                   # boulder radius m, river speed m/s
x0 = 1.2                                          # vortex position behind the boulder centre
def foppl_y(x):                                   # Foppl curve r - a^2/r = 2y, by bisection
    lo, hi = 1e-6, 5.0
    for _ in range(100):
        y = (lo + hi) / 2; r = np.hypot(x, y)
        lo, hi = (y, hi) if r - a * a / r - 2 * y > 0 else (lo, y)
    return y
z1 = x0 + 1j * foppl_y(x0)
G = 4 * np.pi * U * z1.imag * (1 - a**4 / abs(z1) ** 4)     # Foppl's strength for a stationary pair
w_sh = 2 * np.pi * 0.2 * U / (2 * a)                         # shedding frequency from St = 0.2
rc = 0.0                                                     # vortex core radius: 0 for the Foppl check

def vel(z, t, eps):
    """u + iv of uniform flow past the cylinder plus the vortex pair and their images.
    Shedding is modelled by wobbling the two strengths in antiphase, G (1 +- eps sin wt)."""
    out = U * (1 - a * a / z**2)
    for zv, g in ((z1, -G * (1 + eps * np.sin(w_sh * t))), (np.conj(z1), G * (1 - eps * np.sin(w_sh * t)))):
        d = np.abs(z - zv) ** 2
        core = d / (d + rc**2) if rc else 1.0                     # a smooth vortex core instead of a point
        out = out - 1j * g / (2 * np.pi) * (core / (z - zv) - 1 / (z - a * a / np.conj(zv)))
    return np.conj(out)

# check: with point vortices the steady pair does not move
self_v = vel(z1 + 1e-6, 0, 0) - (-1j * -G / (2 * np.pi) / 1e-6).conjugate()
assert abs(self_v) < 1e-3
rc = 0.25                                                    # then a 25 cm core, like a real eddy

def advect(z, T, eps, dt=0.04, t0=0.0, keep=False):
    z = np.array(z, complex); esc = np.full(z.shape, np.inf); t = t0; path = [z.copy()]
    for _ in range(int(round(T / dt))):
        k1 = vel(z, t, eps); k2 = vel(z + dt / 2 * k1, t + dt / 2, eps); k3 = vel(z + dt / 2 * k2, t + dt / 2, eps); k4 = vel(z + dt * k3, t + dt, eps)
        z = z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4); t += dt
        gone = np.isinf(esc) & ((z.real > 4 * 2 * a) | (abs(z) < a))
        esc[gone] = t - t0; z[gone | ~np.isinf(esc)] = 50.0
        if keep: path.append(z.copy())
    return esc, np.array(path)

# ---------- 1. the synthetic field video: 10 frames per second, 2 cm per pixel ----------
eps_true, fps, px = 0.22, 10, 0.02
rng = np.random.default_rng(12)
start = 0.95 + 0.40j
_, truth = advect([start], 240, eps_true, dt=1 / fps / 2, keep=True)
truth = truth[::2, 0]                                             # positions at the frame times
W, H = 170, 100                                                   # frame covers x 0.6..4.0 m (the 4 D box), y -1..1 m
X0, Y0 = 0.6, -1.0
cols, rows = np.meshgrid(np.arange(W), np.arange(H))
bg = 0.35 + 0.05 * np.sin(cols / 7.0) * np.cos(rows / 5.0)         # water texture
frames = np.empty((len(truth), H, W), np.float32)
for k, z in enumerate(truth):
    f = bg + 0.06 * rng.standard_normal((H, W))                   # ripples and sensor noise
    if z.real < 20:
        cx, cy = (z.real - X0) / px, (z.imag - Y0) / px
        f += 0.5 * np.exp(-((cols - cx) ** 2 + (rows - cy) ** 2) / (2 * 3.0**2))   # a 15 cm coconut
    gl = rng.integers(0, W * H, 3); f.flat[gl] += 0.8                               # sun glints
    frames[k] = f

# ---------- 2. tracking ----------
back = np.median(frames[::10], axis=0)                            # background: median over time
track, pos, vel_px = [], None, 0
for k, f in enumerate(frames):
    d = f - back
    d = (d[:-2, :-2] + d[1:-1, :-2] + d[2:, :-2] + d[:-2, 1:-1] + d[1:-1, 1:-1] + d[2:, 1:-1] + d[:-2, 2:] + d[1:-1, 2:] + d[2:, 2:]) / 9   # 3x3 box blur kills single glints
    if pos is None: win = np.ones_like(d, bool)
    else:
        pr = pos + vel_px                                             # constant-velocity prediction
        win = (np.hypot(cols[1:-1, 1:-1] - pr[0], rows[1:-1, 1:-1] - pr[1]) < 15)
    m = (d > 0.2) & win
    if m.sum() < 5: track.append(None); pos = None; continue
    wts = d[m]
    c = np.array([np.sum(cols[1:-1, 1:-1][m] * wts), np.sum(rows[1:-1, 1:-1][m] * wts)]) / wts.sum()
    vel_px = c - pos if pos is not None else 0; pos = c
    track.append(X0 + c[0] * px + 1j * (Y0 + c[1] * px))
seen = np.array([z is not None for z in track])
meas = np.array([z if z is not None else np.nan for z in track], complex)
err = np.abs(meas[seen] - truth[seen])
print(f"tracked {seen.sum()} of {len(frames)} frames; position error median {np.median(err)*100:.2f} cm, max {err.max()*100:.2f} cm")
assert np.median(err) < 0.02 and err.max() < 0.08

# orbit period: unwrap the angle of the coconut around the vortex centre while it is trapped
ang = np.unwrap(np.angle(meas[seen] - z1))
t_seen = np.arange(len(frames))[seen] / fps
t_res_meas = t_seen[-1] + 1 / fps                                 # it leaves the frame, which is the 4 D box
assert seen[:int(t_res_meas * fps)].mean() > 0.97                 # and the track hardly drops a frame before that
orbits = abs(ang[-1] - ang[0]) / (2 * np.pi)
T_orb_meas = (t_seen[-1] - t_seen[0]) / orbits
print(f"measured: the coconut circles {orbits:.2f} times and leaves the 4 D box after {t_res_meas:.1f} s; mean orbit period {T_orb_meas:.2f} s")

# ---------- 3. the model ----------
_, p0 = advect([meas[0]], 200, 0.0, keep=True)                     # steady model from the measured start
ang0 = np.unwrap(np.angle(p0[:, 0] - z1)); T_orb_model = 200 / (abs(ang0[-1] - ang0[0]) / (2 * np.pi))
esc0, _ = advect(meas[0] + 0.03 * (rng.standard_normal(40) + 1j * rng.standard_normal(40)), 240, 0.0)
print(f"steady model: orbit period {T_orb_model:.2f} s ({(T_orb_model/T_orb_meas-1)*100:+.1f} % vs video); escaped {np.isfinite(esc0).sum()} of 40 in 240 s")
assert abs(T_orb_model / T_orb_meas - 1) < 0.15 and np.isfinite(esc0).sum() == 0     # steady bubble: trapped for ever
ens = meas[0] + 0.03 * (rng.standard_normal(60) + 1j * rng.standard_normal(60))     # 3 cm tracking/release uncertainty
esc, _ = advect(ens, 240, eps_true)
fin = np.sort(np.where(np.isfinite(esc), esc, 1e9))
q10, q50, q90 = np.percentile(fin, [10, 50, 90])
print(f"unsteady model (eps = {eps_true}): {np.isfinite(esc).mean()*100:.0f} % escape within 240 s; residence time 10/50/90 % = {q10:.1f} / {q50:.1f} / {'>240' if q90 > 240 else f'{q90:.1f}'} s")
assert q10 <= t_res_meas <= max(q90, 240)          # the single measured coconut is one draw from the model's spread
