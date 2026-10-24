// Small 2D canvas widgets used inside lessons. Each one has thumb-friendly controls below the plot.
const C = { ink: '#000', paper: '#f2f3ec', grey: '#9a9d93', rule: 'rgba(242,243,236,0.14)', lime: '#eeff41', red: '#ff5a36', cyan: '#5cc8ff', amber: '#ffb547' };
const nf = (d) => new Intl.NumberFormat('en-US', { maximumFractionDigits: d, minimumFractionDigits: d });

class Plot {
  constructor(canvas) { this.c = canvas; this.g = canvas.getContext('2d'); }
  size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2), r = this.c.getBoundingClientRect();
    this.w = r.width; this.h = r.height; this.c.width = Math.round(r.width * dpr); this.c.height = Math.round(r.height * dpr);
    this.g.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.pad = { l: 46, r: 12, t: 12, b: 30 };
  }
  frame({ x, y, xlog = false, ylog = false, xlabel = '', ylabel = '' }) {
    this.size();
    Object.assign(this, { xr: x, yr: y, xlog, ylog });
    const g = this.g; g.clearRect(0, 0, this.w, this.h);
    g.font = '11px "Archivo Variable", sans-serif'; g.fillStyle = C.grey; g.strokeStyle = C.rule; g.lineWidth = 1;
    const ticks = (r, log) => log ? range(Math.ceil(Math.log10(r[0])), Math.floor(Math.log10(r[1]))).map((e) => 10 ** e) : niceTicks(r[0], r[1], 5);
    for (const t of ticks(x, xlog)) { const px = this.X(t); g.beginPath(); g.moveTo(px, this.pad.t); g.lineTo(px, this.h - this.pad.b); g.stroke(); g.textAlign = 'center'; g.fillText(lab(t, xlog), px, this.h - this.pad.b + 14); }
    for (const t of ticks(y, ylog)) { const py = this.Y(t); g.beginPath(); g.moveTo(this.pad.l, py); g.lineTo(this.w - this.pad.r, py); g.stroke(); g.textAlign = 'right'; g.fillText(lab(t, ylog), this.pad.l - 6, py + 4); }
    g.textAlign = 'right'; g.fillText(xlabel, this.w - this.pad.r, this.h - 4);
    g.save(); g.translate(11, this.pad.t); g.rotate(-Math.PI / 2); g.textAlign = 'right'; g.fillText(ylabel, 0, 0); g.restore();
    return this;
  }
  X(v) { const [a, b] = this.xr; const t = this.xlog ? (Math.log10(v) - Math.log10(a)) / (Math.log10(b) - Math.log10(a)) : (v - a) / (b - a); return this.pad.l + t * (this.w - this.pad.l - this.pad.r); }
  Y(v) { const [a, b] = this.yr; const t = this.ylog ? (Math.log10(v) - Math.log10(a)) / (Math.log10(b) - Math.log10(a)) : (v - a) / (b - a); return this.h - this.pad.b - t * (this.h - this.pad.t - this.pad.b); }
  line(xs, ys, color = C.lime, width = 2, dash = []) {
    const g = this.g; g.save(); g.beginPath(); g.rect(this.pad.l, this.pad.t, this.w - this.pad.l - this.pad.r, this.h - this.pad.t - this.pad.b); g.clip();
    g.strokeStyle = color; g.lineWidth = width; g.setLineDash(dash); g.beginPath();
    let pen = false;
    xs.forEach((x, i) => { const y = ys[i]; if (!isFinite(y) || (this.ylog && y <= 0)) { pen = false; return; } const px = this.X(x), py = this.Y(y); pen ? g.lineTo(px, py) : g.moveTo(px, py); pen = true; });
    g.stroke(); g.restore(); return this;
  }
  dots(xs, ys, color = C.lime, r = 3.5) { const g = this.g; g.fillStyle = color; xs.forEach((x, i) => { if (!isFinite(ys[i])) return; g.beginPath(); g.arc(this.X(x), this.Y(ys[i]), r, 0, 7); g.fill(); }); return this; }
  rect(x0, x1, y0, y1, fill) { const g = this.g; g.fillStyle = fill; const a = this.X(x0), b = this.X(x1), c = this.Y(y0), d = this.Y(y1); g.fillRect(Math.min(a, b), Math.min(c, d), Math.abs(b - a), Math.abs(d - c)); return this; }
  text(s, x, y, color = C.paper, align = 'left') { const g = this.g; g.fillStyle = color; g.font = '12px "Archivo Variable", sans-serif'; g.textAlign = align; g.fillText(s, this.X(x), this.Y(y)); return this; }
}
function range(a, b) { const r = []; for (let i = a; i <= b; i++) r.push(i); return r; }
function niceTicks(a, b, n) { const span = b - a, step0 = span / n, mag = 10 ** Math.floor(Math.log10(step0)); const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= step0); const out = []; for (let v = Math.ceil(a / step) * step; v <= b + 1e-9 * span; v += step) out.push(+v.toPrecision(12)); return out; }
function lab(t, log) { if (log) return `1e${Math.round(Math.log10(t))}`; return Math.abs(t) >= 1e4 || (Math.abs(t) < 1e-2 && t !== 0) ? t.toExponential(0) : String(+t.toPrecision(4)); }
const linspace = (a, b, n) => Array.from({ length: n }, (_, i) => a + ((b - a) * i) / (n - 1));
const logspace = (a, b, n) => linspace(a, b, n).map((e) => 10 ** e);

const W = {};
function def(name, spec) { W[name] = spec; }

// 00.04 Fermi estimate with log-uniform factors
def('fermi', {
  controls: [{ k: 'spread', label: 'Uncertainty per factor, times or divided by', min: 1.2, max: 4, step: 0.1, v: 2, f: 1 }],
  draw(p, v, out) {
    const N = 4000, nom = [0.8, 0.3, 0.5]; // width m, depth m, mean speed m/s; one day is exact
    const samples = [];
    let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < N; i++) { let q = 86400; for (const x of nom) q *= x * v.spread ** (2 * rnd() - 1); samples.push(q); }
    samples.sort((a, b) => a - b);
    const med = samples[N / 2], lo = samples[Math.floor(N * 0.05)], hi = samples[Math.floor(N * 0.95)];
    const bins = 40, a = Math.log10(samples[0]), b = Math.log10(samples[N - 1]), hgt = new Array(bins).fill(0);
    for (const s of samples) hgt[Math.min(bins - 1, Math.floor(((Math.log10(s) - a) / (b - a)) * bins))]++;
    p.frame({ x: [10 ** a, 10 ** b], y: [0, Math.max(...hgt) * 1.1], xlog: true, xlabel: 'daily volume, m³', ylabel: 'samples' });
    hgt.forEach((c, i) => p.rect(10 ** (a + ((b - a) * i) / bins), 10 ** (a + ((b - a) * (i + 0.9)) / bins), 0, c, 'rgba(238,255,65,0.55)'));
    out(`Median ${nf(0).format(med)} m³/day; 90% of samples between ${nf(0).format(lo)} and ${nf(0).format(hi)}.`);
  },
});

