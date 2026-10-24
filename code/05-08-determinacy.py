"""Static determinacy by the rank of the equilibrium matrix, for one or several pinned rigid bodies."""
import numpy as np


def classify(n_bodies, unknowns):
    """unknowns: list of unit reactions; each is a list of (body, (x, y), (Fx, Fy), Mz) contributions.
    An internal hinge force appears on two bodies with opposite signs. Returns (rank, degree, verdict)."""
    A = np.zeros((3 * n_bodies, len(unknowns)))
    for j, contribs in enumerate(unknowns):
        for body, (x, y), (fx, fy), mz in contribs:
            A[3 * body:3 * body + 3, j] += [fx, fy, x * fy - y * fx + mz]
    rank = np.linalg.matrix_rank(A)
    mech, indet = 3 * n_bodies - rank, len(unknowns) - rank
    if mech > 0:
        verdict = f"mechanism ({mech} free motion{'s' if mech > 1 else ''})" + (f", also {indet}x indeterminate" if indet else "")
    elif indet > 0:
        verdict = f"{indet}x statically indeterminate"
    else:
        verdict = "statically determinate"
    return rank, indet, mech, verdict


def pin(body, at):          # two force components at a ground pin
    return [[(body, at, (1, 0), 0)], [(body, at, (0, 1), 0)]]


def roller(body, at, d=(0, 1)):
    return [[(body, at, d, 0)]]


def clamp(body, at):
    return pin(body, at) + [[(body, at, (0, 0), 1)]]


def hinge(b1, b2, at):      # internal pin: equal and opposite forces on the two bodies
    return [[(b1, at, (1, 0), 0), (b2, at, (-1, 0), 0)], [(b1, at, (0, 1), 0), (b2, at, (0, -1), 0)]]


if __name__ == "__main__":
    cases = {
        "simply supported": (1, pin(0, (0, 0)) + roller(0, (6, 0))),
        "propped cantilever": (1, clamp(0, (0, 0)) + roller(0, (6, 0))),
        "fixed-fixed": (1, clamp(0, (0, 0)) + clamp(0, (6, 0))),
        "two rollers": (1, roller(0, (0, 0)) + roller(0, (6, 0))),
        "pin + horizontal roller in line": (1, pin(0, (0, 0)) + roller(0, (6, 0), (1, 0))),
        "Gerber beam (clamp, hinge, roller)": (2, clamp(0, (0, 0)) + hinge(0, 1, (4, 0)) + roller(1, (10, 0))),
        "three-hinged arch": (2, pin(0, (0, 0)) + hinge(0, 1, (5, 4)) + pin(1, (10, 0))),
        "pin, hinge, roller (two bodies)": (2, pin(0, (0, 0)) + hinge(0, 1, (4, 0)) + roller(1, (10, 0))),
    }
    expect = {"simply supported": (0, 0), "propped cantilever": (1, 0), "fixed-fixed": (3, 0), "two rollers": (0, 1),
              "pin + horizontal roller in line": (1, 1), "Gerber beam (clamp, hinge, roller)": (0, 0),
              "three-hinged arch": (0, 0), "pin, hinge, roller (two bodies)": (0, 1)}
    for name, (nb, unk) in cases.items():
        rank, indet, mech, verdict = classify(nb, unk)
        print(f"{name:36s} unknowns {len(unk):2d}, equations {3 * nb}, rank {rank}: {verdict}")
        assert (indet, mech) == expect[name], name
