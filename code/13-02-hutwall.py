"""Thermal resistance networks: a layered alpine-hut wall with a window in parallel, checked by a layer-by-layer FD solve."""
import numpy as np


def solve_wall(L, T_left, T_right, k_of_x, n=201):
    """Conservative FD: cell faces carry flux -k_face (T[i+1] - T[i]) / dx. Returns x, T and the flux at every face."""
    x = np.linspace(0, L, n); dx = x[1]
    kf = k_of_x((x[:-1] + x[1:]) / 2)                        # conductivity at the faces between nodes
    A = np.zeros((n, n)); b = np.zeros(n)
    A[0, 0] = A[-1, -1] = 1.0; b[0], b[-1] = T_left, T_right
    for i in range(1, n - 1):
        A[i, i - 1] = kf[i - 1]; A[i, i] = -(kf[i - 1] + kf[i]); A[i, i + 1] = kf[i]
    T = np.linalg.solve(A, b)
    q = -kf * np.diff(T) / dx
    return x, T, q


def series(*R):
    return sum(R)


def parallel(*R):
    return 1 / sum(1 / r for r in R)


if __name__ == "__main__":
    Ti, To = 20.0, -10.0
    hi, ho = 7.7, 25.0                                           # inside and outside surface coefficients, W/(m^2 K)
    layers = [("spruce panelling", 0.020, 0.13), ("mineral wool", 0.120, 0.035), ("larch cladding", 0.024, 0.13)]
    R_layers = [L / k for _, L, k in layers]
    R_wall = series(1 / hi, *R_layers, 1 / ho)                    # per m^2
    U = 1 / R_wall
    print("layer resistances (m^2 K/W): " + ", ".join(f"{n} {r:.4f}" for (n, _, _), r in zip(layers, R_layers)))
    print(f"R_total = {R_wall:.4f} m^2 K/W, U = {U:.4f} W/(m^2 K), flux {(Ti-To)*U:.3f} W/m^2")
    # interface temperatures: the same flux through every resistance
    q = (Ti - To) * U; T = Ti; temps = [T]
    for r in [1 / hi] + R_layers + [1 / ho]:
        T -= q * r; temps.append(T)
    print("surface and interface temperatures (C): " + ", ".join(f"{t:.3f}" for t in temps))
    assert abs(temps[-1] - To) < 1e-12
    # check: FD across the solid layers between the two surface temperatures gives the same flux
    Ltot = sum(L for _, L, _ in layers); edges = np.cumsum([0] + [L for _, L, _ in layers])
    kfun = lambda s: np.select([s < edges[1], s < edges[2]], [layers[0][2], layers[1][2]], layers[2][2])
    x, Tfd, qfd = solve_wall(Ltot, temps[1], temps[-2], kfun, n=1641)
    print(f"FD through the layers: flux {qfd.mean():.4f} W/m^2 (network {q:.4f})")
    assert abs(qfd.mean() - q) < 1e-6 * q                         # heat flow = dT / R_total
    # a 12 m^2 wall with a 2 m^2 window (U = 1.1): wall and window conduct in parallel
    A_wall, A_win, U_win = 10.0, 2.0, 1.1
    R_total = parallel(R_wall / A_wall, 1 / (U_win * A_win))
    Q = (Ti - To) / R_total
    print(f"wall + window: R = {R_total:.5f} K/W, heat loss {Q:.2f} W ({(Ti-To)*U_win*A_win/Q*100:.1f} % through the window)")
    assert abs(Q - (Ti - To) * (U * A_wall + U_win * A_win)) < 1e-9
