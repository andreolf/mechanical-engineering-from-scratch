"""Sheet-metal bending: bend allowance from the neutral axis, the flat blank for a bracket, and springback with how far to overbend."""
import math


def bend_allowance(theta_deg, R, t, K=0.33):
    """Arc length of the neutral axis through a bend of angle theta, inside radius R, thickness t, K-factor K."""
    return math.radians(theta_deg) * (R + K * t)


def springback_ratio(R, t, Y, E):
    """Inside radius after release divided by before: Ri/Rf = 4 x^3 - 3 x + 1 with x = R Y / (E t)."""
    x = R * Y / (E * t)
    return 4 * x**3 - 3 * x + 1


if __name__ == "__main__":
    t, R, K = 2.0, 3.0, 0.33
    BA = bend_allowance(90, R, t, K)
    print(f"90 deg bend, R = {R} mm, t = {t} mm, K = {K}: bend allowance {BA:.3f} mm")
    # check against the length of a polyline traced along the neutral axis
    rn = R + K * t; n = 100000
    poly = sum(math.dist((rn * math.cos(a0), rn * math.sin(a0)), (rn * math.cos(a1), rn * math.sin(a1)))
               for a0, a1 in ((math.pi / 2 * i / n, math.pi / 2 * (i + 1) / n) for i in range(n)))
    assert abs(poly - BA) < 1e-6
    # U-channel bracket: outside dimensions 30 x 50 x 30 mm, two 90 deg bends
    setback = R + t                      # from outside mould line to the start of the bend
    flats = (30 - setback) + (50 - 2 * setback) + (30 - setback)
    L = flats + 2 * BA
    print(f"U bracket 30 x 50 x 30 (outside): flats {flats:.2f} mm + 2 bends {2*BA:.3f} mm = blank {L:.2f} mm")
    print(f"  bend deduction per bend: {2*setback - BA:.3f} mm (sum of outside dimensions {30+50+30} minus blank {L:.2f} = {110-L:.3f})")
    assert abs((110 - L) - 2 * (2 * setback - BA)) < 1e-12
    # springback of 5052-H32 aluminium
    Y, E = 193.0, 70000.0
    ratio = springback_ratio(R, t, Y, E)
    Rf = R / ratio
    # neutral (mid-plane) length is conserved: (Ri + t/2) theta_i = (Rf + t/2) theta_f
    theta_f = 90 * (R + t / 2) / (Rf + t / 2)
    theta_i = 90 * 90 / theta_f
    print(f"5052-H32: Ri/Rf = {ratio:.5f}, released radius {Rf:.3f} mm, a 90 deg bend opens to {theta_f:.2f} deg; overbend to {theta_i:.2f} deg")
    for steel in ((350.0, 210000.0, "mild steel"), (1000.0, 210000.0, "spring steel")):
        r = springback_ratio(R, t, steel[0], steel[1])
        print(f"  {steel[2]}: Ri/Rf = {r:.5f}, opens to {90*(R+t/2)/(R/r+t/2):.2f} deg")
