"""Grid convergence index (Roache; Celik et al. 2008, the ASME V&V 20 procedure) with the
observed order of accuracy, for unequal refinement ratios. Applied to laminar flow in a
square duct (where the exact answer is known) and to the OpenFOAM step eddy. numpy only."""
import numpy as np

def dst1(a, axis):
    a = np.moveaxis(a, axis, -1); n = a.shape[-1]
    z = np.zeros(a.shape[:-1] + (1,))
    out = -np.fft.fft(np.concatenate([z, a, z, -a[..., ::-1]], axis=-1), axis=-1).imag[..., 1:n + 1] / 2
    return np.moveaxis(out, -1, axis)

def duct_flow_rate(N):
    """Fully developed laminar flow in a unit square duct: lap(w) = -1, w = 0 on the walls,
    5-point differences on N x N cells (N - 1 interior nodes). Returns Q = integral of w (trapezoid)."""
    n, h = N - 1, 1.0 / N
    k = np.arange(1, n + 1)
    lam = (2 * np.cos(np.pi * k / N) - 2) / h**2
    F = dst1(dst1(-np.ones((n, n)), 0), 1)
    w = dst1(dst1(F / (lam[:, None] + lam[None, :]), 0), 1) * (2 / N) ** 2
    return w.sum() * h * h                      # boundary values are zero, so the trapezoid rule is this sum

def duct_exact(terms=200):
    n = np.arange(1, 2 * terms, 2)
    return (1 / 12) * (1 - 192 / np.pi**5 * np.sum(np.tanh(n * np.pi / 2) / n**5))

def gci(h, f, Fs=1.25):
    """h, f: representative cell sizes and solutions, fine first. Returns observed p, extrapolated value,
    relative errors and GCIs (fine and medium), following Celik et al. (2008)."""
    h1, h2, h3 = h; f1, f2, f3 = f
    r21, r32 = h2 / h1, h3 / h2
    e21, e32 = f2 - f1, f3 - f2
    s = np.sign(e32 / e21)
    if s < 0:
        print("  warning: oscillatory convergence")
    p = 2.0
    for _ in range(100):                          # fixed-point iteration for the observed order
        q = np.log((r21**p - s) / (r32**p - s))
        p = abs(np.log(abs(e32 / e21)) + q) / np.log(r21)
    f_ext = (r21**p * f1 - f2) / (r21**p - 1)
    ea21 = abs((f1 - f2) / f1)
    gci21 = Fs * ea21 / (r21**p - 1)
    ea32 = abs((f2 - f3) / f2)
    gci32 = Fs * ea32 / (r32**p - 1)
    return dict(p=p, f_ext=f_ext, ea21=ea21, gci21=gci21, gci32=gci32, ratio=gci32 / (r21**p * gci21))

Qex = duct_exact()
print(f"square duct: exact Q = {Qex:.10f} (series)")

# 1) constant refinement ratio 2
Ns = (16, 32, 64)
Q = [duct_flow_rate(N) for N in Ns]
for N, q in zip(Ns, Q):
    print(f"  N = {N:3d}: Q = {q:.10f}, true relative error {abs(q-Qex)/Qex*100:.5f} %")
g = gci([1 / Ns[2], 1 / Ns[1], 1 / Ns[0]], [Q[2], Q[1], Q[0]])
print(f"  r = 2: observed p = {g['p']:.4f}, extrapolated Q = {g['f_ext']:.10f} (error {abs(g['f_ext']-Qex)/Qex*100:.6f} %), "
      f"GCI fine = {g['gci21']*100:.5f} %, asymptotic check {g['ratio']:.4f}")
assert abs(g["p"] - 2) < 0.05
assert abs(Q[2] - Qex) / Qex < g["gci21"]                      # the band contains the true answer
assert abs(g["ratio"] - 1) < 0.01

# 2) unequal ratios (21, 30, 45 cells: r = 1.5 and 1.43)
Ns = (21, 30, 45)
Q = [duct_flow_rate(N) for N in Ns]
g = gci([1 / Ns[2], 1 / Ns[1], 1 / Ns[0]], [Q[2], Q[1], Q[0]])
print(f"  r = 1.5, 1.43: observed p = {g['p']:.4f}, extrapolated Q = {g['f_ext']:.10f}, GCI fine = {g['gci21']*100:.5f} %, "
      f"true error {abs(Q[2]-Qex)/Qex*100:.5f} %")
assert abs(g["p"] - 2) < 0.1 and abs(Q[2] - Qex) / Qex < g["gci21"]

# 3) the step eddy from the previous lesson (OpenFOAM, three meshes, r = 2)
xr = [4.3089, 4.2615, 4.0679]
g = gci([1, 2, 4], xr)
print(f"step eddy: p = {g['p']:.3f}, x_r extrapolated {g['f_ext']:.4f} H, GCI fine = {g['gci21']*100:.3f} % "
      f"(x_r = {xr[0]:.4f} +/- {g['gci21']*xr[0]:.4f} H), GCI medium = {g['gci32']*100:.3f} %, asymptotic check {g['ratio']:.3f}")
assert 1.9 < g["p"] < 2.2 and g["gci21"] < 0.01 and abs(g["ratio"] - 1) < 0.05

# 4) what goes wrong with too-coarse grids: N = 4, 8, 16 for the duct
Q = [duct_flow_rate(N) for N in (4, 8, 16)]
g = gci([1 / 16, 1 / 8, 1 / 4], [Q[2], Q[1], Q[0]])
print(f"too coarse (4, 8, 16): p = {g['p']:.3f}, asymptotic check {g['ratio']:.3f}")
