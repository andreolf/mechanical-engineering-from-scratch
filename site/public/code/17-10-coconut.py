"""A coconut caught in the eddy behind a rock: particle tracking in the wake of a cylinder.
The same pseudo-spectral, penalised Navier-Stokes solver as the cylinder lesson, with
passive particles advanced by RK2 and bilinear interpolation. At Re = 30 the wake is a
steady recirculation bubble that traps particles; at Re = 100 shedding flushes them out.
numpy only."""
import numpy as np

U, D = 1.0, 1.0
Lx, Ly, Nx, Ny = 12.0, 6.0, 120, 60
h = Lx / Nx
X, Y = np.meshgrid(np.arange(Nx) * h, np.arange(Ny) * h, indexing="ij")
xc, yc = 3.0, Ly / 2
chi = 0.5 * (1 - np.tanh((np.hypot(X - xc, Y - yc) - D / 2) / (0.5 * h)))
fr = np.clip((X - (Lx - 2.0)) / 1.0, 0, 1)
fringe = np.where(X > Lx - 2.0, np.sin(0.5 * np.pi * fr) ** 2, 0.0)
kx = 2 * np.pi * np.fft.fftfreq(Nx, h); ky = 2 * np.pi * np.fft.rfftfreq(Ny, h)
KX, KY = np.meshgrid(kx, ky, indexing="ij")
K2 = KX**2 + KY**2; K2i = np.where(K2 > 0, 1 / np.where(K2 > 0, K2, 1), 0)
dealias = (abs(KX) < (2 / 3) * abs(kx).max()) & (abs(KY) < (2 / 3) * ky.max())
F, Fi = (lambda a: np.fft.rfft2(a)), (lambda a: np.fft.irfft2(a, s=(Nx, Ny)))

def project(uh, vh):
    d = (KX * uh + KY * vh) * K2i
    return uh - KX * d, vh - KY * d

def interp(f, px, py):
    """Bilinear interpolation of a periodic grid field at particle positions."""
    gx, gy = px / h, py / h
    i0, j0 = np.floor(gx).astype(int), np.floor(gy).astype(int)
    a, b = gx - i0, gy - j0
    i0, j0 = i0 % Nx, j0 % Ny
    i1, j1 = (i0 + 1) % Nx, (j0 + 1) % Ny
    return (1 - a) * (1 - b) * f[i0, j0] + a * (1 - b) * f[i1, j0] + (1 - a) * b * f[i0, j1] + a * b * f[i1, j1]

def simulate(Re, t_release=60.0, t_track=100.0, dt=0.02, seed=1):
    nu = U * D / Re
    u = 1 - chi; v = 0.05 * np.sin(2 * np.pi * X / Lx) * np.exp(-((Y - yc) ** 2))
    uh, vh = project(F(u), F(v))
    visc = 1 / (1 + nu * K2 * dt)
    No = None
    rng = np.random.default_rng(seed)
    # 200 coconuts released in the near wake, 0.6 D to 1.4 D behind the centre
    px = xc + 0.6 + 0.8 * rng.random(200); py = yc + 0.6 * (rng.random(200) - 0.5)
    t, tracking, wake_u = 0.0, False, None
    while t < t_release + t_track - 1e-9:
        ux, uy, vx, vy = Fi(1j * KX * uh), Fi(1j * KY * uh), Fi(1j * KX * vh), Fi(1j * KY * vh)
        u, v = Fi(uh), Fi(vh)
        N = (F(u * ux + v * uy) * dealias, F(u * vx + v * vy) * dealias)
        if No is None: No = N
        uh = (uh - dt * (1.5 * N[0] - 0.5 * No[0])) * visc
        vh = (vh - dt * (1.5 * N[1] - 0.5 * No[1])) * visc
        No = N
        u, v = Fi(uh), Fi(vh)
        a = dt * (1e4 * chi + 20.0 * fringe)
        u = (u + dt * 20.0 * fringe * U) / (1 + a); v = v / (1 + a)
        uh, vh = project(F(u), F(v))
        u, v = Fi(uh), Fi(vh)
        t += dt
        if t >= t_release:
            # RK2 (midpoint) in the current velocity field
            kx1, ky1 = interp(u, px, py), interp(v, px, py)
            mx, my = px + 0.5 * dt * kx1, py + 0.5 * dt * ky1
            px, py = px + dt * interp(u, mx, my), py + dt * interp(v, mx, my)
        if wake_u is None and t >= t_release:
            wake_u = u[:, int(yc / h)].copy()
    inwake = (px > xc) & (px < xc + 4 * D) & (abs(py - yc) < 1.5 * D)
    return u, v, px, py, inwake, wake_u

for Re in (30, 100):
    u, v, px, py, inwake, wu = simulate(Re)
    x = np.arange(Nx) * h
    behind = (x > xc + 0.5) & (x < xc + 6)
    neg = x[behind][wu[behind] < 0]
    Lb = (neg.max() - (xc + 0.5)) if len(neg) else 0.0
    print(f"Re = {Re}: recirculation bubble (u < 0 on the centreline) ends {Lb:.2f} D behind the cylinder; "
          f"after 100 time units, {inwake.sum()} of 200 coconuts are still in the near wake")
    if Re == 30:
        trapped30, L30 = inwake.mean(), Lb
    else:
        trapped100 = inwake.mean()
St = 0.17
print(f"100 time units is {100*St:.1f} shedding periods at Re 100 (St about {St}, as computed in the cylinder lesson)")
assert trapped30 > 0.95 and trapped100 < 0.1 and 1.0 < L30 < 3.5
