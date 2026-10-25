"""Chorin's projection method on a staggered (MAC) grid: the lid-driven cavity at Re = 100
in primitive variables. The pressure Poisson equation with Neumann walls is solved exactly
by diagonalising the 1D Neumann Laplacian, so the projected field is divergence-free to
round-off. numpy only."""
import numpy as np

def neumann_eig(N, h):
    L = (np.diag(-2.0 * np.ones(N)) + np.diag(np.ones(N - 1), 1) + np.diag(np.ones(N - 1), -1)) / h**2
    L[0, 0] = L[-1, -1] = -1 / h**2
    lam, V = np.linalg.eigh(L)
    return lam, V

def run(N=64, Re=100.0, Ulid=1.0, tmax=60.0, tol=1e-6):
    h = 1.0 / N
    dt = min(0.2 * h * h * Re, 0.5 * h / Ulid)
    lam, V = neumann_eig(N, h)
    den = lam[:, None] + lam[None, :]
    k0 = np.argmin(abs(lam))                          # the constant mode (eigenvalue 0): pressure is defined up to a constant
    den[k0, k0] = np.inf
    U = np.zeros((N + 1, N + 2))                      # u at (i h, (j + 1/2) h), ghost rows j = -1 and N
    W = np.zeros((N + 2, N + 1))                      # v at ((i + 1/2) h, j h), ghost columns
    def ghosts():
        U[:, 0] = -U[:, 1]; U[:, -1] = 2 * Ulid - U[:, -2]
        W[0, :] = -W[1, :]; W[-1, :] = -W[-2, :]
    t, it, divmax = 0.0, 0, 0.0
    while t < tmax:
        ghosts()
        uc = 0.5 * (U[1:, 1:-1] + U[:-1, 1:-1])
        vc = 0.5 * (W[1:-1, 1:] + W[1:-1, :-1])
        uv = 0.5 * (U[:, 1:] + U[:, :-1]) * 0.5 * (W[1:, :] + W[:-1, :])     # at cell corners
        lu = (U[2:, 1:-1] + U[:-2, 1:-1] + U[1:-1, 2:] + U[1:-1, :-2] - 4 * U[1:-1, 1:-1]) / h**2
        lv = (W[2:, 1:-1] + W[:-2, 1:-1] + W[1:-1, 2:] + W[1:-1, :-2] - 4 * W[1:-1, 1:-1]) / h**2
        Fu = -(uc[1:] ** 2 - uc[:-1] ** 2) / h - (uv[1:-1, 1:] - uv[1:-1, :-1]) / h + lu / Re
        Fv = -(vc[:, 1:] ** 2 - vc[:, :-1] ** 2) / h - (uv[1:, 1:-1] - uv[:-1, 1:-1]) / h + lv / Re
        U[1:-1, 1:-1] += dt * Fu                      # 1) predictor, ignoring pressure
        W[1:-1, 1:-1] += dt * Fv
        div = (U[1:, 1:-1] - U[:-1, 1:-1] + W[1:-1, 1:] - W[1:-1, :-1]) / h
        divstar = np.max(abs(div))
        p = V @ ((V.T @ (div / dt) @ V) / den) @ V.T   # 2) solve lap p = div u* / dt
        U[1:-1, 1:-1] -= dt * (p[1:] - p[:-1]) / h       # 3) project
        W[1:-1, 1:-1] -= dt * (p[:, 1:] - p[:, :-1]) / h
        div = (U[1:, 1:-1] - U[:-1, 1:-1] + W[1:-1, 1:] - W[1:-1, :-1]) / h
        divmax = max(divmax, np.max(abs(div)))
        t += dt; it += 1
        if it % 200 == 0 and max(np.max(abs(Fu - (p[1:] - p[:-1]) / h)), np.max(abs(Fv - (p[:, 1:] - p[:, :-1]) / h))) < tol:
            break
    ghosts()
    return U, W, p, h, t, it, divmax, divstar

ghia_y = np.array([0.0547, 0.0625, 0.0703, 0.1016, 0.1719, 0.2813, 0.4531, 0.5000, 0.6172, 0.7344, 0.8516, 0.9531, 0.9609, 0.9688, 0.9766])
ghia_u = np.array([-0.03717, -0.04192, -0.04775, -0.06434, -0.10150, -0.15662, -0.21090, -0.20581, -0.13641, 0.00332, 0.23151, 0.68717, 0.73722, 0.78871, 0.84123])

N = 64
U, W, p, h, t, it, divmax, divstar = run(N)
yc = (np.arange(N) + 0.5) * h
uc = U[N // 2, 1:-1]                                  # u nodes lie exactly on x = 0.5
dev = np.max(abs(np.interp(ghia_y, yc, uc) - ghia_u))
psi = np.concatenate([np.zeros((N + 1, 1)), np.cumsum(U[:, 1:-1] * h, axis=1)], axis=1)   # psi at corners
i, j = np.unravel_index(np.argmin(psi), psi.shape)
print(f"N = {N}: steady after {it} steps (t = {t:.1f}); max |div u| after projection, over all steps: {divmax:.2e} (before, last step: {divstar:.2e})")
print(f"psi_min {psi.min():.6f} at ({i*h:.4f}, {j*h:.4f}) (grid node); max |u - Ghia| on x = 0.5: {dev:.4f}; u_min {uc.min():.4f}")
print(f"pressure range {p.max()-p.min():.4f} (rho = 1); the lid's corner singularities hold the extremes: max at x = {(np.unravel_index(np.argmax(p), p.shape)[0]+0.5)*h:.3f}")
assert divmax < 1e-8
assert dev < 0.01 and abs(psi.min() + 0.103423) < 0.002
