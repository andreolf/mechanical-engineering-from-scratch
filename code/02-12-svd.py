"""SVD: geometry checks, low-rank denoising, and why not to go through A^T A."""
import numpy as np


def svd_via_ata(A):
    w, V = np.linalg.eigh(A.T @ A)
    order = np.argsort(w)[::-1]
    return np.sqrt(np.clip(w[order], 0, None)), V[:, order]


def truncate(A, k):
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    return (U[:, :k] * s[:k]) @ Vt[:k]


if __name__ == "__main__":
    A = np.array([[3, 0], [4, 5.0]])
    s = np.linalg.svd(A, compute_uv=False)
    assert np.allclose(s, [45 ** 0.5, 5 ** 0.5]) and abs(s[0] / s[1] - 3) < 1e-12
    # the unit circle maps to an ellipse whose longest radius is sigma_1
    t = np.linspace(0, 2 * np.pi, 20001)
    r = np.linalg.norm(A @ np.vstack([np.cos(t), np.sin(t)]), axis=0)
    assert abs(r.max() - s[0]) < 1e-6 and abs(r.min() - s[1]) < 1e-6
    # low-rank temperature field with noise
    x = np.linspace(0, 1, 100); X, Y = np.meshgrid(x, x)
    T = 20 + 60 * np.exp(-((X - 0.3) ** 2 + (Y - 0.6) ** 2) / 0.05) + 10 * X * Y
    Tn = T + np.random.default_rng(0).normal(0, 0.5, T.shape)
    rms = lambda E: np.sqrt(np.mean(E ** 2))
    sv = np.linalg.svd(Tn, compute_uv=False)
    print("leading singular values:", np.round(sv[:5], 1))
    print(f"RMS error: noisy {rms(Tn - T):.3f} K, rank-3 {rms(truncate(Tn, 3) - T):.3f} K")
    assert np.linalg.matrix_rank(T) == 3 and rms(truncate(Tn, 3) - T) < 0.3 * rms(Tn - T)
    # Eckart-Young: 2-norm error of the rank-k truncation equals sigma_{k+1}
    rng = np.random.default_rng(1)
    B = rng.standard_normal((30, 20)); sb = np.linalg.svd(B, compute_uv=False)
    for k in (1, 5, 10):
        assert abs(np.linalg.norm(B - truncate(B, k), 2) - sb[k]) < 1e-10
    # small singular values are lost through A^T A
    U, _ = np.linalg.qr(rng.standard_normal((6, 6))); V, _ = np.linalg.qr(rng.standard_normal((6, 6)))
    true = np.array([1, 1e-2, 1e-4, 1e-6, 1e-9, 1e-12])
    C = U @ np.diag(true) @ V.T
    s_lib, s_ata = np.linalg.svd(C, compute_uv=False), svd_via_ata(C)[0]
    print("relative error of smallest sigma: library", f"{abs(s_lib[-1]-1e-12)/1e-12:.1e},", "via A^T A", f"{abs(s_ata[-1]-1e-12)/1e-12:.1e}")
    assert abs(s_lib[-1] - 1e-12) < 1e-4 * 1e-12 and abs(s_ata[-1] - 1e-12) > 1e-12   # library: 6 digits; A^T A: none
