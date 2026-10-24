// Physics checks against closed-form results: `npm run test:unit`
import test from 'node:test';
import assert from 'node:assert/strict';
import { cantilever, solveTruss, pipeState, gyroStep, WATER } from '../src/physics.js';

test('cantilever tip deflection equals PL^3/(3EI) and moment PL at the wall', () => {
  const P = 1000, L = 2, EI = 3.5e5;
  assert.ok(Math.abs(cantilever(P, L, L, EI).w - (P * L ** 3) / (3 * EI)) < 1e-12);
  assert.equal(cantilever(P, L, 0, EI).M, P * L);
});

test('two-bar truss matches hand statics; missing bar is detected as mechanism', () => {
  // symmetric V: nodes at (-1,0) and (1,0) pinned, apex at (0,1) loaded with 1000 N down
  const nodes = [{ x: -1, y: 0, fx: true, fy: true }, { x: 1, y: 0, fx: true, fy: true }, { x: 0, y: 1, fx: false, fy: false }];
  const EA = 2e8;
  const loads = new Float64Array(6); loads[5] = -1000;
  const r = solveTruss(nodes, [{ a: 0, b: 2, EA }, { a: 1, b: 2, EA }], loads);
  const expected = -1000 / (2 * Math.sin(Math.PI / 4)); // compression in each bar
  r.forces.forEach((N) => assert.ok(Math.abs(N - expected) < 1e-6, `${N} vs ${expected}`));
  assert.equal(r.mechanism, false);
  const r2 = solveTruss(nodes, [{ a: 0, b: 2, EA }], loads);
  assert.equal(r2.mechanism, true);
});

test('venturi without friction obeys Bernoulli and continuity', () => {
  const s = pipeState({ Q: 0.015, D: 0.1, d: 0.06, p1: 200e3, friction: false });
  assert.ok(Math.abs(s.Ut / s.U1 - (0.1 / 0.06) ** 2) < 1e-9);
  const dp = 0.5 * WATER.rho * (s.Ut ** 2 - s.U1 ** 2);
  assert.ok(Math.abs(200e3 - s.pt - dp) < 1e-6);
  assert.ok(Math.abs(s.p2 - 200e3) < 1e-6, 'pressure fully recovers without losses');
});

test('fast gyroscope precesses at about mgl/(I3 w) and stays near horizontal', () => {
  const p = { m: 2, g: 9.81, l: 0.2, r: 0.15, c: 0 };
  p.I3 = 0.5 * p.m * p.r ** 2; p.I1 = 0.25 * p.m * p.r ** 2 + p.m * p.l ** 2;
  const w = 300; let s = { n: [1, 0, 0], L: [p.I3 * w, 0, 0] };
  const T = 2, h = 2e-4;
  for (let t = 0; t < T; t += h) s = gyroStep(s, p, h);
  const phi = Math.atan2(s.n[1], s.n[0]);
  const predicted = (p.m * p.g * p.l) / (p.I3 * w);
  assert.ok(Math.abs(Math.abs(phi) / T - predicted) / predicted < 0.05, `${phi / T} vs ${predicted}`);
  assert.ok(Math.abs(s.n[2]) < 0.05);
});
