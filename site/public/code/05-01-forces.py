"""Forces as vectors: a small Force class, components, and the resultant of a concurrent system."""
import math
import numpy as np


class Force:
    """A bound vector: magnitude and direction plus the point it acts at (needed later for moments)."""

    def __init__(self, fx, fy, fz=0.0, at=(0.0, 0.0, 0.0)):
        self.v = np.array([fx, fy, fz], float)
        self.at = np.array(at, float)

    @classmethod
    def polar(cls, magnitude, angle_deg, at=(0.0, 0.0, 0.0)):
        a = math.radians(angle_deg)
        return cls(magnitude * math.cos(a), magnitude * math.sin(a), 0.0, at)

    @classmethod
    def along(cls, magnitude, start, end):
        """A force of given magnitude pulling from start towards end, e.g. a cable."""
        d = np.array(end, float) - np.array(start, float)
        return cls(*(magnitude * d / np.linalg.norm(d)), at=start)

    @property
    def magnitude(self):
        return float(np.linalg.norm(self.v))

    @property
    def angle_deg(self):
        return math.degrees(math.atan2(self.v[1], self.v[0]))

    def __add__(self, other):
        return Force(*(self.v + other.v), at=self.at)


def resultant(forces):
    out = Force(0, 0, 0, at=forces[0].at)
    for f in forces:
        out = out + f
    return out


if __name__ == "__main__":
    # three cables pulling on the head of a scaffold pole (kN, angles from the x axis)
    F = [Force.polar(2.0, 30), Force.polar(3.0, 135), Force.polar(1.5, 250)]
    R = resultant(F)
    print("components (kN):", ", ".join(f"({f.v[0]:.4f}, {f.v[1]:.4f})" for f in F))
    print(f"resultant {R.magnitude:.4f} kN at {R.angle_deg:.2f} deg")
    assert np.allclose(R.v, sum(f.v for f in F))                       # component-wise sum
    assert abs(R.magnitude - math.hypot(*sum(f.v for f in F)[:2])) < 1e-12
    # a 3D guy wire: 12 kN from the top of a 20 m mast to an anchor 8 m east and 6 m north of its base
    T = Force.along(12.0, (0, 0, 20), (8, 6, 0))
    L = math.sqrt(8**2 + 6**2 + 20**2)
    print(f"guy wire length {L:.3f} m, components {np.round(T.v, 4)} kN")
    assert np.allclose(T.v, 12 * np.array([8, 6, -20]) / L) and abs(T.magnitude - 12) < 1e-12
    # a fourth cable that brings the pole head to equilibrium is just -R
    F4 = Force(*(-R.v))
    assert resultant(F + [F4]).magnitude < 1e-12
    print(f"balancing force {F4.magnitude:.4f} kN at {F4.angle_deg:.2f} deg")
