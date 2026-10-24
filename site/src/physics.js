// Pure physics models used by the labs. All are educational approximations; assumptions are stated inline.

// Euler-Bernoulli cantilever (fixed at x=0), point load P (N, downward) at x=a. Small deflections, linear elastic.
export function cantilever(P, a, x, EI) {
  if (x <= a) return { w: (P * x * x * (3 * a - x)) / (6 * EI), M: P * (a - x) };
  return { w: (P * a * a * (3 * x - a)) / (6 * EI), M: 0 };
}

export const BEAM_MATERIALS = {
  steel: { name: 'Steel S235', E: 210e9, sy: 235e6, note: 'yield 235 MPa' },
  aluminium: { name: 'Aluminium 6061-T6', E: 69e9, sy: 275e6, note: 'yield ~275 MPa' },
  bamboo: { name: 'Bamboo (typical, varies widely)', E: 15e9, sy: 100e6, note: 'strength order ~100 MPa' },
};

// ---------- Truss: direct stiffness method (2D pin-jointed bars) ----------
// nodes: [{x,y,fx,fy}] (fx/fy true = fixed DOF); members: [{a,b,EA}] ; loads: Float64Array(2n)
export function solveTruss(nodes, members, loads) {
  const n = nodes.length, N = 2 * n;
  const K = Array.from({ length: N }, () => new Float64Array(N));
  const used = new Uint8Array(n);
  for (const m of members) {
    const A = nodes[m.a], B = nodes[m.b];
    const dx = B.x - A.x, dy = B.y - A.y, L = Math.hypot(dx, dy), c = dx / L, s = dy / L;
    const k = m.EA / L, kk = [c * c, c * s, s * s];
    const idx = [2 * m.a, 2 * m.a + 1, 2 * m.b, 2 * m.b + 1];
    const ke = [[kk[0], kk[1], -kk[0], -kk[1]], [kk[1], kk[2], -kk[1], -kk[2]], [-kk[0], -kk[1], kk[0], kk[1]], [-kk[1], -kk[2], kk[1], kk[2]]];
    for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) K[idx[i]][idx[j]] += k * ke[i][j];
    used[m.a] = used[m.b] = 1;
  }
  // free DOFs: not fixed, and (node connected or loaded)
  const free = [];
  for (let i = 0; i < n; i++) {
    const loaded = Math.abs(loads[2 * i]) + Math.abs(loads[2 * i + 1]) > 0;
    if (!used[i] && !loaded) continue;
    if (!nodes[i].fx) free.push(2 * i);
    if (!nodes[i].fy) free.push(2 * i + 1);
  }
  const f = free.length;
  let maxDiag = 0;
  for (const d of free) maxDiag = Math.max(maxDiag, K[d][d]);
  const build = (eps) => {
    const A = free.map((r) => Float64Array.from(free.map((c) => K[r][c] + (r === c ? eps : 0))));
    const b = Float64Array.from(free.map((r) => loads[r]));
    return [A, b];
  };
  const gauss = (A, b) => {
    let minPivot = Infinity;
    for (let col = 0; col < f; col++) {
      let p = col;
      for (let r = col + 1; r < f; r++) if (Math.abs(A[r][col]) > Math.abs(A[p][col])) p = r;
      [A[col], A[p]] = [A[p], A[col]]; [b[col], b[p]] = [b[p], b[col]];
      const piv = A[col][col];
      minPivot = Math.min(minPivot, Math.abs(piv));
      if (Math.abs(piv) < 1e-300) return { x: null, minPivot: 0 };
      for (let r = col + 1; r < f; r++) {
        const fac = A[r][col] / piv;
        if (fac === 0) continue;
        for (let c = col; c < f; c++) A[r][c] -= fac * A[col][c];
        b[r] -= fac * b[col];
      }
    }
    const x = new Float64Array(f);
    for (let r = f - 1; r >= 0; r--) {
      let sum = b[r];
      for (let c = r + 1; c < f; c++) sum -= A[r][c] * x[c];
      x[r] = sum / A[r][r];
    }
    return { x, minPivot };
  };
  let [A, b] = build(0);
  let { x, minPivot } = gauss(A, b);
  const mechanism = !x || minPivot < 1e-9 * maxDiag;
  if (mechanism) {
    // Regularised solve: the response is dominated by the zero-energy (mechanism) mode excited by the load.
    [A, b] = build(1e-7 * maxDiag);
    x = gauss(A, b).x;
  }
  const u = new Float64Array(N);
  free.forEach((d, i) => (u[d] = x ? x[i] : 0));
  const forces = members.map((m) => {
    const A = nodes[m.a], B = nodes[m.b];
    const dx = B.x - A.x, dy = B.y - A.y, L = Math.hypot(dx, dy);
    return (m.EA / L) * ((dx / L) * (u[2 * m.b] - u[2 * m.a]) + (dy / L) * (u[2 * m.b + 1] - u[2 * m.a + 1]));
  });
  return { u, forces, mechanism };
}

