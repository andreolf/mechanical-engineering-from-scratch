"""Finding vortices with the Q-criterion, Q = (|Omega|^2 - |S|^2)/2: positive where rotation
beats strain. Checked on analytic flows: solid-body rotation, pure strain, simple shear, the
Lamb-Oseen vortex (Q > 0 exactly inside the radius of peak swirl), and the 3D Taylor-Green
vortex, where the pressure Poisson identity lap(p)/rho = 2Q is verified. numpy only."""
import numpy as np

def Q_from_grad(G):
    """G[..., i, j] = du_i/dx_j. Returns Q."""
    S = 0.5 * (G + np.swapaxes(G, -1, -2)); W = 0.5 * (G - np.swapaxes(G, -1, -2))
    return 0.5 * (np.sum(W**2, axis=(-1, -2)) - np.sum(S**2, axis=(-1, -2)))

# 1) elementary 2D flows (uniform gradients)
cases = {"solid-body rotation": [[0, -1], [1, 0]], "pure strain": [[1, 0], [0, -1]], "simple shear": [[0, 1], [0, 0]]}
for name, G in cases.items():
    print(f"{name}: Q = {Q_from_grad(np.array(G, float)):+.3f}")
assert Q_from_grad(np.array(cases["solid-body rotation"], float)) == 1.0
assert Q_from_grad(np.array(cases["pure strain"], float)) == -1.0
assert Q_from_grad(np.array(cases["simple shear"], float)) == 0.0     # vorticity alone does not make a vortex

# 2) Lamb-Oseen vortex, by finite differences on a grid
G0, rc = 1.0, 1.0
n = 401; L = 4.0
x = np.linspace(-L, L, n); h = x[1] - x[0]
X, Y = np.meshgrid(x, x, indexing="ij")
R2 = X**2 + Y**2 + 1e-300
ut = G0 / (2 * np.pi) * (1 - np.exp(-R2 / rc**2)) / R2          # u_theta / r
u, v = -ut * Y, ut * X
G = np.empty((n, n, 2, 2))
G[..., 0, 0], G[..., 0, 1] = np.gradient(u, h, h)
G[..., 1, 0], G[..., 1, 1] = np.gradient(v, h, h)
Q = Q_from_grad(G)
r = np.sqrt(R2)
# along the x axis, where Q changes sign
row = Q[n // 2 + 1:, n // 2]; rr = x[n // 2 + 1:]
k = np.where(row < 0)[0][0]
r0 = rr[k - 1] - row[k - 1] * (rr[k] - rr[k - 1]) / (row[k] - row[k - 1])
# radius of peak swirl: d/dr [(1 - e^{-r^2}) / r] = 0, by Newton
rm = 1.1
for _ in range(50):
    f = 2 * rm**2 * np.exp(-rm**2) - (1 - np.exp(-rm**2))
    df = 4 * rm * np.exp(-rm**2) - 4 * rm**3 * np.exp(-rm**2) - 2 * rm * np.exp(-rm**2)
    rm -= f / df
vort = np.gradient(v, h, axis=0) - np.gradient(u, h, axis=1)
w_out = abs(vort[(r > 1.5) & (r < 3.5)]).max() / abs(vort).max()
print(f"Lamb-Oseen: Q > 0 for r < {r0:.4f} r_c; peak swirl at r = {rm:.4f} r_c; analytic Q = (u/r) du/dr changes sign there")
print(f"  outside the core, Q < 0 although the vorticity is not zero (up to {w_out*100:.1f} % of its peak at 1.5 < r < 3.5)")
assert abs(r0 - rm) < 2 * h
assert np.all(Q[(r > 0.2) & (r < 1.0)] > 0) and np.all(Q[(r > 1.25) & (r < 3.5)] < 0)

# 3) Taylor-Green vortex in 3D: u = (sin x cos y cos z, -cos x sin y cos z, 0), p = (cos 2x + cos 2y)(cos 2z + 2)/16
N = 48
s = np.arange(N) * 2 * np.pi / N
X, Y, Z = np.meshgrid(s, s, s, indexing="ij")
U = [np.sin(X) * np.cos(Y) * np.cos(Z), -np.cos(X) * np.sin(Y) * np.cos(Z), 0 * X]
P = (np.cos(2 * X) + np.cos(2 * Y)) * (np.cos(2 * Z) + 2) / 16
k = np.fft.fftfreq(N, 1 / N)
def d(f, ax):                                     # spectral derivative on the periodic box
    K = [k[:, None, None], k[None, :, None], k[None, None, :]][ax]
    return np.real(np.fft.ifftn(1j * K * np.fft.fftn(f)))
G = np.empty((N, N, N, 3, 3))
for i in range(3):
    for j in range(3):
        G[..., i, j] = d(U[i], j)
Q = Q_from_grad(G)
lapP = sum(d(d(P, a), a) for a in range(3))
err = np.max(abs(lapP - 2 * Q))
print(f"Taylor-Green: Q > 0 in {np.mean(Q > 0)*100:.1f} % of the box; max Q {Q.max():.4f}, min {Q.min():.4f}; max |lap p - 2Q| = {err:.1e}")
assert err < 1e-12
# the strongest cores lie on the lines x, y = pi/2 + n pi in the planes z = 0, pi, where the swirl is largest
i = np.unravel_index(np.argmax(Q), Q.shape)
print(f"  Q is largest at (x, y, z) = ({s[i[0]]/np.pi:.3f}, {s[i[1]]/np.pi:.3f}, {s[i[2]]/np.pi:.3f}) pi")
assert abs(np.cos(s[i[2]])) > 0.99 and abs(np.sin(s[i[0]])) > 0.99 and abs(np.sin(s[i[1]])) > 0.99
