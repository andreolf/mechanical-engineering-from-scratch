"""Lattice Boltzmann theory on the D2Q9 lattice: the lattice's isotropy, the moments of
the equilibrium distribution, and the BGK viscosity nu = cs^2 (tau - 1/2) checked by the
decay of a shear wave. numpy only."""
import numpy as np

c = np.array([[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]])
w = np.array([4 / 9] + [1 / 9] * 4 + [1 / 36] * 4)
cs2 = 1 / 3

# 1) lattice tensors up to fourth order
T0 = w.sum()
T1 = w @ c
T2 = np.einsum("i,ia,ib->ab", w, c, c)
T3 = np.einsum("i,ia,ib,ic->abc", w, c, c, c)
T4 = np.einsum("i,ia,ib,ic,id->abcd", w, c, c, c, c)
d = np.eye(2)
iso4 = cs2**2 * (np.einsum("ab,cd->abcd", d, d) + np.einsum("ac,bd->abcd", d, d) + np.einsum("ad,bc->abcd", d, d))
print(f"sum w = {T0}, sum w c = {T1}, sum w c c = {T2.tolist()} (cs^2 I), max |sum w c c c| = {abs(T3).max()}, "
      f"max |4th-order tensor - isotropic| = {abs(T4 - iso4).max():.1e}")
assert abs(T0 - 1) < 1e-15 and abs(T1).max() < 1e-15 and abs(T2 - cs2 * d).max() < 1e-15
assert abs(T3).max() < 1e-15 and abs(T4 - iso4).max() < 1e-15

def feq(rho, u):
    cu = c @ u
    return w * rho * (1 + cu / cs2 + cu**2 / (2 * cs2**2) - (u @ u) / (2 * cs2))

# 2) moments of the equilibrium: density, momentum and momentum flux are exact
rho, u = 1.2, np.array([0.08, -0.05])
f = feq(rho, u)
m0, m1 = f.sum(), f @ c
Pi = np.einsum("i,ia,ib->ab", f, c, c)
Q = np.einsum("i,ia,ib,ic->abc", f, c, c, c)
Q_exact = rho * cs2 * (np.einsum("a,bc->abc", u, d) + np.einsum("b,ac->abc", u, d) + np.einsum("c,ab->abc", u, d)) + rho * np.einsum("a,b,c->abc", u, u, u)
print(f"rho = {m0:.15f}, rho u = {m1}, Pi - (rho u u + rho cs^2 I) = {abs(Pi - rho*np.outer(u,u) - rho*cs2*d).max():.1e}")
print(f"third moment error against the continuous Maxwellian: {abs(Q - Q_exact).max():.2e} (rho u^3 = {rho*abs(u).max()**3:.2e}): the O(Ma^3) defect")
assert abs(m0 - rho) < 1e-15 and abs(m1 - rho * u).max() < 1e-15
assert abs(Pi - rho * np.outer(u, u) - rho * cs2 * d).max() < 1e-15
assert abs(abs(Q - Q_exact).max() - rho * abs(u[0]) ** 3) < 1e-15        # only the u_x^3 diagonal term is missing
# positivity: the rest population goes negative only at large speeds
umax = [s for s in np.linspace(0, 1, 1001) if (feq(1, np.array([s, 0])) < 0).any()]
print(f"some f_eq < 0 first at |u| = {umax[0]:.3f} along x (Mach {umax[0]/np.sqrt(cs2):.2f})")

# 3) BGK: a decaying shear wave measures the viscosity
def shear_wave(tau, N=48, steps=800, U0=0.01):
    y = np.arange(N)
    k = 2 * np.pi / N
    ux = U0 * np.sin(k * y)[None, :] * np.ones((N, 1))
    U = np.stack([ux, np.zeros_like(ux)], axis=-1)
    F = feq_field(np.ones((N, N)), U)
    amp = []
    for s in range(steps):
        rho = F.sum(-1); U = (F @ c) / rho[..., None]
        F += -(F - feq_field(rho, U)) / tau          # collide
        for i in range(9):                              # stream (periodic)
            F[..., i] = np.roll(F[..., i], shift=tuple(c[i]), axis=(0, 1))
        amp.append(2 / N * np.sum(U[0, :, 0] * np.sin(k * y)))
    amp = np.array(amp)
    t = np.arange(steps)
    rate = -np.polyfit(t[100:800], np.log(amp[100:800]), 1)[0]
    return rate / k**2

def feq_field(rho, U):
    cu = np.einsum("xya,ia->xyi", U, c)
    uu = np.sum(U**2, -1)[..., None]
    return w * rho[..., None] * (1 + cu / cs2 + cu**2 / (2 * cs2**2) - uu / (2 * cs2))

for tau in (0.6, 0.8, 1.0, 1.5):
    nu_m = shear_wave(tau)
    nu_t = cs2 * (tau - 0.5)
    print(f"tau = {tau}: measured nu = {nu_m:.6f}, cs^2 (tau - 1/2) = {nu_t:.6f}, error {abs(nu_m/nu_t-1)*100:.3f} %")
    assert abs(nu_m / nu_t - 1) < 0.01
