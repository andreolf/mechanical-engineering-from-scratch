"""A small vector toolkit: length, angle, projection, cross product and moments."""
import math
import random


def dot(a, b): return sum(x * y for x, y in zip(a, b))
def norm(a): return math.sqrt(dot(a, a))
def scale(s, a): return [s * x for x in a]
def sub(a, b): return [x - y for x, y in zip(a, b)]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def angle_deg(a, b):
    c = dot(a, b) / (norm(a) * norm(b))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))   # clamp: rounding can push c past 1


def project(b, a):
    """Vector projection of b on the line of a."""
    return scale(dot(a, b) / dot(a, a), a)


def triangle_area(p, q, r):
    return 0.5 * norm(cross(sub(q, p), sub(r, p)))


if __name__ == "__main__":
    r, F = [0.2, 0.5, 0.0], [30.0, -40.0, 120.0]
    M = cross(r, F)
    print("M =", M, "N m, |M| =", round(norm(M), 2))
    assert M == [60.0, -24.0, -23.0] and abs(norm(F) - 130) < 1e-12
    # the cross product is orthogonal to both inputs, for many random vectors
    rng = random.Random(1)
    for _ in range(10000):
        a = [rng.uniform(-10, 10) for _ in range(3)]
        b = [rng.uniform(-10, 10) for _ in range(3)]
        c = cross(a, b)
        assert abs(dot(c, a)) < 1e-12 * norm(a) * norm(b) * norm(a) + 1e-12
        assert abs(dot(c, b)) < 1e-12 * norm(a) * norm(b) * norm(b) + 1e-12
        # |a x b|^2 + (a.b)^2 = |a|^2 |b|^2 (Lagrange's identity)
        assert abs(dot(c, c) + dot(a, b) ** 2 - dot(a, a) * dot(b, b)) < 1e-9 * dot(a, a) * dot(b, b)
    # the residual of a projection is perpendicular to the line
    a, b = [3.0, 4.0, 0.0], [4.0, -1.0, 2.0]
    assert abs(dot(sub(b, project(b, a)), a)) < 1e-12
    assert abs(angle_deg(a, b) - 69.5647) < 1e-4
    assert abs(triangle_area([0, 0, 0], [1, 0, 0], [0, 1, 0]) - 0.5) < 1e-15
    print("all vector checks passed")
