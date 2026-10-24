"""CSR storage and matrix-vector product, and the Thomas algorithm for tridiagonal systems."""
import time
import numpy as np


class CSR:
    def __init__(self, dense, tol=0.0):
        self.n = len(dense); self.data, self.indices, self.indptr = [], [], [0]
        for row in dense:
            for j, v in enumerate(row):
                if abs(v) > tol:
                    self.data.append(float(v)); self.indices.append(j)
            self.indptr.append(len(self.data))

    @classmethod
    def tridiag(cls, lower, diag, upper):
        m = cls([]); n = len(diag); m.n = n
        for i in range(n):
            if i > 0: m.data.append(lower[i - 1]); m.indices.append(i - 1)
            m.data.append(diag[i]); m.indices.append(i)
            if i < n - 1: m.data.append(upper[i]); m.indices.append(i + 1)
            m.indptr.append(len(m.data))
        return m

    def matvec(self, x):
        return [sum(self.data[k] * x[self.indices[k]] for k in range(self.indptr[i], self.indptr[i + 1])) for i in range(self.n)]


def thomas(a, b, c, d):
    """Solve a tridiagonal system: a = sub-diagonal (n-1), b = diagonal (n), c = super-diagonal (n-1)."""
    n = len(b); cp = [0.0] * (n - 1); dp = [0.0] * n
    cp[0] = c[0] / b[0] if n > 1 else 0.0; dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i - 1] * cp[i - 1]
        if i < n - 1: cp[i] = c[i] / m
        dp[i] = (d[i] - a[i - 1] * dp[i - 1]) / m
    x = [0.0] * n; x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


if __name__ == "__main__":
    A4 = [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 1]]
    m = CSR(A4)
    assert m.data == [2, -1, -1, 2, -1, -1, 2, -1, -1, 1] and m.indptr == [0, 2, 5, 8, 10]
    assert m.matvec([1, 2, 3, 4]) == list(np.array(A4) @ [1, 2, 3, 4])
    for n in (500, 2000):
        a = [-1.0] * (n - 1); c = [-1.0] * (n - 1); b = [2.0] * n; b[-1] = 1.0
        d = [0.0] * n; d[-1] = 1.0                        # pull on the free end of a spring chain
        t = time.perf_counter(); x = thomas(a, b, c, d); tt = time.perf_counter() - t
        K = np.diag(b) + np.diag(a, -1) + np.diag(c, 1)
        t = time.perf_counter(); xd = np.linalg.solve(K, d); td = time.perf_counter() - t
        assert np.allclose(x, np.arange(1, n + 1)) and np.allclose(x, xd)
        assert np.allclose(CSR.tridiag(a, b, c).matvec(x), d)
        print(f"n = {n}: Thomas (Python) {tt*1e3:6.2f} ms, dense LU (NumPy) {td*1e3:6.2f} ms, dense storage {n*n*8/1e6:5.1f} MB vs {3*n*8/1e3:5.1f} kB")
