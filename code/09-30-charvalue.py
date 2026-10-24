"""Design values for a natural material: the 5th-percentile characteristic strength of bamboo from test data, a confidence adjustment for small samples, and a check by simulation."""
import math
import numpy as np

MEAN, COV = 55.0, 0.15                         # true compressive strength of the culms, MPa
SIG_LN = math.sqrt(math.log(1 + COV**2)); MU_LN = math.log(MEAN) - SIG_LN**2 / 2
TRUE_P5 = math.exp(MU_LN - 1.6449 * SIG_LN)


def char_value(x):
    """ISO 12122-style: normal 5th percentile reduced for sample size, f_k = (m - 1.645 s)(1 - 2.7 (s/m)/sqrt(n))."""
    m, s, n = x.mean(), x.std(ddof=1), len(x)
    return (m - 1.645 * s) * (1 - 2.7 * (s / m) / math.sqrt(n)), m - 1.645 * s


def nonparam_p5(x):
    xs = np.sort(x); pos = 0.05 * (len(xs) + 1) - 1
    i = int(math.floor(pos)); f = pos - i
    return xs[max(i, 0)] if i < 0 else xs[i] + f * (xs[i + 1] - xs[i])


if __name__ == "__main__":
    rng = np.random.default_rng(21)
    x = rng.lognormal(MU_LN, SIG_LN, 30)
    fk, p5 = char_value(x)
    print(f"30 culms: mean {x.mean():.1f} MPa, s {x.std(ddof=1):.1f}, CoV {x.std(ddof=1)/x.mean()*100:.1f} %")
    print(f"5th percentile: normal {p5:.1f}, ranked {nonparam_p5(x):.1f}, lognormal {math.exp(np.log(x).mean()-1.645*np.log(x).std(ddof=1)):.1f}; true {TRUE_P5:.1f} MPa")
    print(f"characteristic value with the sample-size factor: {fk:.1f} MPa")
    kmod, gm = 0.8, 1.3
    print(f"design strength k_mod f_k / gamma_M = {kmod*fk/gm:.1f} MPa")
    # how often does each estimate land at or below the true 5th percentile (i.e. is safe)?
    sims = rng.lognormal(MU_LN, SIG_LN, (20000, 30))
    m, s = sims.mean(axis=1), sims.std(axis=1, ddof=1)
    plain = m - 1.645 * s; adj = plain * (1 - 2.7 * (s / m) / math.sqrt(30))
    c_plain, c_adj = np.mean(plain <= TRUE_P5), np.mean(adj <= TRUE_P5)
    print(f"confidence of being safe: plain {c_plain*100:.0f} %, adjusted {c_adj*100:.0f} %")
    assert c_adj > 0.75 and c_adj > c_plain
    # z for 5 %
    assert abs(0.5 * (1 + math.erf(-1.6449 / math.sqrt(2))) - 0.05) < 1e-4
