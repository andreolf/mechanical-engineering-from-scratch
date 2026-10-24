DIMS = ("m", "kg", "s", "A", "K", "mol", "cd")


class UnitError(TypeError):
    pass


class Quantity:
    def __init__(self, value, dims):
        self.value = float(value)
        self.dims = tuple(dims)

    def _check(self, other):
        if self.dims != other.dims:
            raise UnitError(f"cannot combine {self.unit()} and {other.unit()}")

    def __add__(self, other):
        self._check(other)
        return Quantity(self.value + other.value, self.dims)

    def __sub__(self, other):
        self._check(other)
        return Quantity(self.value - other.value, self.dims)

    def __mul__(self, other):
        if not isinstance(other, Quantity):
            return Quantity(self.value * other, self.dims)
        d = tuple(a + b for a, b in zip(self.dims, other.dims))
        return Quantity(self.value * other.value, d)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if not isinstance(other, Quantity):
            return Quantity(self.value / other, self.dims)
        d = tuple(a - b for a, b in zip(self.dims, other.dims))
        return Quantity(self.value / other.value, d)

    def __pow__(self, p):
        return Quantity(self.value ** p, tuple(a * p for a in self.dims))

    def unit(self):
        parts = [f"{n}^{e}" if e != 1 else n
                 for n, e in zip(DIMS, self.dims) if e]
        return " ".join(parts) or "1"


def q(value, m=0, kg=0, s=0, A=0, K=0, mol=0, cd=0):
    return Quantity(value, (m, kg, s, A, K, mol, cd))


N = q(1, m=1, kg=1, s=-2)
LBF = 4.448222 * N
SEC = q(1, s=1)

if __name__ == "__main__":
    J = 12.0 * LBF * SEC
    m = q(338, kg=1)
    dv = J / m
    assert dv.dims == q(1, m=1, s=-1).dims
    assert abs(J.value - 53.378664) < 1e-6
    assert abs(dv.value - 0.15792) < 1e-5
    try:
        q(1, m=1) + q(1, s=1)
    except UnitError as e:
        print("refused:", e)
    else:
        raise AssertionError("adding m and s must fail")
    print(f"impulse {J.value:.2f} {J.unit()}, dv {dv.value:.4f} {dv.unit()}")
