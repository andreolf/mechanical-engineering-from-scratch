"""Forward-mode automatic differentiation with dual numbers."""
import math


class Dual:
    __slots__ = ("a", "b")

    def __init__(self, a, b=0.0):
        self.a, self.b = float(a), float(b)

    @staticmethod
    def lift(x):
        return x if isinstance(x, Dual) else Dual(x)

    def __add__(self, o): o = Dual.lift(o); return Dual(self.a + o.a, self.b + o.b)
    __radd__ = __add__
    def __sub__(self, o): o = Dual.lift(o); return Dual(self.a - o.a, self.b - o.b)
    def __rsub__(self, o): return Dual.lift(o) - self
    def __neg__(self): return Dual(-self.a, -self.b)
    def __mul__(self, o): o = Dual.lift(o); return Dual(self.a * o.a, self.a * o.b + self.b * o.a)
    __rmul__ = __mul__
    def __truediv__(self, o):
        o = Dual.lift(o)
        return Dual(self.a / o.a, (self.b * o.a - self.a * o.b) / (o.a * o.a))
    def __rtruediv__(self, o): return Dual.lift(o) / self
    def __pow__(self, n):  # real exponent
        return Dual(self.a ** n, n * self.a ** (n - 1) * self.b)


def sin(x):  x = Dual.lift(x); return Dual(math.sin(x.a), math.cos(x.a) * x.b)
def cos(x):  x = Dual.lift(x); return Dual(math.cos(x.a), -math.sin(x.a) * x.b)
def exp(x):  x = Dual.lift(x); e = math.exp(x.a); return Dual(e, e * x.b)
def log(x):  x = Dual.lift(x); return Dual(math.log(x.a), x.b / x.a)
def sinh(x): x = Dual.lift(x); return Dual(math.sinh(x.a), math.cosh(x.a) * x.b)
def cosh(x): x = Dual.lift(x); return Dual(math.cosh(x.a), math.sinh(x.a) * x.b)


def derivative(f, x):
    return f(Dual(x, 1.0)).b


if __name__ == "__main__":
    for x in (0.3, 1.5, 4.0):
        d = derivative(lambda t: sin(t ** 2), x)
        assert abs(d - 2 * x * math.cos(x * x)) < 1e-14     # machine precision
    d = derivative(lambda t: t ** 3 * sin(t), 2.0)
    assert abs(d - (12 * math.sin(2) + 8 * math.cos(2))) < 1e-13
    d = derivative(lambda t: exp(t * log(t)), 2.0)         # x^x
    assert abs(d - 4 * (math.log(2) + 1)) < 1e-13
    print(f"d/dx x^3 sin x at 2 = {derivative(lambda t: t ** 3 * sin(t), 2.0):.6f}")