// 00.06 power law on linear vs log axes
def('loglog', {
  controls: [{ k: 'b', label: 'Exponent b in y = 3xᵇ', min: 0.5, max: 3, step: 0.1, v: 1.5, f: 1 }, { k: 'log', label: 'Log-log axes', type: 'check', v: 1 }],
  draw(p, v, out) {
    const xs = v.log ? logspace(-1, 2, 60) : linspace(0.1, 100, 60), ys = xs.map((x) => 3 * x ** v.b);
    p.frame({ x: [0.1, 100], y: v.log ? [3 * 0.1 ** v.b, 3 * 100 ** v.b] : [0, 3 * 100 ** v.b], xlog: !!v.log, ylog: !!v.log, xlabel: 'x', ylabel: 'y' }).line(xs, ys);
    out(v.log ? `On log-log axes the curve is a straight line with slope ${v.b.toFixed(1)}.` : 'On linear axes the power law bends, and the exponent is hard to read.');
  },
});

// 00.07 catastrophic cancellation in (1 - cos x)/x^2
def('cancel', {
  controls: [],
  draw(p, v, out) {
    const xs = logspace(-9, 0, 400);
    const naive = xs.map((x) => Math.abs((1 - Math.cos(x)) / (x * x) - 0.5 + x * x / 24) || 1e-17);
    const stable = xs.map((x) => { const s = Math.sin(x / 2); return Math.abs((2 * s * s) / (x * x) - 0.5 + x * x / 24) || 1e-17; });
    p.frame({ x: [1e-9, 1], y: [1e-18, 10], xlog: true, ylog: true, xlabel: 'x', ylabel: 'absolute error' }).line(xs, naive, C.red, 1.5).line(xs, stable, C.lime, 2);
    p.text('naive (1 − cos x)/x²', 1e-8, 1, C.red).text('stable 2 sin²(x/2)/x²', 1e-8, 1e-15, C.lime);
    out('Below x ≈ 1e-8 the naive formula returns 0 instead of 0.5: every significant digit has cancelled.');
  },
});

// 00.12 train run between two stations
def('trainrun', {
  controls: [{ k: 'vmax', label: 'Top speed (km/h)', min: 60, max: 200, step: 5, v: 125, f: 0 }, { k: 'acc', label: 'Acceleration (m/s²)', min: 0.3, max: 1.3, step: 0.05, v: 0.7, f: 2 }],
  draw(p, v, out) {
    const D = 8000, vm = v.vmax / 3.6, a = v.acc, b = 0.9;
    let t1 = vm / a, t3 = vm / b, s1 = vm * vm / (2 * a), s3 = vm * vm / (2 * b), peak = vm;
    if (s1 + s3 > D) { peak = Math.sqrt((2 * D * a * b) / (a + b)); t1 = peak / a; t3 = peak / b; s1 = peak * peak / (2 * a); s3 = peak * peak / (2 * b); }
    const t2 = (D - s1 - s3) / peak, T = t1 + t2 + t3;
    p.frame({ x: [0, 600], y: [0, 60], xlabel: 'time, s', ylabel: 'speed, m/s' }).line([0, t1, t1 + t2, T], [0, peak, peak, 0]);
    out(`8 km run: ${nf(0).format(T)} s (${nf(1).format(T / 60)} min), peak ${nf(0).format(peak * 3.6)} km/h, braking at 0.9 m/s².`);
  },
});

// 01.01 Babylonian iteration with an epsilon band
def('sequence', {
  controls: [{ k: 'x0', label: 'Start value a₀', min: 0.2, max: 6, step: 0.1, v: 4, f: 1 }, { k: 'eps', label: 'log₁₀ ε', min: -12, max: -1, step: 1, v: -3, f: 0 }],
  draw(p, v, out) {
    const a = [v.x0]; for (let i = 0; i < 9; i++) a.push((a[i] + 2 / a[i]) / 2);
    const eps = 10 ** v.eps, r2 = Math.SQRT2;
    p.frame({ x: [0, 9], y: [0, Math.max(6, v.x0) * 1.05], xlabel: 'n', ylabel: 'aₙ' }).rect(0, 9, r2 - Math.max(eps, 0.02), r2 + Math.max(eps, 0.02), 'rgba(238,255,65,0.12)').line([0, 9], [r2, r2], C.grey, 1, [4, 4]).line(a.map((_, i) => i), a).dots(a.map((_, i) => i), a);
    const N = a.findIndex((x) => Math.abs(x - r2) < eps);
    out(N < 0 ? 'Not inside the band within 9 steps.' : `|aₙ − √2| < 1e${v.eps} from n = ${N} on.`);
  },
});

// 01.02 bisection on the cantilever frequency equation cos(x)cosh(x) + 1 = 0
def('bisection', {
  controls: [{ k: 'n', label: 'Iterations', min: 0, max: 20, step: 1, v: 3, f: 0 }],
  draw(p, v, out) {
    const f = (x) => Math.cos(x) * Math.cosh(x) + 1; let a = 1, b = 3;
    const xs = linspace(0.8, 3.1, 240);
    p.frame({ x: [0.8, 3.1], y: [-10, 4], xlabel: 'x = βL', ylabel: 'cos x cosh x + 1' }).line([0.8, 3.1], [0, 0], C.grey, 1).line(xs, xs.map(f));
    for (let i = 0; i < v.n; i++) { const m = (a + b) / 2; if (f(a) * f(m) <= 0) b = m; else a = m; }
    p.rect(a, b, -10, 4, 'rgba(238,255,65,0.14)').dots([a, b], [f(a), f(b)], C.cyan);
    out(`Bracket [${a.toFixed(6)}, ${b.toFixed(6)}], width ${(b - a).toExponential(2)} = 2/2^${v.n}. Root 1.8751041.`);
  },
});

