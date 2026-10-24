"""Solve 2x2 systems by Cramer's rule, check residuals, and measure conditioning."""
import math


def solve2(A, b):
    (a, c), (d, e) = A
    det = a * e - c * d
    if abs(det) < 1e-14 * max(abs(a * e), abs(c * d), 1e-300):
        raise ValueError("singular or nearly singular matrix")
    return [(b[0] * e - c * b[1]) / det, (a * b[1] - d * b[0]) / det]


def residual(A, x, b):
    return max(abs(sum(A[i][j] * x[j] for j in range(2)) - b[i]) for i in range(2))


def cond_inf(A):
    """Infinity-norm condition number of a 2x2 matrix."""
    (a, c), (d, e) = A
    det = a * e - c * d
    inv = [[e / det, -c / det], [-d / det, a / det]]
    n = lambda M: max(sum(abs(v) for v in row) for row in M)
    return n(A) * n(inv)


if __name__ == "__main__":
    t1, t2 = math.radians(150), math.radians(45)
    A = [[math.cos(t1), math.cos(t2)], [math.sin(t1), math.sin(t2)]]
    T = solve2(A, [0.0, 10.0])
    print(f"T1 = {T[0]:.3f} kN, T2 = {T[1]:.3f} kN, cond = {cond_inf(A):.2f}")
    assert abs(T[0] - 7.3205) < 1e-4 and abs(T[1] - 8.9658) < 1e-4
    assert residual(A, T, [0.0, 10.0]) < 1e-12
    assert solve2([[2, -1], [-1, 2]], [0, 3]) == [1.0, 2.0]
    # a nearly parallel pair: a 0.01 change in b moves x by about 1
    B = [[1.0, -1.0], [1.0, -1.01]]
    x0, x1 = solve2(B, [0.0, -0.01]), solve2(B, [0.0, 0.0])
    print("near-parallel shift:", [round(u - v, 3) for u, v in zip(x0, x1)], "cond", round(cond_inf(B)))
    assert abs(x0[0] - x1[0] - 1.0) < 1e-9 and cond_inf(B) > 400
    try:
        solve2([[1, 2], [2, 4]], [1, 2]); raise AssertionError("should be singular")
    except ValueError:
        pass
    print("all checks passed")
