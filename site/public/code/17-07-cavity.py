"""Lid-driven cavity at Re = 100 with the streamfunction-vorticity formulation:
explicit vorticity transport (central differences), Thom's wall vorticity, and a fast
sine-transform Poisson solver for the streamfunction. Compared with Ghia, Ghia & Shin (1982).
numpy only."""
import numpy as np

def dst1(a, axis):
    """Type-I discrete sine transform along an axis, via the FFT of an odd extension."""
    a = np.moveaxis(a, axis, -1)
    n = a.shape[-1]
    z = np.zeros(a.shape[:-1] + (1,))
    ext = np.concatenate([z, a, z, -a[..., ::-1]], axis=-1)
    out = -np.fft.fft(ext, axis=-1).imag[..., 1:n + 1] / 2
    return np.moveaxis(out, -1, axis)

def poisson_dirichlet(f, h):
    """Solve the 5-point Laplacian lap(u) = f on the interior with u = 0 on the boundary."""
    n = f.shape[0]
    k = np.arange(1, n + 1)
    lam = (2 * np.cos(np.pi * k / (n + 1)) - 2) / h**2
    F = dst1(dst1(f, 0), 1)
    U = F / (lam[:, None] + lam[None, :])
    return dst1(dst1(U, 0), 1) * (2 / (n + 1)) ** 2

# check the Poisson solver on a manufactured solution
n = 31; h = 1 / (n + 1); s = np.arange(1, n + 1) * h
XX, YY = np.meshgrid(s, s, indexing="ij")
ue = np.sin(np.pi * XX) * np.sin(2 * np.pi * YY)
lap = np.zeros_like(ue); up = np.pad(ue, 1)
lap = (up[2:, 1:-1] + up[:-2, 1:-1] + up[1:-1, 2:] + up[1:-1, :-2] - 4 * ue) / h**2
assert np.max(abs(poisson_dirichlet(lap, h) - ue)) < 1e-12

def cavity(N=64, Re=100.0, U=1.0, tol=1e-6, tmax=60.0):
    h = 1.0 / N
    dt = min(0.2 * h * h * Re, 0.5 * h / U)
    psi = np.zeros((N + 1, N + 1)); w = np.zeros((N + 1, N + 1))   # index [i, j] = (x, y)
    t, it = 0.0, 0
    while t < tmax:
        # wall vorticity (Thom): w = -2 psi_adjacent / h^2, lid adds -2U/h
        w[0, :] = -2 * psi[1, :] / h**2
        w[-1, :] = -2 * psi[-2, :] / h**2
        w[:, 0] = -2 * psi[:, 1] / h**2
        w[:, -1] = -2 * psi[:, -2] / h**2 - 2 * U / h
        u = (psi[1:-1, 2:] - psi[1:-1, :-2]) / (2 * h)
        v = -(psi[2:, 1:-1] - psi[:-2, 1:-1]) / (2 * h)
        wx = (w[2:, 1:-1] - w[:-2, 1:-1]) / (2 * h)
        wy = (w[1:-1, 2:] - w[1:-1, :-2]) / (2 * h)
        lapw = (w[2:, 1:-1] + w[:-2, 1:-1] + w[1:-1, 2:] + w[1:-1, :-2] - 4 * w[1:-1, 1:-1]) / h**2
        dw = -u * wx - v * wy + lapw / Re
        w[1:-1, 1:-1] += dt * dw
        psi[1:-1, 1:-1] = poisson_dirichlet(-w[1:-1, 1:-1], h)
        t += dt; it += 1
        if it % 200 == 0 and np.max(abs(dw)) < tol:
            break
    return psi, w, h, t, it, np.max(abs(dw))

ghia_y = np.array([0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813, 0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609, 0.9688, 0.9766])
ghia_u = np.array([-0.03717, -0.04192, -0.04775, -0.06434, -0.10150, -0.15662, -0.21090, -0.20581, -0.13641, 0.00332, 0.23151, 0.68717, 0.73722, 0.78871, 0.84123])

for N in (32, 64):
    psi, w, h, t, it, res = cavity(N)
    y = np.linspace(0, 1, N + 1)
    uc = np.gradient(psi[N // 2, :], h)               # u = dpsi/dy on x = 0.5
    dev = np.max(abs(np.interp(ghia_y, y, uc) - ghia_u))
    i, j = np.unravel_index(np.argmin(psi), psi.shape)
    # sub-cell vortex centre: parabola through the minimum in each direction
    di = 0.5 * (psi[i - 1, j] - psi[i + 1, j]) / (psi[i - 1, j] - 2 * psi[i, j] + psi[i + 1, j])
    dj = 0.5 * (psi[i, j - 1] - psi[i, j + 1]) / (psi[i, j - 1] - 2 * psi[i, j] + psi[i, j + 1])
    xc, yc = (i + di) * h, (j + dj) * h
    print(f"N = {N}: steady after {it} steps (t = {t:.1f}, residual {res:.1e}); psi_min {psi.min():.6f} at ({xc:.4f}, {yc:.4f}); "
          f"max |u - Ghia| on the centreline {dev:.4f}; u_min {uc.min():.4f}")
print("Ghia et al. (129 x 129): psi_min -0.103423 at (0.6172, 0.7344); u_min -0.21090")
assert dev < 0.01
assert abs(xc - 0.6172) < h and abs(yc - 0.7344) < h
assert abs(psi.min() + 0.103423) < 0.002
