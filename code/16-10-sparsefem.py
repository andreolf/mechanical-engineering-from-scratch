"""Sparse FEM at scale without scipy: vectorised COO assembly, our own COO-to-CSR conversion, CSR mat-vec, Jacobi-preconditioned conjugate gradients and reverse Cuthill-McKee reordering. Solves a 100k-dof Poisson problem."""
import math
import time
from collections import deque
import numpy as np

KQ4 = np.array([[4, -1, -2, -1], [-1, 4, -1, -2], [-2, -1, 4, -1], [-1, -2, -1, 4]]) / 6.0   # Laplace Q4 on a square, any size


def assemble_coo(nx, ny, perm=None):
    """Poisson -lap u = 1 on the unit square with Q4 elements; returns COO triplets and the load, interior dofs only."""
    h = 1.0 / nx
    idx = np.arange((nx + 1) * (ny + 1)).reshape(ny + 1, nx + 1)
    e = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    rows = np.repeat(e, 4, axis=1).ravel(); cols = np.tile(e, (1, 4)).ravel(); vals = np.tile(KQ4.ravel(), len(e))
    F = np.zeros(idx.size); np.add.at(F, e.ravel(), h * h / 4)
    bnd = np.zeros(idx.size, bool); bnd[idx[0]] = bnd[idx[-1]] = bnd[idx[:, 0]] = bnd[idx[:, -1]] = True
    newid = -np.ones(idx.size, int); newid[~bnd] = np.arange((~bnd).sum())
    if perm is not None:
        newid[~bnd] = perm[newid[~bnd]]
    keep = ~bnd[rows] & ~bnd[cols]
    Fi = np.zeros((~bnd).sum()); Fi[newid[~bnd]] = F[~bnd]
    return newid[rows[keep]], newid[cols[keep]], vals[keep], Fi


def coo_to_csr(r, c, v, n):
    """Sort by (row, col), sum duplicates, build row pointers."""
    order = np.lexsort((c, r)); r, c, v = r[order], c[order], v[order]
    new = np.ones(len(r), bool); new[1:] = (r[1:] != r[:-1]) | (c[1:] != c[:-1])
    start = np.flatnonzero(new)
    data = np.add.reduceat(v, start); ri, ci = r[start], c[start]
    indptr = np.zeros(n + 1, int); np.add.at(indptr, ri + 1, 1); indptr = np.cumsum(indptr)
    return data, ci, indptr


def csr_matvec(data, ind, ptr, x):
    rows = np.repeat(np.arange(len(ptr) - 1), np.diff(ptr))
    return np.bincount(rows, weights=data * x[ind], minlength=len(ptr) - 1)


def pcg(data, ind, ptr, b, tol=1e-10, maxit=10000):
    rows = np.repeat(np.arange(len(ptr) - 1), np.diff(ptr))
    diag = np.bincount(rows, weights=data * (ind == rows), minlength=len(b))
    mv = lambda x: np.bincount(rows, weights=data * x[ind], minlength=len(b))
    x = np.zeros_like(b); r = b.copy(); z = r / diag; p = z.copy(); rz = r @ z; nb = np.linalg.norm(b)
    for k in range(maxit):
        Ap = mv(p); a = rz / (p @ Ap); x += a * p; r -= a * Ap
        if np.linalg.norm(r) < tol * nb:
            return x, k + 1
        z = r / diag; rz2 = r @ z; p = z + rz2 / rz * p; rz = rz2
    raise RuntimeError("CG did not converge")


def bandwidth(ind, ptr):
    rows = np.repeat(np.arange(len(ptr) - 1), np.diff(ptr))
    return int(np.max(np.abs(rows - ind)))


def rcm(ind, ptr):
    """Reverse Cuthill-McKee: breadth-first search from a low-degree node, neighbours by increasing degree, then reverse."""
    n = len(ptr) - 1; deg = np.diff(ptr); seen = np.zeros(n, bool); order = []
    for s in np.argsort(deg, kind="stable"):
        if seen[s]: continue
        seen[s] = True; q = deque([s])
        while q:
            i = q.popleft(); order.append(i)
            nb = [j for j in ind[ptr[i]:ptr[i + 1]] if not seen[j]]
            for j in sorted(nb, key=lambda j: deg[j]):
                seen[j] = True; q.append(j)
    order = np.array(order[::-1])
    perm = np.empty(n, int); perm[order] = np.arange(n)   # old index -> new index
    return perm


def u_centre_exact(terms=200):
    """Series solution of -lap u = 1 on the unit square, at the centre."""
    s = 0.0
    for m in range(1, terms, 2):
        for n in range(1, terms, 2):
            s += 16 / (math.pi**4 * m * n * (m * m + n * n)) * math.sin(m * math.pi / 2) * math.sin(n * math.pi / 2)
    return s


if __name__ == "__main__":
    # small problem: sparse pipeline equals the dense solve
    nx = 12; n = (nx - 1) ** 2
    r, c, v, F = assemble_coo(nx, nx)
    data, ind, ptr = coo_to_csr(r, c, v, n)
    Kd = np.zeros((n, n)); np.add.at(Kd, (r, c), v)
    x = np.random.default_rng(1).normal(size=n)
    assert np.allclose(csr_matvec(data, ind, ptr, x), Kd @ x)
    u_cg, it = pcg(data, ind, ptr, F)
    u_d = np.linalg.solve(Kd, F)
    print(f"12 x 12 mesh, {n} dofs: CG ({it} iterations) vs dense, max difference {np.max(np.abs(u_cg - u_d)):.2e}")
    assert np.max(np.abs(u_cg - u_d)) < 1e-12
    # bandwidth: a scrambled numbering, then RCM
    rng = np.random.default_rng(16); scr = rng.permutation(n)
    r2, c2, v2, F2 = assemble_coo(nx, nx, scr); d2, i2, p2 = coo_to_csr(r2, c2, v2, n)
    perm = rcm(i2, p2)
    d3, i3, p3 = coo_to_csr(perm[r2], perm[c2], v2, n)
    print(f"bandwidth: natural {bandwidth(ind, ptr)}, scrambled {bandwidth(i2, p2)}, after RCM {bandwidth(i3, p3)}")
    assert bandwidth(i3, p3) < bandwidth(i2, p2) / 4
    F3 = np.empty(n); F3[perm] = F2
    u3, _ = pcg(d3, i3, p3, F3)
    assert np.allclose(u3[perm[scr]], u_d, atol=1e-12)     # same answer in any numbering
    # at scale: 317 x 317 elements, 99 856 dofs
    nx = 317; n = (nx - 1) ** 2; t0 = time.time()
    r, c, v, F = assemble_coo(nx, nx); data, ind, ptr = coo_to_csr(r, c, v, n); t1 = time.time()
    u, it = pcg(data, ind, ptr, F); t2 = time.time()
    mid = (nx // 2 - 1) * (nx - 1) + (nx // 2 - 1)        # node nearest the centre (x = y = 158/317)
    ue = u_centre_exact()
    print(f"{n} dofs, {len(data)} stored nonzeros ({len(data)/n**2*100:.4f} % of the dense matrix, which would need {n*n*8/1e9:.0f} GB)")
    print(f"assembly {t1-t0:.2f} s, CG {it} iterations {t2-t1:.2f} s; u near the centre {u[mid]:.6f}, series at the centre {ue:.6f}")
    assert n > 99_000 and abs(u[mid] - ue) < 1e-4
