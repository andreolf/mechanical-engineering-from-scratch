"""Supports and constraints: count reactions, Grubler mobility of planar linkages, and the rank check behind it."""
import numpy as np

REACTIONS = {"roller": 1, "pin": 2, "clamp": 3}           # planar: unknown reaction components per support


def beam_dof(supports):
    """A single rigid beam in the plane has 3 DOF; each support removes as many as it has reactions (if they're independent)."""
    r = sum(REACTIONS[s] for s in supports)
    return 3 - r, r


def grubler(n_links, j1, j2=0):
    """Planar mobility M = 3(n - 1) - 2 j1 - j2, counting the ground as a link; j1 = pins/sliders, j2 = cam/rolling contacts."""
    return 3 * (n_links - 1) - 2 * j1 - j2


def support_rank(points_dirs):
    """Rank of the reaction matrix: rows are (Fx, Fy, M about origin) of each unit reaction. Rank < 3 means a mechanism."""
    rows = []
    for (x, y), (dx, dy) in points_dirs:
        rows.append([dx, dy, x * dy - y * dx])
    return np.linalg.matrix_rank(np.array(rows, float))


if __name__ == "__main__":
    for s in (["pin", "roller"], ["clamp"], ["pin", "pin"], ["roller", "roller"]):
        dof, r = beam_dof(s)
        print(f"beam on {' + '.join(s):15s}: {r} reactions, DOF = {dof}")
    assert beam_dof(["pin", "roller"]) == (0, 3)
    # rank catches what counting misses: three rollers all vertical give 3 reactions but cannot stop sliding
    vertical = [((0, 0), (0, 1)), ((2, 0), (0, 1)), ((4, 0), (0, 1))]
    pin_roller = [((0, 0), (1, 0)), ((0, 0), (0, 1)), ((4, 0), (0, 1))]
    concurrent = [((0, 0), (1, 0)), ((0, 0), (0, 1)), ((4, 0), (-1, 0))]    # roller reaction pointing through the pin
    print("rank: pin + roller", support_rank(pin_roller), "| three vertical rollers", support_rank(vertical),
          "| reactions through one point", support_rank(concurrent))
    assert support_rank(pin_roller) == 3 and support_rank(vertical) == 2 and support_rank(concurrent) == 2
    # linkages
    cases = {"four-bar": (4, 4), "slider-crank": (4, 4), "five-bar": (5, 5), "triangle (rigid truss)": (3, 3), "Stephenson six-bar": (6, 7)}
    for name, (n, j) in cases.items():
        print(f"{name:22s}: n = {n}, j1 = {j}, M = {grubler(n, j)}")
    assert grubler(4, 4) == 1 and grubler(5, 5) == 2 and grubler(3, 3) == 0 and grubler(6, 7) == 1
