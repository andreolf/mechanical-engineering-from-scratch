"""Flux schemes for linear advection on a periodic domain: first-order upwind, Lax-Wendroff, and TVD schemes with the minmod and superbee limiters. A square pulse is advected once around; TVD schemes create no new extrema and never increase the total variation."""
import numpy as np


def minmod(r):
    return np.maximum(0, np.minimum(1, r))


def superbee(r):
    return np.maximum(0, np.maximum(np.minimum(2 * r, 1), np.minimum(r, 2)))


def vanleer(r):
    return (r + np.abs(r)) / (1 + np.abs(r))


LIMITERS = {"upwind": lambda r: 0 * r, "Lax-Wendroff": lambda r: 1 + 0 * r, "minmod": minmod, "superbee": superbee, "van Leer": vanleer}


def step(q, c, phi):
    """Flux-limited scheme for a > 0, Courant number c: F = a q_i + a/2 (1 - c) phi(r) (q_{i+1} - q_i)."""
    dq = np.roll(q, -1) - q                          # q_{i+1} - q_i  at face i+1/2
    dqm = q - np.roll(q, 1)                          # q_i - q_{i-1}
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(np.abs(dq) > 1e-14, dqm / dq, 0.0)
    F = q + 0.5 * (1 - c) * phi(r) * dq              # flux / a
    return q - c * (F - np.roll(F, 1))


def tv(q):
    return np.abs(np.roll(q, -1) - q).sum()


def run(name, N=200, c=0.5, periods=1):
    x = (np.arange(N) + 0.5) / N; q = ((x > 0.2) & (x < 0.5)).astype(float)
    n = int(round(periods * N / c)); tvs = [tv(q)]; ext = [0.0, 1.0]
    for _ in range(n):
        q = step(q, c, LIMITERS[name]); tvs.append(tv(q))
    return x, q, np.array(tvs)


if __name__ == "__main__":
    exact = None
    for name in LIMITERS:
        x, q, tvs = run(name)
        if exact is None: exact = ((x > 0.2) & (x < 0.5)).astype(float)
        err = np.abs(q - exact).mean()
        print(f"{name:13s}: min {q.min():+.5f}, max {q.max():.5f}, TV {tvs[0]:.3f} -> {tvs[-1]:.4f}, L1 error {err:.4f}")
        if name in ("upwind", "minmod", "superbee", "van Leer"):
            assert q.min() >= -1e-12 and q.max() <= 1 + 1e-12          # no new extrema
            assert np.all(np.diff(tvs) <= 1e-12)                       # total variation never grows
    x, q, tvs = run("Lax-Wendroff")
    assert q.min() < -0.05 and q.max() > 1.05 and tvs[-1] > tvs[0]     # second order but oscillates
    e = {n: np.abs(run(n)[1] - exact).mean() for n in ("upwind", "minmod", "superbee")}
    assert e["superbee"] < e["minmod"] < e["upwind"]
