"""E-bike battery thermal model: a two-node (cells, case) RC network driven by I^2 R heating over a ride, checked against the steady resistance network."""
import math

# pack: 36 V, 10s5p of 18650 cells, 45 mOhm each -> R_pack = 10 * 0.045 / 5
R_PACK = 10 * 0.045 / 5          # ohm
C_CELLS = 2.3 * 900.0            # J/K, 50 cells and their holders
C_CASE = 0.6 * 900.0             # J/K, aluminium case
R_INT = 0.25                     # K/W, cells to case through foam and air gaps
A_CASE = 0.12                    # m^2 of case exposed to the air


def h_air(riding):
    return 15.0 if riding else 5.0   # forced convection while riding, natural when parked


def derivs(Tcell, Tcase, current, riding, T_amb):
    q = current ** 2 * R_PACK
    q_in = (Tcell - Tcase) / R_INT
    q_out = h_air(riding) * A_CASE * (Tcase - T_amb)
    return (q - q_in) / C_CELLS, (q_in - q_out) / C_CASE


def simulate(profile, T_amb, dt=1.0):
    """profile: list of (minutes, current A, riding?). RK4 with a 1 s step. Returns times (min), cell and case temperatures."""
    Tcell = Tcase = T_amb; t = 0.0
    ts, cells, cases = [0.0], [Tcell], [Tcase]
    for minutes, I, riding in profile:
        for _ in range(int(round(minutes * 60 / dt))):
            a1, b1 = derivs(Tcell, Tcase, I, riding, T_amb)
            a2, b2 = derivs(Tcell + dt / 2 * a1, Tcase + dt / 2 * b1, I, riding, T_amb)
            a3, b3 = derivs(Tcell + dt / 2 * a2, Tcase + dt / 2 * b2, I, riding, T_amb)
            a4, b4 = derivs(Tcell + dt * a3, Tcase + dt * b3, I, riding, T_amb)
            Tcell += dt / 6 * (a1 + 2 * a2 + 2 * a3 + a4); Tcase += dt / 6 * (b1 + 2 * b2 + 2 * b3 + b4); t += dt
            ts.append(t / 60); cells.append(Tcell); cases.append(Tcase)
    return ts, cells, cases


if __name__ == "__main__":
    T_amb = 32.0   # a Bali afternoon
    # steady state at a constant 15 A: Q = I^2 R through R_int + 1/(hA) in series
    I = 15.0
    Q = I * I * R_PACK
    R_tot = R_INT + 1 / (h_air(True) * A_CASE)
    print(f"15 A steady: Q = {Q:.3f} W, R_total = {R_tot:.4f} K/W, cells {T_amb + Q*R_tot:.3f} C, case {T_amb + Q/(h_air(True)*A_CASE):.3f} C")
    ts, cells, cases = simulate([(600, I, True)], T_amb)
    print(f"after a 10 h simulated ride at 15 A: cells {cells[-1]:.4f} C, case {cases[-1]:.4f} C")
    assert abs(cells[-1] - (T_amb + Q * R_tot)) < 1e-3 and abs(cases[-1] - (T_amb + Q / (h_air(True) * A_CASE))) < 1e-3
    # time constants of the network: eigenvalues of the 2x2 system
    a = -1 / (R_INT * C_CELLS); b = 1 / (R_INT * C_CELLS)
    c = 1 / (R_INT * C_CASE); d = -(1 / R_INT + h_air(True) * A_CASE) / C_CASE
    tr, det = a + d, a * d - b * c
    l1, l2 = (tr + math.sqrt(tr * tr - 4 * det)) / 2, (tr - math.sqrt(tr * tr - 4 * det)) / 2
    print(f"time constants: {-1/l1/60:.2f} min (slow, whole pack) and {-1/l2/60:.2f} min (fast, case)")
    # a ride: 20 min flat at 10 A, a 15 min climb at 25 A, 25 min rolling at 8 A, then parked 30 min
    ride = [(20, 10.0, True), (15, 25.0, True), (25, 8.0, True), (30, 0.0, False)]
    ts, cells, cases = simulate(ride, T_amb)
    k = max(range(len(cells)), key=cells.__getitem__)
    print(f"ride: peak cell temperature {cells[k]:.3f} C at {ts[k]:.2f} min; at the end of the climb (35 min) {cells[35*60]:.3f} C; parked at 90 min {cells[-1]:.3f} C")
    assert cells[k] < 60.0 and cells[k] < T_amb + 25.0**2 * R_PACK * R_tot   # below the cell limit and below the 25 A steady value
    # energy check: heat generated = heat stored + heat convected
    gen = sum(m * 60 * i * i * R_PACK for m, i, _ in ride)
    stored = C_CELLS * (cells[-1] - T_amb) + C_CASE * (cases[-1] - T_amb)
    lost, idx = 0.0, 0
    for m, i, riding in ride:
        for _ in range(m * 60):
            lost += h_air(riding) * A_CASE * 0.5 * (cases[idx] + cases[idx + 1] - 2 * T_amb); idx += 1
    print(f"energy: generated {gen:.1f} J = stored {stored:.1f} J + convected {lost:.1f} J (gap {gen - stored - lost:.2f} J)")
    assert abs(gen - stored - lost) < 1e-3 * gen