// 01.03 finite-difference error vs step
def('fderror', {
  controls: [{ k: 'x', label: 'Point x', min: 0.2, max: 3, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const hs = logspace(-16, 0, 200), d = Math.cos(v.x);
    const fwd = hs.map((h) => Math.abs((Math.sin(v.x + h) - Math.sin(v.x)) / h - d));
    const cen = hs.map((h) => Math.abs((Math.sin(v.x + h) - Math.sin(v.x - h)) / (2 * h) - d));
    p.frame({ x: [1e-16, 1], y: [1e-13, 10], xlog: true, ylog: true, xlabel: 'step h', ylabel: 'error' }).line(hs, fwd, C.red, 1.5).line(hs, cen, C.lime, 2);
    p.text('forward', 1e-3, 1e-1, C.red).text('central', 1e-3, 1e-9, C.lime);
    out('Right side: truncation error (slope 1 forward, 2 central). Left side: round-off grows like ε/h.');
  },
});

// 01.05 Newton iterations
def('newton', {
  controls: [{ k: 'x0', label: 'Start x₀', min: 0.5, max: 4, step: 0.05, v: 3.5, f: 2 }, { k: 'n', label: 'Steps', min: 0, max: 6, step: 1, v: 2, f: 0 }],
  draw(p, v, out) {
    const f = (x) => x * x - 2, df = (x) => 2 * x, xs = linspace(0, 4, 200);
    p.frame({ x: [0, 4], y: [-3, 14], xlabel: 'x', ylabel: 'x² − 2' }).line([0, 4], [0, 0], C.grey, 1).line(xs, xs.map(f));
    let x = v.x0; const errs = [];
    for (let i = 0; i < v.n; i++) { const x1 = x - f(x) / df(x); p.line([x, x1], [f(x), 0], C.cyan, 1.5).line([x1, x1], [0, f(x1)], C.grey, 1, [3, 3]); x = x1; }
    for (let i = 0, y = v.x0; i < 6; i++) { errs.push(Math.abs(y - Math.SQRT2)); y = y - f(y) / df(y); }
    p.dots([x], [0], C.lime, 4.5);
    out(`x = ${x.toPrecision(12)}. Errors per step: ${errs.slice(0, 5).map((e) => e.toExponential(1)).join(', ')}`);
  },
});

// 01.07 Taylor polynomials of sin
def('taylor', {
  controls: [{ k: 'n', label: 'Terms', min: 1, max: 8, step: 1, v: 3, f: 0 }],
  draw(p, v, out) {
    const xs = linspace(-8, 8, 400), T = (x) => { let s = 0, term = x; for (let k = 0; k < v.n; k++) { s += term; term *= -x * x / ((2 * k + 2) * (2 * k + 3)); } return s; };
    p.frame({ x: [-8, 8], y: [-2, 2], xlabel: 'x', ylabel: '' }).line(xs, xs.map(Math.sin), C.grey, 2).line(xs, xs.map(T), C.lime, 2);
    const deg = 2 * v.n - 1, err = Math.abs(T(Math.PI) - Math.sin(Math.PI));
    out(`Degree ${deg}. Error at x = π: ${err.toExponential(2)}.`);
  },
});

// 01.08 pendulum period vs amplitude
def('pendulum', {
  controls: [{ k: 'amp', label: 'Amplitude (°)', min: 1, max: 170, step: 1, v: 30, f: 0 }],
  draw(p, v, out) {
    const K = (k) => { let a = 1, b = Math.sqrt(1 - k * k); for (let i = 0; i < 30; i++) { const t = (a + b) / 2; b = Math.sqrt(a * b); a = t; } return Math.PI / (2 * a); };
    const amps = linspace(1, 170, 170), ratio = amps.map((d) => (2 / Math.PI) * K(Math.sin((d * Math.PI) / 360)));
    const r = (2 / Math.PI) * K(Math.sin((v.amp * Math.PI) / 360));
    p.frame({ x: [0, 180], y: [0.98, 2.2], xlabel: 'amplitude, degrees', ylabel: 'T / T₀' }).line(amps, ratio).line([0, 180], [1.01, 1.01], C.grey, 1, [4, 4]).dots([v.amp], [r], C.cyan, 5);
    out(`At ${v.amp}° the true period is ${((r - 1) * 100).toFixed(2)}% longer than 2π√(L/g).`);
  },
});

// 01.09 Riemann sums
def('riemann', {
  controls: [{ k: 'n', label: 'Rectangles', min: 1, max: 64, step: 1, v: 6, f: 0 }, { k: 'rule', label: 'Rule', type: 'select', options: ['left', 'midpoint', 'right'], v: 'midpoint' }],
  draw(p, v, out) {
    const f = (x) => 1 + x * Math.sin(2 * x) * 0.6 + 0.3 * x, a = 0, b = 3, xs = linspace(a, b, 200), h = (b - a) / v.n;
    p.frame({ x: [0, 3], y: [0, 3.2], xlabel: 'x', ylabel: 'f(x)' });
    let S = 0;
    for (let i = 0; i < v.n; i++) { const xl = a + i * h, xe = v.rule === 'left' ? xl : v.rule === 'right' ? xl + h : xl + h / 2; S += f(xe) * h; p.rect(xl, xl + h, 0, f(xe), 'rgba(238,255,65,0.22)'); }
    p.line(xs, xs.map(f));
    let exact = 0; const N = 20000; for (let i = 0; i < N; i++) exact += f(a + (i + 0.5) * (b - a) / N) * (b - a) / N;
    out(`Sum ${S.toFixed(5)}, integral ${exact.toFixed(5)}, error ${Math.abs(S - exact).toExponential(2)}.`);
  },
});

// 01.15 Torricelli tank: Euler vs exact
def('tank', {
  controls: [{ k: 'dt', label: 'Euler step (s)', min: 5, max: 200, step: 5, v: 60, f: 0 }],
  draw(p, v, out) {
    const A = 1.0, a = 0.002, g = 9.81, h0 = 2, k = (a / A) * Math.sqrt(2 * g), T = (2 * Math.sqrt(h0)) / k;
    const ts = linspace(0, T, 200), exact = ts.map((t) => Math.max(0, Math.sqrt(h0) - (k * t) / 2) ** 2);
    const et = [0], eh = [h0]; let hh = h0, t = 0; while (hh > 0 && t < 2 * T) { hh = Math.max(0, hh - v.dt * k * Math.sqrt(hh)); t += v.dt; et.push(t); eh.push(hh); }
    p.frame({ x: [0, T * 1.15], y: [0, 2.1], xlabel: 'time, s', ylabel: 'level h, m' }).line(ts, exact, C.grey, 2).line(et, eh, C.lime, 2).dots(et, eh, C.lime, 2.5);
    out(`Exact empty time ${T.toFixed(0)} s. Euler with Δt = ${v.dt} s reaches zero at about ${t.toFixed(0)} s.`);
  },
});

// 01.16 damping regimes
def('damping', {
  controls: [{ k: 'zeta', label: 'Damping ratio ζ', min: 0, max: 2.5, step: 0.05, v: 0.2, f: 2 }],
  draw(p, v, out) {
    const wn = 2 * Math.PI, z = v.zeta, ts = linspace(0, 4, 400);
    const x = ts.map((t) => {
      if (z < 1) { const wd = wn * Math.sqrt(1 - z * z); return Math.exp(-z * wn * t) * (Math.cos(wd * t) + (z * wn / wd) * Math.sin(wd * t)); }
      if (z === 1) return Math.exp(-wn * t) * (1 + wn * t);
      const s = wn * Math.sqrt(z * z - 1), r1 = -z * wn + s, r2 = -z * wn - s; return (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r2 - r1);
    });
    p.frame({ x: [0, 4], y: [-1.05, 1.05], xlabel: 'time, s', ylabel: 'x / x₀' }).line([0, 4], [0, 0], C.grey, 1).line(ts, x);
    out(z < 1 ? `Underdamped: oscillates at ${(Math.sqrt(1 - z * z)).toFixed(3)} × the natural frequency while decaying.` : z === 1 ? 'Critically damped: fastest return without overshoot.' : 'Overdamped: no oscillation, slower return than critical.');
  },
});

// 01.18 projectile with and without linear drag
def('projectile', {
  controls: [{ k: 'v0', label: 'Launch speed (m/s)', min: 2, max: 30, step: 1, v: 8, f: 0 }, { k: 'ang', label: 'Angle (°)', min: -30, max: 60, step: 1, v: 0, f: 0 }, { k: 'c', label: 'Drag rate k (1/s)', min: 0, max: 1.5, step: 0.05, v: 0.3, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, th = (v.ang * Math.PI) / 180, vx = v.v0 * Math.cos(th), vy = v.v0 * Math.sin(th), H = 23;
    const traj = (k) => { const X = [], Y = []; let x = 0, y = H, ux = vx, uy = vy; const dt = 0.002; while (y > 0 && X.length < 20000) { X.push(x); Y.push(y); ux -= k * ux * dt; uy -= (g + k * uy) * dt; x += ux * dt; y += uy * dt; } return [X, Y, x]; };
    const [x0, y0, r0] = traj(0), [x1, y1, r1] = traj(v.c);
    p.frame({ x: [0, Math.max(10, r0 * 1.1)], y: [0, H + 8], xlabel: 'distance, m', ylabel: 'height, m' }).line(x0, y0, C.grey, 1.5, [5, 4]).line(x1, y1);
    out(`Falls 23 m. Lands ${r0.toFixed(1)} m out without drag, ${r1.toFixed(1)} m with k = ${v.c}.`);
  },
});

// ---------- Phase 02 ----------
// arrows in plot coordinates
function arrow(p, x0, y0, x1, y1, color, w = 2.5) {
  const g = p.g, a = p.X(x0), b = p.Y(y0), c = p.X(x1), d = p.Y(y1), ang = Math.atan2(d - b, c - a), L = Math.hypot(c - a, d - b);
  g.save(); g.strokeStyle = color; g.fillStyle = color; g.lineWidth = w; g.beginPath(); g.moveTo(a, b); g.lineTo(c, d); g.stroke();
  if (L > 6) { g.beginPath(); g.moveTo(c, d); g.lineTo(c - 10 * Math.cos(ang - 0.4), d - 10 * Math.sin(ang - 0.4)); g.lineTo(c - 10 * Math.cos(ang + 0.4), d - 10 * Math.sin(ang + 0.4)); g.closePath(); g.fill(); }
  g.restore();
}
function poly(p, pts, stroke, fill, w = 1.5) {
  const g = p.g; g.save(); g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(p.X(x), p.Y(y)) : g.moveTo(p.X(x), p.Y(y)))); g.closePath();
  if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = w; g.stroke(); } g.restore();
}
// square frame: equal scaling on both axes
function sqframe(p, R, xlabel = 'x', ylabel = 'y') {
  p.size(); const asp = (p.w - p.pad.l - p.pad.r) / (p.h - p.pad.t - p.pad.b);
  return asp >= 1 ? p.frame({ x: [-R * asp, R * asp], y: [-R, R], xlabel, ylabel }) : p.frame({ x: [-R, R], y: [-R / asp, R / asp], xlabel, ylabel });
}

