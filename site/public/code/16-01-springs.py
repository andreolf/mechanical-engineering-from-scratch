"""Finite elements as springs: element stiffness k[[1,-1],[-1,1]], assembly into a global matrix, supports, and a check against the series-spring formula."""
import numpy as np


def assemble(ks):
    """Chain of springs between nodes 0-1, 1-2, ...; returns the (n+1) x (n+1) global stiffness matrix."""
    n = len(ks)
    K = np.zeros((n + 1, n + 1))
    for e, k in enumerate(ks):
        ke = k * np.array([[1.0, -1.0], [-1.0, 1.0]])
        dofs = [e, e + 1]
        K[np.ix_(dofs, dofs)] += ke
    return K


def solve(K, F, fixed):
    """Remove fixed degrees of freedom (zero displacement), solve the rest, recover reactions."""
    n = len(F)
    free = [i for i in range(n) if i not in fixed]
    u = np.zeros(n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    R = K @ u - F
    return u, R


if __name__ == "__main__":
    ks = [200.0, 100.0, 400.0, 250.0]           # N/mm, a chain fixed at node 0
    K = assemble(ks)
    print("global stiffness matrix (N/mm):")
    print(K)
    assert np.allclose(K, K.T) and abs(np.linalg.det(K)) < 1e-6 * np.abs(K).max() ** len(K)  # symmetric and singular until supported
    F = np.zeros(5); F[-1] = 1000.0               # 1 kN pull at the free end
    u, R = solve(K, F, fixed=[0])
    series = 1 / sum(1 / k for k in ks)
    print(f"node displacements (mm): {np.round(u, 4)}")
    print(f"tip stiffness {F[-1]/u[-1]:.4f} N/mm, series formula {series:.4f} N/mm, reaction {R[0]:.1f} N")
    assert abs(F[-1] / u[-1] - series) < 1e-9 and abs(R[0] + 1000) < 1e-9
    # every spring carries the same force in a chain: k (u_j+1 - u_j)
    forces = [k * (u[e + 1] - u[e]) for e, k in enumerate(ks)]
    assert np.allclose(forces, 1000.0)
    # loads at interior nodes too, fixed at both ends
    F2 = np.array([0, 300.0, 0, -200.0, 0])
    u2, R2 = solve(K, F2, fixed=[0, 4])
    print(f"both ends fixed: displacements {np.round(u2, 4)} mm, reactions {R2[0]:.2f} and {R2[4]:.2f} N")
    assert abs(R2.sum() - (-F2.sum())) < 1e-9
