"""Process selection by cost: Ashby's cost model for an aluminium bracket made by four processes, and the batch sizes where each one wins."""
import math

MASS = 0.25        # kg finished part
CM = 3.0           # USD/kg aluminium
#  name: (material scrap fraction, dedicated tooling USD, overhead rate USD/h, parts per hour)
PROC = {
    "CNC machining":  (0.60, 300.0, 80.0, 4.0),
    "sand casting":   (0.30, 2000.0, 50.0, 10.0),
    "die casting":    (0.10, 40000.0, 120.0, 120.0),
    "metal 3D print": (0.05, 0.0, 60.0, 0.5),
}


def unit_cost(proc, n):
    f, tool, rate, nd = PROC[proc]
    return MASS * CM / (1 - f) + tool / n + rate / nd


def crossover(a, b):
    """Batch size where processes a and b cost the same: equate the 1/n terms."""
    fa, ta, ra, na = PROC[a]; fb, tb, rb, nb = PROC[b]
    fixed = lambda f, r, nd: MASS * CM / (1 - f) + r / nd
    return (tb - ta) / (fixed(fa, ra, na) - fixed(fb, rb, nb))


if __name__ == "__main__":
    for n in (1, 10, 100, 1000, 10000, 100000):
        costs = {p: unit_cost(p, n) for p in PROC}
        best = min(costs, key=costs.get)
        print(f"n = {n:6d}: " + ", ".join(f"{p} {c:.2f}" for p, c in costs.items()) + f"  -> {best}")
    for a, b in (("metal 3D print", "CNC machining"), ("CNC machining", "sand casting"), ("sand casting", "die casting")):
        nx = crossover(a, b)
        print(f"{b} beats {a} above {nx:.0f} parts")
        assert abs(unit_cost(a, nx) - unit_cost(b, nx)) < 1e-9
    # each crossover is where the cheaper-tooled process stops winning
    assert unit_cost("CNC machining", 10) < unit_cost("die casting", 10) and unit_cost("die casting", 1e5) < unit_cost("CNC machining", 1e5)