// 02.01 dot, projection and cross product of two plane vectors
def('vectors', {
  controls: [{ k: 'ta', label: 'Angle of a (°)', min: 0, max: 180, step: 1, v: 20, f: 0 }, { k: 'tb', label: 'Angle of b (°)', min: 0, max: 360, step: 1, v: 75, f: 0 }, { k: 'lb', label: 'Length of b', min: 0.5, max: 3, step: 0.1, v: 2, f: 1 }],
  draw(p, v, out) {
    const r = Math.PI / 180, a = [2.5 * Math.cos(v.ta * r), 2.5 * Math.sin(v.ta * r)], b = [v.lb * Math.cos(v.tb * r), v.lb * Math.sin(v.tb * r)];
    const dot = a[0] * b[0] + a[1] * b[1], cr = a[0] * b[1] - a[1] * b[0], na = Math.hypot(...a), pr = [(dot / na ** 2) * a[0], (dot / na ** 2) * a[1]];
    sqframe(p, 3.3);
    poly(p, [[0, 0], a, [a[0] + b[0], a[1] + b[1]], b], null, cr >= 0 ? 'rgba(238,255,65,0.12)' : 'rgba(255,90,54,0.14)');
    p.line([b[0], pr[0]], [b[1], pr[1]], C.grey, 1, [4, 4]);
    arrow(p, 0, 0, pr[0], pr[1], C.cyan, 5); arrow(p, 0, 0, ...a, C.lime); arrow(p, 0, 0, ...b, C.paper);
    p.text('a', a[0] * 1.08, a[1] * 1.08, C.lime); p.text('b', b[0] * 1.1, b[1] * 1.1);
    const ang = Math.acos(Math.max(-1, Math.min(1, dot / (na * v.lb)))) / r;
    out(`a·b = ${nf(2).format(dot)}, angle ${nf(1).format(ang)}°. Projection of b on a: ${nf(2).format(dot / na)} (cyan). Cross product z = ${nf(2).format(cr)}, the shaded area${cr < 0 ? ', negative because b is clockwise from a' : ''}.`);
  },
});

// 02.02 two lines: the row picture and conditioning
def('lines2x2', {
  controls: [{ k: 's', label: 'Slope of line 2', min: -2, max: 2, step: 0.01, v: -0.5, f: 2 }, { k: 'db', label: 'Measurement error in b₂', min: -0.2, max: 0.2, step: 0.01, v: 0.05, f: 2 }],
  draw(p, v, out) {
    // line 1: y = 0.5 x + 0.5 ; line 2: y = s x + c2, both pass through (1, 1) when db = 0
    const s1 = 0.5, c1 = 0.5, c2 = 1 - v.s, xs = [-4, 4];
    sqframe(p, 3);
    p.line(xs, xs.map((x) => s1 * x + c1), C.lime).line(xs, xs.map((x) => v.s * x + c2), C.grey, 1.5, [5, 4]).line(xs, xs.map((x) => v.s * x + c2 + v.db), C.cyan);
    // A = [[-s1,1],[-s,1]]
    const det = -s1 + v.s;
    if (Math.abs(det) < 1e-9) { out('The lines are parallel: det A = 0, no unique solution.'); return; }
    const x = (c1 - c2 - v.db) / (v.s - s1), y = s1 * x + c1;
    p.dots([1], [1], C.grey, 4).dots([x], [y], C.cyan, 5);
    const A = [[-s1, 1], [-v.s, 1]], n = Math.hypot(...A.flat()), inv = [[1, -1], [v.s, -s1]].map((r) => r.map((e) => e / det)), ni = Math.hypot(...inv.flat());
    out(`det A = ${nf(3).format(det)}. A shift of ${v.db} in b₂ moves the solution by ${nf(2).format(Math.hypot(x - 1, y - 1))}. Condition number (Frobenius) ≈ ${nf(1).format(n * ni)}.`);
  },
});

