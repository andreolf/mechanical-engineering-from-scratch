"""Loop versus vectorised force evaluation, plus broadcasting for pairwise distances."""
import time
import numpy as np

K = 50.0                      # spring stiffness, N/m
G = np.array([0.0, -9.81])    # gravity, m/s^2


def forces_loop(pos, mass):
    out = []
    for (x, y), m in zip(pos.tolist(), mass.tolist()):
        out.append((-K * x + m * G[0], -K * y + m * G[1]))
    return np.array(out)


def forces_vec(pos, mass):
    return -K * pos + mass[:, None] * G      # (N,2) + (N,1)*(2,) -> (N,2)


def pairwise_distances(p):
    d = p[:, None, :] - p[None, :, :]        # (N,1,2) - (1,N,2) -> (N,N,2)
    return np.sqrt((d ** 2).sum(axis=-1))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    pos = rng.normal(size=(100_000, 2))
    mass = rng.uniform(0.1, 2.0, size=100_000)

    t0 = time.perf_counter(); a = forces_loop(pos, mass); t1 = time.perf_counter()
    b = forces_vec(pos, mass); t2 = time.perf_counter()
    assert np.max(np.abs(a - b)) < 1e-12
    speedup = (t1 - t0) / max(t2 - t1, 1e-9)
    print(f"loop {t1 - t0:.3f} s, vectorised {t2 - t1:.4f} s, {speedup:.0f}x faster")
    assert speedup > 5   # usually 20x or more; kept loose so slow machines still pass

    # resultant of the worked example
    ang = np.radians([30, 120, 250])
    F = np.array([400, 250, 300])[:, None] * np.c_[np.cos(ang), np.sin(ang)]
    R = F.sum(axis=0)
    assert abs(np.linalg.norm(R) - 179.53) < 0.01
    assert abs(np.degrees(np.arctan2(R[1], R[0])) - 48.57) < 0.01

    # broadcasting: distances between the corners of a 3-4-5 triangle
    D = pairwise_distances(np.array([[0.0, 0.0], [3.0, 0.0], [3.0, 4.0]]))
    assert np.allclose(D, D.T) and abs(D[0, 2] - 5.0) < 1e-12
    print("resultant", R.round(1), "distances ok")
