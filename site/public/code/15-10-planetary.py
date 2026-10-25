"""Planetary gear set: the Willis equation, checked by solving the rolling-without-slip conditions at the two meshes, plus assembly conditions and the ratios of a three-speed bicycle hub."""
import numpy as np
from fractions import Fraction


def willis(zs, zr, ws=None, wr=None, wc=None):
    """(wr - wc)/(ws - wc) = -zs/zr. Give two speeds, get the third."""
    k = Fraction(zs, zr)
    if wc is None:
        return (wr + k * ws) / (1 + k)
    if wr is None:
        return wc - k * (ws - wc)
    return wc - (wr - wc) / k


def kinematics(zs, zp, zr, given, m=1.0):
    """Unknowns ws, wp (planet spin, absolute), wr, wc. Pitch-point velocities must match at sun-planet and planet-ring.
    given: dict with two of 'ws', 'wr', 'wc'. Returns all four speeds."""
    rs, rp, rr = m * zs / 2, m * zp / 2, m * zr / 2
    assert abs(rr - (rs + 2 * rp)) < 1e-12
    names = ["ws", "wp", "wr", "wc"]
    A, b = [], []
    # planet centre at radius rs + rp moves at wc (rs + rp); its contact with the sun is rp nearer the centre
    A.append([rs, rp, 0, -(rs + rp)]); b.append(0.0)    # sun surface speed = planet-centre speed - wp rp
    A.append([0, -rp, rr, -(rs + rp)]); b.append(0.0)   # ring surface speed = planet-centre speed + wp rp
    for k, v in given.items():
        row = [0.0] * 4; row[names.index(k)] = 1.0; A.append(row); b.append(float(v))
    sol = np.linalg.solve(np.array(A, float), np.array(b))
    return dict(zip(names, sol))


def can_assemble(zs, zp, zr, n_planets):
    return zr == zs + 2 * zp and (zs + zr) % n_planets == 0


if __name__ == "__main__":
    zs, zp, zr = 18, 18, 54
    assert can_assemble(zs, zp, zr, 3) and can_assemble(zs, zp, zr, 4) and not can_assemble(zs, zp, zr, 5)
    for given in ({"ws": 0, "wc": 1}, {"wr": 1, "ws": 0}, {"ws": 1, "wr": 0}, {"ws": 2.5, "wr": -1.0}):
        k = kinematics(zs, zp, zr, given)
        lhs = (k["wr"] - k["wc"]) / (k["ws"] - k["wc"])
        print(", ".join(f"{n} {v:+.4f}" for n, v in k.items()), f"-> Willis ratio {lhs:.6f}")
        assert abs(lhs + zs / zr) < 1e-12
    # three-speed hub: sun locked to the axle. High: carrier in, ring out. Low: ring in, carrier out.
    high = willis(zs, zr, ws=0, wc=1)
    low = willis(zs, zr, ws=0, wr=1)
    print(f"hub gears: low {float(low):.4f}, direct 1, high {float(high):.4f}; spread {float(high/low):.4f}")
    assert high == Fraction(4, 3) and low == Fraction(3, 4)
    # e-bike hub motor stage: motor on the sun, ring fixed, carrier drives the wheel
    zs2, zp2, zr2 = 14, 34, 82
    red = 1 / willis(zs2, zr2, ws=1, wr=0)
    print(f"hub motor reduction {float(red):.4f} : 1 = 1 + zr/zs")
    assert red == 1 + Fraction(zr2, zs2)
