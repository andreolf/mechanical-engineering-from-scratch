"""Experimental modal analysis: a simulated hammer test on a 3-storey lab frame, FRF estimation and peak picking."""
import math
import numpy as np
from scipy.linalg import eigh, expm

m, k, zeta = 2.0, 8000.0, 0.01
M = np.eye(3) * m
K = k * np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 1]])
w2, Phi = eigh(K, M); w = np.sqrt(w2)
C = M @ Phi @ np.diag(2 * zeta * w) @ Phi.T @ M         # 1 % damping in every mode


def hammer_test(fs=1024, T=64.0, tap_dof=2, meas_dof=2, noise=0.0, seed=0):
    """Exact zero-order-hold discretisation of the state equations, a 2 ms half-sine 50 N tap, displacement output."""
    dt = 1 / fs; n = int(T * fs)
    A = np.block([[np.zeros((3, 3)), np.eye(3)], [-np.linalg.solve(M, K), -np.linalg.solve(M, C)]])
    B = np.zeros((6, 3)); B[3:, :] = np.linalg.inv(M)
    E = expm(np.block([[A, B], [np.zeros((3, 9))]]) * dt); Ad, Bd = E[:6, :6], E[:6, 6:]
    t = np.arange(n) * dt
    F = np.where(t < 0.002, 50 * np.sin(math.pi * t / 0.002), 0.0)
    s = np.zeros(6); x = np.empty(n)
    for i in range(n):
        x[i] = s[meas_dof]; u = np.zeros(3); u[tap_dof] = F[i]; s = Ad @ s + Bd @ u
    x = x + np.random.default_rng(seed).normal(0, noise, n)
    return t, F, x


def frf(F, x, fs):
    H = np.fft.rfft(x) / np.fft.rfft(F); f = np.fft.rfftfreq(len(x), 1 / fs)
    return f, H


def pick_peaks(f, H, fmin=1.0, fmax=40.0, rel=0.005):
    a = np.abs(H); out = []
    for i in range(1, len(a) - 1):
        win = (f > f[i] - 0.5) & (f < f[i] + 0.5)          # a real mode is the largest value within +-0.5 Hz
        if fmin < f[i] < fmax and a[i] >= a[win].max() and a[i] > rel * a[(f > fmin) & (f < fmax)].max():
            la = np.log(a[i-1:i+2]); d = 0.5 * (la[0] - la[2]) / (la[0] - 2 * la[1] + la[2])
            fp = f[i] + d * (f[1] - f[0]); peak = math.exp(la[1] - 0.25 * (la[0] - la[2]) * d)
            # half-power points by linear interpolation either side
            j = i
            while a[j] > peak / math.sqrt(2): j -= 1
            fl = f[j] + (peak / math.sqrt(2) - a[j]) / (a[j+1] - a[j]) * (f[1] - f[0])
            j = i
            while a[j] > peak / math.sqrt(2): j += 1
            fh = f[j-1] + (a[j-1] - peak / math.sqrt(2)) / (a[j-1] - a[j]) * (f[1] - f[0])
            out.append((fp, (fh - fl) / (2 * fp)))
    return out


if __name__ == "__main__":
    fm = w / (2 * math.pi)
    print("model natural frequencies (Hz):", np.round(fm, 4))
    t, F, x = hammer_test(noise=2e-7)
    f, H = frf(F, x, 1024)
    found = pick_peaks(f, H)
    for (fp, zp), fe in zip(found, fm):
        print(f"identified {fp:.4f} Hz (model {fe:.4f}, error {abs(fp/fe-1)*100:.3f} %), damping {zp*100:.3f} %")
    assert len(found) == 3 and all(abs(fp / fe - 1) < 0.01 for (fp, _), fe in zip(found, fm))
    assert all(abs(zp / zeta - 1) < 0.1 for _, zp in found)
    # a short record smears the peaks: 4 s gives 0.25 Hz resolution
    t, F, x = hammer_test(T=4.0)
    f, H = frf(F, x, 1024); short = pick_peaks(f, H)
    print("4 s record:", ", ".join(f"{fp:.3f} Hz / {zp*100:.2f} %" for fp, zp in short))
