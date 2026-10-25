"""Lattice Boltzmann flows: body-force-driven Poiseuille flow in a channel with half-way
bounce-back walls and Guo forcing, against the exact parabola. numpy only."""
import numpy as np

c = np.array([[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]])
w = np.array([4 / 9] + [1 / 9] * 4 + [1 / 36] * 4)
opp = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])
cs2 = 1 / 3

def feq(rho, U):
    cu = np.einsum("xya,ia->xyi", U, c)
    uu = np.sum(U**2, -1)[..., None]
    return w * rho[..., None] * (1 + cu / cs2 + cu**2 / (2 * cs2**2) - uu / (2 * cs2))

def poiseuille(tau, Ny=24, g=1e-6, Nx=3, tol=1e-12, maxit=200000):
    """Channel of Ny fluid nodes; walls half a cell outside the first and last rows."""
    G = np.array([g, 0.0])
    F = feq(np.ones((Nx, Ny)), np.zeros((Nx, Ny, 2)))
    cG = c @ G
    old = None
    for it in range(maxit):
        rho = F.sum(-1)
        U = (F @ c + 0.5 * G) / rho[..., None]              # Guo: half the force in the velocity
        cu = np.einsum("xya,ia->xyi", U, c)
        uG = (U @ G)[..., None]
        S = (1 - 0.5 / tau) * w * ((cG - uG) / cs2 + cu * cG / cs2**2)     # Guo forcing term
        Fp = F - (F - feq(rho, U)) / tau + S
        F = np.empty_like(Fp)
        for i in range(9):
            F[..., i] = np.roll(Fp[..., i], shift=tuple(c[i]), axis=(0, 1))
        # half-way bounce-back: populations that would leave through a wall come back reversed
        for i in range(9):
            if c[i, 1] == 1:      # moving up, left through the top wall, re-enter at the top row as opp
                F[:, -1, opp[i]] = Fp[:, -1, i]
            if c[i, 1] == -1:
                F[:, 0, opp[i]] = Fp[:, 0, i]
        if it % 1000 == 0:
            ux = U[1, :, 0].copy()
            if old is not None and np.max(abs(ux - old)) < tol * np.max(abs(ux)) * 1000:
                break
            old = ux
    nu = cs2 * (tau - 0.5)
    y = np.arange(Ny) + 0.5
    exact = g / (2 * nu) * y * (Ny - y)
    err = np.sqrt(np.sum((ux - exact) ** 2) / np.sum(exact**2))
    mass = F.sum() / (Nx * Ny)
    return ux, exact, err, it, mass

for tau in (0.6, 0.8, np.sqrt(3 / 16) + 0.5, 1.2, 1.5):
    ux, ex, err, it, mass = poiseuille(tau)
    print(f"tau = {tau:.4f}: centreline u {ux.max():.6e} vs exact {ex.max():.6e}; relative L2 error {err*100:.4f} %; {it} steps; mean density {mass:.12f}")
    assert abs(mass - 1) < 1e-9
    if tau < 1.3:
        assert err < 0.01
    else:
        assert err > 0.01   # large tau: the bounce-back wall slips by O((tau - 1/2)^2 / H^2) and the 1 % target is lost
    if abs(tau - 0.933) < 0.01:
        assert err < 1e-6   # BGK + half-way bounce-back is exact for Poiseuille at this tau
# resolution at fixed tau = 0.8
for Ny in (6, 12, 24):
    ux, ex, err, it, mass = poiseuille(0.8, Ny=Ny, g=1e-6 * (24 / Ny) ** 2)
    print(f"Ny = {Ny:2d}, tau = 0.8: relative L2 error {err*100:.4f} %")
