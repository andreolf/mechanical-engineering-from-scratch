"""A free-body diagram as data: forces with points of application, plus couples, and an equilibrium check."""
import math
import numpy as np


class FBD:
    def __init__(self, name):
        self.name, self.forces, self.couples = name, [], []

    def force(self, label, at, F):
        self.forces.append((label, np.array(at, float), np.array(F, float)))

    def couple(self, label, M):
        self.couples.append((label, float(M)))

    def residual(self, about=(0.0, 0.0)):
        """(sum Fx, sum Fy, sum M about a point). All three are zero for a body in equilibrium."""
        o = np.array(about, float)
        Fx = sum(F[0] for _, _, F in self.forces)
        Fy = sum(F[1] for _, _, F in self.forces)
        M = sum((p - o)[0] * F[1] - (p - o)[1] * F[0] for _, p, F in self.forces) + sum(m for _, m in self.couples)
        return np.array([Fx, Fy, M])


def ladder(L, theta, W, P, s):
    """Ladder of length L at angle theta to the floor, smooth wall, rough floor.
    Ladder weight W at mid-length, person P at distance s up the ladder. Returns (wall N, floor N, floor friction)."""
    c, sn = math.cos(theta), math.sin(theta)
    Nf = W + P                                         # sum Fy = 0
    Nw = (W * L / 2 * c + P * s * c) / (L * sn)        # moments about the foot
    Ff = Nw                                            # sum Fx = 0: friction pushes towards the wall
    return Nw, Nf, Ff


if __name__ == "__main__":
    L, th, W, P, s = 5.0, math.radians(65), 200.0, 800.0, 3.75
    Nw, Nf, Ff = ladder(L, th, W, P, s)
    print(f"wall reaction {Nw:.2f} N, floor normal {Nf:.1f} N, floor friction {Ff:.2f} N, needs mu >= {Ff / Nf:.4f}")
    top = (L * math.cos(th), L * math.sin(th))
    b = FBD("ladder")
    b.force("weight", (top[0] / 2, top[1] / 2), (0, -W))
    b.force("person", (s / L * top[0], s / L * top[1]), (0, -P))
    b.force("wall", top, (-Nw, 0))
    b.force("floor normal", (0, 0), (0, Nf))
    b.force("floor friction", (0, 0), (Ff, 0))
    for about in ((0, 0), top, (10, -3)):                  # moments balance about ANY point once forces balance
        r = b.residual(about)
        print(f"residual about {np.round(about, 3)}: {np.round(r, 10)}")
        assert np.allclose(r, 0, atol=1e-9)
    # how high can the person climb before the ladder slips with mu = 0.25?
    mu = 0.25
    s_max = (mu * (W + P) * L * math.sin(th) - W * L / 2 * math.cos(th)) / (P * math.cos(th))
    print(f"with mu = {mu}: safe up to s = {s_max:.3f} m of {L} m")
    assert abs(ladder(L, th, W, P, s_max)[2] - mu * (W + P)) < 1e-9
    # a wrong FBD: forget the friction and the check catches it
    bad = FBD("ladder, no friction")
    for lab, p, F in b.forces[:-1]:
        bad.force(lab, p, F)
    assert not np.allclose(bad.residual(), 0)
    print("forgotten friction: residual", np.round(bad.residual(), 3))
