"""Weak form of -(EA u')' = f: Galerkin with hat test functions, integrals by Gauss quadrature, compared with the bar stiffness method; a rod hanging under its own weight is reproduced exactly at the nodes."""
import math
import numpy as np

GP = np.array([-math.sqrt(3 / 5), 0.0, math.sqrt(3 / 5)])
GW = np.array([5 / 9, 8 / 9, 5 / 9])


def hat(i, x, nodes):
    """Piecewise-linear test function: 1 at node i, 0 at all other nodes."""
    phi = np.zeros_like(x); dphi = np.zeros_like(x)
    if i > 0:
        a, b = nodes[i - 1], nodes[i]
        m = (x >= a) & (x <= b)
        phi[m] = (x[m] - a) / (b - a); dphi[m] = 1 / (b - a)
    if i < len(nodes) - 1:
        a, b = nodes[i], nodes[i + 1]
        m = (x > a) & (x <= b) if i > 0 else (x >= a) & (x <= b)
        phi[m] = (b - x[m]) / (b - a); dphi[m] = -1 / (b - a)
    return phi, dphi


def galerkin(nodes, EA, f, P_end):
    """K_ij = int EA phi_i' phi_j' dx, F_i = int f phi_i dx + P phi_i(L). Integrated element by element with Gauss points."""
    n = len(nodes)
    K = np.zeros((n, n)); F = np.zeros(n)
    for e in range(n - 1):
        a, b = nodes[e], nodes[e + 1]
        x = 0.5 * (a + b) + 0.5 * (b - a) * GP
        w = 0.5 * (b - a) * GW
        for i in (e, e + 1):
            phi_i, dphi_i = hat(i, x, nodes)
            F[i] += np.sum(w * f(x) * phi_i)
            for j in (e, e + 1):
                _, dphi_j = hat(j, x, nodes)
                K[i, j] += np.sum(w * EA(x) * dphi_i * dphi_j)
    F[-1] += P_end
    return K, F


def bar_stiffness_assembly(nodes, EA):
    n = len(nodes); K = np.zeros((n, n))
    for e in range(n - 1):
        k = EA / (nodes[e + 1] - nodes[e])
        K[e:e + 2, e:e + 2] += k * np.array([[1, -1], [-1, 1]])
    return K


if __name__ == "__main__":
    # a 100 m steel rod hanging from the top (x = 0) under its own weight, plus a 2 kN weight at the bottom
    L, E, A, rho, g, P = 100.0, 210e9, 2e-4, 7850.0, 9.81, 2000.0
    nodes = np.linspace(0, L, 6)
    K, F = galerkin(nodes, lambda x: E * A + 0 * x, lambda x: rho * g * A + 0 * x, P)
    Kb = bar_stiffness_assembly(nodes, E * A)
    print("Galerkin K equals the assembled bar matrices:", np.allclose(K, Kb))
    assert np.allclose(K, Kb, rtol=1e-12)
    w = rho * g * A
    h = nodes[1] - nodes[0]
    assert np.allclose(F[1:-1], w * h) and abs(F[-1] - (w * h / 2 + P)) < 1e-9  # consistent load: half an element to the end nodes
    u = np.zeros(len(nodes))
    u[1:] = np.linalg.solve(K[1:, 1:], F[1:])
    exact = lambda x: (w * (L * x - x**2 / 2) + P * x) / (E * A)
    print("node  FEM (mm)    exact (mm)")
    for x, ui in zip(nodes, u):
        print(f"{x:5.0f} {1000*ui:10.5f} {1000*exact(x):10.5f}")
    assert np.allclose(u, exact(nodes), rtol=1e-12, atol=1e-15)   # linear elements are exact at the nodes in 1D
    mid = 0.5 * (nodes[0] + nodes[1])
    print(f"between nodes (x = {mid}): FEM {1000*0.5*(u[0]+u[1]):.5f} mm, exact {1000*exact(mid):.5f} mm")
