"""Weighted decision matrix for choosing a bike drivetrain: normalise the weights, score, rank, and find how far a weight can move before the winner changes."""
import numpy as np

CRITERIA = ["cost", "mass", "efficiency", "maintenance", "gear range"]
CONCEPTS = ["1x derailleur", "8-speed hub", "belt + hub", "single speed"]
# scores 1 (poor) to 5 (excellent); rows are concepts, columns are criteria
SCORES = np.array([
    [4, 5, 5, 2, 4],
    [3, 2, 3, 4, 3],
    [1, 2, 3, 5, 3],
    [5, 5, 5, 4, 1],
], float)


def normalise(raw):
    raw = np.asarray(raw, float)
    assert np.all(raw >= 0) and raw.sum() > 0
    return raw / raw.sum()


def totals(weights, scores=SCORES):
    return scores @ normalise(weights)


def ranking(weights, scores=SCORES):
    return list(np.argsort(-totals(weights, scores), kind="stable"))


def with_weight(weights, i, wi):
    """Set criterion i to weight wi (0..1) and scale the others so the total stays 1."""
    w = normalise(weights)
    rest = np.delete(np.arange(len(w)), i)
    out = w.copy()
    out[rest] = w[rest] * (1 - wi) / w[rest].sum()
    out[i] = wi
    return out


def switch_point(weights, i, n=20001):
    """Smallest weight on criterion i at which the winner changes (None if it never does)."""
    w0 = normalise(weights)
    first = ranking(w0)[0]
    for wi in np.linspace(0, 1, n):
        if wi <= w0[i]:
            continue
        if ranking(with_weight(w0, i, wi))[0] != first:
            return wi
    return None


if __name__ == "__main__":
    raw = [25, 20, 15, 30, 10]  # importance points out of 100: a commuter in a wet city
    w = normalise(raw)
    t = totals(raw)
    for k in ranking(raw):
        print(f"{CONCEPTS[k]:14s} {t[k]:.2f}")
    # the ranking is reproducible from the weights: a hand sum for the winner
    hand = sum(SCORES[3, j] * w[j] for j in range(5))
    assert abs(hand - t[3]) < 1e-12
    assert ranking(raw) == ranking(np.array(raw) * 7)  # only the ratios of the weights matter
    assert [CONCEPTS[k] for k in ranking(raw)] == ["single speed", "1x derailleur", "8-speed hub", "belt + hub"]
    # a hilly route: raise the weight on gear range until single speed loses
    ws = switch_point(raw, 4)
    print(f"single speed stops winning when gear range carries {ws:.4f} of the weight")
    # check the crossover by hand: totals are linear in the weight, so solve for equality
    a = with_weight(raw, 4, 0.0); b = with_weight(raw, 4, 1.0)
    ta, tb = SCORES @ a, SCORES @ b
    lam = [(ta[3] - ta[k]) / ((ta[3] - ta[k]) - (tb[3] - tb[k])) for k in range(3) if (tb[3] - tb[k]) < 0]
    exact = min(x for x in lam if x > w[4])
    print(f"exact crossover {exact:.4f}")
    assert abs(ws - exact) < 1e-4
