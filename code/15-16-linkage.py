"""Four-bar linkage synthesis with the Freudenstein equation: three input-output angle pairs give the link lengths; the assembled linkage is then solved by circle intersection and checked against the targets."""
import math
import numpy as np


def synthesize(pairs, d=1.0):
    """pairs: [(phi, psi)] in radians. K1 cos(psi) - K2 cos(phi) + K3 = cos(phi - psi)."""
    A = np.array([[math.cos(ps), -math.cos(ph), 1.0] for ph, ps in pairs])
    rhs = np.array([math.cos(ph - ps) for ph, ps in pairs])
    K1, K2, K3 = np.linalg.solve(A, rhs)
    a, c = d / K1, d / K2
    b2 = a * a + c * c + d * d - 2 * a * c * K3
    if b2 <= 0:
        raise ValueError("no real coupler length")
    return a, math.sqrt(b2), c, d


def output_angle(a, b, c, d, phi, branch):
    """Rocker angle for crank angle phi: intersect the circle of radius b about the crank pin with radius c about (d, 0)."""
    A = np.array([a * math.cos(phi), a * math.sin(phi)])
    O = np.array([d, 0.0])
    D = np.linalg.norm(O - A)
    if D > b + abs(c) or D < abs(b - abs(c)):
        return None
    x = (b * b - c * c + D * D) / (2 * D)
    h = math.sqrt(max(b * b - x * x, 0.0))
    u = (O - A) / D
    n = np.array([-u[1], u[0]])
    B = A + x * u + branch * h * n
    return math.atan2(B[1] - O[1], B[0] - O[0]) if c > 0 else math.atan2(O[1] - B[1], O[0] - B[0])


def grashof(lengths):
    s, *mid, l = sorted(map(abs, lengths))
    return s + l <= sum(mid)


if __name__ == "__main__":
    deg = math.pi / 180
    # a wiper-style drive: crank at 40, 70, 100 degrees should put the rocker at 70, 80, 95 degrees
    targets = [(40 * deg, 70 * deg), (70 * deg, 80 * deg), (100 * deg, 95 * deg)]
    a, b, c, d = synthesize(targets, d=100.0)
    print(f"crank a = {a:.3f} mm, coupler b = {b:.3f} mm, rocker c = {c:.3f} mm, ground d = {d:.1f} mm; Grashof: {grashof([a, b, c, d])}")
    for branch in (+1, -1):
        errs = []
        for ph, ps in targets:
            out = output_angle(a, b, c, d, ph, branch)
            errs.append(None if out is None else abs((out - ps + math.pi) % (2 * math.pi) - math.pi))
        print(f"branch {branch:+d}: errors {['%.2e' % e if e is not None else 'none' for e in errs]}")
        if all(e is not None and e < 1e-9 for e in errs):
            good = branch
    for ph, ps in targets:
        print(f"phi {ph/deg:.0f} deg -> psi {output_angle(a, b, c, d, ph, good)/deg:.6f} deg (target {ps/deg:.0f})")
        assert abs(output_angle(a, b, c, d, ph, good) - ps) < 1e-9
    assert min(a, b, c, d) == a and grashof([a, b, c, d])  # shortest link is the crank: it can turn fully
    sweep = [output_angle(a, b, c, d, ph, good) for ph in np.linspace(0, 2 * math.pi, 3601)]
    assert all(x is not None for x in sweep)
    print(f"full crank turn: rocker swings between {min(sweep)/deg:.2f} and {max(sweep)/deg:.2f} deg")
