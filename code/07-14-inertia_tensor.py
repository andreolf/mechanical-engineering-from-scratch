"""Inertia tensor of a body made of point masses; principal axes as its eigenvectors."""
import math
import numpy as np


def inertia_tensor(pts, m):
    """I = sum m (|r|^2 1 - r r^T) about the centre of mass."""
    c = (m[:, None] * pts).sum(0) / m.sum()
    r = pts - c
    I = np.sum(m * (r**2).sum(1)) * np.eye(3) - (r * m[:, None]).T @ r
    return I, c


def box_cloud(a, b, c, n, mass, rng):
    """Uniform random point cloud filling an a x b x c box (an approximation of a solid block)."""
    pts = rng.uniform(-0.5, 0.5, (n, 3)) * np.array([a, b, c])
    return pts, np.full(n, mass / n)


if __name__ == "__main__":
    np.set_printoptions(suppress=True)
    rng = np.random.default_rng(11)
    # 1. a solid block 0.4 x 0.2 x 0.1 m of 8 kg, as 200,000 points: compare with m (b^2 + c^2) / 12 etc.
    a, b, c, M = 0.4, 0.2, 0.1, 8.0
    pts, m = box_cloud(a, b, c, 200000, M, rng)
    I, cg = inertia_tensor(pts, m)
    exact = M / 12 * np.array([b*b + c*c, a*a + c*c, a*a + b*b])
    print("block, diagonal of I:", np.round(np.diag(I), 5), " exact:", np.round(exact, 5))
    assert np.allclose(np.diag(I), exact, rtol=0.01)
    # 2. tilt the block by a known rotation: off-diagonal products of inertia appear, but the eigenvalues don't change
    th = math.radians(30)
    Rz = np.array([[math.cos(th), -math.sin(th), 0], [math.sin(th), math.cos(th), 0], [0, 0, 1]])
    I_t, _ = inertia_tensor(pts @ Rz.T, m)
    print("tilted block I (kg m^2):\n", np.round(I_t, 5))
    lam, V = np.linalg.eigh(I_t)
    print("principal moments (eigenvalues):", np.round(lam, 5), " untilted diagonal sorted:", np.round(np.sort(np.diag(I)), 5))
    assert np.allclose(lam, np.sort(np.linalg.eigvalsh(I)), atol=1e-12)
    # the principal axis with the smallest moment lies along the block's long edge, now turned by 30 degrees
    ax = V[:, 0] * np.sign(V[0, 0])
    print(f"axis of least inertia at {math.degrees(math.atan2(ax[1], ax[0])):.2f} deg in the x-y plane (block turned 30 deg)")
    # 3. an L-shaped bracket from three point masses: no symmetry, so the axes must be computed
    P = np.array([[0, 0, 0], [0.3, 0, 0], [0, 0.2, 0.1]], float); mm = np.array([1.0, 2.0, 1.5])
    IL, cL = inertia_tensor(P, mm)
    lamL, VL = np.linalg.eigh(IL)
    print(f"three-mass bracket: centre {np.round(cL, 4)}, principal moments {np.round(lamL, 5)}")
    assert np.allclose(IL @ VL, VL * lamL)
