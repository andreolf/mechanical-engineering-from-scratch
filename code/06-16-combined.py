"""Combined loading of a bicycle crank arm: axial + bending + torsion, then von Mises around the section."""
import math
import numpy as np


def crank_root_stresses(F, crank_deg, L=170.0, a=60.0, D=24.0, d=16.0, n=721):
    """Stresses round the circumference of a tubular crank arm at the spindle.

    The pedal force F (N) acts straight down at the pedal, L mm along the crank and a mm out
    to the side. crank_deg is the crank angle from horizontal-forward. Returns the angles,
    von Mises stress round the outer surface, and the individual parts.
    """
    th = math.radians(crank_deg)
    A = math.pi * (D**2 - d**2) / 4
    I = math.pi * (D**4 - d**4) / 64
    J = 2 * I
    # resolve F into components along the crank (axial) and across it (bending)
    N = -F * math.sin(th)                  # compressive when the crank points up and you push down
    M = F * math.cos(th) * L               # bending moment at the root (in the plane of rotation)
    T = F * a                              # torque about the crank axis from the pedal offset
    phi = np.linspace(0, 2 * np.pi, n)     # phi = 0 at the top of the section (tension side when M > 0)
    c = D / 2
    sigma = N / A + M * c * np.cos(phi) / I
    tau = T * c / J * np.ones_like(phi)
    vm = np.sqrt(sigma**2 + 3 * tau**2)
    return phi, vm, sigma, tau, dict(N=N, M=M, T=T, A=A, I=I, J=J)


if __name__ == "__main__":
    F = 1000.0                                             # N, a strong rider standing on the pedal
    phi, vm, s, t, k = crank_root_stresses(F, 0.0)
    sb = k["M"] * 12 / k["I"]; st = k["T"] * 12 / k["J"]
    print(f"crank horizontal: M = {k['M']/1e3:.0f} N m, T = {k['T']/1e3:.0f} N m, I = {k['I']:.1f} mm^4")
    print(f"  bending {sb:.2f} MPa, torsion {st:.2f} MPa, hand von Mises {math.hypot(sb, math.sqrt(3) * st):.2f} MPa")
    i = int(np.argmax(vm))
    print(f"  numerical hotspot {vm[i]:.2f} MPa at phi = {math.degrees(phi[i]):.1f} deg (top of the arm)")
    assert abs(vm[i] - math.hypot(sb, math.sqrt(3) * st)) < 1e-9 and math.degrees(phi[i]) % 360 < 1e-9
    # crank at 30 degrees above horizontal: axial compression joins in, and the hotspot moves to the compressed side
    phi, vm, s, t, k = crank_root_stresses(F, 30.0)
    i = int(np.argmax(vm))
    hand = math.hypot(abs(k["N"]) / k["A"] + k["M"] * 12 / k["I"], math.sqrt(3) * st)
    print(f"crank at 30 deg: N = {k['N']:.0f} N, M = {k['M']/1e3:.2f} N m; hotspot {vm[i]:.2f} MPa at phi = {math.degrees(phi[i]):.0f} deg (hand {hand:.2f})")
    assert abs(vm[i] - hand) < 1e-9 and abs(math.degrees(phi[i]) - 180) < 1e-9
    # sweep the crank round: the worst position is horizontal
    angs = np.arange(-90, 91, 5)
    peak = [crank_root_stresses(F, a)[1].max() for a in angs]
    print(f"worst crank angle {angs[int(np.argmax(peak))]} deg, {max(peak):.2f} MPa; safety factor on 355 MPa steel {355 / max(peak):.2f}")