// 02.05 / 02.09 / 02.12 / 02.13 a 2x2 matrix acting on the plane
def('matrix2d', {
  controls: [{ k: 'a', label: 'a₁₁', min: -3, max: 3, step: 0.1, v: 2, f: 1 }, { k: 'b', label: 'a₁₂', min: -3, max: 3, step: 0.1, v: 1, f: 1 }, { k: 'c', label: 'a₂₁', min: -3, max: 3, step: 0.1, v: 1, f: 1 }, { k: 'd', label: 'a₂₂', min: -3, max: 3, step: 0.1, v: 2, f: 1 }],
  draw(p, v, out) {
    const { a, b, c, d } = v, M = (x, y) => [a * x + b * y, c * x + d * y];
    sqframe(p, 4);
    const circ = linspace(0, 2 * Math.PI, 121);
    p.line(circ.map(Math.cos), circ.map(Math.sin), C.grey, 1, [3, 3]);
    poly(p, [[0, 0], [1, 0], [1, 1], [0, 1]], C.grey, null, 1);
    const E = circ.map((t) => M(Math.cos(t), Math.sin(t)));
    p.line(E.map((e) => e[0]), E.map((e) => e[1]), C.paper, 1.5);
    const det = a * d - b * c;
    poly(p, [[0, 0], M(1, 0), M(1, 1), M(0, 1)], C.lime, det >= 0 ? 'rgba(238,255,65,0.18)' : 'rgba(255,90,54,0.2)');
    // singular values from A^T A
    const p11 = a * a + c * c, p12 = a * b + c * d, p22 = b * b + d * d, tr = p11 + p22, dis = Math.sqrt(Math.max(0, (p11 - p22) ** 2 + 4 * p12 ** 2));
    const s1 = Math.sqrt((tr + dis) / 2), s2 = Math.sqrt(Math.max(0, (tr - dis) / 2));
    // eigenvalues
    const T = a + d, D = (a - d) ** 2 + 4 * b * c; let eig;
    if (D >= 0) {
      const l1 = (T + Math.sqrt(D)) / 2, l2 = (T - Math.sqrt(D)) / 2;
      for (const l of [l1, l2]) { let vx = b, vy = l - a; if (Math.hypot(vx, vy) < 1e-9) { vx = l - d; vy = c; } if (Math.hypot(vx, vy) < 1e-9) { vx = 1; vy = 0; } const n = Math.hypot(vx, vy); arrow(p, 0, 0, (l * vx) / n, (l * vy) / n, C.cyan, 2); p.line([-4 * vx / n, 4 * vx / n], [-4 * vy / n, 4 * vy / n], 'rgba(92,200,255,0.35)', 1); }
      eig = `eigenvalues ${nf(2).format(l1)} and ${nf(2).format(l2)} (cyan lines are eigenvector directions)`;
    } else eig = `complex eigenvalues ${nf(2).format(T / 2)} ± ${nf(2).format(Math.sqrt(-D) / 2)}i, so no real direction is left unrotated`;
    out(`det = ${nf(2).format(det)} (area scale${det < 0 ? ', orientation flipped' : ''}). Singular values ${nf(2).format(s1)}, ${nf(2).format(s2)} (ellipse semi-axes). ${eig[0].toUpperCase() + eig.slice(1)}.`);
  },
});

// 02.07 least-squares polynomial fit to noisy spring data
def('lsq', {
  controls: [{ k: 'deg', label: 'Polynomial degree', min: 1, max: 9, step: 1, v: 1, f: 0 }, { k: 'noise', label: 'Noise (N)', min: 0, max: 3, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    let seed = 3; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) - 0.5;
    const xs = linspace(0, 10, 12), k = 2.4, ys = xs.map((x) => k * x + 2 * v.noise * rnd() * 1.7);
    // fit with normal equations on scaled x (fine for degree <= 9 on 12 points with scaling)
    const n = v.deg + 1, t = xs.map((x) => x / 5 - 1), A = t.map((ti) => Array.from({ length: n }, (_, j) => ti ** j));
    const N = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => A.reduce((s, r) => s + r[i] * r[j], 0)));
    const rhs = Array.from({ length: n }, (_, i) => A.reduce((s, r, m) => s + r[i] * ys[m], 0));
    for (let i = 0; i < n; i++) { let piv = i; for (let r = i + 1; r < n; r++) if (Math.abs(N[r][i]) > Math.abs(N[piv][i])) piv = r; [N[i], N[piv]] = [N[piv], N[i]]; [rhs[i], rhs[piv]] = [rhs[piv], rhs[i]]; for (let r = i + 1; r < n; r++) { const f = N[r][i] / N[i][i]; for (let cI = i; cI < n; cI++) N[r][cI] -= f * N[i][cI]; rhs[r] -= f * rhs[i]; } }
    const cf = new Array(n); for (let i = n - 1; i >= 0; i--) { let sum = rhs[i]; for (let j = i + 1; j < n; j++) sum -= N[i][j] * cf[j]; cf[i] = sum / N[i][i]; }
    const f = (x) => cf.reduce((s, c, j) => s + c * (x / 5 - 1) ** j, 0), fx = linspace(0, 10, 300);
    const res = Math.sqrt(xs.reduce((s, x, i) => s + (ys[i] - f(x)) ** 2, 0));
    p.frame({ x: [0, 10], y: [-5, 30], xlabel: 'extension, mm', ylabel: 'force, N' }).line([0, 10], [0, 10 * k], C.grey, 1, [4, 4]).line(fx, fx.map(f)).dots(xs, ys, C.paper, 3.5);
    const slope = v.deg === 1 ? ` Fitted stiffness ${nf(2).format(cf[1] / 5)} N/mm (true 2.40).` : '';
    out(`Residual norm ${nf(2).format(res)} N.${slope} ${v.deg > 4 ? 'A high degree chases the noise: smaller residual, worse model.' : ''}`);
  },
});

