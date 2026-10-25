"""An error budget for a toy CFD problem: steady 1D advection-diffusion. The 'truth' has a small heat source the model leaves out (modelling error); the model is discretised with central differences (discretisation error) and solved in float32 or float64 (round-off). Each part is estimated separately, and the budget is compared with the observed error."""
import math
import numpy as np

U, GAMMA, S0 = 1.0, 0.05, 0.05          # velocity, diffusivity, neglected source strength
XP = 0.9                                 # quantity of interest: phi at x = 0.9


def exact(x, s):
    """u phi' - Gamma phi'' = s on [0, 1], phi(0) = 0, phi(1) = 1."""
    Pe = U / GAMMA
    hom = (np.exp(Pe * x) - 1) / (math.exp(Pe) - 1)
    # particular solution s x / U, corrected so that phi(1) = 1
    return hom + s / U * (x - hom)


def solve_fd(N, s, dtype=np.float64):
    """Central differences on N intervals, Thomas algorithm carried out in the given precision."""
    h = 1.0 / N; x = np.linspace(0, 1, N + 1)
    a = dtype(-U / (2 * h) - GAMMA / h**2); b = dtype(2 * GAMMA / h**2); c = dtype(U / (2 * h) - GAMMA / h**2)
    n = N - 1; d = np.full(n, s, dtype=dtype); d[-1] -= c * dtype(1.0)
    cp = np.zeros(n, dtype); dp = np.zeros(n, dtype)
    cp[0] = c / b; dp[0] = d[0] / b
    for i in range(1, n):
        m = b - a * cp[i - 1]; cp[i] = c / m; dp[i] = (d[i] - a * dp[i - 1]) / m
    phi = np.zeros(n, dtype); phi[-1] = dp[-1]
    for i in range(n - 2, -1, -1): phi[i] = dp[i] - cp[i] * phi[i + 1]
    return x, np.concatenate([[0.0], phi.astype(np.float64), [1.0]])


def at(x, phi, xp=XP):
    return float(np.interp(xp, x, phi))


def budget(N, dtype):
    truth = float(exact(np.array(XP), S0))
    x, ph = solve_fd(N, 0.0, dtype)
    observed = at(x, ph) - truth
    # estimates, each computed without knowing the truth:
    xa, pa = solve_fd(4 * N, 0.0); xb, pb = solve_fd(4 * N, S0)
    model = at(xa, pa) - at(xb, pb)                                           # sensitivity run: switch the source on
    x2, ph2 = solve_fd(2 * N, 0.0, np.float64); x1, ph1 = solve_fd(N, 0.0, np.float64)
    disc = (at(x1, ph1) - at(x2, ph2)) * 4 / 3                               # Richardson, order 2
    roundoff = at(x, ph) - at(x1, ph1)                                        # same grid, float64 reference
    return observed, model, disc, roundoff


if __name__ == "__main__":
    print(f"Peclet number {U/GAMMA:.0f}; quantity of interest phi({XP})")
    for N, dt in ((20, np.float64), (40, np.float64), (40, np.float32), (2000, np.float32)):
        obs, m, d, r = budget(N, dt)
        total = m + d + r
        print(f"N = {N:5d}, {np.dtype(dt).name}: model {m:+.6f}, discretisation {d:+.6f}, round-off {r:+.2e}; budget {total:+.6f}, observed {obs:+.6f}")
        assert abs(total - obs) < 0.02 * abs(obs)
    # the cell Peclet number h U / Gamma must stay below 2 for central differences to avoid wiggles
    x, ph = solve_fd(8, 0.0)
    print(f"N = 8 (cell Peclet {U/GAMMA/8:.1f}): min phi {ph.min():.4f} (negative: unphysical oscillation)")
    assert ph.min() < 0
