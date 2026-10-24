"""Free-body diagrams as data: solve for unknown reactions and check equilibrium."""
import math


def solve3(A, b):
    """Gaussian elimination with partial pivoting for a 3x3 system."""
    M = [row[:] + [bi] for row, bi in zip(A, b)]
    n = 3
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14:
            raise ValueError("singular: the diagram is a mechanism or indeterminate")
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    x = [0.0] * n
    for r in reversed(range(n)):
        x[r] = (M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))) / M[r][r]
    return x


def resultant(forces):
    """forces: list of (point (x, y), force (Fx, Fy)). Returns (sum Fx, sum Fy, moment about origin)."""
    fx = sum(f[0] for _, f in forces)
    fy = sum(f[1] for _, f in forces)
    m = sum(p[0] * f[1] - p[1] * f[0] for p, f in forces)
    return fx, fy, m


def ladder(L=4.0, mass=15.0, theta_deg=60.0, person=None):
    th = math.radians(theta_deg)
    foot, top = (0.0, 0.0), (L * math.cos(th), L * math.sin(th))
    known = [((L / 2 * math.cos(th), L / 2 * math.sin(th)), (0.0, -mass * 9.81))]
    if person:
        m, d = person
        known.append(((d * math.cos(th), d * math.sin(th)), (0.0, -m * 9.81)))
    # unknown unit forces: N_w at top pointing -x, N_f at foot +y, F at foot +x
    unknown = [(top, (-1.0, 0.0)), (foot, (0.0, 1.0)), (foot, (1.0, 0.0))]
    A = [[0.0] * 3 for _ in range(3)]
    for j, (p, f) in enumerate(unknown):
        A[0][j], A[1][j], A[2][j] = resultant([(p, f)])
    rhs = [-v for v in resultant(known)]
    Nw, Nf, F = solve3(A, rhs)
    all_forces = known + [(p, (f[0] * s, f[1] * s)) for (p, f), s in zip(unknown, (Nw, Nf, F))]
    assert all(abs(v) < 1e-9 for v in resultant(all_forces)), "diagram does not balance"
    return Nw, Nf, F


if __name__ == "__main__":
    Nw, Nf, F = ladder()
    print(f"N_w = {Nw:.2f} N, N_f = {Nf:.2f} N, F = {F:.2f} N, mu_min = {F / Nf:.4f}")
    assert abs(Nw - 42.4785) < 1e-3 and abs(F / Nf - 1 / (2 * math.sqrt(3))) < 1e-12
    Nw2, Nf2, F2 = ladder(person=(80.0, 3.0))
    assert abs(F2 / Nf2 - 0.41022) < 1e-4
    print(f"with an 80 kg person 3 m up: mu_min = {F2 / Nf2:.3f}")