// 02.15 Jacobi, Gauss-Seidel and CG on the 1D Poisson matrix
def('iterative', {
  controls: [{ k: 'n', label: 'Unknowns n', min: 10, max: 100, step: 10, v: 40, f: 0 }, { k: 'w', label: 'SOR factor ω (1 = Gauss-Seidel)', min: 1, max: 1.98, step: 0.01, v: 1, f: 2 }],
  draw(p, v, out) {
    const n = v.n, b = new Array(n).fill(1 / (n + 1) ** 2), its = 3000;
    const resid = (x) => { let s = 0; for (let i = 0; i < n; i++) { const r = b[i] - (2 * x[i] - (x[i - 1] || 0) - (x[i + 1] || 0)); s += r * r; } return Math.sqrt(s); };
    const r0 = resid(new Array(n).fill(0)), hj = [], hg = [], hc = [];
    let x = new Array(n).fill(0);
    for (let k = 0; k < its; k++) { const y = x.map((_, i) => (b[i] + (x[i - 1] || 0) + (x[i + 1] || 0)) / 2); x = y; if (k % 10 === 0) hj.push([k, resid(x) / r0]); }
    x = new Array(n).fill(0);
    for (let k = 0; k < its; k++) { for (let i = 0; i < n; i++) { const gs = (b[i] + (x[i - 1] || 0) + (x[i + 1] || 0)) / 2; x[i] += v.w * (gs - x[i]); } if (k % 10 === 0) hg.push([k, resid(x) / r0]); }
    // CG
    x = new Array(n).fill(0); let r = b.slice(), d = r.slice(), rr = r.reduce((s, e) => s + e * e, 0); hc.push([0, 1]);
    for (let k = 1; k <= n + 2 && Math.sqrt(rr) / r0 > 1e-13; k++) { const Ad = d.map((_, i) => 2 * d[i] - (d[i - 1] || 0) - (d[i + 1] || 0)); const al = rr / d.reduce((s, e, i) => s + e * Ad[i], 0); x = x.map((e, i) => e + al * d[i]); r = r.map((e, i) => e - al * Ad[i]); const rn = r.reduce((s, e) => s + e * e, 0); d = r.map((e, i) => e + (rn / rr) * d[i]); rr = rn; hc.push([k, Math.sqrt(rr) / r0]); }
    p.frame({ x: [0, its], y: [1e-12, 2], ylog: true, xlabel: 'iteration', ylabel: 'relative residual' });
    p.line(hj.map((h) => h[0]), hj.map((h) => h[1]), C.grey).line(hg.map((h) => h[0]), hg.map((h) => h[1]), C.cyan).line(hc.map((h) => h[0]), hc.map((h) => Math.max(h[1], 1e-12)), C.lime, 2.5);
    const at = (h) => h[h.length - 1][1];
    out(`After ${its} sweeps: Jacobi (grey) ${at(hj).toExponential(1)}, ${v.w === 1 ? 'Gauss-Seidel' : 'SOR'} (cyan) ${at(hg).toExponential(1)}. CG (lime) reaches 1e-12 in ${hc.length - 1} steps, at most n.`);
  },
});

// 02.13 two-link arm: forward kinematics by chained rotations
def('arm2', {
  controls: [{ k: 't1', label: 'Shoulder θ₁ (°)', min: -90, max: 180, step: 1, v: 30, f: 0 }, { k: 't2', label: 'Elbow θ₂ (°)', min: -150, max: 150, step: 1, v: 45, f: 0 }],
  draw(p, v, out) {
    const L1 = 0.4, L2 = 0.3, r = Math.PI / 180, a = v.t1 * r, b = (v.t1 + v.t2) * r;
    const e = [L1 * Math.cos(a), L1 * Math.sin(a)], t = [e[0] + L2 * Math.cos(b), e[1] + L2 * Math.sin(b)];
    sqframe(p, 0.8, 'x, m', 'y, m');
    const c = linspace(0, 2 * Math.PI, 121);
    p.line(c.map((u) => 0.7 * Math.cos(u)), c.map((u) => 0.7 * Math.sin(u)), C.rule, 1, [3, 3]).line(c.map((u) => 0.1 * Math.cos(u)), c.map((u) => 0.1 * Math.sin(u)), C.rule, 1, [3, 3]);
    p.line([0, e[0], t[0]], [0, e[1], t[1]], C.paper, 6);
    // local frames: x axis lime, y axis cyan
    const fr = (o, ang) => { arrow(p, o[0], o[1], o[0] + 0.12 * Math.cos(ang), o[1] + 0.12 * Math.sin(ang), C.lime, 2); arrow(p, o[0], o[1], o[0] - 0.12 * Math.sin(ang), o[1] + 0.12 * Math.cos(ang), C.cyan, 2); };
    fr([0, 0], a); fr(e, b); p.dots([0, e[0]], [0, e[1]], C.grey, 5).dots([t[0]], [t[1]], C.lime, 5);
    out(`Tool tip at x = ${nf(4).format(t[0])} m, y = ${nf(4).format(t[1])} m. The tip frame is rotated by θ₁ + θ₂ = ${v.t1 + v.t2}°.`);
  },
});

// ---------- Phase 03 ----------
// banded contour fill of f over the current frame
function bands(p, f, lo, hi, nb = 12, cells = 90) {
  const [x0, x1] = p.xr, [y0, y1] = p.yr, ny = Math.round(cells * (p.h / p.w)) || cells, g = p.g;
  const dx = (x1 - x0) / cells, dy = (y1 - y0) / ny;
  g.save(); g.beginPath(); g.rect(p.pad.l, p.pad.t, p.w - p.pad.l - p.pad.r, p.h - p.pad.t - p.pad.b); g.clip();
  for (let i = 0; i < cells; i++) for (let j = 0; j < ny; j++) {
    const v = f(x0 + (i + 0.5) * dx, y0 + (j + 0.5) * dy), t = Math.max(0, Math.min(0.999, (v - lo) / (hi - lo))), b = Math.floor(t * nb);
    g.fillStyle = `rgba(238,255,65,${0.04 + 0.5 * (b / nb) ** 1.4})`;
    const a = p.X(x0 + i * dx), c = p.Y(y0 + (j + 1) * dy);
    g.fillRect(a, c, p.X(x0 + (i + 1) * dx) - a + 0.6, p.Y(y0 + j * dy) - c + 0.6);
  }
  g.restore();
}

