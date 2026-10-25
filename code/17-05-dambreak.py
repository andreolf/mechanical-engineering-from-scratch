"""Dam break with the 1D shallow water equations: finite volumes with the HLL flux,
MUSCL (minmod) reconstruction and SSP-RK2, compared with the exact Ritter (dry bed)
and Stoker (wet bed) solutions. numpy only."""
import numpy as np

g = 9.81

def hll(hL, qL, hR, qR):
    """HLL flux for the shallow water equations, safe on dry cells."""
    uL = np.where(hL > 1e-8, qL / np.maximum(hL, 1e-8), 0.0)
    uR = np.where(hR > 1e-8, qR / np.maximum(hR, 1e-8), 0.0)
    cL, cR = np.sqrt(g * hL), np.sqrt(g * hR)
    sL = np.minimum(uL - cL, uR - 2 * cR)      # dry-front estimates (Toro)
    sR = np.maximum(uR + cR, uL + 2 * cL)
    FL = np.array([qL, qL * uL + 0.5 * g * hL**2])
    FR = np.array([qR, qR * uR + 0.5 * g * hR**2])
    UL, UR = np.array([hL, qL]), np.array([hR, qR])
    Fs = (sR * FL - sL * FR + sL * sR * (UR - UL)) / np.maximum(sR - sL, 1e-12)
    return np.where(sL >= 0, FL, np.where(sR <= 0, FR, Fs))

def minmod(a, b):
    return np.where(a * b > 0, np.sign(a) * np.minimum(abs(a), abs(b)), 0.0)

def solve(hl, hr, N, T, L=10.0, cfl=0.45):
    dx = L / N
    x = -L / 2 + (np.arange(N) + 0.5) * dx
    U = np.array([np.where(x < 0, hl, hr), np.zeros(N)])
    def rhs(U):
        Ue = np.concatenate([U[:, :1], U[:, :1], U, U[:, -1:], U[:, -1:]], axis=1)   # outflow ghosts
        s = minmod(Ue[:, 1:-1] - Ue[:, :-2], Ue[:, 2:] - Ue[:, 1:-1])
        UL = Ue[:, 1:-2] + 0.5 * s[:, :-1]
        UR = Ue[:, 2:-1] - 0.5 * s[:, 1:]
        F = hll(UL[0], UL[1], UR[0], UR[1])        # N + 1 faces
        return -(F[:, 1:] - F[:, :-1]) / dx
    t = 0.0
    while t < T - 1e-12:
        h = U[0]
        u = np.where(h > 1e-8, U[1] / np.maximum(h, 1e-8), 0)
        dt = min(cfl * dx / np.max(abs(u) + np.sqrt(g * h)), T - t)
        U1 = U + dt * rhs(U)
        U1[0] = np.maximum(U1[0], 0)
        U = 0.5 * (U + U1 + dt * rhs(U1))
        U[0] = np.maximum(U[0], 0)
        t += dt
    return x, U, dx

def ritter(x, t, h0):
    c0 = np.sqrt(g * h0)
    h = np.where(x < -c0 * t, h0, (2 * c0 - x / t) ** 2 / (9 * g))
    return np.where(x > 2 * c0 * t, 0.0, h)

def stoker_state(hl, hr):
    """Middle depth and shock speed for a wet-bed dam break, by bisection."""
    f = lambda hm: 2 * (np.sqrt(g * hl) - np.sqrt(g * hm)) - (hm - hr) * np.sqrt(0.5 * g * (hm + hr) / (hm * hr))
    a, b = hr, hl
    for _ in range(200):
        m = 0.5 * (a + b)
        a, b = (m, b) if f(m) > 0 else (a, m)
    hm = 0.5 * (a + b)
    um = 2 * (np.sqrt(g * hl) - np.sqrt(g * hm))
    return hm, um, hm * um / (hm - hr)

def stoker(x, t, hl, hr):
    hm, um, s = stoker_state(hl, hr)
    cl, cm = np.sqrt(g * hl), np.sqrt(g * hm)
    h = np.where(x < -cl * t, hl, (2 * cl - x / t) ** 2 / (9 * g))
    h = np.where(x >= (um - cm) * t, hm, h)
    return np.where(x > s * t, hr, h)

T, h0 = 0.5, 1.0
c0 = np.sqrt(g * h0)
x1mm = T * (2 * c0 - np.sqrt(9 * g * 1e-3))
print(f"Ritter: h0 = 1 m, c0 = {c0:.4f} m/s, at t = {T}: rarefaction head x = {-c0*T:.4f}, front x = {2*c0*T:.4f}, exact 1 mm contour {x1mm:.4f}, depth at the dam 4h0/9 = {4/9:.4f}")
errs = []
for N in (200, 400, 800, 1600):
    x, U, dx = solve(h0, 0.0, N, T)
    e = np.sum(abs(U[0] - ritter(x, T, h0))) * dx
    wet = x[U[0] > 1e-3]
    mass = np.sum(U[0]) * dx
    errs.append(e)
    print(f"  N = {N:5d}: L1 error in h {e:.5f}, front (h > 1 mm) at {wet.max():.4f}, h at dam {np.interp(0, x, U[0]):.4f}, mass {mass:.10f}")
    assert abs(mass - 5.0) < 1e-10          # water is conserved exactly (no outflow yet)
    assert U[0].min() >= 0
orders = [np.log2(errs[i] / errs[i + 1]) for i in range(3)]
print("  observed order of the L1 error:", ", ".join(f"{o:.2f}" for o in orders))
assert errs[-1] < 0.01 and all(o > 0.6 for o in orders)
x, U, dx = solve(h0, 0.0, 1600, T)
assert abs(np.interp(0, x, U[0]) - 4 / 9) < 0.005

hl, hr = 1.0, 0.1
hm, um, s = stoker_state(hl, hr)
print(f"Stoker: hl = 1, hr = 0.1: middle depth {hm:.4f} m, velocity {um:.4f} m/s, bore speed {s:.4f} m/s, bore at x = {s*T:.4f}")
x, U, dx = solve(hl, hr, 800, T)
e = np.sum(abs(U[0] - stoker(x, T, hl, hr))) * dx
i = np.argmin(abs(x - 0.5 * (um - np.sqrt(g * hm) + s) * T))
print(f"  N = 800: L1 error {e:.5f}, plateau depth {U[0][i]:.4f}")
xs = x[np.argmax(U[0] < 0.5 * (hm + hr))]
print(f"  computed bore position {xs:.4f}")
assert abs(U[0][i] - hm) < 2e-3 and abs(xs - s * T) < 0.03 and e < 0.01