// ---------- Heavy symmetric gyroscope on a frictionless pivot ----------
// State: n (unit axle vector, world), L (angular momentum about pivot, world). z is up.
export function gyroDerivs(n, L, p) {
  const Ln = L[0] * n[0] + L[1] * n[1] + L[2] * n[2];
  const Lp = [L[0] - Ln * n[0], L[1] - Ln * n[1], L[2] - Ln * n[2]];
  const w = [Lp[0] / p.I1, Lp[1] / p.I1, Lp[2] / p.I1]; // only the perpendicular part moves the axle
  const dn = [w[1] * n[2] - w[2] * n[1], w[2] * n[0] - w[0] * n[2], w[0] * n[1] - w[1] * n[0]];
  // torque of gravity about pivot: (l n) x (0,0,-m g)
  const mg = p.m * p.g;
  const tau = [-p.l * n[1] * mg, p.l * n[0] * mg, 0];
  const dL = [tau[0] - p.c * Lp[0], tau[1] - p.c * Lp[1], tau[2] - p.c * Lp[2]];
  return { dn, dL };
}
export function gyroStep(s, p, h) {
  const add = (a, b, k) => [a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k];
  const k1 = gyroDerivs(s.n, s.L, p);
  const k2 = gyroDerivs(add(s.n, k1.dn, h / 2), add(s.L, k1.dL, h / 2), p);
  const k3 = gyroDerivs(add(s.n, k2.dn, h / 2), add(s.L, k2.dL, h / 2), p);
  const k4 = gyroDerivs(add(s.n, k3.dn, h), add(s.L, k3.dL, h), p);
  const n = [0, 1, 2].map((i) => s.n[i] + (h / 6) * (k1.dn[i] + 2 * k2.dn[i] + 2 * k3.dn[i] + k4.dn[i]));
  const L = [0, 1, 2].map((i) => s.L[i] + (h / 6) * (k1.dL[i] + 2 * k2.dL[i] + 2 * k3.dL[i] + k4.dL[i]));
  const nn = Math.hypot(n[0], n[1], n[2]);
  return { n: n.map((v) => v / nn), L };
}

// ---------- 1D pipe flow (Bernoulli + optional Darcy loss) ----------
export const WATER = { rho: 998, mu: 1.0e-3, pv: 2340 }; // 20 C, vapour pressure ~2.34 kPa
export function venturiRadius(x, Rin, Rt, len) {
  // x in [0,len]; inlet straight 0..0.3, contraction 0.3..0.45, throat 0.45..0.55, diffuser 0.55..0.85, outlet
  const t = x / len;
  const blend = (a, b, s) => a + (b - a) * (0.5 - 0.5 * Math.cos(Math.PI * Math.min(1, Math.max(0, s))));
  if (t < 0.3) return Rin;
  if (t < 0.45) return blend(Rin, Rt, (t - 0.3) / 0.15);
  if (t < 0.55) return Rt;
  if (t < 0.85) return blend(Rt, Rin, (t - 0.55) / 0.3);
  return Rin;
}
export function pipeState({ Q, D, d, p1, friction, len = 2.0, samples = 120, f = 0.02 }) {
  const Rin = D / 2, Rt = d / 2;
  const A1 = Math.PI * Rin * Rin, U1 = Q / A1;
  const xs = [], U = [], p = [];
  let loss = 0, prevX = 0;
  for (let i = 0; i <= samples; i++) {
    const x = (i / samples) * len;
    const R = venturiRadius(x, Rin, Rt, len);
    const u = Q / (Math.PI * R * R);
    if (friction && i > 0) loss += f * ((x - prevX) / (2 * R)) * 0.5 * WATER.rho * u * u; // Darcy-Weisbach, assumed f
    prevX = x;
    xs.push(x); U.push(u);
    p.push(p1 + 0.5 * WATER.rho * (U1 * U1 - u * u) - loss);
  }
  const Ut = Q / (Math.PI * Rt * Rt);
  const pt = p[Math.round(samples / 2)];
  return { xs, U, p, U1, Ut, pt, p2: p[samples], Re1: (WATER.rho * U1 * D) / WATER.mu, cavitating: Math.min(...p) < WATER.pv };
}