// 03.01 / 03.02 gradient descent on a quadratic bowl
def('gradient', {
  controls: [{ k: 'kappa', label: 'Bowl elongation (condition number)', min: 1, max: 25, step: 1, v: 8, f: 0 }, { k: 'eta', label: 'Step size (fraction of the stable limit)', min: 0.1, max: 1.05, step: 0.05, v: 0.6, f: 2 }],
  draw(p, v, out) {
    const a = 1, b = v.kappa, f = (x, y) => 0.5 * (a * x * x + b * y * y);
    sqframe(p, 2.2);
    bands(p, f, 0, 0.5 * b * 4, 14);
    const h = (v.eta * 2) / b; let x = -2, y = 1.2; const X = [x], Y = [y];
    let k = 0; for (; k < 200 && Math.hypot(x, y) > 1e-3; k++) { x -= h * a * x; y -= h * b * y; X.push(x); Y.push(y); if (Math.abs(y) > 50) break; }
    p.line(X, Y, C.paper, 1.5).dots(X.slice(0, 40), Y.slice(0, 40), C.paper, 2.5).dots([0], [0], C.lime, 5);
    // gradient arrows on a coarse grid
    for (let i = -2; i <= 2; i += 1) for (let j = -1; j <= 1; j += 1) { const gx = a * i, gy = b * j, n = Math.hypot(gx, gy) || 1; if (i || j) arrow(p, i, j, i + 0.35 * gx / n, j + 0.35 * gy / n, 'rgba(92,200,255,0.8)', 1.5); }
    out(Math.abs(y) > 50 || v.eta > 1 ? `Step too large: the steep direction overshoots and diverges.` : `Gradient descent from (−2, 1.2): ${k} steps to reach the minimum within 0.001. Cyan arrows are ∇f, perpendicular to the contours.`);
  },
});

// 03.10 uniform flow past a cylinder: uniform stream + doublet
def('cylinder', {
  controls: [{ k: 'G', label: 'Clockwise circulation Γ / (U R)', min: 0, max: 12, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const U = 1, R = 1, G = v.G;
    const psi = (x, y) => { const r2 = x * x + y * y; if (r2 < R * R) return NaN; return U * y * (1 - (R * R) / r2) + (G / (2 * Math.PI)) * Math.log(Math.sqrt(r2) / R); };
    sqframe(p, 2.6);
    // streamlines: integrate the velocity field from seeds on the left
    const vel = (x, y) => { const r2 = x * x + y * y, th = Math.atan2(y, x), r = Math.sqrt(r2); const ur = U * (1 - R * R / r2) * Math.cos(th), ut = -U * (1 + R * R / r2) * Math.sin(th) - G / (2 * Math.PI * r); return [ur * Math.cos(th) - ut * Math.sin(th), ur * Math.sin(th) + ut * Math.cos(th)]; };
    for (let y0 = -2.6; y0 <= 2.61; y0 += 0.26) {
      let x = p.xr[0], y = y0 + 0.0001; const X = [x], Y = [y];
      for (let i = 0; i < 1600 && x < p.xr[1]; i++) { const [u1, v1] = vel(x, y), n = Math.hypot(u1, v1) || 1; const ds = 0.02; const [u2, v2] = vel(x + 0.5 * ds * u1 / n, y + 0.5 * ds * v1 / n), n2 = Math.hypot(u2, v2) || 1; x += ds * u2 / n2; y += ds * v2 / n2; if (x * x + y * y < R * R * 0.98) break; X.push(x); Y.push(y); }
      p.line(X, Y, 'rgba(242,243,236,0.55)', 1.2);
    }
    const c = linspace(0, 2 * Math.PI, 100);
    poly(p, c.map((t) => [Math.cos(t), Math.sin(t)]), C.lime, 'rgba(238,255,65,0.15)', 2);
    // stagnation points on the surface: sin th = G / (4 pi U R)
    const sth = G / (4 * Math.PI * U * R);
    let msg;
    if (sth <= 1) { const th = Math.asin(sth); p.dots([-Math.cos(th), Math.cos(th)], [-Math.sin(th), -Math.sin(th)], C.red, 5); msg = `Stagnation points (red) move ${nf(1).format((th * 180) / Math.PI)}° below the axis.`; }
    else msg = 'Γ > 4πUR: the stagnation point leaves the surface and sits in the flow below the cylinder.';
    out(`Surface speed ${nf(2).format(2 * U + G / (2 * Math.PI * R))} U on top, ${nf(2).format(Math.abs(2 * U - G / (2 * Math.PI * R)))} U underneath. Upward lift per unit span ρUΓ (Kutta-Joukowski). ${msg}`);
    void psi;
  },
});

// 03.11 Fourier partial sums of a square wave
def('fourier', {
  controls: [{ k: 'n', label: 'Number of odd harmonics', min: 1, max: 60, step: 1, v: 5, f: 0 }, { type: 'select', k: 'wave', label: 'Signal', options: ['square', 'sawtooth', 'triangle'], v: 'square' }],
  draw(p, v, out) {
    const xs = linspace(-Math.PI, 3 * Math.PI, 900);
    const tgt = { square: (x) => Math.sign(Math.sin(x)), sawtooth: (x) => ((((x + Math.PI) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)) / Math.PI - 1, triangle: (x) => (2 / Math.PI) * Math.asin(Math.sin(x)) }[v.wave];
    const S = (x) => { let s = 0; for (let m = 1; m <= v.n; m++) { if (v.wave === 'square') { const k = 2 * m - 1; s += (4 / (Math.PI * k)) * Math.sin(k * x); } else if (v.wave === 'sawtooth') { s += ((2 * (-1) ** (m + 1)) / (Math.PI * m)) * Math.sin(m * x); } else { const k = 2 * m - 1; s += ((8 / (Math.PI * Math.PI * k * k)) * (-1) ** (m - 1)) * Math.sin(k * x); } } return s; };
    p.frame({ x: [-Math.PI, 3 * Math.PI], y: [-1.5, 1.5], xlabel: 'x', ylabel: '' }).line(xs, xs.map(tgt), C.grey, 1.5).line(xs, xs.map(S));
    let mx = 0; for (const x of linspace(0.0001, Math.PI - 0.0001, 4000)) mx = Math.max(mx, S(x));
    out(v.wave === 'square' ? `Peak ${nf(4).format(mx)}: the overshoot near the jump tends to about 9% of the jump (Gibbs), however many terms you add.` : v.wave === 'triangle' ? `Coefficients fall like 1/k²: a continuous signal converges fast. Max error ${nf(4).format(Math.max(...xs.map((x) => Math.abs(S(x) - tgt(x)))))}.` : `Coefficients fall like 1/m: the jump causes Gibbs overshoot again.`);
  },
});

// 03.14 heat equation in a rod, ends held at 0, initial temperature 100
def('heat1d', {
  controls: [{ k: 't', label: 'Time t (minutes)', min: 0, max: 120, step: 1, v: 10, f: 0 }, { type: 'select', k: 'mat', label: 'Material (rod 0.5 m)', options: ['steel', 'aluminium', 'copper'], v: 'steel' }],
  draw(p, v, out) {
    const alpha = { steel: 1.2e-5, aluminium: 9.7e-5, copper: 1.11e-4 }[v.mat], L = 0.5, t = v.t * 60, xs = linspace(0, L, 200);
    const T = (x) => { if (t === 0) return x > 0 && x < L ? 100 : 0; let s = 0; for (let k = 1; k < 400; k += 2) s += (400 / (Math.PI * k)) * Math.sin((k * Math.PI * x) / L) * Math.exp(-alpha * ((k * Math.PI) / L) ** 2 * t); return s; };
    p.frame({ x: [0, L], y: [0, 110], xlabel: 'x, m', ylabel: 'T, °C' });
    p.line(xs, xs.map(T));
    const tau = (L * L) / (Math.PI * Math.PI * alpha);
    out(`Centre ${nf(1).format(T(L / 2))} °C. Slowest mode decays with time constant L²/(π²α) = ${nf(0).format(tau / 60)} min for ${v.mat}.`);
  },
});

// 03.15 plucked string: d'Alembert travelling waves
def('wave1d', {
  controls: [{ k: 't', label: 'Time (fraction of a period)', min: 0, max: 1, step: 0.01, v: 0.1, f: 2 }, { k: 'pos', label: 'Pluck position (fraction of L)', min: 0.1, max: 0.5, step: 0.05, v: 0.25, f: 2 }],
  draw(p, v, out) {
    const L = 1, a = v.pos, f0 = (x) => { x = ((x % (2 * L)) + 2 * L) % (2 * L); const s = x > L ? -1 : 1; if (x > L) x = 2 * L - x; return s * (x < a ? x / a : (L - x) / (L - a)); };
    const ct = 2 * L * v.t, xs = linspace(0, L, 300);
    p.frame({ x: [0, L], y: [-1.2, 1.2], xlabel: 'x / L', ylabel: 'u' });
    p.line(xs, xs.map((x) => 0.5 * f0(x - ct)), C.cyan, 1, [4, 4]).line(xs, xs.map((x) => 0.5 * f0(x + ct)), C.grey, 1, [4, 4]).line(xs, xs.map((x) => 0.5 * (f0(x - ct) + f0(x + ct))));
    // harmonic content: b_n ∝ sin(n pi a)/n^2
    const bn = [1, 2, 3, 4, 5].map((n) => Math.abs(Math.sin(n * Math.PI * a)) / (n * n)), b1 = bn[0];
    out(`Two half-size copies travel left (grey) and right (cyan); the string (lime) is their sum. Harmonic amplitudes relative to the fundamental: ${bn.map((b) => nf(2).format(b / b1)).join(', ')}.`);
  },
});

// 03.19 phase plane of a damped pendulum
def('phaseplane', {
  controls: [{ k: 'c', label: 'Damping ratio ζ', min: 0, max: 1.2, step: 0.05, v: 0.1, f: 2 }, { k: 'w0', label: 'Initial speed (rad/s)', min: 0, max: 3, step: 0.05, v: 1.9, f: 2 }],
  draw(p, v, out) {
    const rhs = (x, y) => [y, -Math.sin(x) - 2 * v.c * y];
    p.frame({ x: [-Math.PI * 1.6, Math.PI * 3.2], y: [-3.2, 3.2], xlabel: 'angle θ, rad', ylabel: 'θ̇' });
    // direction field
    for (let x = -4.5; x <= 10; x += 0.7) for (let y = -2.8; y <= 2.8; y += 0.7) { const [u, w] = rhs(x, y), n = Math.hypot(u, w) || 1; p.line([x, x + 0.25 * u / n], [y, y + 0.25 * w / n], 'rgba(242,243,236,0.25)', 1); }
    // separatrix of the undamped pendulum
    const sx = linspace(-Math.PI, 3 * Math.PI, 300);
    p.line(sx, sx.map((x) => 2 * Math.cos(x / 2)), C.rule, 1, [4, 4]).line(sx, sx.map((x) => -2 * Math.cos(x / 2)), C.rule, 1, [4, 4]);
    let x = 0, y = v.w0; const X = [x], Y = [y], h = 0.01;
    for (let i = 0; i < 6000; i++) { const k1 = rhs(x, y), k2 = rhs(x + h / 2 * k1[0], y + h / 2 * k1[1]), k3 = rhs(x + h / 2 * k2[0], y + h / 2 * k2[1]), k4 = rhs(x + h * k3[0], y + h * k3[1]); x += h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); y += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); X.push(x); Y.push(y); }
    p.line(X, Y).dots([0, 2 * Math.PI], [0, 0], C.cyan, 4).dots([Math.PI], [0], C.red, 4);
    const turns = Math.round(x / (2 * Math.PI));
    out(`${turns > 0 ? `The pendulum goes over the top ${turns} time${turns > 1 ? 's' : ''} before settling.` : 'It swings back and forth without going over the top.'} Cyan: stable equilibria (spirals or centres). Red: unstable (a saddle). Dashed: the undamped separatrix.`);
  },
});

export function mountWidgets(root) {
  root.querySelectorAll('.widget[data-widget]').forEach((el) => {
    const spec = W[el.dataset.widget];
    if (!spec) { el.innerHTML = '<p class="muted small">This figure is missing.</p>'; return; }
    el.innerHTML = `<canvas class="w-canvas" role="img" aria-label="Interactive plot"></canvas><p class="w-out small" aria-live="polite"></p><div class="w-controls"></div>`;
    const canvas = el.querySelector('canvas'), outEl = el.querySelector('.w-out'), ctr = el.querySelector('.w-controls');
    const vals = {};
    spec.controls.forEach((c, i) => {
      vals[c.k] = c.v;
      const id = `w-${el.dataset.widget}-${i}-${Math.random().toString(36).slice(2, 6)}`;
      const row = document.createElement('div'); row.className = 'w-row';
      if (c.type === 'check') row.innerHTML = `<label class="w-check"><input id="${id}" type="checkbox" ${c.v ? 'checked' : ''}/> <span>${c.label}</span></label>`;
      else if (c.type === 'select') row.innerHTML = `<label for="${id}">${c.label}</label><select id="${id}">${c.options.map((o) => `<option ${o === c.v ? 'selected' : ''}>${o}</option>`).join('')}</select>`;
      else row.innerHTML = `<label for="${id}">${c.label} <output class="num">${(+c.v).toFixed(c.f)}</output></label><input id="${id}" type="range" min="${c.min}" max="${c.max}" step="${c.step}" value="${c.v}"/>`;
      ctr.appendChild(row);
      const inp = row.querySelector('input,select');
      const paint = () => { if (inp.type === 'range') inp.style.setProperty('--fill', `${((inp.value - c.min) / (c.max - c.min)) * 100}%`); };
      paint();
      inp.addEventListener('input', () => {
        vals[c.k] = c.type === 'check' ? (inp.checked ? 1 : 0) : c.type === 'select' ? inp.value : +inp.value;
        const o = row.querySelector('output'); if (o) o.textContent = (+inp.value).toFixed(c.f);
        paint(); draw();
      });
    });
    const plot = new Plot(canvas);
    const draw = () => { try { spec.draw(plot, vals, (t) => (outEl.textContent = t)); } catch (e) { console.warn(e); } };
    new ResizeObserver(draw).observe(canvas);
    draw();
    el.dataset.ready = '1';
  });
}
