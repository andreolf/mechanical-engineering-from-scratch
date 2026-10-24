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
  frame({ x, y, xlog = false, ylog = false, xlabel = '', ylabel = '', noy = false }) {
    this.size();
    Object.assign(this, { xr: x, yr: y, xlog, ylog });
    const g = this.g; g.clearRect(0, 0, this.w, this.h);
    g.font = '11px "Archivo Variable", sans-serif'; g.fillStyle = C.grey; g.strokeStyle = C.rule; g.lineWidth = 1;
    const ticks = (r, log) => log ? range(Math.ceil(Math.log10(r[0])), Math.floor(Math.log10(r[1]))).map((e) => 10 ** e) : niceTicks(r[0], r[1], 5);
    for (const t of ticks(x, xlog)) { const px = this.X(t); g.beginPath(); g.moveTo(px, this.pad.t); g.lineTo(px, this.h - this.pad.b); g.stroke(); g.textAlign = 'center'; g.fillText(lab(t, xlog), px, this.h - this.pad.b + 14); }
    if (!noy) for (const t of ticks(y, ylog)) { const py = this.Y(t); g.beginPath(); g.moveTo(this.pad.l, py); g.lineTo(this.w - this.pad.r, py); g.stroke(); g.textAlign = 'right'; g.fillText(lab(t, ylog), this.pad.l - 6, py + 4); }
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
function bands(p, f, lo, hi, nb = 12, cells = 160) {
  // render quantised values into a small offscreen bitmap, then scale it into the plot area (no seams)
  const [x0, x1] = p.xr, [y0, y1] = p.yr, pw = p.w - p.pad.l - p.pad.r, ph = p.h - p.pad.t - p.pad.b;
  const nx = cells, ny = Math.max(2, Math.round(cells * (ph / pw)));
  const off = document.createElement('canvas'); off.width = nx; off.height = ny;
  const og = off.getContext('2d'), img = og.createImageData(nx, ny);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const v = f(x0 + ((i + 0.5) / nx) * (x1 - x0), y1 - ((j + 0.5) / ny) * (y1 - y0));
    const t = Math.max(0, Math.min(0.999, (v - lo) / (hi - lo))), b = Math.floor(t * nb), a = 0.05 + 0.55 * (b / nb) ** 1.3;
    const k = 4 * (j * nx + i); img.data[k] = 238; img.data[k + 1] = 255; img.data[k + 2] = 65; img.data[k + 3] = Math.round(255 * a);
  }
  og.putImageData(img, 0, 0);
  const g = p.g; g.save(); g.imageSmoothingEnabled = false; g.drawImage(off, p.pad.l, p.pad.t, pw, ph); g.restore();
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

// 03.16 steady temperature in a square plate: superposition of edge series
const sinhRatio = (a, b) => Math.exp(a - b) * (1 - Math.exp(-2 * a)) / (1 - Math.exp(-2 * b));
const plateTop = (x, y, terms = 41) => { if (y >= 1) return x > 0 && x < 1 ? 1 : 0.5; let s = 0; for (let n = 1; n < terms; n += 2) s += (4 / (n * Math.PI)) * Math.sin(n * Math.PI * x) * sinhRatio(n * Math.PI * y, n * Math.PI); return s; };
def('plate', {
  controls: [{ k: 'top', label: 'Top edge (°C)', min: 0, max: 100, step: 5, v: 100, f: 0 }, { k: 'right', label: 'Right edge (°C)', min: 0, max: 100, step: 5, v: 0, f: 0 }, { k: 'left', label: 'Left edge (°C)', min: 0, max: 100, step: 5, v: 0, f: 0 }],
  draw(p, v, out) {
    // bottom edge held at 0 °C; the other three by the sliders
    const T = (x, y) => v.top * plateTop(x, y) + v.right * plateTop(y, x) + v.left * plateTop(y, 1 - x);
    sqframe(p, 0.62, 'x, m', 'y, m');
    bands(p, (x, y) => (Math.abs(x) <= 0.5 && Math.abs(y) <= 0.5 ? T(x + 0.5, y + 0.5) : -1), 0, 100, 10, 120);
    p.line([-0.5, 0.5, 0.5, -0.5, -0.5], [-0.5, -0.5, 0.5, 0.5, -0.5], C.paper, 1.5);
    p.text(`${v.top} °C`, 0, 0.53, C.lime, 'center').text('0 °C', 0, -0.59, C.grey, 'center');
    p.dots([0, 0], [0, 0.25], C.cyan, 4);
    const c = T(0.5, 0.5), q = T(0.5, 0.75);
    out(`Centre ${nf(2).format(c)} °C, the average of the four edges (${nf(2).format((v.top + v.right + v.left) / 4)}). At (0.5, 0.75): ${nf(1).format(q)} °C. Brighter is hotter; the hottest and coldest points are always on the edges.`);
  },
});

// 03.18 step response of m x'' + c x' + k x = F via the Laplace solution
def('step2', {
  controls: [{ k: 'c', label: 'Damping c (N·s/m)', min: 0.5, max: 12, step: 0.5, v: 4, f: 1 }, { k: 'k', label: 'Stiffness k (N/m)', min: 5, max: 60, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const m = 1, F = 10, wn = Math.sqrt(v.k / m), z = v.c / (2 * Math.sqrt(v.k * m)), xs = F / v.k, ts = linspace(0, 4, 400);
    const x = (t) => {
      if (z < 1) { const wd = wn * Math.sqrt(1 - z * z); return xs * (1 - Math.exp(-z * wn * t) * (Math.cos(wd * t) + (z / Math.sqrt(1 - z * z)) * Math.sin(wd * t))); }
      if (Math.abs(z - 1) < 1e-9) return xs * (1 - Math.exp(-wn * t) * (1 + wn * t));
      const r1 = -wn * (z - Math.sqrt(z * z - 1)), r2 = -wn * (z + Math.sqrt(z * z - 1));
      return xs * (1 + (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r1 - r2));
    };
    p.frame({ x: [0, 4], y: [0, 2 * xs], xlabel: 't, s', ylabel: 'x, m' });
    p.line([0, 4], [xs, xs], C.grey, 1, [4, 4]).line(ts, ts.map(x));
    let msg = `Steady state F/k = ${nf(3).format(xs)} m, ζ = ${nf(3).format(z)}.`;
    if (z < 1) { const wd = wn * Math.sqrt(1 - z * z), tp = Math.PI / wd, os = Math.exp(-z * Math.PI / Math.sqrt(1 - z * z)); p.dots([tp], [x(tp)], C.cyan, 4); msg += ` Peak ${nf(3).format(x(tp))} m at ${nf(3).format(tp)} s: overshoot ${nf(1).format(100 * os)}%.`; }
    else msg += ' No overshoot: the poles are real.';
    out(msg + ` Poles of 1/(s² + ${nf(1).format(v.c)}s + ${v.k}).`);
  },
});

// 03.20 Green's function of a simply supported beam: deflection under a moving point load
def('beamgreen', {
  controls: [{ k: 'xi', label: 'Load position ξ (m)', min: 0.1, max: 3.9, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const L = 4, EI = 200e9 * 1943e-8, P = 1e4, xs = linspace(0, L, 200);
    const G = (x, xi) => { let a = Math.min(x, xi), b = L - Math.max(x, xi); return (b * a * (L * L - b * b - a * a)) / (6 * EI * L); };
    p.frame({ x: [0, L], y: [-5, 0.8], xlabel: 'x, m', ylabel: 'deflection, mm' });
    p.line(xs, xs.map((x) => -1e3 * P * G(x, 2)), C.grey, 1, [4, 4]);
    p.line(xs, xs.map((x) => -1e3 * P * G(x, v.xi)));
    p.line([v.xi, v.xi], [0.75, 0.1], C.cyan, 2).dots([v.xi], [0.1], C.cyan, 3).dots([0, L], [0, 0], C.paper, 4);
    const mid = 1e3 * P * G(2, v.xi);
    let xm = 0, dm = 0; xs.forEach((x) => { const d = 1e3 * P * G(x, v.xi); if (d > dm) { dm = d; xm = x; } });
    out(`10 kN at ξ = ${nf(1).format(v.xi)} m on a 4 m IPE 200: midspan ${nf(3).format(mid)} mm, largest ${nf(3).format(dm)} mm at x = ${nf(2).format(xm)} m. Dashed: load at midspan (3.431 mm). Reciprocity: the midspan deflection here equals the deflection at ξ for a load at midspan.`);
  },
});

// 04.01 observed convergence order on a log-log plot
def('convorder', {
  controls: [{ type: 'select', k: 'm', label: 'Difference formula for (sin x)′ at x = 1', options: ['forward', 'central', 'five-point'], v: 'central' }, { k: 'hmin', label: 'Smallest step h = 10^', min: -12, max: -2, step: 1, v: -10, f: 0 }],
  draw(p, v, out) {
    const f = Math.sin, x = 1, ex = Math.cos(1);
    const D = { forward: (h) => (f(x + h) - f(x)) / h, central: (h) => (f(x + h) - f(x - h)) / (2 * h), 'five-point': (h) => (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12 * h) }[v.m];
    const hs = logspace(v.hmin, -0.5, 40), es = hs.map((h) => Math.max(Math.abs(D(h) - ex), 1e-17));
    p.frame({ x: [10 ** v.hmin, 10 ** -0.5], y: [1e-16, 1], xlog: true, ylog: true, xlabel: 'step h', ylabel: 'error' });
    p.line(hs, es).dots(hs, es, C.lime, 2.5);
    // fit the slope on the three largest steps, where truncation error dominates
    const n = hs.length, a = [n - 6, n - 1].map((i) => [Math.log10(hs[i]), Math.log10(es[i])]);
    const slope = (a[1][1] - a[0][1]) / (a[1][0] - a[0][0]);
    let imin = 0; es.forEach((e, i) => { if (e < es[imin]) imin = i; });
    out(`Slope at large h: ${nf(2).format(slope)} (the order). Best error ${es[imin].toExponential(1)} at h ≈ ${hs[imin].toExponential(0)}; below that, round-off grows like ε/h and the curve turns back up.`);
  },
});

// 04.02 race of root finders
function rootRace(f, a, b, x0, df) {
  const res = { bisection: [], secant: [], Newton: [], Brent: [] };
  let lo = a, hi = b, flo = f(a);
  for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2, fm = f(m); res.bisection.push(m); if (flo * fm <= 0) hi = m; else { lo = m; flo = fm; } }
  let s0 = a, s1 = b;
  for (let i = 0; i < 60; i++) { const f0 = f(s0), f1 = f(s1); if (f1 === f0 || !isFinite(s1)) break; const s2 = s1 - f1 * (s1 - s0) / (f1 - f0); s0 = s1; s1 = s2; res.secant.push(s1); }
  let xn = x0;
  for (let i = 0; i < 60; i++) { const d = df(xn); if (!d || !isFinite(xn)) break; xn = xn - f(xn) / d; res.Newton.push(xn); }
  // simplified Brent: inverse quadratic / secant inside the bracket, else bisection
  let A = a, B = b, fa = f(A), fb = f(B); if (Math.abs(fa) < Math.abs(fb)) [A, B, fa, fb] = [B, A, fb, fa];
  let Cc = A, fc = fa;
  for (let i = 0; i < 60 && Math.abs(B - A) > 1e-15 && fb !== 0; i++) {
    let s = fa !== fc && fb !== fc ? A * fb * fc / ((fa - fb) * (fa - fc)) + B * fa * fc / ((fb - fa) * (fb - fc)) + Cc * fa * fb / ((fc - fa) * (fc - fb)) : B - fb * (B - A) / (fb - fa);
    const lo2 = Math.min((3 * A + B) / 4, B), hi2 = Math.max((3 * A + B) / 4, B);
    if (!(s > lo2 && s < hi2) || Math.abs(s - B) >= Math.abs(B - Cc) / 2) s = (A + B) / 2;
    const fs = f(s); Cc = B; fc = fb;
    if (fa * fs < 0) { B = s; fb = fs; } else { A = s; fa = fs; }
    if (Math.abs(fa) < Math.abs(fb)) [A, B, fa, fb] = [B, A, fb, fa];
    res.Brent.push(B);
  }
  return res;
}
def('rootrace', {
  controls: [{ type: 'select', k: 'fn', label: 'Equation', options: ['Colebrook friction factor', 'x³ − 2x − 5 = 0', 'atan(x − 1) = 0'], v: 'Colebrook friction factor' }],
  draw(p, v, out) {
    const P = {
      'Colebrook friction factor': { f: (x) => x + 2 * Math.log10(1e-4 / 3.7 + 2.51 * x / 1e5), df: (x) => 1 + 2 / Math.LN10 * (2.51 / 1e5) / (1e-4 / 3.7 + 2.51 * x / 1e5), a: 1, b: 20, x0: 1 },
      'x³ − 2x − 5 = 0': { f: (x) => x ** 3 - 2 * x - 5, df: (x) => 3 * x * x - 2, a: 2, b: 3, x0: 3 },
      'atan(x − 1) = 0': { f: (x) => Math.atan(x - 1), df: (x) => 1 / (1 + (x - 1) ** 2), a: -5, b: 30, x0: 3 },
    }[v.fn];
    const r = rootRace(P.f, P.a, P.b, P.x0, P.df), root = r.Brent[r.Brent.length - 1];
    p.frame({ x: [0, 50], y: [1e-16, 1e2], ylog: true, xlabel: 'iteration', ylabel: '|x − root|' });
    const col = { bisection: C.grey, secant: C.cyan, Newton: C.amber, Brent: C.lime }, msg = [];
    for (const k of Object.keys(r)) {
      const e = r[k].map((x) => Math.max(Math.abs(x - root), 1e-16)), it = e.map((_, i) => i + 1);
      p.line(it, e.map((y) => (isFinite(y) ? y : NaN)), col[k], k === 'Brent' ? 2.5 : 1.5);
      const n = e.findIndex((y) => y < 1e-12);
      msg.push(`${k} ${n < 0 ? 'fails' : n + 1}`);
    }
    out(`Iterations to 1e-12: ${msg.join(', ')}. Grey bisection, cyan secant, amber Newton, lime Brent.`);
  },
});

// 04.03 node hanging from two elastic cables, solved with Newton
def('cables', {
  controls: [{ k: 'W', label: 'Hanging load W (N)', min: 200, max: 6000, step: 100, v: 2000, f: 0 }, { k: 'it', label: 'Newton iterations shown', min: 0, max: 6, step: 1, v: 6, f: 0 }],
  draw(p, v, out) {
    const A = [[0, 0], [4, 0]], L0 = [2.5, 2.0], EA = 50e3;
    const res = (x, y) => { let rx = 0, ry = -v.W; for (let i = 0; i < 2; i++) { const dx = A[i][0] - x, dy = A[i][1] - y, L = Math.hypot(dx, dy), T = L > L0[i] ? EA * (L - L0[i]) / L0[i] : 0; rx += T * dx / L; ry += T * dy / L; } return [rx, ry]; };
    const jac = (x, y) => { const J = [[0, 0], [0, 0]]; for (let i = 0; i < 2; i++) { const dx = A[i][0] - x, dy = A[i][1] - y, L = Math.hypot(dx, dy); if (L <= L0[i]) continue; const u = [dx / L, dy / L], k = EA / L0[i], T = k * (L - L0[i]); for (let r = 0; r < 2; r++) for (let c = 0; c < 2; c++) J[r][c] -= k * u[r] * u[c] + (T / L) * ((r === c ? 1 : 0) - u[r] * u[c]); } return J; };
    let x = 2, y = -2; const P = [[x, y]], R = [Math.hypot(...res(x, y))];
    for (let k = 0; k < v.it; k++) { const [rx, ry] = res(x, y), J = jac(x, y), det = J[0][0] * J[1][1] - J[0][1] * J[1][0]; x -= (J[1][1] * rx - J[0][1] * ry) / det; y -= (-J[1][0] * rx + J[0][0] * ry) / det; P.push([x, y]); R.push(Math.hypot(...res(x, y))); }
    p.frame({ x: [-0.5, 4.5], y: [-3, 0.6], xlabel: 'x, m', ylabel: 'y, m' });
    p.line([-0.3, 4.3], [0, 0], C.grey, 3);
    P.slice(0, -1).forEach(([px, py]) => p.line([0, px, 4], [0, py, 0], 'rgba(242,243,236,0.25)', 1));
    p.line([0, x, 4], [0, y, 0], C.lime, 2).dots(P.map((q) => q[0]), P.map((q) => q[1]), C.cyan, 3).dots([x], [y], C.lime, 5).dots([0, 4], [0, 0], C.paper, 4);
    const T = A.map((a, i) => EA * (Math.hypot(a[0] - x, a[1] - y) - L0[i]) / L0[i]);
    out(`Node at (${nf(3).format(x)}, ${nf(3).format(y)}) m, residual ${R[R.length - 1].toExponential(1)} N. Tensions: left ${nf(0).format(T[0])} N, right ${nf(0).format(T[1])} N. Residual per step: ${R.map((r) => r.toExponential(0)).join(' → ')}.`);
  },
});

// 04.04 Runge phenomenon: equispaced vs Chebyshev nodes
def('runge', {
  controls: [{ k: 'n', label: 'Polynomial degree n', min: 2, max: 24, step: 1, v: 12, f: 0 }, { type: 'select', k: 'nodes', label: 'Nodes', options: ['equispaced', 'Chebyshev'], v: 'equispaced' }],
  draw(p, v, out) {
    const f = (x) => 1 / (1 + 25 * x * x), n = v.n;
    const xn = v.nodes === 'equispaced' ? linspace(-1, 1, n + 1) : Array.from({ length: n + 1 }, (_, k) => Math.cos((2 * k + 1) * Math.PI / (2 * (n + 1))));
    const w = xn.map((xj, j) => 1 / xn.reduce((acc, xk, k) => (k === j ? acc : acc * (xj - xk)), 1)), yn = xn.map(f);
    const P = (x) => { let num = 0, den = 0; for (let j = 0; j <= n; j++) { const d = x - xn[j]; if (Math.abs(d) < 1e-14) return yn[j]; num += w[j] * yn[j] / d; den += w[j] / d; } return num / den; };
    const xs = linspace(-1, 1, 801), ps = xs.map(P), err = Math.max(...xs.map((x, i) => Math.abs(ps[i] - f(x))));
    p.frame({ x: [-1, 1], y: [-0.6, 1.6], xlabel: 'x', ylabel: 'y' });
    p.line(xs, xs.map(f), C.grey, 1.5, [4, 4]).line(xs, ps).dots(xn, yn, C.cyan, 3.5);
    out(`Max error ${nf(4).format(err)} with ${n + 1} ${v.nodes} nodes. Dashed: 1/(1 + 25x²). ${v.nodes === 'equispaced' && n > 10 ? 'The wiggles near the ends grow with n: the Runge phenomenon.' : 'Clustering nodes towards the ends tames the wiggles.'}`);
  },
});

// 04.05 natural cubic spline vs a single interpolating polynomial
def('spline', {
  controls: [{ k: 'y3', label: 'Height of the middle station (mm)', min: 0, max: 90, step: 1, v: 80, f: 0 }],
  draw(p, v, out) {
    const x = [0, 60, 150, 260, 400, 520, 600], y = [0, 18, 40, v.y3, 47, 30, 22], n = x.length - 1, h = x.slice(1).map((xi, i) => xi - x[i]);
    // tridiagonal system for interior second derivatives (Thomas algorithm)
    const m = n - 1, a = [], b = [], c = [], d = [];
    for (let i = 1; i < n; i++) { a.push(h[i - 1]); b.push(2 * (h[i - 1] + h[i])); c.push(h[i]); d.push(6 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])); }
    for (let i = 1; i < m; i++) { const w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; d[i] -= w * d[i - 1]; }
    const Mi = Array(m).fill(0); Mi[m - 1] = d[m - 1] / b[m - 1]; for (let i = m - 2; i >= 0; i--) Mi[i] = (d[i] - c[i] * Mi[i + 1]) / b[i];
    const M = [0, ...Mi, 0];
    const S = (t, der = 0) => { let i = 0; while (i < n - 1 && t > x[i + 1]) i++; const hh = h[i], A = (x[i + 1] - t) / hh, B = (t - x[i]) / hh; return der === 2 ? A * M[i] + B * M[i + 1] : A * y[i] + B * y[i + 1] + ((A ** 3 - A) * M[i] + (B ** 3 - B) * M[i + 1]) * hh * hh / 6; };
    const w = x.map((xj, j) => 1 / x.reduce((acc, xk, k) => (k === j ? acc : acc * (xj - xk)), 1));
    const Poly = (t) => { let num = 0, den = 0; for (let j = 0; j <= n; j++) { const dd = t - x[j]; if (Math.abs(dd) < 1e-12) return y[j]; num += w[j] * y[j] / dd; den += w[j] / dd; } return num / den; };
    const ts = linspace(0, 600, 601);
    p.frame({ x: [0, 600], y: [-20, 110], xlabel: 'x, mm', ylabel: 'y, mm' });
    p.line(ts, ts.map(Poly), C.grey, 1.5, [4, 4]).line(ts, ts.map((t) => S(t))).dots(x, y, C.cyan, 4);
    const kmax = Math.max(...ts.map((t) => Math.abs(S(t, 2))));
    out(`Lime: natural cubic spline, smooth to the second derivative at every station; largest |y″| = ${kmax.toExponential(2)} per mm. Dashed: the single degree-6 polynomial through the same points.`);
  },
});

// seeded normal random numbers, so widgets draw the same noise every time
function gaussRng(seed) { let s = seed >>> 0; const u = () => { s = (s * 1664525 + 1013904223) >>> 0; return (s + 0.5) / 4294967296; }; return () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u()); }

// 04.06 differentiating noisy position data
def('noisydiff', {
  controls: [{ k: 'sig', label: 'Sensor noise σ (mm)', min: 0, max: 0.5, step: 0.01, v: 0.1, f: 2 }, { k: 'half', label: 'Savitzky-Golay half-window (samples)', min: 2, max: 60, step: 1, v: 25, f: 0 }],
  draw(p, v, out) {
    const h = 1e-3, N = 1000, rnd = gaussRng(7), w = 2 * Math.PI * 1.5;
    const t = linspace(0, (N - 1) * h, N), x = t.map((ti) => 0.05 * Math.sin(w * ti) + rnd() * v.sig * 1e-3), vt = t.map((ti) => 0.05 * w * Math.cos(w * ti));
    const raw = t.map((_, i) => (i > 0 && i < N - 1 ? (x[i + 1] - x[i - 1]) / (2 * h) : NaN));
    // quadratic SG first derivative on a symmetric window equals the least-squares slope
    const m = v.half; let den = 0; for (let k = -m; k <= m; k++) den += k * k;
    const sg = t.map((_, i) => { if (i < m || i >= N - m) return NaN; let s = 0; for (let k = -m; k <= m; k++) s += k * x[i + k]; return s / (den * h); });
    const rms = (a) => { let s = 0, n = 0; a.forEach((y, i) => { if (isFinite(y) && i >= 60 && i < N - 60) { s += (y - vt[i]) ** 2; n++; } }); return Math.sqrt(s / n); };
    p.frame({ x: [0, 1], y: [-0.8, 0.8], xlabel: 't, s', ylabel: 'velocity, m/s' });
    p.line(t, raw, 'rgba(154,157,147,0.55)', 1).line(t, vt, C.paper, 1, [4, 4]).line(t, sg);
    out(`RMS error: raw central difference ${nf(4).format(rms(raw))} m/s (theory σ/(√2 h) = ${nf(4).format(v.sig * 1e-3 / (Math.SQRT2 * h))}), Savitzky-Golay ${nf(4).format(rms(sg))} m/s. Too wide a window starts to flatten the peaks.`);
  },
});

// 04.07 Gauss-Legendre nodes and weights
function gaussLegendre(n) {
  const x = [], w = [];
  for (let i = 1; i <= n; i++) {
    let z = Math.cos(Math.PI * (i - 0.25) / (n + 0.5)), dp = 1;
    for (let it = 0; it < 100; it++) { let p0 = 1, p1 = z; for (let k = 2; k <= n; k++) { const p2 = ((2 * k - 1) * z * p1 - (k - 1) * p0) / k; p0 = p1; p1 = p2; } const pn = n === 1 ? z : p1, pm = n === 1 ? 1 : p0; dp = n * (z * pn - pm) / (z * z - 1); const dz = pn / dp; z -= dz; if (Math.abs(dz) < 1e-15) break; }
    x.push(z); w.push(2 / ((1 - z * z) * dp * dp));
  }
  return [x, w];
}
def('gaussnodes', {
  controls: [{ k: 'n', label: 'Number of points n', min: 1, max: 10, step: 1, v: 3, f: 0 }],
  draw(p, v, out) {
    const [x, w] = gaussLegendre(v.n), xs = linspace(-1, 1, 400);
    const P = (z) => { let p0 = 1, p1 = z; if (v.n === 1) return z; for (let k = 2; k <= v.n; k++) { const p2 = ((2 * k - 1) * z * p1 - (k - 1) * p0) / k; p0 = p1; p1 = p2; } return p1; };
    p.frame({ x: [-1.05, 1.05], y: [-1.1, 2.1], xlabel: 'x', ylabel: 'Pₙ(x), weight' });
    p.line(xs, xs.map(P), C.grey, 1.5);
    x.forEach((xi, i) => p.line([xi, xi], [0, w[i]], C.lime, 3));
    p.dots(x, x.map(() => 0), C.cyan, 4);
    const f = (z) => Math.exp(-z * z), exact = 0.882081390762422, I = x.reduce((s, xi, i) => s + w[i] * f(xi + 1), 0);
    out(`Nodes (cyan) are the roots of the Legendre polynomial P${v.n} (grey); bar heights are the weights, summing to 2. Exact for polynomials up to degree ${2 * v.n - 1}. ∫₀² e^(−x²) dx with ${v.n} points: error ${Math.abs(I - exact).toExponential(1)}.`);
  },
});

// 04.08 explicit Euler stability region
def('stability', {
  controls: [{ k: 'h', label: 'Step h (s)', min: 0.02, max: 1.4, step: 0.02, v: 0.3, f: 2 }],
  draw(p, v, out) {
    const lams = [{ re: -2, im: 0, name: 'cooling, λ = −2' }, { re: -0.5, im: 3, name: 'damped oscillator, λ = −0.5 ± 3i' }];
    sqframe(p, 2.6, 'Re(hλ)', 'Im(hλ)');
    bands(p, (x, y) => (Math.hypot(1 + x, y) <= 1 ? 1 : 0), 0, 1.2, 2, 160);
    const th = linspace(0, 2 * Math.PI, 200); p.line(th.map((a) => -1 + Math.cos(a)), th.map((a) => Math.sin(a)), C.lime, 1.5);
    p.line([-9, 9], [0, 0], C.rule, 1).line([0, 0], [-9, 9], C.rule, 1);
    const msg = lams.map((l, i) => { const zr = v.h * l.re, zi = v.h * l.im, g = Math.hypot(1 + zr, zi), col = i ? C.amber : C.cyan; p.dots([zr], [zi], col, 5); if (zi) p.dots([zr], [-zi], col, 5); return `${l.name}: |1 + hλ| = ${nf(3).format(g)} ${g <= 1 ? 'stable' : 'unstable'}`; });
    out(`Lime disc: |1 + hλ| ≤ 1, where explicit Euler is stable. ${msg.join('; ')}. The oscillator needs h < ${nf(3).format(2 * 0.5 / (0.25 + 9))} s; the cooling mode h ≤ 1 s.`);
  },
});

// 04.09 pendulum: Euler vs Heun vs RK4
function rkPend(name, h, T, th0) {
  const f = (y) => [y[1], -9.81 * Math.sin(y[0])], add = (a, b, s) => [a[0] + s * b[0], a[1] + s * b[1]];
  let y = [th0, 0]; const ts = [0], ys = [y[0]];
  for (let t = 0; t < T - 1e-12; t += h) {
    if (name === 'Euler') y = add(y, f(y), h);
    else if (name === 'Heun') { const k1 = f(y), k2 = f(add(y, k1, h)); y = [y[0] + h / 2 * (k1[0] + k2[0]), y[1] + h / 2 * (k1[1] + k2[1])]; }
    else { const k1 = f(y), k2 = f(add(y, k1, h / 2)), k3 = f(add(y, k2, h / 2)), k4 = f(add(y, k3, h)); y = [y[0] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), y[1] + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])]; }
    ts.push(t + h); ys.push(y[0]);
  }
  return [ts, ys];
}
def('rkorder', {
  controls: [{ k: 'h', label: 'Step h (s)', min: 0.005, max: 0.2, step: 0.005, v: 0.05, f: 3 }],
  draw(p, v, out) {
    const th0 = Math.PI / 3, T = 10, R = rkPend('RK4', 0.0005, T, th0), deg = (a) => a.map((r) => r * 180 / Math.PI);
    p.frame({ x: [0, T], y: [-120, 120], xlabel: 't, s', ylabel: 'angle, °' });
    p.line(R[0], deg(R[1]), C.paper, 1, [4, 4]);
    const res = ['Euler', 'Heun', 'RK4'].map((m, i) => { const [ts, ys] = rkPend(m, v.h, T, th0); p.line(ts, deg(ys), [C.grey, C.cyan, C.lime][i], i === 2 ? 2 : 1.5); const ref = R[1][Math.round(ts[ts.length - 1] / 0.0005)]; const e = Math.abs(ys[ys.length - 1] - ref) * 180 / Math.PI; return `${m} ${e > 1e3 ? 'diverged' : e < 0.01 ? e.toExponential(1) + '°' : nf(2).format(e) + '°'}`; });
    out(`Error at t = 10 s: ${res.join(', ')}. Grey Euler gains energy and swings ever wider; cyan Heun (RK2) and lime RK4 track the dashed reference. Halve h: Euler's error halves, Heun's quarters, RK4's drops 16 times.`);
  },
});

// 04.10 adaptive Dormand-Prince on a bouncing ball
def('adaptive', {
  controls: [{ k: 'tol', label: 'Relative tolerance 10^', min: -10, max: -2, step: 1, v: -6, f: 0 }],
  draw(p, v, out) {
    const Cc = [0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1], A = [[], [1 / 5], [3 / 40, 9 / 40], [44 / 45, -56 / 15, 32 / 9], [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729], [9017 / 3168, -355 / 33, 46732 / 5247, 49 / 176, -5103 / 18656], [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84]];
    const B5 = [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0], B4 = [5179 / 57600, 0, 7571 / 16695, 393 / 640, -92097 / 339200, 187 / 2100, 1 / 40];
    const f = (y) => { const F = -0.06 * 9.81 + (y[0] < 0 ? -2e5 * y[0] - 8 * y[1] : 0); return [y[1], F / 0.06]; };
    const rtol = 10 ** v.tol, atol = rtol * 1e-3, T = 2.5;
    let t = 0, y = [1, 0], h = 1e-3, rej = 0; const ts = [0], xs = [1], vs = [0], hs = [];
    while (t < T && hs.length < 20000) {
      h = Math.min(h, T - t); const k = [];
      for (let i = 0; i < 7; i++) { const yi = [y[0], y[1]]; A[i].forEach((a, j) => { yi[0] += h * a * k[j][0]; yi[1] += h * a * k[j][1]; }); k.push(f(yi)); }
      const y5 = [0, 1].map((c) => y[c] + h * B5.reduce((s, b, i) => s + b * k[i][c], 0)), e = [0, 1].map((c) => h * B5.reduce((s, b, i) => s + (b - B4[i]) * k[i][c], 0));
      const en = Math.sqrt(0.5 * [0, 1].reduce((s, c) => s + (e[c] / (atol + rtol * Math.max(Math.abs(y[c]), Math.abs(y5[c])))) ** 2, 0));
      if (en <= 1) { t += h; y = y5; ts.push(t); xs.push(y[0]); vs.push(y[1]); hs.push(h); } else rej++;
      h *= en > 0 ? Math.min(5, Math.max(0.2, 0.9 * en ** -0.2)) : 5;
    }
    p.frame({ x: [0, T], y: [-0.1, 1.1], xlabel: 't, s', ylabel: 'height, m' });
    // dense output: cubic Hermite through position and velocity at each accepted step (exact for free-flight parabolas)
    const dt = [], dx = [];
    for (let i = 0; i < ts.length - 1; i++) { const H = ts[i + 1] - ts[i], m = Math.max(1, Math.ceil(H / 0.004)); for (let j = 0; j < m; j++) { const s = j / m, h00 = 2 * s ** 3 - 3 * s * s + 1, h10 = s ** 3 - 2 * s * s + s, h01 = -2 * s ** 3 + 3 * s * s, h11 = s ** 3 - s * s; dt.push(ts[i] + s * H); dx.push(h00 * xs[i] + h10 * H * vs[i] + h01 * xs[i + 1] + h11 * H * vs[i + 1]); } }
    dt.push(ts[ts.length - 1]); dx.push(xs[xs.length - 1]);
    p.line(dt, dx).dots(ts, xs, C.cyan, 2.5);
    out(`${hs.length} accepted steps (cyan dots), ${rej} rejected. Largest ${nf(0).format(Math.max(...hs) * 1e3)} ms in flight, smallest ${nf(1).format(Math.min(...hs) * 1e6)} µs during the 1.7 ms contacts. A tighter tolerance adds steps mainly around the impacts.`);
  },
});

// 04.11 explicit vs implicit Euler on a stiff, stiffening bushing
def('stiffstep', {
  controls: [{ k: 'lh', label: 'Step h = 10^ (s)', min: -4, max: -1, step: 0.1, v: -2.5, f: 1 }],
  draw(p, v, out) {
    const M = 0.01, Cd = 20, K = 1e4, D = 1e-3, F = 10, h = 10 ** v.lh, T = Math.max(0.02, 3 * h);
    const f = (x, w) => [w, (F - Cd * w - K * x * (1 + (x / D) ** 2)) / M];
    const ex = [[0, 0]], im = [[0, 0]], ts = [0]; let blown = false;
    for (let t = 0; t < T - 1e-12; t += h) {
      const [x, w] = ex[ex.length - 1], d = f(x, w), nx = x + h * d[0], nw = w + h * d[1];
      if (!blown && Math.abs(nx) > 1) blown = true;
      ex.push(blown ? [NaN, NaN] : [nx, nw]);
      // implicit Euler: Newton on z - y - h f(z) = 0
      let [zx, zw] = im[im.length - 1]; const [yx, yw] = im[im.length - 1];
      for (let it = 0; it < 30; it++) {
        const g = f(zx, zw), G0 = zx - yx - h * g[0], G1 = zw - yw - h * g[1];
        const a = 1, b = -h, c = h * K * (1 + 3 * (zx / D) ** 2) / M, dd = 1 + h * Cd / M, det = a * dd - b * c;
        const dx = (-G0 * dd + b * G1) / det, dw = (-a * G1 + c * G0) / det; zx += dx; zw += dw;
        if (Math.abs(dx) < 1e-15) break;
      }
      im.push([zx, zw]); ts.push(t + h);
    }
    const ms = ts.map((t) => t * 1e3);
    p.frame({ x: [0, T * 1e3], y: [-0.2, 1.2], xlabel: 't, ms', ylabel: 'x, mm' });
    p.line([0, T * 1e3], [0.6823, 0.6823], C.grey, 1, [4, 4]);
    p.line(ms, ex.map((s) => s[0] * 1e3), C.red, 1.5).line(ms, im.map((s) => s[0] * 1e3)).dots(ms.length < 80 ? ms : [], im.map((s) => s[0] * 1e3), C.lime, 2.5);
    out(`h = ${h < 1e-3 ? nf(0).format(h * 1e6) + ' µs' : nf(2).format(h * 1e3) + ' ms'}, h|λ| = ${nf(1).format(h * 1000)}. Explicit Euler (red) ${h > 0.002 ? 'blows up: the step is past 2/|λ| = 2 ms' : 'is stable'}; implicit Euler (lime) settles on the static deflection 0.682 mm at any step${h > 0.002 ? ', though it smooths out the fast transient' : ''}.`);
  },
});

// 04.12 energy drift: explicit Euler, RK4, velocity Verlet
def('symplectic', {
  controls: [{ k: 'h', label: 'Step h (s)', min: 0.01, max: 0.2, step: 0.01, v: 0.05, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, h = v.h, T = 500, n = Math.round(T / h), th0 = Math.PI / 3, E = (t, w) => 0.5 * w * w - g * Math.cos(t), E0 = E(th0, 0);
    const every = Math.max(1, Math.floor(n / 400)), ts = [], eu = [], rk = [], vv = [];
    let a = [th0, 0], b = [th0, 0], c = [th0, 0], acc = -g * Math.sin(th0);
    const fr = (t, w) => [w, -g * Math.sin(t)];
    for (let i = 0; i <= n; i++) {
      if (i % every === 0) { ts.push(i * h); eu.push(100 * (E(...a) - E0) / Math.abs(E0)); rk.push(100 * (E(...b) - E0) / Math.abs(E0)); vv.push(100 * (E(...c) - E0) / Math.abs(E0)); }
      a = [a[0] + h * a[1], a[1] - h * g * Math.sin(a[0])];
      const k1 = fr(...b), k2 = fr(b[0] + h / 2 * k1[0], b[1] + h / 2 * k1[1]), k3 = fr(b[0] + h / 2 * k2[0], b[1] + h / 2 * k2[1]), k4 = fr(b[0] + h * k3[0], b[1] + h * k3[1]);
      b = [b[0] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), b[1] + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])];
      const wh = c[1] + 0.5 * h * acc, nt = c[0] + h * wh; acc = -g * Math.sin(nt); c = [nt, wh + 0.5 * h * acc];
    }
    const last = (a) => a[a.length - 1], worst = Math.max(...vv.map(Math.abs)), R = Math.max(2.5 * worst, 1.5 * Math.abs(last(rk)), 0.05);
    p.frame({ x: [0, T], y: [-R, R], xlabel: 't, s', ylabel: 'energy error, %' });
    p.line(ts, eu.map((e) => Math.max(-2 * R, Math.min(2 * R, e))), C.red, 1.5).line(ts, rk, C.cyan, 2).line(ts, vv, C.lime, 1);
    out(`After 500 s: explicit Euler ${Math.abs(last(eu)) > 1e3 ? 'off the chart' : nf(1).format(last(eu)) + '%'} (red), RK4 ${nf(2).format(last(rk))}% and still drifting (cyan), Verlet within ±${nf(2).format(worst)}% the whole time (lime). RK4 costs 4 evaluations per step, Verlet 1.`);
  },
});

// 04.13 finite differences for -u'' = f
def('fdgrid', {
  controls: [{ k: 'n', label: 'Number of cells n', min: 2, max: 40, step: 1, v: 6, f: 0 }],
  draw(p, v, out) {
    const n = v.n, h = 1 / n, solve = (n) => { const h = 1 / n, m = n - 1, a = Array(m).fill(-1), b = Array(m).fill(2), c = Array(m).fill(-1), d = Array.from({ length: m }, (_, i) => h * h * Math.PI ** 2 * Math.sin(Math.PI * (i + 1) * h)); for (let i = 1; i < m; i++) { const w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; d[i] -= w * d[i - 1]; } const u = Array(m).fill(0); u[m - 1] = d[m - 1] / b[m - 1]; for (let i = m - 2; i >= 0; i--) u[i] = (d[i] - c[i] * u[i + 1]) / b[i]; return [0, ...u, 0]; };
    const u = solve(n), xs = u.map((_, i) => i * h), err = (uu, nn) => Math.max(...uu.map((ui, i) => Math.abs(ui - Math.sin(Math.PI * i / nn))));
    const e1 = err(u, n), e2 = n >= 2 ? err(solve(2 * n), 2 * n) : NaN, xx = linspace(0, 1, 200);
    p.frame({ x: [0, 1], y: [-0.05, 1.15], xlabel: 'x', ylabel: 'u' });
    p.line(xx, xx.map((x) => Math.sin(Math.PI * x)), C.grey, 1.5, [4, 4]).line(xs, u, C.lime, 1.5).dots(xs, u, C.lime, 3.5);
    out(`${n} cells, h = ${nf(3).format(h)}: max error ${e1.toExponential(2)}. With ${2 * n} cells it is ${e2.toExponential(2)}, a ratio of ${nf(2).format(e1 / e2)} (second order gives 4).`);
  },
});

// 04.14 FTCS vs Crank-Nicolson on a cooling rod
def('heatscheme', {
  controls: [{ type: 'select', k: 'm', label: 'Scheme', options: ['FTCS (explicit)', 'Crank-Nicolson'], v: 'FTCS (explicit)' }, { k: 'r', label: 'r = α Δt / Δx²', min: 0.1, max: 5, step: 0.02, v: 0.48, f: 2 }, { k: 't', label: 'Time (s)', min: 0, max: 1200, step: 20, v: 300, f: 0 }],
  draw(p, v, out) {
    const alpha = 9.7e-5, L = 0.5, n = 30, dx = L / n, dt = v.r * dx * dx / alpha, steps = Math.round(v.t / dt), xs = linspace(0, L, n + 1);
    let u = xs.map((x, i) => (i === 0 || i === n ? 0 : 100)); const r = v.r;
    for (let s = 0; s < steps; s++) {
      if (v.m.startsWith('FTCS')) { const nu = u.slice(); for (let i = 1; i < n; i++) nu[i] = u[i] + r * (u[i + 1] - 2 * u[i] + u[i - 1]); u = nu; if (Math.abs(u[n >> 1]) > 1e6) break; }
      else { const m = n - 1, a = Array(m).fill(-r / 2), b = Array(m).fill(1 + r), c = Array(m).fill(-r / 2), d = Array.from({ length: m }, (_, k) => (1 - r) * u[k + 1] + r / 2 * (u[k + 2] + u[k])); for (let i = 1; i < m; i++) { const w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; d[i] -= w * d[i - 1]; } const z = Array(m).fill(0); z[m - 1] = d[m - 1] / b[m - 1]; for (let i = m - 2; i >= 0; i--) z[i] = (d[i] - c[i] * z[i + 1]) / b[i]; u = [0, ...z, 0]; }
    }
    const tt = steps * dt, ex = (x) => { if (tt === 0) return x > 0 && x < L ? 100 : 0; let s = 0; for (let k = 1; k < 200; k += 2) s += 400 / (Math.PI * k) * Math.sin(k * Math.PI * x / L) * Math.exp(-alpha * (k * Math.PI / L) ** 2 * tt); return s; };
    const xx = linspace(0, L, 200);
    p.frame({ x: [0, L], y: [-20, 120], xlabel: 'x, m', ylabel: 'T, °C' });
    p.line(xx, xx.map(ex), C.grey, 1.5, [4, 4]).line(xs, u.map((y) => Math.max(-1e3, Math.min(1e3, y)))).dots(xs, u.map((y) => Math.max(-1e3, Math.min(1e3, y))), C.lime, 2.5);
    const bad = Math.abs(u[n >> 1]) > 200;
    out(`${steps} steps of ${nf(1).format(dt)} s. Centre ${bad ? 'blown up' : nf(2).format(u[n >> 1]) + ' °C'} vs exact ${nf(2).format(ex(L / 2))} °C. ${v.m.startsWith('FTCS') ? (r > 0.5 ? 'r > 1/2: the zig-zag mode grows every step.' : 'Stable while r ≤ 1/2.') : 'Stable at any r; large r costs accuracy, and the sharp initial corners ring briefly.'}`);
  },
});

// 04.15 leapfrog wave on a guitar string, CFL number
def('cfl', {
  controls: [{ k: 'cfl', label: 'CFL number c Δt / Δx', min: 0.3, max: 1.05, step: 0.01, v: 1, f: 2 }, { k: 'per', label: 'Time (periods)', min: 0, max: 3, step: 0.05, v: 0.25, f: 2 }],
  draw(p, v, out) {
    const L = 0.648, n = 60, dx = L / n, xs = linspace(0, L, n + 1), a = 0.2 * L, pl = (x) => (x < a ? 2 * x / a : 2 * (L - x) / (L - a));
    const stepsPer = Math.round(2 * n / v.cfl), s = (2 * n / stepsPer) ** 2, N = Math.round(v.per * stepsPer);
    let uo = xs.map(pl), u = uo.map((y, i) => (i === 0 || i === n ? 0 : y + 0.5 * s * (uo[i + 1] - 2 * y + uo[i - 1])));
    if (N === 0) u = uo;
    for (let k = 1; k < N; k++) { const un = u.map((y, i) => (i === 0 || i === n ? 0 : 2 * y - uo[i] + s * (u[i + 1] - 2 * y + u[i - 1]))); uo = u; u = un; if (Math.abs(u[n >> 1]) > 1e6) break; }
    // exact: d'Alembert with odd periodic extension
    const ext = (x) => { x = ((x % (2 * L)) + 2 * L) % (2 * L); return x <= L ? pl(x) : -pl(2 * L - x); }, ct = 2 * L * v.per;
    const xx = linspace(0, L, 300);
    p.frame({ x: [0, L], y: [-2.5, 2.5], xlabel: 'x, m', ylabel: 'u, mm' });
    p.line(xx, xx.map((x) => 0.5 * (ext(x - ct) + ext(x + ct))), C.grey, 1.5, [4, 4]).line(xs, u.map((y) => Math.max(-9, Math.min(9, y))));
    const cfl = Math.sqrt(s), err = Math.max(...u.map((y, i) => Math.abs(y - 0.5 * (ext(xs[i] - ct) + ext(xs[i] + ct)))));
    out(`CFL ${nf(3).format(cfl)}, ${stepsPer} steps per period. Max error ${err > 100 ? 'unbounded: unstable' : nf(3).format(err) + ' mm'}. ${cfl > 1 ? 'Past CFL = 1 the scheme blows up.' : cfl > 0.999 ? 'At exactly 1 the scheme is exact.' : 'Below 1 it is stable, but waves of different lengths travel at slightly wrong speeds, so the kinks smear.'}`);
  },
});

// 04.16 pollutant pulse: upwind vs Lax-Wendroff vs central
def('advect', {
  controls: [{ type: 'select', k: 's', label: 'Scheme', options: ['upwind', 'Lax-Wendroff', 'central (FTCS)'], v: 'upwind' }, { k: 'c', label: 'CFL number U Δt / Δx', min: 0.1, max: 1.1, step: 0.05, v: 0.8, f: 2 }, { k: 't', label: 'Time (min)', min: 0, max: 50, step: 1, v: 33, f: 0 }],
  draw(p, v, out) {
    const U = 0.5, LEN = 2000, n = 400, dx = LEN / n, c = v.c, dt = c * dx / U, steps = Math.round(v.t * 60 / dt);
    const xs = Array.from({ length: n }, (_, i) => (i + 0.5) * dx);
    let q = xs.map((x) => (Math.abs(x - 300) <= 50 ? 1 : 0));
    for (let s = 0; s < steps; s++) {
      const qn = new Array(n);
      for (let i = 0; i < n; i++) { const l = q[(i - 1 + n) % n], r = q[(i + 1) % n], m = q[i];
        qn[i] = v.s === 'upwind' ? m - c * (m - l) : v.s === 'Lax-Wendroff' ? m - 0.5 * c * (r - l) + 0.5 * c * c * (r - 2 * m + l) : m - 0.5 * c * (r - l); }
      q = qn; if (Math.abs(q[0]) > 1e6) break;
    }
    const tt = steps * dt, ex = xs.map((x) => { const x0 = ((300 + U * tt) % LEN); return Math.min(Math.abs(x - x0), LEN - Math.abs(x - x0)) <= 50 ? 1 : 0; });
    p.frame({ x: [0, LEN], y: [-0.4, 1.4], xlabel: 'distance downstream, m', ylabel: 'concentration' });
    p.line(xs, ex, C.grey, 1.5, [4, 4]).line(xs, q.map((y) => Math.max(-5, Math.min(5, y))));
    const mx = Math.max(...q), mn = Math.min(...q);
    out(`${steps} steps. Peak ${Math.abs(mx) > 100 ? 'blown up' : nf(3).format(mx)}, minimum ${Math.abs(mn) > 100 ? '—' : nf(3).format(mn)}. ${c > 1 ? 'CFL > 1: unstable for every scheme here.' : v.s === 'upwind' ? 'Upwind never creates new peaks or negative values, but smears the slug: numerical diffusion U Δx (1 − c)/2.' : v.s === 'Lax-Wendroff' ? 'Second order and sharper, but it over- and undershoots near the edges: negative concentrations.' : 'Central differences with forward Euler are unstable at any CFL: the wiggles grow.'}`);
  },
});

// 04.17 convergence race: Jacobi vs Gauss-Seidel vs SOR
def('sorrace', {
  controls: [{ k: 'w', label: 'SOR relaxation factor ω', min: 1, max: 1.98, step: 0.01, v: 1.77, f: 2 }],
  draw(p, v, out) {
    const n = 24, h = 1 / n, maxit = 2500, f = [];
    for (let i = 0; i <= n; i++) { f.push([]); for (let j = 0; j <= n; j++) f[i].push(2 * Math.PI ** 2 * Math.sin(Math.PI * i * h) * Math.sin(Math.PI * j * h)); }
    const resid = (u) => { let s = 0; for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) { const r = f[i][j] + (u[i + 1][j] + u[i - 1][j] + u[i][j + 1] + u[i][j - 1] - 4 * u[i][j]) / (h * h); s += r * r; } return Math.sqrt(s); };
    const r0 = resid(Array.from({ length: n + 1 }, () => new Array(n + 1).fill(0)));
    const run = (kind, w) => { let u = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(0)); const hist = [1]; let hit = -1;
      for (let it = 1; it <= maxit; it++) {
        if (kind === 'J') { const un = u.map((r) => r.slice()); for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) un[i][j] = 0.25 * (u[i + 1][j] + u[i - 1][j] + u[i][j + 1] + u[i][j - 1] + h * h * f[i][j]); u = un; }
        else for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) { const gs = 0.25 * (u[i + 1][j] + u[i - 1][j] + u[i][j + 1] + u[i][j - 1] + h * h * f[i][j]); u[i][j] += w * (gs - u[i][j]); }
        const r = resid(u) / r0; hist.push(r); if (r < 1e-8) { hit = it; break; }
      } return [hist, hit]; };
    const J = run('J', 1), G = run('G', 1), S = run('G', v.w), wopt = 2 / (1 + Math.sin(Math.PI * h));
    p.frame({ x: [0, maxit], y: [1e-9, 2], ylog: true, xlabel: 'iteration', ylabel: 'relative residual' });
    [[J, C.grey], [G, C.cyan], [S, C.lime]].forEach(([[hst], col]) => p.line(hst.map((_, i) => i), hst, col, 2));
    const s = (x) => (x[1] < 0 ? `> ${maxit}` : String(x[1]));
    out(`Iterations to 1e-8 on a 24 × 24 grid: Jacobi ${s(J)}, Gauss-Seidel ${s(G)}, SOR (ω = ${nf(2).format(v.w)}) ${s(S)}. The optimum is ω = 2/(1 + sin πh) = ${nf(3).format(wopt)}.`);
  },
});

// 04.18 smoothing and coarse-grid correction
def('multigrid', {
  controls: [{ k: 'sw', label: 'Weighted Jacobi sweeps', min: 0, max: 30, step: 1, v: 6, f: 0 }, { k: 'cg', label: 'Then apply the coarse-grid correction', type: 'check', v: 0 }],
  draw(p, v, out) {
    const n = 64, h = 1 / n, rnd = gaussRng(3), xs = linspace(0, 1, n + 1);
    // error equation A e = 0 starting from a mix of smooth and rough modes
    let e = xs.map((x, i) => (i === 0 || i === n ? 0 : Math.sin(Math.PI * x) + 0.5 * Math.sin(3 * Math.PI * x) + 0.4 * rnd()));
    const e0 = Math.sqrt(e.reduce((s, y) => s + y * y, 0));
    for (let s = 0; s < v.sw; s++) { const en = e.slice(); for (let i = 1; i < n; i++) en[i] = e[i] / 3 + (2 / 3) * 0.5 * (e[i - 1] + e[i + 1]); e = en; }
    const eSmooth = e.slice();
    if (v.cg) {
      // residual r = -A e, restrict, solve exactly on the coarse grid, interpolate and subtract
      const r = e.map((y, i) => (i === 0 || i === n ? 0 : -(2 * y - e[i - 1] - e[i + 1]) / (h * h)));
      const m = n / 2, H = 2 * h, rc = Array.from({ length: m + 1 }, (_, I) => (I === 0 || I === m ? 0 : 0.25 * r[2 * I - 1] + 0.5 * r[2 * I] + 0.25 * r[2 * I + 1]));
      const a = Array(m - 1).fill(-1), b = Array(m - 1).fill(2), c = Array(m - 1).fill(-1), d = rc.slice(1, m).map((y) => y * H * H);
      for (let i = 1; i < m - 1; i++) { const w = a[i] / b[i - 1]; b[i] -= w * c[i - 1]; d[i] -= w * d[i - 1]; }
      const z = Array(m - 1).fill(0); z[m - 2] = d[m - 2] / b[m - 2]; for (let i = m - 3; i >= 0; i--) z[i] = (d[i] - c[i] * z[i + 1]) / b[i];
      const ec = [0, ...z, 0], fine = xs.map((_, i) => (i % 2 === 0 ? ec[i / 2] : 0.5 * (ec[(i - 1) / 2] + ec[(i + 1) / 2])));
      e = e.map((y, i) => y + fine[i]);
    }
    const norm = Math.sqrt(e.reduce((s, y) => s + y * y, 0));
    p.frame({ x: [0, 1], y: [-1.6, 1.6], xlabel: 'x', ylabel: 'error' });
    if (v.cg) p.line(xs, eSmooth, C.grey, 1.5, [4, 4]);
    p.line(xs, e).dots(xs, e, C.lime, 2);
    out(`Error norm ${nf(3).format(norm / e0)} of the initial. ${v.cg ? 'The coarse grid removed the smooth error the sweeps could not touch (dashed: before the correction).' : v.sw === 0 ? 'Rough plus smooth error.' : 'Smoothing kills the jagged part in a few sweeps, then stalls on the smooth hump. Tick the box for the coarse-grid correction.'}`);
  },
});

// 04.19 gradient descent vs BFGS on Rosenbrock
def('rosen', {
  controls: [{ type: 'select', k: 'm', label: 'Method', options: ['BFGS', 'gradient descent'], v: 'BFGS' }, { k: 'it', label: 'Iterations', min: 1, max: 300, step: 1, v: 40, f: 0 }],
  draw(p, v, out) {
    const f = (x, y) => (1 - x) ** 2 + 100 * (y - x * x) ** 2, g = (x, y) => [-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)];
    p.frame({ x: [-2, 2], y: [-1, 3], xlabel: 'x₁', ylabel: 'x₂' });
    bands(p, (x, y) => Math.log10(1 + f(x, y)), 0, 3.5, 14, 140);
    let x = [-1.2, 1], H = [[1, 0], [0, 1]], gr = g(...x); const P = [x.slice()]; let k = 0;
    for (; k < v.it && Math.hypot(...gr) > 1e-10; k++) {
      const d = v.m === 'BFGS' ? [-(H[0][0] * gr[0] + H[0][1] * gr[1]), -(H[1][0] * gr[0] + H[1][1] * gr[1])] : [-gr[0], -gr[1]];
      let a = 1; const fx = f(...x), slope = gr[0] * d[0] + gr[1] * d[1]; while (f(x[0] + a * d[0], x[1] + a * d[1]) > fx + 1e-4 * a * slope && a > 1e-12) a *= 0.5;
      const s = [a * d[0], a * d[1]], xn = [x[0] + s[0], x[1] + s[1]], gn = g(...xn), y = [gn[0] - gr[0], gn[1] - gr[1]], ys = y[0] * s[0] + y[1] * s[1];
      if (v.m === 'BFGS' && ys > 1e-12) { const r = 1 / ys, A = [[1 - r * s[0] * y[0], -r * s[0] * y[1]], [-r * s[1] * y[0], 1 - r * s[1] * y[1]]], mul = (X, Y) => [[X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]], [X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]]]; const At = [[A[0][0], A[1][0]], [A[0][1], A[1][1]]]; H = mul(mul(A, H), At); H[0][0] += r * s[0] * s[0]; H[0][1] += r * s[0] * s[1]; H[1][0] += r * s[1] * s[0]; H[1][1] += r * s[1] * s[1]; }
      x = xn; gr = gn; P.push(x.slice());
    }
    p.line(P.map((q) => q[0]), P.map((q) => q[1]), C.paper, 1.5).dots(P.map((q) => q[0]), P.map((q) => q[1]), C.cyan, 2.5).dots([1], [1], C.red, 5);
    out(`${k} iterations: x = (${nf(5).format(x[0])}, ${nf(5).format(x[1])}), f = ${f(...x).toExponential(2)}. ${v.m === 'BFGS' ? 'BFGS learns the curvature and runs along the curved valley; it reaches (1, 1) to 1e-10 in about 36 iterations.' : 'Steepest descent zig-zags across the narrow valley; it needs about 25 000 iterations.'}`);
  },
});

// 04.20 observed order of accuracy: correct solver vs a planted bug (errors from mms.py)
def('mmsorder', {
  controls: [{ k: 'bug', label: 'Plant the off-by-one spacing bug', type: 'check', v: 0 }],
  draw(p, v, out) {
    const ns = [8, 16, 32, 64, 128], hs = ns.map((n) => 1 / n);
    const good = [1.32e-2, 3.34e-3, 8.36e-4, 2.09e-4, 5.23e-5], bad = [1.65e-1, 9.41e-2, 5.02e-2, 2.59e-2, 1.32e-2], e = v.bug ? bad : good;
    p.frame({ x: [0.005, 0.2], y: [1e-5, 1], xlog: true, ylog: true, xlabel: 'grid spacing h', ylabel: 'max error' });
    p.line([0.005, 0.2], [0.005 ** 2 * 0.85, 0.2 ** 2 * 0.85], C.grey, 1, [4, 4]).line([0.005, 0.2], [0.005 * 1.3, 0.2 * 1.3], C.grey, 1, [2, 4]);
    p.line(hs, e, v.bug ? C.red : C.lime, 2).dots(hs, e, v.bug ? C.red : C.lime, 4);
    const pobs = Math.log2(e[3] / e[4]);
    out(`Observed order on the finest pair: ${nf(2).format(pobs)}. Grey guides: slope 2 (dashed) and slope 1 (dotted). ${v.bug ? 'The buggy solver still converges and its pictures look right, but at first order: the test fails.' : 'The 5-point solver converges at second order, as designed: verified.'}`);
  },
});

// equal-scale frame centred anywhere
function sqAt(p, cx, cy, R, xlabel = 'x', ylabel = 'y') {
  p.size(); const asp = (p.w - p.pad.l - p.pad.r) / (p.h - p.pad.t - p.pad.b);
  return asp >= 1 ? p.frame({ x: [cx - R * asp, cx + R * asp], y: [cy - R, cy + R], xlabel, ylabel }) : p.frame({ x: [cx - R, cx + R], y: [cy - R / asp, cy + R / asp], xlabel, ylabel });
}
// equal-scale frame that fits a box of half-sizes hx, hy around (cx, cy)
function fitAt(p, cx, cy, hx, hy, xlabel = 'x', ylabel = 'y') {
  p.size(); const asp = (p.w - p.pad.l - p.pad.r) / (p.h - p.pad.t - p.pad.b);
  if (hx / hy > asp) hy = hx / asp; else hx = hy * asp;
  return p.frame({ x: [cx - hx, cx + hx], y: [cy - hy, cy + hy], xlabel, ylabel });
}
// small support symbols for beams (planar)
function drawSupport(p, kind, x, y, s, dir = -1) {
  if (kind === 'none') return;
  if (kind === 'clamp') { p.line([x, x], [y - 1.4 * s, y + 1.4 * s], C.paper, 3); for (let k = -1.2; k <= 1.2; k += 0.6) p.line([x, x + dir * 0.5 * s], [y + k * s, y + (k - 0.5) * s], C.grey, 1); return; }
  poly(p, [[x, y], [x - 0.6 * s, y - s], [x + 0.6 * s, y - s]], C.paper, null, 1.5);
  if (kind === 'roller') { p.dots([x - 0.35 * s, x + 0.35 * s], [y - 1.25 * s, y - 1.25 * s], C.paper, 3); p.line([x - 0.9 * s, x + 0.9 * s], [y - 1.5 * s, y - 1.5 * s], C.grey, 1); }
  else p.line([x - 0.9 * s, x + 0.9 * s], [y - s, y - s], C.grey, 1);
}

// 05.01 adding forces tip to tail
def('forceadd', {
  controls: [{ k: 'm', label: 'Cable 2 force (kN)', min: 0, max: 5, step: 0.1, v: 3, f: 1 }, { k: 'a', label: 'Cable 2 angle (°)', min: 0, max: 360, step: 5, v: 135, f: 0 }],
  draw(p, v, out) {
    const F = [[2, 30], [v.m, v.a], [1.5, 250]].map(([m, a]) => [m * Math.cos(a * Math.PI / 180), m * Math.sin(a * Math.PI / 180)]);
    const R = F.reduce((s, f) => [s[0] + f[0], s[1] + f[1]], [0, 0]);
    sqAt(p, 0, 0, 4.2, 'Fx, kN', 'Fy, kN');
    const cols = [C.cyan, C.amber, C.grey];
    F.forEach((f, i) => arrow(p, 0, 0, f[0], f[1], cols[i], 1.5));
    let x = 0, y = 0; F.forEach((f, i) => { arrow(p, x, y, x + f[0], y + f[1], cols[i], 2.5); x += f[0]; y += f[1]; });
    arrow(p, 0, 0, R[0], R[1], C.lime, 3.5);
    const mag = Math.hypot(...R), ang = (Math.atan2(R[1], R[0]) * 180 / Math.PI + 360) % 360;
    out(`Resultant (lime) ${nf(3).format(mag)} kN at ${nf(1).format(ang)}°: components (${nf(3).format(R[0])}, ${nf(3).format(R[1])}) kN, the sums of the components. Thin arrows start at the pole head; thick ones are laid tip to tail.`);
  },
});

// 05.02 spanner: moment = force x lever arm
def('spanner', {
  controls: [{ k: 'P', label: 'Force (N)', min: 0, max: 200, step: 5, v: 120, f: 0 }, { k: 'a', label: 'Angle to the handle (°)', min: 0, max: 180, step: 1, v: 70, f: 0 }, { k: 'd', label: 'Grip distance from the nut (mm)', min: 50, max: 250, step: 5, v: 250, f: 0 }],
  draw(p, v, out) {
    const L = v.d / 1000, a = v.a * Math.PI / 180, F = [v.P * Math.cos(a), v.P * Math.sin(a)], s = 0.0011;
    sqAt(p, 0.13, 0.03, 0.17, 'x, m', 'y, m');
    poly(p, [[-0.01, -0.012], [0.27, -0.008], [0.27, 0.008], [-0.01, 0.012]], C.grey, 'rgba(154,157,147,0.2)');
    p.dots([0], [0], C.paper, 7);
    // line of action and perpendicular distance
    const ux = Math.cos(a), uy = Math.sin(a), t = -(L * ux), fx = L + t * ux, fy = t * uy;
    p.line([L - 0.3 * ux, L + 0.3 * ux], [-0.3 * uy, 0.3 * uy], C.rule, 1, [4, 4]).line([0, fx], [0, fy], C.cyan, 1.5, [3, 3]);
    arrow(p, L, 0, L + F[0] * s * 0.6, F[1] * s * 0.6, C.lime, 3);
    const M = L * F[1], arm = Math.abs(L * Math.sin(a));
    out(`Moment about the nut M = r × F = ${nf(2).format(M)} N m (counter-clockwise positive). Lever arm, the perpendicular distance from the nut to the line of action (cyan): ${nf(1).format(arm * 1000)} mm. Pull at 90° for the most moment per newton.`);
  },
});

// 05.03 distributed load reduced to a single resultant
def('distload', {
  controls: [{ k: 'q1', label: 'Left intensity q₁ (kN/m)', min: 0, max: 6, step: 0.1, v: 2, f: 1 }, { k: 'q2', label: 'Right intensity q₂ (kN/m)', min: 0, max: 6, step: 0.1, v: 5, f: 1 }],
  draw(p, v, out) {
    const L = 6, R = (v.q1 + v.q2) * L / 2, xb = R > 0 ? (v.q1 * L * L / 2 + (v.q2 - v.q1) * L / 2 * 2 * L / 3) / R : L / 2;
    p.frame({ x: [-0.5, 6.5], y: [-1.5, 9], xlabel: 'x, m', ylabel: 'q, kN/m' });
    poly(p, [[0, 0], [0, v.q1], [L, v.q2], [L, 0]], C.cyan, 'rgba(92,200,255,0.15)');
    for (let x = 0; x <= L + 1e-9; x += 0.5) { const q = v.q1 + (v.q2 - v.q1) * x / L; if (q > 0.15) arrow(p, x, q, x, 0.05, C.cyan, 1); }
    p.line([0, L], [0, 0], C.paper, 4);
    arrow(p, xb, 8.5, xb, 0.1, C.lime, 3.5);
    p.text(`R = ${nf(1).format(R)} kN`, xb + 0.15, 8, C.lime);
    out(`Resultant R = (q₁ + q₂)L/2 = ${nf(2).format(R)} kN acting at x = ${nf(3).format(xb)} m, through the centroid of the load area. With q₁ = 0 it sits at 2L/3 = 4 m, L/3 from the high end.`);
  },
});

// 05.04 slider-crank velocities and the instantaneous centre of the rod
def('crank', {
  controls: [{ k: 'th', label: 'Crank angle θ (°)', min: 0, max: 360, step: 1, v: 60, f: 0 }],
  draw(p, v, out) {
    const r = 0.05, l = 0.2, w = 100, th = v.th * Math.PI / 180, A = [r * Math.cos(th), r * Math.sin(th)], B = [A[0] + Math.sqrt(l * l - A[1] * A[1]), 0];
    const vA = [-w * A[1], w * A[0]], rAB = [B[0] - A[0], B[1] - A[1]], wr = -vA[1] / rAB[0], vB = vA[0] - wr * rAB[1];
    sqAt(p, 0.11, 0.02, 0.15, 'x, m', 'y, m');
    p.line([-0.06, 0.3], [0, 0], C.rule, 1);
    poly(p, [[B[0] - 0.02, -0.012], [B[0] + 0.02, -0.012], [B[0] + 0.02, 0.012], [B[0] - 0.02, 0.012]], C.paper, 'rgba(242,243,236,0.15)');
    p.line([0, A[0]], [0, A[1]], C.grey, 5).line([A[0], B[0]], [A[1], B[1]], C.paper, 4).dots([0, A[0], B[0]], [0, A[1], 0], C.paper, 4);
    const s = 0.006; arrow(p, A[0], A[1], A[0] + vA[0] * s, A[1] + vA[1] * s, C.cyan, 2.5); arrow(p, B[0], 0, B[0] + vB * s, 0, C.lime, 3);
    let msg;
    if (Math.abs(wr) > 1e-6) { const I = [A[0] - vA[1] / wr, A[1] + vA[0] / wr]; if (Math.abs(I[1]) < 1) { p.line([0, I[0]], [0, I[1]], C.amber, 1, [4, 4]).line([B[0], I[0]], [0, I[1]], C.amber, 1, [4, 4]).dots([I[0]], [I[1]], C.amber, 5); } msg = `Rod instantaneous centre (amber) at (${nf(3).format(I[0])}, ${nf(3).format(I[1])}) m, where line OA meets the vertical through B.`; }
    else msg = 'The rod is momentarily translating (ω = 0): its instantaneous centre is at infinity.';
    out(`Crank 100 rad/s: crank pin speed 5.00 m/s (cyan). Rod ω = ${nf(2).format(wr)} rad/s, piston velocity ${nf(3).format(vB)} m/s (lime). ${msg}`);
  },
});

// 05.05 supports: count reactions and check rank
def('supports', {
  controls: [{ type: 'select', k: 'a', label: 'Left support', options: ['none', 'roller', 'pin', 'clamp'], v: 'pin' }, { type: 'select', k: 'b', label: 'Right support', options: ['none', 'roller', 'pin', 'clamp'], v: 'roller' }],
  draw(p, v, out) {
    const R = { none: 0, roller: 1, pin: 2, clamp: 3 }, n = R[v.a] + R[v.b];
    // reaction rows (Fx, Fy, M about the left end); beam 0..4 m
    const rows = [], add = (kind, x) => { if (kind === 'roller') rows.push([0, 1, x]); if (kind === 'pin' || kind === 'clamp') { rows.push([1, 0, 0]); rows.push([0, 1, x]); } if (kind === 'clamp') rows.push([0, 0, 1]); };
    add(v.a, 0); add(v.b, 4);
    // rank by Gaussian elimination
    const m = rows.map((r) => r.slice()); let rank = 0;
    for (let c = 0; c < 3; c++) { const piv = m.findIndex((r, i) => i >= rank && Math.abs(r[c]) > 1e-9); if (piv < 0) continue; [m[rank], m[piv]] = [m[piv], m[rank]]; for (let i = 0; i < m.length; i++) if (i !== rank) { const f = m[i][c] / m[rank][c]; m[i] = m[i].map((x, k) => x - f * m[rank][k]); } rank++; }
    p.frame({ x: [-0.8, 4.8], y: [-1.6, 1.6], xlabel: 'x, m', ylabel: '' });
    p.line([0, 4], [0, 0], C.lime, 5);
    drawSupport(p, v.a, 0, 0, 0.3, -1); drawSupport(p, v.b, 4, 0, 0.3, 1);
    const dof = 3 - rank, cls = dof > 0 ? `a mechanism with ${dof} free motion${dof > 1 ? 's' : ''}` : n > 3 ? `statically indeterminate (degree ${n - 3})` : 'statically determinate';
    out(`${n} reaction component${n === 1 ? '' : 's'}, of which ${rank} independent. The beam is ${cls}. ${v.a === 'roller' && v.b === 'roller' ? 'Two rollers cannot stop it sliding sideways.' : ''}`);
  },
});

// dense Gaussian elimination with partial pivoting; returns null when singular
function linSolve(A0, b0) {
  const n = b0.length, A = A0.map((r, i) => [...r, b0[i]]);
  for (let c = 0; c < n; c++) {
    let piv = c; for (let i = c + 1; i < n; i++) if (Math.abs(A[i][c]) > Math.abs(A[piv][c])) piv = i;
    if (Math.abs(A[piv][c]) < 1e-9) return null;
    [A[c], A[piv]] = [A[piv], A[c]];
    for (let i = c + 1; i < n; i++) { const f = A[i][c] / A[c][c]; for (let k = c; k <= n; k++) A[i][k] -= f * A[c][k]; }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) { let s = A[i][n]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / A[i][i]; }
  return x;
}
function rankOf(M0) {
  const M = M0.map((r) => r.slice()); if (!M.length) return 0; const nc = M[0].length; let rank = 0;
  for (let c = 0; c < nc && rank < M.length; c++) {
    let piv = -1, best = 1e-9; for (let i = rank; i < M.length; i++) if (Math.abs(M[i][c]) > best) { best = Math.abs(M[i][c]); piv = i; }
    if (piv < 0) continue; [M[rank], M[piv]] = [M[piv], M[rank]];
    for (let i = 0; i < M.length; i++) if (i !== rank) { const f = M[i][c] / M[rank][c]; for (let k = c; k < nc; k++) M[i][k] -= f * M[rank][k]; }
    rank++;
  }
  return rank;
}
// method of joints for a plane truss; supports [node, dx, dy]; loads {node: [Fx, Fy]}; returns member forces or null
function trussSolve(nodes, members, supports, loads) {
  const n = nodes.length, m = members.length, nu = m + supports.length;
  if (2 * n !== nu) return null;
  const A = Array.from({ length: 2 * n }, () => new Array(nu).fill(0)), b = new Array(2 * n).fill(0);
  members.forEach(([i, j], k) => { const dx = nodes[j][0] - nodes[i][0], dy = nodes[j][1] - nodes[i][1], L = Math.hypot(dx, dy); A[2 * i][k] += dx / L; A[2 * i + 1][k] += dy / L; A[2 * j][k] -= dx / L; A[2 * j + 1][k] -= dy / L; });
  supports.forEach(([nd, dx, dy], k) => { A[2 * nd][m + k] += dx; A[2 * nd + 1][m + k] += dy; });
  Object.entries(loads).forEach(([nd, F]) => { b[2 * nd] -= F[0]; b[2 * nd + 1] -= F[1]; });
  return linSolve(A, b);
}
function drawTruss(p, nodes, members, F, scale, removed = -1) {
  members.forEach(([i, j], k) => {
    if (k === removed) { p.line([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], C.red, 1, [3, 4]); return; }
    if (!F) { p.line([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], C.grey, 2); return; }
    const f = F[k], col = Math.abs(f) < 1e-6 * scale ? C.grey : f > 0 ? C.cyan : C.amber;
    p.line([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], col, 1.5 + 6 * Math.min(1, Math.abs(f) / scale));
  });
  p.dots(nodes.map((q) => q[0]), nodes.map((q) => q[1]), C.paper, 3.5);
}

// 05.06 ladder free-body diagram
def('ladder', {
  controls: [{ k: 'th', label: 'Ladder angle to the floor (°)', min: 45, max: 85, step: 1, v: 65, f: 0 }, { k: 's', label: 'Person, distance up the ladder (m)', min: 0, max: 5, step: 0.05, v: 3.75, f: 2 }, { k: 'mu', label: 'Floor friction μ', min: 0.1, max: 0.6, step: 0.01, v: 0.25, f: 2 }],
  draw(p, v, out) {
    const L = 5, W = 200, P = 800, th = v.th * Math.PI / 180, c = Math.cos(th), sn = Math.sin(th);
    const Nf = W + P, Nw = (W * L / 2 * c + P * v.s * c) / (L * sn), Ff = Nw, slips = Ff > v.mu * Nf;
    const T = [L * c, L * sn], k = 0.0022;
    sqAt(p, 1.6, 2.4, 2.9, 'x, m', 'y, m');
    p.line([T[0], T[0]], [-0.2, 5.4], C.grey, 3).line([-1.2, T[0] + 0.3], [0, 0], C.grey, 3);
    p.line([0, T[0]], [0, T[1]], slips ? C.red : C.paper, 4);
    const pm = [v.s / L * T[0], v.s / L * T[1]], mid = [T[0] / 2, T[1] / 2];
    arrow(p, mid[0], mid[1], mid[0], mid[1] - W * k, C.grey, 2); arrow(p, pm[0], pm[1], pm[0], pm[1] - P * k, C.grey, 2.5);
    arrow(p, T[0], T[1], T[0] - Nw * k, T[1], C.cyan, 2.5);
    arrow(p, 0, -Nf * k, 0, 0, C.cyan, 2.5); arrow(p, -Ff * k, 0.05, 0, 0.05, slips ? C.red : C.lime, 2.5);
    p.dots([pm[0]], [pm[1]], C.amber, 6);
    out(`Wall push ${nf(1).format(Nw)} N, floor normal ${nf(0).format(Nf)} N, friction needed ${nf(1).format(Ff)} N against ${nf(1).format(v.mu * Nf)} N available (μN). ${slips ? 'Not enough friction: the ladder slips.' : 'Friction is sufficient: the ladder holds.'} Higher up and flatter both need more friction.`);
  },
});

// 05.07 beam reactions with movable loads
def('beamload', {
  controls: [{ k: 'x1', label: 'Load P₁ position (m)', min: 0, max: 8, step: 0.1, v: 2, f: 1 }, { k: 'P1', label: 'P₁ (kN)', min: 0, max: 40, step: 1, v: 20, f: 0 }, { k: 'P2', label: 'Tip load P₂ at 8 m (kN)', min: 0, max: 30, step: 1, v: 10, f: 0 }, { type: 'check', k: 'q', label: 'Uniform load 5 kN/m on the span', v: 1 }],
  draw(p, v, out) {
    const q = v.q ? 5 : 0, Rb = (v.P1 * v.x1 + q * 6 * 3 + v.P2 * 8) / 6, Ra = v.P1 + q * 6 + v.P2 - Rb, k = 0.035;
    p.frame({ x: [-0.8, 8.8], y: [-2.6, 2.6], xlabel: 'x, m', ylabel: '' });
    if (q) { poly(p, [[0, 0.1], [0, 0.55], [6, 0.55], [6, 0.1]], C.cyan, 'rgba(92,200,255,0.12)'); for (let x = 0; x <= 6; x += 0.75) arrow(p, x, 0.55, x, 0.12, C.cyan, 1); }
    p.line([0, 8], [0, 0], C.paper, 5); drawSupport(p, 'pin', 0, -0.05, 0.25); drawSupport(p, 'roller', 6, -0.05, 0.25);
    if (v.P1 > 0) arrow(p, v.x1, 0.15 + v.P1 * k, v.x1, 0.1, C.amber, 3);
    if (v.P2 > 0) arrow(p, 8, 0.15 + v.P2 * k, 8, 0.1, C.amber, 3);
    const ra = (x, R) => { if (Math.abs(R) < 1e-9) return; if (R > 0) arrow(p, x, -0.45 - R * k * 0.6, x, -0.45, C.lime, 3); else arrow(p, x, -0.45, x, -0.45 + R * k * 0.6, C.red, 3); };
    ra(0, Ra); ra(6, Rb);
    out(`Reactions: Rₐ = ${nf(2).format(Ra)} kN at the pin, R_b = ${nf(2).format(Rb)} kN at the roller (lime up, red down). From ΣM about the pin: 6 R_b = ${v.P1} · ${nf(1).format(v.x1)} + ${q * 6} · 3 + ${v.P2} · 8.${Ra < 0 ? ' The pin must pull down: the overhang load tips the beam, so the support needs a tie-down.' : ''}`);
  },
});

// 05.08 determinacy of a two-part beam with an optional hinge
def('determinacy', {
  controls: [{ type: 'select', k: 'a', label: 'Left support (x = 0)', options: ['none', 'roller', 'pin', 'clamp'], v: 'clamp' }, { type: 'select', k: 'm', label: 'Middle support (x = 6)', options: ['none', 'roller', 'pin'], v: 'none' }, { type: 'select', k: 'b', label: 'Right support (x = 10)', options: ['none', 'roller', 'pin', 'clamp'], v: 'roller' }, { type: 'check', k: 'h', label: 'Hinge at x = 4 (two bodies)', v: 1 }],
  draw(p, v, out) {
    const nb = v.h ? 2 : 1, body = (x) => (v.h && x > 4 ? 1 : 0), cols = [];
    const add = (kind, x) => { const bd = body(x), col = (fx, fy, mz) => { const c = new Array(3 * nb).fill(0); c[3 * bd] = fx; c[3 * bd + 1] = fy; c[3 * bd + 2] = x * fy + mz; return c; };
      if (kind === 'roller') cols.push(col(0, 1, 0)); if (kind === 'pin' || kind === 'clamp') { cols.push(col(1, 0, 0)); cols.push(col(0, 1, 0)); } if (kind === 'clamp') cols.push(col(0, 0, 1)); };
    add(v.a, 0); add(v.m, 6); add(v.b, 10);
    if (v.h) { const hx = [1, 0, 0, -1, 0, 0], hy = [0, 1, 4, 0, -1, -4]; cols.push(hx, hy); }
    const rows = Array.from({ length: 3 * nb }, (_, i) => cols.map((c) => c[i])), rank = cols.length ? rankOf(rows) : 0;
    const mech = 3 * nb - rank, indet = cols.length - rank;
    p.frame({ x: [-1, 11], y: [-2.2, 2.2], xlabel: 'x, m', ylabel: '' });
    p.line([0, 4], [0, 0], C.lime, 5).line([4, 10], [0, 0], v.h ? C.cyan : C.lime, 5);
    if (v.h) p.dots([4], [0], C.paper, 6);
    drawSupport(p, v.a, 0, 0, 0.35, -1); drawSupport(p, v.m, 6, 0, 0.35); drawSupport(p, v.b, 10, 0, 0.35, 1);
    const verdict = mech > 0 ? `a mechanism with ${mech} free motion${mech > 1 ? 's' : ''}${indet ? ` (and ${indet} redundant reaction${indet > 1 ? 's' : ''})` : ''}` : indet > 0 ? `${indet}× statically indeterminate` : 'statically determinate';
    out(`${nb} bod${nb > 1 ? 'ies' : 'y'}: ${3 * nb} equations, ${cols.length} unknowns (hinge forces included), rank ${rank}. The structure is ${verdict}.`);
  },
});

// 05.09 Warren truss: member forces, delete a member
const warrenNodes = (() => { const a = 4, h = a * Math.sqrt(3) / 2, n = []; for (let i = 0; i <= 4; i++) n.push([i * a, 0]); for (let i = 0; i < 4; i++) n.push([(i + 0.5) * a, h]); return n; })();
const warrenMembers = (() => { const m = []; for (let i = 0; i < 4; i++) m.push([i, i + 1]); for (let i = 0; i < 3; i++) m.push([5 + i, 6 + i]); for (let i = 0; i < 4; i++) { m.push([i, 5 + i]); m.push([5 + i, i + 1]); } return m; })();
def('truss', {
  controls: [{ type: 'select', k: 'at', label: 'Load at node', options: ['bottom 1', 'bottom 2', 'bottom 3', 'top 5', 'top 6', 'top 7', 'top 8'], v: 'bottom 2' }, { k: 'P', label: 'Load (kN)', min: 0, max: 40, step: 1, v: 20, f: 0 }, { type: 'select', k: 'del', label: 'Delete member', options: ['none', ...warrenMembers.map(([i, j]) => `${i}-${j}`)], v: 'none' }],
  draw(p, v, out) {
    const node = +v.at.split(' ')[1], removed = v.del === 'none' ? -1 : warrenMembers.findIndex(([i, j]) => `${i}-${j}` === v.del);
    const mem = warrenMembers.filter((_, k) => k !== removed), sup = [[0, 1, 0], [0, 0, 1], [4, 0, 1]];
    const F = trussSolve(warrenNodes, mem, sup, { [node]: [0, -v.P] });
    fitAt(p, 8, 1.4, 8.8, 2.6, 'x, m', 'y, m');
    drawSupport(p, 'pin', 0, 0, 0.45); drawSupport(p, 'roller', 16, 0, 0.45);
    const full = F ? warrenMembers.map((_, k) => (k === removed ? 0 : F[k < removed || removed < 0 ? k : k - 1])) : null;
    drawTruss(p, warrenNodes, warrenMembers, full, Math.max(1, v.P), removed);
    if (v.P > 0) arrow(p, warrenNodes[node][0], warrenNodes[node][1] + 0.4 + v.P * 0.04, warrenNodes[node][0], warrenNodes[node][1] + 0.1, C.lime, 3);
    warrenNodes.forEach((q, i) => p.text(String(i), q[0] + 0.15, q[1] + (q[1] > 0 ? 0.3 : -0.45), C.grey));
    if (!full) { out(`Without member ${v.del} the truss has ${mem.length} members and 3 reactions for ${2 * warrenNodes.length} joint equations: a mechanism. The bridge collapses.`); return; }
    let big = 0; full.forEach((f, k) => { if (Math.abs(f) > Math.abs(full[big])) big = k; });
    const [bi, bj] = warrenMembers[big];
    out(`Cyan = tension, amber = compression, width ∝ force, grey = zero force. Largest: member ${bi}-${bj} at ${nf(2).format(full[big])} kN. ${removed >= 0 ? 'This member was carrying zero force for this load, so the truss stands. For other loads it would fail.' : 'Delete a member to break the load path.'}`);
  },
});

// 05.10 method of sections on a Pratt truss
const prattNodes = (() => { const n = []; for (let i = 0; i <= 6; i++) n.push([3 * i, 0]); for (let i = 1; i <= 5; i++) n.push([3 * i, 4]); return n; })();
const prattMembers = (() => { const T = (i) => 6 + i, m = []; for (let i = 0; i < 6; i++) m.push([i, i + 1]); for (let i = 1; i < 5; i++) m.push([T(i), T(i + 1)]); m.push([0, T(1)], [6, T(5)]); for (let i = 1; i < 6; i++) m.push([i, T(i)]); m.push([T(1), 2], [T(2), 3], [T(4), 3], [T(5), 4]); return m; })();
def('section', {
  controls: [{ k: 'c', label: 'Cut through panel', min: 1, max: 6, step: 1, v: 3, f: 0 }, { k: 'P', label: 'Load at each bottom node (kN)', min: 0, max: 30, step: 1, v: 12, f: 0 }],
  draw(p, v, out) {
    const loads = {}; for (let i = 1; i < 6; i++) loads[i] = [0, -v.P];
    const F = trussSolve(prattNodes, prattMembers, [[0, 1, 0], [0, 0, 1], [6, 0, 1]], loads), xc = 3 * v.c - 1.5;
    fitAt(p, 9, 1.8, 9.8, 3.2, 'x, m', 'y, m');
    drawSupport(p, 'pin', 0, 0, 0.5); drawSupport(p, 'roller', 18, 0, 0.5);
    drawTruss(p, prattNodes, prattMembers, F, Math.max(1, 3 * v.P));
    for (let i = 1; i < 6; i++) if (v.P > 0) arrow(p, 3 * i, -0.1, 3 * i, -0.4 - v.P * 0.05, C.lime, 1.5);
    p.line([xc + 0.6, xc - 0.6], [5, -1.2], C.red, 2, [6, 4]);
    const cut = prattMembers.map((mb, k) => [mb, k]).filter(([[i, j]]) => (prattNodes[i][0] - xc) * (prattNodes[j][0] - xc) < 0);
    const name = (i) => (i <= 6 ? `B${i}` : `T${i - 6}`);
    out(`The cut crosses ${cut.length} members: ${cut.map(([[i, j], k]) => `${name(i)}-${name(j)} ${nf(2).format(F[k])} kN`).join(', ')}. Each follows from equilibrium of the left part alone, e.g. the bottom chord from moments about the top node where the other two cut members meet.`);
  },
});

// 3D truss solve (3 equations per joint); supports [node, dx, dy, dz]
function truss3(nodes, members, supports, loads) {
  const n = nodes.length, m = members.length, nu = m + supports.length;
  if (3 * n !== nu) return null;
  const A = Array.from({ length: 3 * n }, () => new Array(nu).fill(0)), b = new Array(3 * n).fill(0);
  members.forEach(([i, j], k) => { const d = [0, 1, 2].map((c) => nodes[j][c] - nodes[i][c]), L = Math.hypot(...d); for (let c = 0; c < 3; c++) { A[3 * i + c][k] += d[c] / L; A[3 * j + c][k] -= d[c] / L; } });
  supports.forEach(([nd, ...d], k) => { for (let c = 0; c < 3; c++) A[3 * nd + c][m + k] += d[c]; });
  Object.entries(loads).forEach(([nd, F]) => { for (let c = 0; c < 3; c++) b[3 * nd + c] -= F[c]; });
  return linSolve(A, b);
}

// 05.11 ski-lift pylon as a space truss
def('spacetruss', {
  controls: [{ k: 'yaw', label: 'View angle (°)', min: 0, max: 360, step: 2, v: 30, f: 0 }, { k: 'wx', label: 'Wind at the top, x direction (kN)', min: -8, max: 8, step: 0.5, v: 3, f: 1 }, { k: 'G', label: 'Rope load per top joint (kN)', min: 0, max: 15, step: 0.5, v: 5, f: 1 }, { type: 'check', k: 'bad', label: 'Unbrace the front face (brace the side twice)', v: 0 }],
  draw(p, v, out) {
    const nodes = [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], [-0.5, -0.5, 6], [0.5, -0.5, 6], [0.5, 0.5, 6], [-0.5, 0.5, 6]];
    let mem = []; for (let i = 0; i < 4; i++) mem.push([i, i + 4]); for (let i = 0; i < 4; i++) mem.push([4 + i, 4 + (i + 1) % 4]); for (let i = 0; i < 4; i++) mem.push([i, 4 + (i + 1) % 4]);
    if (v.bad) mem = mem.filter(([i, j]) => !(i === 0 && j === 5)).concat([[2, 5]]);
    const sup = []; for (let i = 0; i < 4; i++) sup.push([i, 1, 0, 0], [i, 0, 1, 0], [i, 0, 0, 1]);
    const F = truss3(nodes, mem, sup, { 4: [0, 0, -v.G], 5: [0, 0, -v.G], 6: [v.wx, 0, -v.G], 7: [v.wx, 0, -v.G] });
    const a = v.yaw * Math.PI / 180, el = 0.35, P = ([x, y, z]) => { const xr = x * Math.cos(a) - y * Math.sin(a), yr = x * Math.sin(a) + y * Math.cos(a); return [xr, z * Math.cos(el) + yr * Math.sin(el) * 0.9]; };
    fitAt(p, 0, 2.6, 2.4, 3.4, '', ''); 
    const pts = nodes.map(P);
    poly(p, [0, 1, 2, 3].map((i) => pts[i]), C.rule, 'rgba(154,157,147,0.12)', 1);
    const sc = Math.max(1, ...((F || []).slice(0, mem.length).map(Math.abs)));
    mem.forEach(([i, j], k) => { const f = F ? F[k] : 0, col = !F ? C.red : Math.abs(f) < 1e-6 ? C.grey : f > 0 ? C.cyan : C.amber; p.line([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], col, F ? 1.5 + 5 * Math.abs(f) / sc : 2, F ? [] : [5, 4]); });
    p.dots(pts.map((q) => q[0]), pts.map((q) => q[1]), C.paper, 3);
    if (!F) { out(`12 members + 12 reactions = 24 = 3 × 8 joints, so Maxwell's count is satisfied, yet the equilibrium matrix has rank 23: the unbraced front face can shear sideways. Counting is necessary, not sufficient.`); return; }
    let big = 0; F.slice(0, mem.length).forEach((f, k) => { if (Math.abs(f) > Math.abs(F[big])) big = k; });
    out(`Maxwell: m + r = 12 + 12 = 3j = 24, rank 24: determinate. Cyan tension, amber compression, width ∝ force. Largest: member ${mem[big].join('-')} at ${nf(2).format(F[big])} kN. Wind sets one leg in tension and loads the face diagonals.`);
  },
});

// 05.12 bicycle rim brake: lever and arm
def('brake', {
  controls: [{ k: 'F', label: 'Finger squeeze (N)', min: 0, max: 120, step: 1, v: 60, f: 0 }, { k: 'c', label: 'Cable anchor distance on the lever (mm)', min: 15, max: 40, step: 1, v: 25, f: 0 }, { k: 'pad', label: 'Pad distance from the arm pivot (mm)', min: 30, max: 60, step: 1, v: 40, f: 0 }],
  draw(p, v, out) {
    const T = v.F * 70 / v.c, N = T * 100 / v.pad, mu = 0.6;
    p.frame({ x: [-20, 200], y: [-70, 130], xlabel: 'mm', ylabel: '', noy: true });
    // hand lever, pivot at (0, 0), horizontal to 70 mm
    p.line([0, 80], [0, 0], C.paper, 5).dots([0], [0], C.grey, 6);
    arrow(p, 70, 8 + v.F * 0.45, 70, 4, C.lime, 3); p.text('finger', 74, 30, C.lime);
    arrow(p, v.c, -4, v.c, -4 - T * 0.12, C.cyan, 2.5); p.text('cable', v.c + 4, -40, C.cyan);
    // brake arm, pivot at (150, -60), vertical to 100 mm above
    const ax = 150, ay = -60; p.line([ax, ax], [ay, ay + 110], C.paper, 5).dots([ax], [ay], C.grey, 6);
    arrow(p, ax + 4, ay + 100, ax + 4 + T * 0.12, ay + 100, C.cyan, 2.5);
    p.rect(ax - 14, ax - 4, ay + v.pad - 7, ay + v.pad + 7, 'rgba(255,170,60,0.85)');
    arrow(p, ax - 16, ay + v.pad, ax - 16 - N * 0.05, ay + v.pad, C.amber, 3); p.text('pad', ax - 40, ay + v.pad + 12, C.amber);
    out(`Lever ratio 70/${v.c} = ${nf(2).format(70 / v.c)} gives cable tension ${nf(1).format(T)} N. Arm ratio 100/${v.pad} = ${nf(2).format(100 / v.pad)} gives pad force ${nf(1).format(N)} N. Overall mechanical advantage ${nf(2).format(N / Math.max(v.F, 1e-9))}, the product of the arm ratios. Two pads with μ = ${mu}: ${nf(0).format(2 * mu * N)} N of friction on the rim.`);
  },
});

// 05.13 live shear and moment diagrams
def('vmdiag', {
  controls: [{ k: 'a', label: 'Point load position (m)', min: 0, max: 6, step: 0.1, v: 3, f: 1 }, { k: 'P', label: 'Point load P (kN)', min: 0, max: 40, step: 1, v: 30, f: 0 }, { k: 'q', label: 'Uniform load q (kN/m)', min: 0, max: 10, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const L = 6, Rb = (v.P * v.a + v.q * L * L / 2) / L, Ra = v.P + v.q * L - Rb, xs = linspace(0, L, 601);
    const V = xs.map((x) => Ra - v.q * x - (x > v.a ? v.P : 0)), M = xs.map((x) => Ra * x - v.q * x * x / 2 - v.P * Math.max(0, x - v.a));
    const Vs = Math.max(1, ...V.map(Math.abs)), Ms = Math.max(1, ...M.map(Math.abs));
    p.frame({ x: [-0.3, 6.3], y: [-3.3, 1.5], xlabel: 'x, m', ylabel: '', noy: true });
    // beam and loads
    p.line([0, L], [0.9, 0.9], C.paper, 4); drawSupport(p, 'pin', 0, 0.86, 0.12); drawSupport(p, 'roller', L, 0.86, 0.12);
    if (v.P > 0) arrow(p, v.a, 1.45, v.a, 0.95, C.amber, 2.5);
    if (v.q > 0) for (let x = 0; x <= L + 1e-9; x += 0.5) arrow(p, x, 1.2, x, 0.96, C.cyan, 1);
    // V band centred at -0.35, M band baseline at -2.0 (positive moment drawn downward, the sagging side)
    p.line([0, L], [-0.35, -0.35], C.rule, 1).line([0, L], [-2.0, -2.0], C.rule, 1);
    p.line([0, ...xs, L], [-0.35, ...V.map((y) => -0.35 + 0.6 * y / Vs), -0.35], C.cyan, 2);
    p.line([0, ...xs, L], [-2.0, ...M.map((y) => -2.0 - 1.15 * y / Ms), -2.0], C.lime, 2);
    let k = 0; M.forEach((m, i) => { if (m > M[k]) k = i; });
    p.dots([xs[k]], [-2.0 - 1.15 * M[k] / Ms], C.lime, 4);
    p.text('V', -0.25, -0.2, C.cyan).text('M', -0.25, -1.85, C.lime);
    out(`Reactions ${nf(2).format(Ra)} and ${nf(2).format(Rb)} kN. Shear V (cyan) jumps by P under the load and slopes at −q. Moment M (lime, drawn on the sagging side) peaks at ${nf(2).format(M[k])} kN m at x = ${nf(2).format(xs[k])} m, where V crosses zero. Central load alone: PL/4 = ${nf(1).format(v.P * L / 4)} kN m.`);
  },
});

// 05.14 cable car track rope: catenary vs parabola
function catA(S, L) { let lo = S / 500, hi = S * 1000; const f = (a) => 2 * a * Math.sinh(S / (2 * a)) - L; for (let i = 0; i < 200; i++) { const m = 0.5 * (lo + hi); if (f(m) > 0) lo = m; else hi = m; } return 0.5 * (lo + hi); }
def('catenary', {
  controls: [{ k: 'ex', label: 'Rope length beyond the span (%)', min: 0.2, max: 40, step: 0.1, v: 1, f: 1 }, { k: 'w', label: 'Rope mass (kg/m)', min: 5, max: 60, step: 1, v: 30, f: 0 }],
  draw(p, v, out) {
    const S = 400, L = S * (1 + v.ex / 100), a = catA(S, L), w = v.w * 9.81 / 1000, sag = a * (Math.cosh(S / (2 * a)) - 1), H = w * a, T = H + w * sag;
    const d = Math.sqrt(3 * S * (L - S) / 8), xs = linspace(-S / 2, S / 2, 201);
    const top = 30, low = Math.min(top - sag, top - d);
    p.frame({ x: [-220, 220], y: [Math.min(-10, low - 15), top + 20], xlabel: 'x, m', ylabel: 'height, m' });
    p.line([-S / 2, -S / 2], [-200, top], C.grey, 4).line([S / 2, S / 2], [-200, top], C.grey, 4);
    p.line(xs, xs.map((x) => top - d + 4 * d * x * x / (S * S)), C.amber, 1.5, [5, 4]);
    p.line(xs, xs.map((x) => top - sag + a * (Math.cosh(x / a) - 1)), C.lime, 2.5);
    out(`Catenary (lime): a = ${nf(1).format(a)} m, sag ${nf(2).format(sag)} m, horizontal tension ${nf(1).format(H)} kN, ${nf(1).format(T)} kN at the towers. Parabola (amber dashed) sag ${nf(2).format(d)} m, ${nf(1).format((d / sag - 1) * 100)} % off. Tight ropes: almost identical. Slack: the parabola fails.`);
  },
});

// 05.15 crate on a tilting ramp: slide or tip
def('ramp', {
  controls: [{ k: 'th', label: 'Ramp angle θ (°)', min: 0, max: 45, step: 0.5, v: 15, f: 1 }, { k: 'mu', label: 'Friction coefficient μ', min: 0.1, max: 0.9, step: 0.01, v: 0.3, f: 2 }, { k: 'h', label: 'Crate height (m), width 0.6 m', min: 0.3, max: 2, step: 0.05, v: 1.2, f: 2 }],
  draw(p, v, out) {
    const th = v.th * Math.PI / 180, b = 0.6, h = v.h, t = Math.tan(th), slide = t > v.mu, tip = t > b / h;
    const state = slide && tip ? (v.mu < b / h ? 'slides' : 'tips') : slide ? 'slides' : tip ? 'tips' : 'stays';
    sqAt(p, 1.2, 0.9, 1.3, 'm', 'm');
    const R = (x, y) => [x * Math.cos(th) - y * Math.sin(th), x * Math.sin(th) + y * Math.cos(th)];
    poly(p, [R(-0.3, 0), R(2.8, 0), [R(2.8, 0)[0], 0], [-0.3, 0]], C.grey, 'rgba(154,157,147,0.15)');
    const x0 = 1.0, crate = [[x0, 0], [x0 + b, 0], [x0 + b, h], [x0, h]].map(([x, y]) => R(x, y));
    poly(p, crate, state === 'stays' ? C.paper : C.red, state === 'stays' ? 'rgba(242,243,236,0.1)' : 'rgba(255,90,90,0.15)', 2);
    const G = R(x0 + b / 2, h / 2); p.dots([G[0]], [G[1]], C.lime, 4);
    p.line([G[0], G[0]], [G[1], G[1] - 1.5], C.lime, 1.5, [4, 3]);
    const edge = R(x0, 0); p.dots([edge[0]], [edge[1]], C.amber, 4);
    const crit = Math.atan(Math.min(v.mu, b / h)) * 180 / Math.PI;
    out(`tan θ = ${nf(3).format(t)}, μ = ${nf(2).format(v.mu)}, b/h = ${nf(3).format(b / h)}. The crate ${state === 'stays' ? 'stays put' : state === 'slides' ? 'slides (tan θ > μ)' : 'tips over the lower edge (the weight line, dashed, passes the amber corner)'}. While tilting from flat it would first ${v.mu < b / h ? 'slide' : 'tip'} at ${nf(2).format(crit)}°.`);
  },
});

// 05.16 rope round a bollard: exponential in the wrap angle
def('bollard', {
  controls: [{ k: 't', label: 'Wrap (turns)', min: 0, max: 4, step: 0.05, v: 1.5, f: 2 }, { k: 'mu', label: 'Friction μ', min: 0.1, max: 0.6, step: 0.01, v: 0.3, f: 2 }],
  draw(p, v, out) {
    const r = Math.exp(v.mu * 2 * Math.PI * v.t), xs = linspace(0, 4, 161);
    p.frame({ x: [0, 4], y: [1, 1e6], ylog: true, xlabel: 'wrap, turns', ylabel: 'holding ratio T₂/T₁' });
    p.line(xs, xs.map((t) => Math.exp(v.mu * 2 * Math.PI * t)), C.lime, 2).dots([v.t], [r], C.amber, 5);
    [0.1, 0.3, 0.6].forEach((m) => { if (Math.abs(m - v.mu) > 0.02) p.line(xs, xs.map((t) => Math.exp(m * 2 * Math.PI * t)), C.rule, 1, [4, 4]); });
    out(`T₂/T₁ = e^(μβ) = e^(${nf(2).format(v.mu)} · ${nf(2).format(2 * Math.PI * v.t)}) = ${r < 1e4 ? nf(2).format(r) : r.toExponential(2)}. A deckhand holding 200 N controls ${r * 0.2 < 1e4 ? nf(1).format(r * 0.2) : (r * 0.2).toExponential(2)} kN. A straight line on the log scale: each extra turn multiplies the ratio by e^(2πμ) = ${nf(2).format(Math.exp(2 * Math.PI * v.mu))}.`);
  },
});

// 05.17 composite centroid
def('composite', {
  controls: [{ type: 'check', k: 'blk', label: 'Add a 100 × 120 mm block on top', v: 1 }, { k: 'bx', label: 'Block position x (mm)', min: 0, max: 200, step: 5, v: 200, f: 0 }, { k: 'd', label: 'Hole diameter (mm)', min: 0, max: 140, step: 5, v: 80, f: 0 }, { k: 'hx', label: 'Hole centre x (mm)', min: 70, max: 230, step: 5, v: 90, f: 0 }],
  draw(p, v, out) {
    const parts = [[300 * 200, 150, 100]];
    if (v.blk) parts.push([100 * 120, v.bx + 50, 260]);
    const ah = Math.PI * v.d * v.d / 4; if (v.d > 0) parts.push([-ah, v.hx, 100]);
    const A = parts.reduce((s, q) => s + q[0], 0), xb = parts.reduce((s, q) => s + q[0] * q[1], 0) / A, yb = parts.reduce((s, q) => s + q[0] * q[2], 0) / A;
    fitAt(p, 150, 160, 170, 170, 'x, mm', 'y, mm');
    poly(p, [[0, 0], [300, 0], [300, 200], [0, 200]], C.grey, 'rgba(154,157,147,0.2)');
    if (v.blk) poly(p, [[v.bx, 200], [v.bx + 100, 200], [v.bx + 100, 320], [v.bx, 320]], C.grey, 'rgba(154,157,147,0.2)');
    if (v.d > 0) { const t = linspace(0, 2 * Math.PI, 73); poly(p, t.map((a) => [v.hx + v.d / 2 * Math.cos(a), 100 + v.d / 2 * Math.sin(a)]), C.red, 'rgba(10,10,10,0.9)'); }
    p.line([xb - 14, xb + 14], [yb, yb], C.lime, 2).line([xb, xb], [yb - 14, yb + 14], C.lime, 2).dots([xb], [yb], C.lime, 3);
    out(`A = ${nf(0).format(A)} mm², centroid (${nf(1).format(xb)}, ${nf(1).format(yb)}) mm: Σ Aᵢxᵢ / Σ Aᵢ with the hole counted as negative area. Added material pulls the centroid towards it; a hole pushes it away.`);
  },
});

// 05.18 water pressure on a dam
def('dam', {
  controls: [{ k: 'h', label: 'Reservoir level (m)', min: 0, max: 60, step: 0.5, v: 45, f: 1 }],
  draw(p, v, out) {
    const H = 60, h = v.h, F = 1000 * 9.81 * h * h / 2 / 1e6;
    fitAt(p, 15, 32, 50, 34, 'x, m', 'height, m');
    poly(p, [[0, 0], [0, 64], [6, 64], [45, 0]], C.grey, 'rgba(154,157,147,0.25)');
    if (h > 0) {
      poly(p, [[-60, 0], [0, 0], [0, h], [-60, h]], C.cyan, 'rgba(92,200,255,0.18)', 1);
      const s = 30 / (1000 * 9.81 * H);   // pressure diagram, 30 m wide at full depth
      poly(p, [[0, h], [0, 0], [-1000 * 9.81 * h * s, 0]], C.amber, 'rgba(255,170,60,0.2)', 1.5);
      for (let y = 0; y < h - 1e-9; y += Math.max(3, h / 8)) arrow(p, -1000 * 9.81 * (h - y) * s, y, -0.4, y, C.amber, 1);
      arrow(p, -26, h / 3, -0.3, h / 3, C.lime, 3.5);
      p.text(`F = ${nf(1).format(F)} MN/m`, -25, h / 3 + 3, C.lime);
    }
    out(`Pressure grows linearly with depth, p = ρgh = ${nf(0).format(9.81 * h)} kPa at the base. Resultant per metre of dam: ρgh²/2 = ${nf(2).format(F)} MN, acting h/3 = ${nf(1).format(h / 3)} m above the base (2h/3 below the surface). Overturning moment ${nf(0).format(F * h / 3)} MN m per metre: it grows with h³.`);
  },
});

// 05.19 scissor lift: virtual work
def('scissor', {
  controls: [{ k: 'th', label: 'Link angle θ (°)', min: 8, max: 75, step: 1, v: 35, f: 0 }, { type: 'select', k: 'n', label: 'Stages', options: ['1', '2', '3', '4'], v: '2' }, { k: 'W', label: 'Platform load W (kN)', min: 0, max: 10, step: 0.5, v: 4, f: 1 }],
  draw(p, v, out) {
    const n = +v.n, L = 1.2, th = v.th * Math.PI / 180, c = L * Math.cos(th), s = L * Math.sin(th), P = n * v.W / Math.tan(th), ytop = n * s;
    fitAt(p, 0.6, ytop / 2 + 0.25, 1.0, Math.max(0.9, ytop / 2 + 0.6), 'x, m', 'y, m');
    p.line([-0.3, 1.5], [0, 0], C.grey, 2);
    for (let i = 0; i < n; i++) { p.line([0, c], [i * s, (i + 1) * s], C.paper, 3).line([c, 0], [i * s, (i + 1) * s], C.paper, 3); p.dots([c / 2], [(i + 0.5) * s], C.grey, 3); }
    p.rect(-0.1, c + 0.15, ytop, ytop + 0.08, 'rgba(242,243,236,0.35)');
    if (v.W > 0) arrow(p, c / 2, ytop + 0.5, c / 2, ytop + 0.1, C.lime, 3);
    p.dots([0, c], [0, 0], C.paper, 4);
    arrow(p, c + 0.4, 0.06, c + 0.02, 0.06, C.amber, 3);
    out(`Height y = n L sin θ = ${nf(2).format(ytop)} m, actuator span x = L cos θ = ${nf(2).format(c)} m. Virtual work: W δy = P δx, so P = n W cot θ = ${nf(2).format(P)} kN. Fold the lift (small θ) or add stages and the actuator force soars.`);
  },
});

// 05.20 energy landscape of a hinged bar with a rotational spring
def('energy', {
  controls: [{ k: 'P', label: 'Load P on top of the bar (kN)', min: 0, max: 20, step: 0.1, v: 8, f: 1 }],
  draw(p, v, out) {
    const k = 20, L = 2, Vf = (t) => 0.5 * k * t * t + v.P * L * Math.cos(t), ts = linspace(-2.2, 2.2, 441);
    const Vs = ts.map(Vf), lo = Math.min(...Vs), hi = Math.max(...Vs);
    p.frame({ x: [-2.2, 2.2], y: [lo - 0.08 * (hi - lo) - 0.5, hi + 0.08 * (hi - lo) + 0.5], xlabel: 'lean angle θ, rad', ylabel: 'V(θ), kJ' });
    p.line(ts, Vs, C.cyan, 2);
    const eq = [0]; if (v.P * L > k) { let a = 1e-9, b = Math.PI - 1e-9; for (let i = 0; i < 100; i++) { const m = 0.5 * (a + b); if (k * m - v.P * L * Math.sin(m) < 0) a = m; else b = m; } eq.push(a, -a); }
    eq.forEach((t) => { const st = k - v.P * L * Math.cos(t) > 0; p.dots([t], [Vf(t)], st ? C.lime : C.red, 6); });
    const ball = eq.length > 1 ? eq[1] : 0; p.dots([ball], [Vf(ball) + 0.03 * (hi - lo) + 0.25], C.amber, 7);
    const c0 = k - v.P * L;
    out(`P_cr = k/L = 10 kN. At θ = 0, V'' = k − PL = ${nf(1).format(c0)} kN m: ${c0 > 0 ? 'a valley, so upright is stable.' : c0 < 0 ? `a hilltop, so upright is unstable and the bar settles at θ = ±${nf(1).format(eq[1] * 180 / Math.PI)}° (lime valleys).` : 'flat: the critical load, neutral equilibrium.'} Lime dots are stable, red unstable; the ball rests in a valley.`);
  },
});

// 06.01 traction on a rotating plane
def('traction', {
  controls: [{ k: 'sx', label: 'σx (MPa)', min: -100, max: 100, step: 1, v: 60, f: 0 }, { k: 'sy', label: 'σy (MPa)', min: -100, max: 100, step: 1, v: 0, f: 0 }, { k: 't', label: 'τxy (MPa)', min: -60, max: 60, step: 1, v: 25, f: 0 }, { k: 'ph', label: 'Plane normal angle φ (°)', min: 0, max: 180, step: 1, v: 30, f: 0 }],
  draw(p, v, out) {
    const ph = v.ph * Math.PI / 180, n = [Math.cos(ph), Math.sin(ph)], m = [-n[1], n[0]];
    const t = [v.sx * n[0] + v.t * n[1], v.t * n[0] + v.sy * n[1]], sn = t[0] * n[0] + t[1] * n[1], ts = t[0] * m[0] + t[1] * m[1];
    sqAt(p, 0, 0, 1.6, '', '');
    poly(p, [[-0.6, -0.6], [0.6, -0.6], [0.6, 0.6], [-0.6, 0.6]], C.rule, 'rgba(154,157,147,0.1)', 1);
    p.line([-1.3 * m[0], 1.3 * m[0]], [-1.3 * m[1], 1.3 * m[1]], C.paper, 2);
    arrow(p, 0, 0, 0.5 * n[0], 0.5 * n[1], C.grey, 1.5); p.text('n', 0.58 * n[0], 0.58 * n[1], C.grey);
    const s = 0.016; arrow(p, 0, 0, t[0] * s, t[1] * s, C.lime, 3);
    arrow(p, 0, 0, sn * n[0] * s, sn * n[1] * s, C.cyan, 1.5); arrow(p, sn * n[0] * s, sn * n[1] * s, t[0] * s, t[1] * s, C.amber, 1.5);
    out(`Traction t = σn = (${nf(1).format(t[0])}, ${nf(1).format(t[1])}) MPa (lime). Normal part σn = ${nf(2).format(sn)} MPa (cyan), shear part τ = ${nf(2).format(ts)} MPa (amber). Rotate the plane: the normal stress peaks at the largest principal stress.`);
  },
});

// 06.02 deforming grid and small strain
def('straingrid', {
  controls: [{ k: 'ex', label: 'Stretch εxx (%)', min: -20, max: 20, step: 0.5, v: 10, f: 1 }, { k: 'ey', label: 'Stretch εyy (%)', min: -20, max: 20, step: 0.5, v: -3, f: 1 }, { k: 'g', label: 'Shear γxy (%)', min: -40, max: 40, step: 1, v: 10, f: 0 }, { k: 'th', label: 'Rigid rotation (°)', min: -45, max: 45, step: 1, v: 0, f: 0 }],
  draw(p, v, out) {
    const exx = v.ex / 100, eyy = v.ey / 100, exy = v.g / 200, th = v.th * Math.PI / 180, c = Math.cos(th), s = Math.sin(th);
    const F = (x, y) => { const X = x + exx * x + exy * y, Y = y + exy * x + eyy * y; return [c * X - s * Y, s * X + c * Y]; };
    sqAt(p, 0, 0, 1.5, 'x', 'y');
    for (let i = -4; i <= 4; i++) { const k = i / 4; p.line([-1, 1], [k, k], C.rule, 1).line([k, k], [-1, 1], C.rule, 1); }
    for (let i = -4; i <= 4; i++) { const k = i / 4, a = linspace(-1, 1, 9); const r = a.map((x) => F(x, k)), q = a.map((y) => F(k, y)); p.line(r.map((z) => z[0]), r.map((z) => z[1]), C.cyan, 1.5).line(q.map((z) => z[0]), q.map((z) => z[1]), C.cyan, 1.5); }
    // small strain of the total displacement u = F(x) - x
    const H = [[(1 + exx) * c - exy * s - 1, exy * c - (1 + eyy) * s], [(1 + exx) * s + exy * c, exy * s + (1 + eyy) * c - 1]];
    const sxx = H[0][0], syy = H[1][1], sxy = 0.5 * (H[0][1] + H[1][0]);
    out(`Small strain of the displacement: εxx = ${nf(4).format(sxx)}, εyy = ${nf(4).format(syy)}, εxy = ${nf(4).format(sxy)}. ${Math.abs(v.th) > 0 ? `The rotation of ${v.th}° adds a false strain of about θ²/2 = ${nf(4).format(th * th / 2)} on the diagonal: small strain is only valid for small rotations.` : 'With no rotation, these are exactly the strains you set.'}`);
  },
});

// 06.03 stress-strain lines and Poisson contraction
def('hooke', {
  controls: [{ type: 'select', k: 'm', label: 'Material', options: ['steel', 'aluminium', 'bamboo'], v: 'steel' }, { k: 's', label: 'Applied stress σ (MPa)', min: 0, max: 400, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const M = { steel: [210e3, 0.3, 355, C.lime], aluminium: [70e3, 0.33, 275, C.cyan], bamboo: [18e3, 0.3, 150, C.amber] };
    p.frame({ x: [0, 1], y: [0, 400], xlabel: 'strain ε, %', ylabel: 'stress σ, MPa' });
    Object.entries(M).forEach(([k, [E, , fy, col]]) => { const ey = fy / E * 100; p.line([0, Math.min(1, ey)], [0, Math.min(1, ey) / 100 * E], col, k === v.m ? 3 : 1.5).line([Math.min(1, ey), 1], [fy, fy], col, 1, [4, 4]); });
    const [E, nu, fy] = M[v.m], s = Math.min(v.s, fy), e = s / E;
    p.dots([e * 100], [s], C.paper, 5);
    out(`${v.m}: E = ${nf(0).format(E / 1e3)} GPa, ν = ${nu}. At ${nf(0).format(s)} MPa the strain is ${nf(3).format(e * 100)} % and the bar narrows by ${nf(4).format(nu * e * 100)} %. ${v.s > fy ? `Above about ${fy} MPa it yields (dashed, idealised): Hooke's law no longer holds.` : 'Linear and reversible.'}${v.m === 'bamboo' ? ' Bamboo values are along the fibres; across them it is far softer.' : ''}`);
  },
});

// 06.04 stepped bar stretch
def('axialbar', {
  controls: [{ k: 'P', label: 'End load P (kN)', min: -60, max: 60, step: 1, v: 30, f: 0 }, { k: 'd2', label: 'Aluminium part diameter (mm)', min: 15, max: 45, step: 1, v: 30, f: 0 }, { k: 'x', label: 'Exaggeration of the stretch (×)', min: 100, max: 2000, step: 50, v: 500, f: 0 }],
  draw(p, v, out) {
    const As = Math.PI * 100, Aa = Math.PI * v.d2 * v.d2 / 4, P = v.P * 1e3;
    const d1 = P * 400 / (210e3 * As), d2 = P * 300 / (70e3 * Aa), k = v.x;
    p.frame({ x: [-50, 1060], y: [-60, 60], xlabel: 'x, mm', ylabel: '', noy: true });
    p.rect(-40, 0, -50, 50, 'rgba(154,157,147,0.4)');
    const e1 = 400 + d1 * k, e2 = e1 + 300 + d2 * k;
    p.rect(0, e1, -10, 10, 'rgba(184,255,92,0.5)').rect(e1, e2, -v.d2 / 2, v.d2 / 2, 'rgba(92,200,255,0.5)');
    p.line([400, 400], [-45, 45], C.grey, 1, [3, 3]).line([700, 700], [-45, 45], C.grey, 1, [3, 3]);
    if (v.P !== 0) arrow(p, e2 + (v.P > 0 ? 5 : 120), 0, e2 + (v.P > 0 ? 120 : 5), 0, C.amber, 3);
    out(`Steel 400 mm × Ø20 stretches ${nf(4).format(d1)} mm (σ = ${nf(1).format(P / As)} MPa); aluminium 300 mm × Ø${v.d2} stretches ${nf(4).format(d2)} mm (σ = ${nf(1).format(P / Aa)} MPa). Total δ = ΣNL/(EA) = ${nf(4).format(d1 + d2)} mm, drawn ${k}× larger. Dashed lines: unloaded joint and end.`);
  },
});

// 06.05 bar between two walls
def('fixedbar', {
  controls: [{ k: 'a', label: 'Load position from wall A (mm)', min: 50, max: 950, step: 10, v: 300, f: 0 }, { k: 'P', label: 'Load P (kN)', min: 0, max: 100, step: 1, v: 60, f: 0 }, { type: 'select', k: 'm', label: 'Part to the right of the load', options: ['same as the left', 'aluminium, 1.5× the area', 'half the area'], v: 'same as the left' }],
  draw(p, v, out) {
    const L = 1000, EA1 = 210e3 * 400, EA2 = v.m === 'same as the left' ? EA1 : v.m === 'half the area' ? EA1 / 2 : 70e3 * 600;
    const f1 = v.a / EA1, f2 = (L - v.a) / EA2, RA = v.P * f2 / (f1 + f2), RB = v.P - RA;
    p.frame({ x: [-80, 1080], y: [-1.6, 1.3], xlabel: 'x, mm', ylabel: '', noy: true });
    p.rect(-60, 0, -0.5, 1.2, 'rgba(154,157,147,0.4)').rect(L, L + 60, -0.5, 1.2, 'rgba(154,157,147,0.4)');
    p.rect(0, v.a, 0.25, 0.45, 'rgba(184,255,92,0.5)').rect(v.a, L, EA2 === EA1 ? 0.25 : EA2 > EA1 * 0.6 && v.m.startsWith('al') ? 0.2 : 0.3, EA2 === EA1 ? 0.45 : v.m.startsWith('al') ? 0.5 : 0.4, v.m.startsWith('al') ? 'rgba(92,200,255,0.5)' : 'rgba(184,255,92,0.5)');
    if (v.P > 0) arrow(p, v.a - 120, 0.85, v.a, 0.85, C.amber, 3);
    // axial force diagram: +RA tension left of the load, -RB compression right of it
    const sc = 0.9 / Math.max(1, v.P);
    p.line([0, L], [-0.6, -0.6], C.rule, 1);
    p.rect(0, v.a, -0.6, -0.6 + RA * sc, 'rgba(92,200,255,0.35)').rect(v.a, L, -0.6, -0.6 - RB * sc, 'rgba(255,170,60,0.35)');
    p.text(`N = +${nf(1).format(RA)} kN`, 10, -0.5 + RA * sc * 0.5, C.cyan).text(`−${nf(1).format(RB)} kN`, v.a + 10, -0.75 - RB * sc * 0.5, C.amber);
    out(`Equilibrium RA + RB = P, compatibility (total stretch zero) RA·a/EA₁ = RB·b/EA₂. RA = ${nf(2).format(RA)} kN, RB = ${nf(2).format(RB)} kN, sum ${nf(2).format(RA + RB)} kN. The stiffer, shorter side takes more of the load.`);
  },
});

// diverging colour: -1 cyan (compression) .. 0 dark .. +1 amber (tension)
function divCol(t) { t = Math.max(-1, Math.min(1, t)); const a = Math.abs(t); const [r, g, b] = t < 0 ? [92, 200, 255] : [255, 170, 60]; return `rgba(${r},${g},${b},${0.08 + 0.85 * a})`; }

// 06.06 continuous welded rail on a hot or cold day
def('railtemp', {
  controls: [{ k: 'T', label: 'Rail temperature (°C)', min: -30, max: 65, step: 1, v: 55, f: 0 }, { k: 'Tn', label: 'Stress-free (neutral) temperature (°C)', min: 10, max: 35, step: 1, v: 25, f: 0 }],
  draw(p, v, out) {
    const E = 210e3, a = 11.5e-6, A = 7686, s = (T) => -E * a * (T - v.Tn), sig = s(v.T), F = sig * A / 1e3, risk = v.T - v.Tn >= 30;
    p.frame({ x: [-30, 65], y: [-120, 160], xlabel: 'rail temperature, °C', ylabel: 'stress, MPa (+ tension)' });
    p.rect(v.Tn + 30, 65, -120, 160, 'rgba(255,90,90,0.12)');
    p.line([-30, 65], [s(-30), s(65)], C.lime, 2).line([-30, 65], [0, 0], C.grey, 1).dots([v.T], [sig], risk ? C.red : C.amber, 6);
    p.text('buckling risk', 64, 140, C.red, 'right');
    out(`σ = −Eα(T − T₀) = ${nf(1).format(sig)} MPa, a rail force of ${nf(0).format(Math.abs(F))} kN in ${sig < 0 ? 'compression' : 'tension'}. ${risk ? 'More than 30 K above neutral: the track can buckle sideways unless the ballast holds it. Track engineers lay rail at a high neutral temperature for this reason.' : sig > 0 ? 'Cold rail pulls in tension: the risk is a broken weld, not buckling.' : 'Within the normal range.'}`);
  },
});

// 06.07 Mohr's circle
def('mohr', {
  controls: [{ k: 'sx', label: 'σx (MPa)', min: -100, max: 100, step: 1, v: 80, f: 0 }, { k: 'sy', label: 'σy (MPa)', min: -100, max: 100, step: 1, v: -20, f: 0 }, { k: 't', label: 'τxy (MPa)', min: -60, max: 60, step: 1, v: 30, f: 0 }, { k: 'th', label: 'Element rotation θ (°)', min: 0, max: 180, step: 1, v: 0, f: 0 }],
  draw(p, v, out) {
    const C0 = (v.sx + v.sy) / 2, d = (v.sx - v.sy) / 2, R = Math.hypot(d, v.t), th = v.th * Math.PI / 180, c2 = Math.cos(2 * th), s2 = Math.sin(2 * th);
    const a = C0 + d * c2 + v.t * s2, b = C0 - d * c2 - v.t * s2, tt = -d * s2 + v.t * c2;
    sqAt(p, C0, 0, Math.max(30, R * 1.25), 'σ, MPa', 'τ, MPa (down positive)');
    const ang = linspace(0, 2 * Math.PI, 145); p.line(ang.map((q) => C0 + R * Math.cos(q)), ang.map((q) => R * Math.sin(q)), C.cyan, 2);
    p.line([C0 - R * 1.3, C0 + R * 1.3], [0, 0], C.grey, 1);
    // plot tau downward-positive so the rotation sense on the circle matches the element (2θ counter-clockwise)
    p.line([a, b], [-tt, tt], C.paper, 1.5).dots([a], [-tt], C.lime, 6).dots([b], [tt], C.amber, 5).dots([C0 + R, C0 - R], [0, 0], C.paper, 4);
    const tp = 0.5 * Math.atan2(2 * v.t, v.sx - v.sy) * 180 / Math.PI;
    out(`Centre ${nf(1).format(C0)}, radius ${nf(2).format(R)} MPa. σ₁ = ${nf(2).format(C0 + R)}, σ₂ = ${nf(2).format(C0 - R)} MPa at θp = ${nf(1).format(tp)}°. Rotated face x′ (lime): σ = ${nf(2).format(a)}, τ = ${nf(2).format(tt)} MPa. Turning the element by θ moves the point 2θ round the circle.`);
  },
});

// 06.08 yield surfaces in the σ1-σ2 plane
def('yieldsurf', {
  controls: [{ k: 's', label: 'Bending stress σ (MPa)', min: -300, max: 300, step: 5, v: 120, f: 0 }, { k: 't', label: 'Torsional shear τ (MPa)', min: 0, max: 250, step: 5, v: 70, f: 0 }],
  draw(p, v, out) {
    const fy = 355, C0 = v.s / 2, R = Math.hypot(v.s / 2, v.t), s1 = C0 + R, s2 = C0 - R;
    sqAt(p, 0, 0, 470, 'σ₁, MPa', 'σ₂, MPa');
    const ang = linspace(0, 2 * Math.PI, 241);
    // von Mises ellipse s1^2 - s1 s2 + s2^2 = fy^2, parametrised along its axes
    p.line(ang.map((q) => fy * Math.sqrt(2) * (Math.cos(q) / Math.sqrt(2) - Math.sin(q) / Math.sqrt(6))), ang.map((q) => fy * Math.sqrt(2) * (Math.cos(q) / Math.sqrt(2) + Math.sin(q) / Math.sqrt(6))), C.cyan, 2);
    poly(p, [[fy, 0], [fy, fy], [0, fy], [-fy, 0], [-fy, -fy], [0, -fy]], C.amber, null, 1.5);
    p.line([-470, 470], [0, 0], C.rule, 1).line([0, 0], [-470, 470], C.rule, 1);
    const vm = Math.sqrt(v.s * v.s + 3 * v.t * v.t), tr = Math.sqrt(v.s * v.s + 4 * v.t * v.t);
    p.dots([s1], [s2], vm > fy ? C.red : C.lime, 6);
    out(`Principal stresses σ₁ = ${nf(1).format(s1)}, σ₂ = ${nf(1).format(s2)} MPa. von Mises √(σ² + 3τ²) = ${nf(1).format(vm)} MPa (cyan ellipse), Tresca √(σ² + 4τ²) = ${nf(1).format(tr)} MPa (amber hexagon), against fy = 355 MPa for S355. Safety factor ${nf(2).format(fy / vm)} (von Mises). ${vm > fy ? 'Outside the ellipse: it yields.' : 'Inside both: elastic.'}`);
  },
});

// 06.09 cantilever bending stress map
def('bendstress', {
  controls: [{ k: 'a', label: 'Load position from the wall (m)', min: 0.2, max: 2, step: 0.05, v: 2, f: 2 }, { k: 'P', label: 'Load P (kN)', min: -10, max: 10, step: 0.5, v: 5, f: 1 }],
  draw(p, v, out) {
    const L = 2, b = 0.08, h = 0.2, I = b * h ** 3 / 12, nx = 60, ny = 12;
    const M = (x) => (x < v.a ? -v.P * (v.a - x) : 0);       // kN m, hogging negative for a downward load
    fitAt(p, 1.0, 0, 1.15, 0.5, 'x, m', 'y, m');
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
      const x = (i + 0.5) * L / nx, y = -h / 2 + (j + 0.5) * h / ny, s = -M(x) * 1e3 * y / I / 1e6;   // MPa
      p.rect(i * L / nx, (i + 1) * L / nx, 2 * (-h / 2 + j * h / ny), 2 * (-h / 2 + (j + 1) * h / ny), divCol(s / 37.5));
    }
    p.rect(-0.08, 0, -0.35, 0.35, 'rgba(154,157,147,0.5)');
    if (v.P !== 0) arrow(p, v.a, v.P > 0 ? 0.55 : -0.55, v.a, v.P > 0 ? 0.22 : -0.22, C.lime, 3);
    const Mw = Math.abs(M(0)), sw = Mw * 1e3 * (h / 2) / I / 1e6;
    out(`80 × 200 mm section (depth drawn 2× larger), I = ${nf(2).format(I * 1e12 / 1e6)}×10⁶ mm⁴. Wall moment ${nf(2).format(Mw)} kN m, so σmax = Mc/I = ${nf(2).format(sw)} MPa at the top and bottom fibres. Amber tension, cyan compression; the neutral axis in the middle carries nothing.`);
  },
});

// 06.10 sections at equal area
def('sectioncmp', {
  controls: [{ type: 'select', k: 's', label: 'Section (all 2725 mm²)', options: ['square', 'round bar', 'tube 100 mm', 'I-section 200 mm', 'flat plate on edge 10 mm'], v: 'I-section 200 mm' }],
  draw(p, v, out) {
    const A = 2724.8, sq = Math.sqrt(A), Dr = Math.sqrt(4 * A / Math.PI), di = Math.sqrt(1e4 - 4 * A / Math.PI);
    const I = { square: sq ** 4 / 12, 'round bar': Math.PI * Dr ** 4 / 64, 'tube 100 mm': Math.PI * (1e8 - di ** 4) / 64, 'I-section 200 mm': 1.8456e7, 'flat plate on edge 10 mm': 10 * (A / 10) ** 3 / 12 };
    sqAt(p, 0, 0, 160, 'mm', 'mm');
    const ang = linspace(0, 2 * Math.PI, 97), fill = 'rgba(184,255,92,0.35)';
    if (v.s === 'square') poly(p, [[-sq / 2, -sq / 2], [sq / 2, -sq / 2], [sq / 2, sq / 2], [-sq / 2, sq / 2]], C.lime, fill);
    if (v.s === 'round bar') poly(p, ang.map((q) => [Dr / 2 * Math.cos(q), Dr / 2 * Math.sin(q)]), C.lime, fill);
    if (v.s === 'tube 100 mm') { poly(p, ang.map((q) => [50 * Math.cos(q), 50 * Math.sin(q)]), C.lime, fill); poly(p, ang.map((q) => [di / 2 * Math.cos(q), di / 2 * Math.sin(q)]), C.lime, 'rgba(10,10,10,1)'); }
    if (v.s === 'I-section 200 mm') poly(p, [[-50, -100], [50, -100], [50, -91.5], [2.8, -91.5], [2.8, 91.5], [50, 91.5], [50, 100], [-50, 100], [-50, 91.5], [-2.8, 91.5], [-2.8, -91.5], [-50, -91.5]], C.lime, fill);
    if (v.s === 'flat plate on edge 10 mm') poly(p, [[-5, -A / 20], [5, -A / 20], [5, A / 20], [-5, A / 20]], C.lime, fill);
    p.line([-150, 150], [0, 0], C.grey, 1, [4, 4]);
    out(`I about the horizontal axis = ${nf(2).format(I[v.s] / 1e6)}×10⁶ mm⁴, ${nf(1).format(I[v.s] / I.square)}× the square. Same material, same weight per metre: putting the area far from the neutral axis (dashed) is what makes a section stiff in bending.${v.s.startsWith('flat') ? ' A deep thin plate is stiff too, but it buckles sideways easily.' : ''}`);
  },
});

// beam deflection by double integration of M/EI (w up, sagging M positive)
function deflectBeam(xs, Ms, EI, bc) {
  const n = xs.length, th = new Array(n).fill(0), w = new Array(n).fill(0);
  for (let i = 1; i < n; i++) th[i] = th[i - 1] + (Ms[i] + Ms[i - 1]) / 2 / EI * (xs[i] - xs[i - 1]);
  for (let i = 1; i < n; i++) w[i] = w[i - 1] + (th[i] + th[i - 1]) / 2 * (xs[i] - xs[i - 1]);
  if (bc === 'simple') { const L = xs[n - 1] - xs[0], wl = w[n - 1]; for (let i = 0; i < n; i++) w[i] -= (xs[i] - xs[0]) / L * wl; }
  return w;
}

// 06.11 live deflected shape
def('deflect', {
  controls: [{ k: 'a', label: 'Point load position (m)', min: 0, max: 6, step: 0.1, v: 3, f: 1 }, { k: 'P', label: 'Point load P (kN)', min: 0, max: 40, step: 1, v: 20, f: 0 }, { k: 'q', label: 'Uniform load q (kN/m)', min: 0, max: 10, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const L = 6, EI = 210e9 * 1.8456e-5, xs = linspace(0, L, 601);     // N m^2, the I-section of 06.10
    const Rb = (v.P * v.a + v.q * L * L / 2) / L, Ra = v.P + v.q * L - Rb;
    const Ms = xs.map((x) => (Ra * x - v.q * x * x / 2 - v.P * Math.max(0, x - v.a)) * 1e3);
    const w = deflectBeam(xs, Ms, EI, 'simple').map((z) => z * 1e3);   // mm
    let k = 0; w.forEach((z, i) => { if (z < w[k]) k = i; });
    const wmax = -w[k], sc = Math.max(10, wmax * 1.3);
    p.frame({ x: [-0.3, 6.3], y: [-sc, sc * 0.5], xlabel: 'x, m', ylabel: 'deflection, mm' });
    p.line([0, L], [0, 0], C.rule, 1, [4, 4]).line(xs, w, C.cyan, 3);
    [0, L].forEach((x0) => poly(p, [[x0, 0], [x0 - 0.12, -sc * 0.08], [x0 + 0.12, -sc * 0.08]], C.paper, null, 1.5));
    if (v.P > 0) arrow(p, v.a, sc * 0.45, v.a, sc * 0.08, C.amber, 2.5);
    p.dots([xs[k]], [w[k]], C.lime, 5);
    out(`IPE-like steel beam (EI = ${nf(2).format(EI / 1e6)} MN m²), 6 m span. Largest deflection ${nf(2).format(wmax)} mm at x = ${nf(2).format(xs[k])} m, span/${wmax > 0 ? nf(0).format(6000 / wmax) : '∞'}. Central load alone: PL³/48EI = ${nf(2).format(v.P * 1e3 * 216 / (48 * EI) * 1e3)} mm. Footbridges usually aim for span/300 or stiffer.`);
  },
});

// 06.12 moment redistribution with and without a prop
def('propped', {
  controls: [{ type: 'select', k: 'c', label: 'Supports (4 m beam, 5 kN/m)', options: ['cantilever', 'propped cantilever', 'simply supported'], v: 'propped cantilever' }],
  draw(p, v, out) {
    const L = 4, q = 5, xs = linspace(0, L, 401), EI = 210e9 * 1.8456e-5;
    let M, w, txt;
    if (v.c === 'cantilever') { M = xs.map((x) => -q * (L - x) ** 2 / 2); w = deflectBeam(xs, M.map((m) => m * 1e3), EI, 'cant'); txt = `Wall moment −qL²/2 = ${nf(1).format(-q * L * L / 2)} kN m, tip drops qL⁴/8EI.`; }
    else if (v.c === 'propped cantilever') { const R = 3 * q * L / 8; M = xs.map((x) => -q * (L - x) ** 2 / 2 + R * (L - x)); w = deflectBeam(xs, M.map((m) => m * 1e3), EI, 'cant'); txt = `Prop reaction 3qL/8 = ${nf(2).format(R)} kN. Wall moment −qL²/8 = ${nf(2).format(-q * L * L / 8)} kN m, largest sagging 9qL²/128 = ${nf(3).format(9 * q * L * L / 128)} kN m at 5L/8 from the wall.`; }
    else { M = xs.map((x) => q * x * (L - x) / 2); w = deflectBeam(xs, M.map((m) => m * 1e3), EI, 'simple'); txt = `No wall moment; mid-span moment qL²/8 = ${nf(1).format(q * L * L / 8)} kN m.`; }
    const wm = w.map((z) => z * 1e3), Ms = 40, Ws = Math.max(5, ...wm.map(Math.abs));
    p.frame({ x: [-0.3, 4.3], y: [-2.4, 1.3], xlabel: 'x, m', ylabel: '', noy: true });
    p.line([0, L], [0.6, 0.6], C.rule, 1, [4, 4]).line(xs, wm.map((z) => 0.6 + 0.55 * z / Ws), C.cyan, 3);
    if (v.c !== 'simply supported') p.rect(-0.12, 0, 0.2, 1.0, 'rgba(154,157,147,0.5)'); else drawSupport(p, 'pin', 0, 0.6, 0.12);
    if (v.c !== 'cantilever') drawSupport(p, 'roller', L, 0.6, 0.12);
    p.line([0, L], [-1.55, -1.55], C.rule, 1).line([0, ...xs, L], [-1.55, ...M.map((m) => -1.55 - 1.4 * m / Ms), -1.55], C.lime, 2);
    p.text('deflection (cyan, scaled)', 0.1, 1.15, C.cyan).text('M, sagging down (lime)', 0.1, -0.2, C.lime);
    out(`${txt} Max deflection ${nf(2).format(Math.max(...wm.map(Math.abs)))} mm. Adding a support makes the beam indeterminate and redistributes the moment: the prop cuts the wall moment from qL²/2 to qL²/8.`);
  },
});

// 06.13 shear stress profile over a section
def('shearprofile', {
  controls: [{ type: 'select', k: 's', label: 'Section', options: ['rectangle 50 × 200', 'I-section 200 × 100'], v: 'I-section 200 × 100' }, { k: 'V', label: 'Shear force V (kN)', min: 0, max: 60, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const rect = v.s.startsWith('rect'), H = 200, B = rect ? 50 : 100, tf = 8.5, tw = 5.6, ys = linspace(-H / 2, H / 2, 801);
    const b = (y) => (rect ? 50 : Math.abs(y) > H / 2 - tf ? B : tw);
    let I = 0; for (let i = 1; i < ys.length; i++) { const y = (ys[i] + ys[i - 1]) / 2; I += b(y) * y * y * (ys[i] - ys[i - 1]); }
    const Q = new Array(ys.length).fill(0); for (let i = ys.length - 2; i >= 0; i--) { const y = (ys[i] + ys[i + 1]) / 2; Q[i] = Q[i + 1] + b(y) * y * (ys[i + 1] - ys[i]); }
    const tau = ys.map((y, i) => v.V * 1e3 * Q[i] / (I * b(y)));
    const tm = Math.max(...tau), sc = 110 / Math.max(1, tm);
    sqAt(p, 60, 0, 120, '', 'y, mm');
    if (rect) poly(p, [[-25, -100], [25, -100], [25, 100], [-25, 100]], C.grey, 'rgba(154,157,147,0.2)');
    else poly(p, [[-50, -100], [50, -100], [50, -91.5], [2.8, -91.5], [2.8, 91.5], [50, 91.5], [50, 100], [-50, 100], [-50, 91.5], [-2.8, 91.5], [-2.8, -91.5], [-50, -91.5]], C.grey, 'rgba(154,157,147,0.2)');
    p.line([70, 70], [-100, 100], C.rule, 1).line(tau.map((t) => 70 + t * sc), ys, C.lime, 2);
    out(`τ = VQ/(Ib), drawn to the right of the section. Maximum ${nf(2).format(tm)} MPa at the neutral axis. ${rect ? `For a rectangle that's exactly 1.5 V/A = ${nf(2).format(1.5 * v.V * 1e3 / (50 * 200))} MPa: parabolic, zero at the top and bottom.` : `The web carries nearly all of V, at almost uniform stress (V/(h_w t_w) = ${nf(2).format(v.V * 1e3 / (183 * 5.6))} MPa); the stress drops sharply where the width jumps to the flange.`}`);
  },
});

// 06.14 twisting shaft
def('shafttwist', {
  controls: [{ k: 'T', label: 'Torque T (kN m)', min: 0, max: 3, step: 0.05, v: 1.2, f: 2 }, { k: 'D', label: 'Outer diameter D (mm)', min: 30, max: 80, step: 1, v: 50, f: 0 }, { k: 'd', label: 'Inner diameter d (mm)', min: 0, max: 70, step: 1, v: 42, f: 0 }],
  draw(p, v, out) {
    const d = Math.min(v.d, v.D - 2), L = 1400, G = 80e3, J = Math.PI * (v.D ** 4 - d ** 4) / 32, T = v.T * 1e6, tau = T * v.D / 2 / J, phi = T * L / (G * J);
    p.frame({ x: [-100, 1500], y: [-90, 90], xlabel: 'x, mm', ylabel: '', noy: true });
    p.rect(0, L, -v.D / 2, v.D / 2, 'rgba(154,157,147,0.22)'); p.rect(-60, 0, -80, 80, 'rgba(154,157,147,0.45)');
    // grid lines on the surface: a line at angle a round the shaft rotates by phi x / L
    for (let k = 0; k < 12; k++) { const a0 = k * Math.PI / 6, xs = linspace(0, L, 60), ys = xs.map((x) => v.D / 2 * Math.sin(a0 + phi * x / L * 8)), vis = xs.map((x) => Math.cos(a0 + phi * x / L * 8) > 0); p.line(xs.filter((_, i) => vis[i]), ys.filter((_, i) => vis[i]), C.cyan, 1.2); }
    p.line([0, L], [d / 2, d / 2], C.rule, 1, [3, 3]).line([0, L], [-d / 2, -d / 2], C.rule, 1, [3, 3]);
    out(`J = π(D⁴ − d⁴)/32 = ${nf(0).format(J)} mm⁴. τmax = TR/J = ${nf(1).format(tau)} MPa at the surface, zero at the centre. Twist over 1.4 m: φ = TL/GJ = ${nf(2).format(phi * 180 / Math.PI)}° (grid lines drawn 8× twisted). The dashed bore removes lightly stressed material.`);
  },
});

// 06.15 closed tube against a slit tube
def('slittube', {
  controls: [{ k: 'D', label: 'Tube diameter (mm)', min: 20, max: 60, step: 1, v: 35, f: 0 }, { k: 't', label: 'Wall thickness (mm)', min: 0.6, max: 4, step: 0.1, v: 1.2, f: 1 }, { type: 'check', k: 'slit', label: 'Slit the tube along its length', v: 0 }],
  draw(p, v, out) {
    const rm = (v.D - v.t) / 2, Am = Math.PI * rm * rm, s = 2 * Math.PI * rm, Jc = 4 * Am * Am * v.t / s, Jo = s * v.t ** 3 / 3, T = 60e3, G = 26e3;
    const J = v.slit ? Jo : Jc, tau = v.slit ? T * v.t / Jo : T / (2 * Am * v.t), phi = T * 1000 / (G * J) * 180 / Math.PI;
    sqAt(p, 0, 0, 40, 'mm', 'mm');
    const a0 = v.slit ? 0.06 : 0, ang = linspace(a0, 2 * Math.PI - a0, 121), ro = v.D / 2, ri = v.D / 2 - v.t;
    poly(p, [...ang.map((q) => [ro * Math.cos(q), ro * Math.sin(q)]), ...ang.slice().reverse().map((q) => [ri * Math.cos(q), ri * Math.sin(q)])], C.lime, 'rgba(184,255,92,0.35)');
    // shear flow arrows: closed tube circulates; slit tube runs up one face and down the other
    out(`${v.slit ? 'Slit' : 'Closed'} tube: J = ${nf(1).format(J)} mm⁴ (closed ${nf(0).format(Jc)}, slit ${nf(1).format(Jo)}, ratio ${nf(0).format(Jc / Jo)} = 3(r/t)²). Under 60 N m: τ = ${nf(1).format(tau)} MPa, twist ${phi < 1000 ? nf(2).format(phi) : '> 1000'}° per metre in aluminium. ${v.slit ? 'Open sections are hopeless in torsion.' : 'Closed: the shear flow circulates round the wall, q = T/(2Aₘ).'}`);
  },
});

// 06.16 combined loading at the root of a crank arm
def('crankarm', {
  controls: [{ k: 'F', label: 'Pedal force F (N)', min: 0, max: 1500, step: 10, v: 1000, f: 0 }, { k: 'ang', label: 'Crank angle above horizontal (°)', min: -90, max: 90, step: 5, v: 0, f: 0 }],
  draw(p, v, out) {
    const L = 170, a = 60, D = 24, d = 16, A = Math.PI * (D * D - d * d) / 4, I = Math.PI * (D ** 4 - d ** 4) / 64, J = 2 * I, th = v.ang * Math.PI / 180;
    const N = -v.F * Math.sin(th) + 0, M = v.F * Math.cos(th) * L, T = v.F * a, tau = T * 12 / J;
    const ph = linspace(0, 2 * Math.PI, 181), sig = ph.map((q) => N / A + M * 12 * Math.cos(q) / I), vm = sig.map((s) => Math.sqrt(s * s + 3 * tau * tau));
    let im = 0; vm.forEach((x, i) => { if (x > vm[im]) im = i; });
    fitAt(p, 0, 0, 34, 34, 'mm (section at the spindle, top = up)', '');
    // the section, and von Mises plotted radially outside it (1 mm per 10 MPa)
    const ring = linspace(0, 2 * Math.PI, 97);
    p.line(ring.map((q) => 12 * Math.sin(q)), ring.map((q) => 12 * Math.cos(q)), C.paper, 2).line(ring.map((q) => 8 * Math.sin(q)), ring.map((q) => 8 * Math.cos(q)), C.paper, 1.5);
    p.line(ph.map((q, i) => (12 + vm[i] / 10) * Math.sin(q)), ph.map((q, i) => (12 + vm[i] / 10) * Math.cos(q)), C.lime, 2);
    p.line(ph.map((q) => (12 + 355 / 10) * Math.sin(q)), ph.map((q) => (12 + 355 / 10) * Math.cos(q)), C.red, 1, [4, 4]);
    p.dots([12 * Math.sin(ph[im])], [12 * Math.cos(ph[im])], C.red, 6);
    out(`Axial ${nf(0).format(Math.abs(N) < 0.5 ? 0 : N)} N (${nf(1).format(Math.abs(N) < 0.5 ? 0 : N / A)} MPa), bending ${nf(1).format(M / 1e3)} N m (±${nf(1).format(M * 12 / I)} MPa), torsion ${nf(0).format(T / 1e3)} N m (${nf(1).format(tau)} MPa). Hotspot (red dot) ${nf(1).format(vm[im])} MPa von Mises on the ${Math.cos(ph[im]) > 0 ? 'top' : 'bottom'} of the arm; dashed ring = 355 MPa yield, safety factor ${nf(2).format(355 / vm[im])}.`);
  },
});

// 06.17 strain energy per load type
def('energybars', {
  controls: [{ k: 'P', label: 'Tie force (kN), 20 mm bar, 2 m', min: 0, max: 60, step: 1, v: 30, f: 0 }, { k: 'F', label: 'Balcony tip load (kN), 1.8 m beam', min: 0, max: 10, step: 0.5, v: 5, f: 1 }, { k: 'T', label: 'Shaft torque (kN m), 50 × 42 tube, 1.4 m', min: 0, max: 2, step: 0.05, v: 1.2, f: 2 }],
  draw(p, v, out) {
    const E = 210e3, G = 80e3, A = Math.PI * 100, I = 1.8456e7, J = Math.PI * (50 ** 4 - 42 ** 4) / 32;
    const P = v.P * 1e3, F = v.F * 1e3, T = v.T * 1e6;
    const db = P * 2000 / (E * A), dc = F * 1800 ** 3 / (3 * E * I), ph = T * 1400 / (G * J);
    const U = [P * db / 2e3, F * dc / 2e3, T * ph / 2e3], top = Math.max(60, ...U) * 1.15;
    p.frame({ x: [0, 3], y: [0, top], xlabel: '', ylabel: 'strain energy, J' });
    const names = ['bar, P²L/2EA', 'beam, ∫M²/2EI', 'shaft, T²L/2GJ'], cols = [C.cyan, C.lime, C.amber];
    U.forEach((u, i) => { p.rect(i + 0.2, i + 0.8, 0, u, cols[i]); p.text(nf(1).format(u) + ' J', i + 0.5, u + top * 0.03, C.paper, 'center'); p.text(names[i], i + 0.5, top * 0.93, C.grey, 'center'); });
    out(`Each bar equals half the load times its deflection: ${nf(1).format(v.P)} kN × ${nf(3).format(db)} mm / 2, ${nf(1).format(v.F)} kN × ${nf(2).format(dc)} mm / 2, ${nf(2).format(v.T)} kN m × ${nf(4).format(ph)} rad / 2. Double a load and its energy goes up four times.`);
  },
});

// 06.18 a ceiling bike hook: deflection by integrating curvature (what Castigliano gives in one line)
def('hook', {
  controls: [{ k: 'pos', label: 'Load position round the J (°, 90 = bottom)', min: 10, max: 170, step: 5, v: 90, f: 0 }, { k: 'm', label: 'Bike mass (kg)', min: 5, max: 30, step: 1, v: 15, f: 0 }],
  draw(p, v, out) {
    const a = 100, R = 40, EI = 210e3 * Math.PI * 8 ** 4 / 64, P = v.m * 9.81, mag = 15;
    const pts = [];
    linspace(0, -a, 101).forEach((y) => pts.push([0, y]));
    linspace(0, Math.PI, 181).slice(1).forEach((q) => pts.push([R - R * Math.cos(q), -a - R * Math.sin(q)]));
    const iL = 100 + Math.round(v.pos);
    const [xL, yL] = pts[iL];
    const rot = [], mid = [];
    for (let k = 0; k < pts.length - 1; k++) {
      const m = [(pts[k][0] + pts[k + 1][0]) / 2, (pts[k][1] + pts[k + 1][1]) / 2], ds = Math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]);
      mid.push(m); rot.push(k < iL ? -P * (xL - m[0]) * ds / EI : 0);
    }
    const def = pts.map(([x, y], j) => { let ux = 0, uy = 0; for (let k = 0; k < Math.min(j, iL); k++) { ux -= rot[k] * (y - mid[k][1]); uy += rot[k] * (x - mid[k][0]); } return [x + mag * ux, y + mag * uy, ux, uy]; });
    fitAt(p, 30, -80, 75, 80, 'mm', '');
    p.rect(-40, 40, 0, 8, 'rgba(154,157,147,0.5)');
    p.line(pts.map((q) => q[0]), pts.map((q) => q[1]), C.grey, 4).line(def.map((q) => q[0]), def.map((q) => q[1]), C.cyan, 2.5);
    arrow(p, def[iL][0], def[iL][1] + 4, def[iL][0], def[iL][1] - 30, C.amber);
    const [, , ux, uy] = def[iL];
    out(`Load point moves ${nf(3).format(-uy)} mm down and ${nf(3).format(Math.abs(ux))} mm ${ux < 0 ? 'towards' : 'away from'} the shank (cyan shape drawn ${mag}× exaggerated). Bending moment at the ceiling ${nf(1).format(P * xL / 1e3)} N m, so ${nf(0).format(P * xL * 4 / (Math.PI * 8 ** 4 / 64))} MPa in the rod.`);
  },
});

// 06.19 Euler buckling: compress a column until it snaps sideways
def('buckle', {
  controls: [{ type: 'select', k: 'ends', label: 'End conditions', options: ['pinned-pinned', 'fixed-free', 'fixed-fixed', 'fixed-pinned'], v: 'pinned-pinned' }, { k: 'P', label: 'Axial load P (kN)', min: 0, max: 120, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const E = 210e3, D = 48.3, t = 3.2, L = 3000, I = Math.PI * (D ** 4 - (D - 2 * t) ** 4) / 64, A = Math.PI * (D * D - (D - 2 * t) ** 2) / 4;
    const K = { 'pinned-pinned': 1, 'fixed-free': 2, 'fixed-fixed': 0.5, 'fixed-pinned': 0.6992 }[v.ends], Pcr = Math.PI ** 2 * E * I / (K * L) ** 2 / 1e3;
    const k = 4.4934 / L, tk = Math.tan(4.4934);
    const shape = { 'pinned-pinned': (x) => Math.sin(Math.PI * x / L), 'fixed-free': (x) => 1 - Math.cos(Math.PI * x / (2 * L)), 'fixed-fixed': (x) => (1 - Math.cos(2 * Math.PI * x / L)) / 2, 'fixed-pinned': (x) => (Math.sin(k * x) - tk * Math.cos(k * x) - k * x + tk) / 1.2 }[v.ends];
    const ys = linspace(0, L, 121), buckled = v.P >= Pcr, amp = buckled ? 450 : 0;
    fitAt(p, 0, L / 2, 900, L / 2 + 250, 'sideways, mm', 'height, mm');
    p.line([0, 0], [0, L], C.grey, 1, [4, 4]);
    p.line(ys.map((y) => amp * shape(y)), ys, buckled ? C.red : C.cyan, 4);
    const fixedBase = v.ends !== 'pinned-pinned', fixedTop = v.ends === 'fixed-fixed';
    if (fixedBase) p.rect(-250, 250, -120, 0, 'rgba(154,157,147,0.6)'); else poly(p, [[0, 0], [-90, -160], [90, -160]], C.paper, null, 1.5);
    const topX = amp * shape(L);
    if (fixedTop) p.rect(-250, 250, L, L + 120, 'rgba(154,157,147,0.6)'); else if (v.ends !== 'fixed-free') poly(p, [[topX, L], [topX - 90, L + 160], [topX + 90, L + 160]], C.paper, null, 1.5);
    arrow(p, topX, L + 480, topX, L + 30, C.amber);
    out(`Scaffold tube 48.3 × 3.2 mm, 3 m. ${v.ends}: K = ${K}, P_cr = π²EI/(KL)² = ${nf(2).format(Pcr)} kN (squash load ${nf(1).format(0.235 * A)} kN). ${buckled ? 'P ≥ P_cr: the straight column is no longer stable and it bows out sideways (red, amplitude not to scale).' : `Straight and stable, at ${nf(0).format(100 * v.P / Pcr)} % of P_cr.`}`);
  },
});

// 06.20 imperfect column: load against mid-span bow
def('imperfect', {
  controls: [{ k: 'e', label: 'Initial bow e₀ (mm)', min: 0, max: 15, step: 0.5, v: 3, f: 1 }, { k: 'r', label: 'Load P / P_cr', min: 0, max: 0.98, step: 0.01, v: 0.6, f: 2 }],
  draw(p, v, out) {
    const E = 210e3, D = 48.3, t = 3.2, L = 3000, I = Math.PI * (D ** 4 - (D - 2 * t) ** 4) / 64, A = Math.PI * (D * D - (D - 2 * t) ** 2) / 4, Pcr = Math.PI ** 2 * E * I / L ** 2;
    const rs = linspace(0, 0.995, 200);
    p.frame({ x: [0, 60], y: [0, 1.05], xlabel: 'total mid-span bow, mm', ylabel: 'P / P_cr' });
    p.line([0, 0, 60], [0, 1, 1], C.grey, 1.5, [5, 4]);
    [1, 3, 6, 10].forEach((e) => p.line(rs.map((r) => e / (1 - r)), rs, C.rule, 1.5));
    p.line(rs.map((r) => v.e / (1 - r)), rs, C.lime, 2.5);
    // first yield: P/A + P w c / I = 235
    const fy = 235, sig = (r) => r * Pcr / A + r * Pcr * (v.e / (1 - r)) * (D / 2) / I;
    let lo = 0, hi = 0.9999; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; if (sig(m) < fy) lo = m; else hi = m; }
    p.dots([v.e / (1 - lo)], [lo], C.red, 5);
    const w = v.e / (1 - v.r);
    p.dots([w], [v.r], C.cyan, 6);
    out(`Bow ${nf(2).format(w)} mm = e₀ × ${nf(2).format(1 / (1 - v.r))}. Peak stress P/A + Pwc/I = ${nf(0).format(sig(v.r))} MPa${sig(v.r) > fy ? ', past yield' : ''}. First yield (red dot) at ${nf(3).format(lo)} P_cr = ${nf(1).format(lo * Pcr / 1e3)} kN. Grey curves: e₀ = 1, 3, 6, 10 mm; dashed: a perfect column.`);
  },
});

// 06.21 penstock wall: hoop and axial stress
def('penstock', {
  controls: [{ k: 'H', label: 'Head below the intake (m)', min: 0, max: 800, step: 10, v: 650, f: 0 }, { k: 'D', label: 'Pipe diameter (m)', min: 0.5, max: 2.5, step: 0.1, v: 1.2, f: 1 }, { k: 't', label: 'Wall thickness (mm)', min: 5, max: 60, step: 1, v: 36, f: 0 }],
  draw(p, v, out) {
    const pr = (H) => 1000 * 9.81 * H * 1.25 / 1e6, need = (H) => pr(H) * v.D * 500 / (160 * 0.9) + 2;
    const Hs = linspace(0, 800, 81), top = Math.max(60, need(800) * 1.1);
    p.frame({ x: [0, 800], y: [0, top], xlabel: 'head, m', ylabel: 'wall needed, mm' });
    p.line(Hs, Hs.map(need), C.lime, 2.5).line([0, 800], [v.t, v.t], C.cyan, 1.5, [5, 4]);
    const ok = v.t >= need(v.H); p.dots([v.H], [need(v.H)], ok ? C.lime : C.red, 6);
    const P = pr(v.H), r = v.D * 500, tc = Math.max(v.t - 2, 0.1), hoop = P * r / tc;
    out(`Design pressure ${nf(2).format(P)} MPa (static head × 1.25 for water hammer). With 2 mm corrosion allowance: hoop pr/t = ${nf(1).format(hoop)} MPa, axial pr/2t = ${nf(1).format(hoop / 2)} MPa (exactly half). Needs ${nf(1).format(need(v.H))} mm against a 144 MPa limit (160 MPa × 0.9 weld efficiency): ${ok ? 'OK' : 'too thin'}.`);
  },
});

// 06.22 Kirsch: stress round a hole in a plate under tension
def('kirsch', {
  controls: [{ type: 'select', k: 'c', label: 'Stress shown', options: ['σx (along the load)', 'σy (across the load)'], v: 'σx (along the load)' }, { k: 's', label: 'Remote tension σ (MPa)', min: 10, max: 200, step: 5, v: 100, f: 0 }],
  draw(p, v, out) {
    const a = 5, s = v.s;
    const f = (x, y) => {
      const r = Math.hypot(x, y); if (r < a) return NaN;
      const th = Math.atan2(y, x), q = (a / r) ** 2, c2 = Math.cos(2 * th), s2 = Math.sin(2 * th);
      const srr = s / 2 * (1 - q) + s / 2 * (1 - 4 * q + 3 * q * q) * c2, stt = s / 2 * (1 + q) - s / 2 * (1 + 3 * q * q) * c2, trt = -s / 2 * (1 + 2 * q - 3 * q * q) * s2;
      const c = Math.cos(th), sn = Math.sin(th);
      return v.c.startsWith('σx') ? srr * c * c + stt * sn * sn - 2 * trt * sn * c : srr * sn * sn + stt * c * c + 2 * trt * sn * c;
    };
    fitAt(p, 0, 0, 20, 20, 'x, mm (load along x)', 'y, mm');
    bands(p, (x, y) => { const z = f(x, y); return isNaN(z) ? -1e9 : z; }, v.c.startsWith('σx') ? 0 : -s, 3 * s, 14, 140);
    const ring = linspace(0, 2 * Math.PI, 97); p.line(ring.map((q) => a * Math.cos(q)), ring.map((q) => a * Math.sin(q)), C.paper, 1.5);
    const px = v.c.startsWith('σx') ? [0, 0] : [a, -a], py = v.c.startsWith('σx') ? [a, -a] : [0, 0];
    p.dots(px, py, v.c.startsWith('σx') ? C.red : C.cyan, 5);
    arrow(p, 15, 0, 19.5, 0, C.amber); arrow(p, -15, 0, -19.5, 0, C.amber);
    out(v.c.startsWith('σx') ? `σx peaks at ${nf(0).format(3 * s)} MPa = 3σ on the hole edge at the top and bottom (red), and fades to σ within a couple of radii: ${nf(1).format(s * (1 + 1 / 8 + 3 / 32))} MPa at y = 2a.` : `σy is −σ = ${nf(0).format(-s)} MPa (compression) at the hole edge on the load axis (cyan), even though the plate is only pulled.`);
  },
});

// 07.01 path coordinates: tangential and normal acceleration on a track
def('pathaccel', {
  controls: [{ k: 's', label: 'Position along the track (m)', min: 0, max: 280, step: 1, v: 120, f: 0 }, { k: 'v', label: 'Speed (m/s)', min: 1, max: 20, step: 0.5, v: 10, f: 1 }, { k: 'at', label: 'Braking (−) or speeding up (+), m/s²', min: -3, max: 3, step: 0.1, v: -1, f: 1 }],
  draw(p, v, out) {
    const L1 = 100, Rb = 30, arc = Math.PI / 2 * Rb;
    const place = (s) => s < L1 ? [s, 0, 0] : s < L1 + arc ? [L1 + Rb * Math.sin((s - L1) / Rb), Rb * (1 - Math.cos((s - L1) / Rb)), (s - L1) / Rb] : [L1 + Rb, Rb + (s - L1 - arc), Math.PI / 2];
    const ss = linspace(0, 280, 300), pts = ss.map(place);
    fitAt(p, 75, 70, 85, 90, 'x, m', 'y, m');
    p.line(pts.map((q) => q[0]), pts.map((q) => q[1]), C.grey, 3);
    const [x, y, th] = place(v.s), onArc = v.s > L1 && v.s < L1 + arc, an = onArc ? v.v * v.v / Rb : 0;
    const tx = Math.cos(th), ty = Math.sin(th), nx = -ty, ny = tx, k = 12;
    p.dots([x], [y], C.lime, 5);
    if (Math.abs(v.at) > 0.01) arrow(p, x, y, x + k * v.at * tx, y + k * v.at * ty, C.cyan, 3);
    if (an > 0) arrow(p, x, y, x + k * an * nx, y + k * an * ny, C.amber, 3);
    out(`Tangential a_t = dv/dt = ${nf(1).format(v.at)} m/s² (cyan) changes the speed. Normal a_n = v²/ρ = ${nf(2).format(an)} m/s² (amber) ${onArc ? `points to the centre of the ${Rb} m bend` : 'is zero on a straight (ρ → ∞)'}. Total ${nf(2).format(Math.hypot(v.at, an))} m/s².`);
  },
});

// 07.02 ski jump with drag
def('skijump', {
  controls: [{ k: 'v0', label: 'Take-off speed (km/h)', min: 60, max: 100, step: 1, v: 90, f: 0 }, { k: 'cda', label: 'Drag area CdA (m²)', min: 0, max: 1, step: 0.05, v: 0.5, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, m = 65, rho = 1.2, ang = -11 * Math.PI / 180, slope = Math.tan(35 * Math.PI / 180), dt = 0.005;
    const run = (cda) => { let s = [0, 0, v.v0 / 3.6 * Math.cos(ang), v.v0 / 3.6 * Math.sin(ang)]; const xs = [0], ys = [0]; let t = 0;
      const f = (q) => { const sp = Math.hypot(q[2], q[3]), k = 0.5 * rho * cda * sp / m; return [q[2], q[3], -k * q[2], -g - k * q[3]]; };
      let prev = s;
      while (s[1] + slope * s[0] > 0 || t === 0) { prev = s; const k1 = f(s), k2 = f(s.map((q, i) => q + dt / 2 * k1[i])), k3 = f(s.map((q, i) => q + dt / 2 * k2[i])), k4 = f(s.map((q, i) => q + dt * k3[i])); s = s.map((q, i) => q + dt / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])); t += dt; xs.push(s[0]); ys.push(s[1]); if (t > 10) break; }
      const g0 = prev[1] + slope * prev[0], g1 = s[1] + slope * s[0], fr = g0 / (g0 - g1), q = prev.map((u, i) => u + fr * (s[i] - u));
      xs[xs.length - 1] = q[0]; ys[ys.length - 1] = q[1];
      return { xs, ys, t: t - dt + fr * dt, v: Math.hypot(q[2], q[3]), d: Math.hypot(q[0], q[1]) }; };
    const a = run(v.cda), b = run(0);
    fitAt(p, 40, -30, 50, 35, 'x, m', 'y, m');
    p.line([0, 90], [0, -90 * slope], C.grey, 2).line(b.xs, b.ys, C.grey, 1.5, [5, 4]).line(a.xs, a.ys, C.lime, 2.5);
    out(`Lands ${nf(1).format(a.d)} m down the 35° slope after ${nf(2).format(a.t)} s at ${nf(0).format(a.v * 3.6)} km/h. Without drag (dashed parabola): ${nf(1).format(b.d)} m. Real jumpers fly further than both, because their body and skis also make lift.`);
  },
});

// 07.03 roller coaster speed from energy
def('coaster', {
  controls: [{ k: 'h1', label: 'Bump height near x = 80 m (m)', min: 0, max: 30, step: 1, v: 12, f: 0 }, { k: 'h2', label: 'Last hill height (m)', min: 0, max: 40, step: 1, v: 17, f: 0 }, { k: 'v0', label: 'Speed at the top (m/s)', min: 0, max: 10, step: 0.5, v: 1, f: 1 }],
  draw(p, v, out) {
    const tr = (x) => 40 - 30 / (1 + Math.exp(-(x - 30) / 8)) + v.h1 * Math.exp(-(((x - 80) / 15) ** 2)) + v.h2 * Math.exp(-(((x - 150) / 18) ** 2));
    const xs = linspace(0, 190, 191), hs = xs.map(tr), E = v.v0 ** 2 / 2 + 9.81 * tr(0);
    p.frame({ x: [0, 190], y: [0, Math.max(50, ...hs) + 5], xlabel: 'x, m', ylabel: 'height, m' });
    let stall = -1;
    for (let i = 0; i < xs.length - 1; i++) {
      const vv = 2 * (E - 9.81 * hs[i]);
      if (vv < 0) { stall = xs[i]; break; }
      const sp = Math.sqrt(vv), t = Math.min(1, sp / 30);
      p.line([xs[i], xs[i + 1]], [hs[i], hs[i + 1]], `rgba(${Math.round(92 + 146 * t)},${Math.round(200 + 55 * t)},${Math.round(255 - 190 * t)},1)`, 4);
    }
    if (stall >= 0) { p.line(xs.filter((x) => x >= stall), hs.filter((_, i) => xs[i] >= stall), C.grey, 2, [4, 4]); p.dots([stall], [tr(stall)], C.red, 6); }
    const vmax = Math.sqrt(2 * (E - 9.81 * Math.min(...hs.slice(0, stall >= 0 ? xs.indexOf(stall) + 1 : xs.length))));
    out(stall >= 0 ? `The car can't climb above ${nf(1).format(E / 9.81)} m (its total energy per unit weight): it stops at x = ${nf(0).format(stall)} m and rolls back.` : `v = √(v₀² + 2g(h₀ − h)): fastest ${nf(1).format(vmax)} m/s = ${nf(0).format(vmax * 3.6)} km/h at the lowest point; ${nf(1).format(Math.sqrt(2 * (E - 9.81 * tr(150))))} m/s over the last hill. Colour: slow cyan to fast lime. Mass never enters.`);
  },
});

// 07.04 two-cart collision
def('carts', {
  controls: [{ k: 'm1', label: 'Cart 1 mass (kg)', min: 0.2, max: 2, step: 0.1, v: 0.5, f: 1 }, { k: 'm2', label: 'Cart 2 mass (kg)', min: 0.2, max: 2, step: 0.1, v: 1, f: 1 }, { k: 'e', label: 'Restitution e', min: 0, max: 1, step: 0.05, v: 0.6, f: 2 }],
  draw(p, v, out) {
    const v1 = 2, v2 = 0, P = v.m1 * v1 + v.m2 * v2;
    const a = (P - v.m2 * v.e * (v1 - v2)) / (v.m1 + v.m2), b = (P + v.m1 * v.e * (v1 - v2)) / (v.m1 + v.m2);
    p.frame({ x: [0, 2], y: [-0.5, 2.5], xlabel: 'time, s (impact at 1 s)', ylabel: 'position, m' });
    const ts = linspace(0, 2, 81), x1 = (t) => t < 1 ? -1 + 2 * t + 0.5 : 1.5 + a * (t - 1) - 0.0, x2 = (t) => t < 1 ? 1.5 + 0.0 : 1.5 + b * (t - 1);
    p.line(ts, ts.map(x1), C.cyan, 2.5).line(ts, ts.map(x2), C.amber, 2.5);
    p.line([1, 1], [-0.5, 2.5], C.rule, 1, [3, 3]);
    const vc = P / (v.m1 + v.m2); p.line(ts, ts.map((t) => (v.m1 * x1(t) + v.m2 * x2(t)) / (v.m1 + v.m2)), C.paper, 1.5, [6, 4]);
    const loss = 0.5 * v.m1 * v1 * v1 - 0.5 * v.m1 * a * a - 0.5 * v.m2 * b * b;
    out(`Cart 1 (cyan) hits cart 2 (amber) at 2 m/s. After: ${nf(3).format(a)} and ${nf(3).format(b)} m/s. Momentum ${nf(3).format(P)} kg m/s before and ${nf(3).format(v.m1 * a + v.m2 * b)} after; the centre of mass (dashed) moves at ${nf(3).format(vc)} m/s throughout. Kinetic energy lost: ${nf(3).format(loss)} J.`);
  },
});

// 07.05 rocket mass ratio
def('rocket', {
  controls: [{ k: 'mr', label: 'Mass ratio m₀ / m₁', min: 1.2, max: 20, step: 0.1, v: 4, f: 1 }, { k: 've', label: 'Exhaust speed (m/s)', min: 1500, max: 4500, step: 50, v: 2500, f: 0 }],
  draw(p, v, out) {
    const mrs = linspace(1, 20, 200), dv = v.ve * Math.log(v.mr);
    p.frame({ x: [1, 20], y: [0, 14], xlabel: 'mass ratio m₀/m₁', ylabel: 'Δv, km/s' });
    p.line([1, 20], [7.8, 7.8], C.red, 1, [5, 4]).text('orbit ≈ 7.8 km/s + ~1.5 km/s losses', 1.5, 8.2, C.red);
    p.line([1, 20], [9.3, 9.3], C.grey, 1, [2, 4]);
    [2500, 4500].forEach((ve) => p.line(mrs, mrs.map((r) => ve * Math.log(r) / 1e3), C.rule, 1.5));
    p.line(mrs, mrs.map((r) => v.ve * Math.log(r) / 1e3), C.lime, 2.5).dots([v.mr], [dv / 1e3], C.cyan, 6);
    const need = Math.exp(9300 / v.ve);
    out(`Δv = v_e ln(m₀/m₁) = ${nf(0).format(dv)} m/s. Propellant is ${nf(1).format(100 * (1 - 1 / v.mr))} % of lift-off mass. Reaching orbit (about 9.3 km/s including losses) in one stage needs m₀/m₁ = ${nf(1).format(need)}: ${nf(1).format(100 * (1 - 1 / need))} % propellant. That's why rockets have stages.`);
  },
});

// 07.06 system of particles with the centre of mass tracked
def('comtracker', {
  controls: [{ k: 't', label: 'Time', min: 0, max: 6, step: 0.05, v: 3, f: 2 }, { type: 'select', k: 'set', label: 'Starting set', options: ['five bodies', 'binary pair', 'three bodies'], v: 'five bodies' }, { type: 'check', k: 'g', label: 'Add uniform gravity (external force)', v: 0 }],
  draw(p, v, out) {
    const sets = { 'five bodies': [[1.5, -0.6, 0.3, 0.2, 0.1], [0.8, 0.5, -0.4, -0.3, 0.2], [1.0, 0.1, 0.7, 0.1, -0.35], [0.6, -0.8, -0.5, 0.35, 0.3], [1.2, 0.7, 0.4, -0.1, 0.25]], 'binary pair': [[2, -0.3, 0, 0, -0.6], [1, 0.6, 0, 0.1, 1.2]], 'three bodies': [[1, -0.7, 0, 0.1, -0.5], [1, 0.7, 0, 0.1, 0.5], [1, 0, 0.6, -0.2, 0]] };
    const B = sets[v.set].map((q) => ({ m: q[0], x: q[1], y: q[2], vx: q[3], vy: q[4] })), M = B.reduce((s, b) => s + b.m, 0), g = v.g ? -0.4 : 0, dt = 0.002;
    const acc = () => B.map((b, i) => { let ax = 0, ay = g; B.forEach((c, j) => { if (i === j) return; const dx = c.x - b.x, dy = c.y - b.y, r2 = dx * dx + dy * dy + 0.0025, f = c.m / (r2 * Math.sqrt(r2)); ax += f * dx; ay += f * dy; }); return [ax, ay]; });
    const trails = B.map(() => [[], []]), com = [[], []];
    let a = acc();
    const n = Math.round(v.t / dt);
    for (let s = 0; s <= n; s++) {
      if (s % 10 === 0) { B.forEach((b, i) => { trails[i][0].push(b.x); trails[i][1].push(b.y); }); com[0].push(B.reduce((q, b) => q + b.m * b.x, 0) / M); com[1].push(B.reduce((q, b) => q + b.m * b.y, 0) / M); }
      if (s === n) break;
      B.forEach((b, i) => { b.vx += 0.5 * dt * a[i][0]; b.vy += 0.5 * dt * a[i][1]; b.x += dt * b.vx; b.y += dt * b.vy; });
      a = acc(); B.forEach((b, i) => { b.vx += 0.5 * dt * a[i][0]; b.vy += 0.5 * dt * a[i][1]; });
    }
    fitAt(p, 0, -0.3, 2, 1.6, 'x', 'y');
    const cols = [C.cyan, C.amber, C.paper, C.red, C.grey];
    trails.forEach((tr, i) => p.line(tr[0], tr[1], cols[i], 1.2).dots([B[i].x], [B[i].y], cols[i], 3 + 2 * B[i].m));
    p.line(com[0], com[1], C.lime, 2.5, [5, 3]).dots([com[0][com[0].length - 1]], [com[1][com[1].length - 1]], C.lime, 6);
    const P = [B.reduce((q, b) => q + b.m * b.vx, 0), B.reduce((q, b) => q + b.m * b.vy, 0)];
    out(`Total momentum (${nf(4).format(P[0])}, ${nf(4).format(P[1])}). The centre of mass (lime) ${v.g ? 'falls along a parabola, exactly like a single particle under the external force' : 'moves in a straight line at constant speed, however wildly the bodies swing round each other'}: internal forces cancel in pairs.`);
  },
});

// 07.07 mass on a shrinking string
def('spinstring', {
  controls: [{ k: 'r', label: 'String length r (m)', min: 0.2, max: 0.8, step: 0.01, v: 0.4, f: 2 }],
  draw(p, v, out) {
    const m = 0.2, r0 = 0.8, w0 = 2 * Math.PI, w = w0 * (r0 / v.r) ** 2, L = m * r0 * r0 * w0;
    const rs = linspace(0.2, 0.8, 121);
    p.frame({ x: [0.15, 0.85], y: [0, 110], xlabel: 'radius r, m', ylabel: 'ω, rad/s' });
    p.line(rs, rs.map((r) => w0 * (r0 / r) ** 2), C.lime, 2.5).dots([v.r], [w], C.cyan, 6);
    const T0 = 0.5 * m * (r0 * w0) ** 2, T = 0.5 * m * (v.r * w) ** 2;
    out(`L = m r² ω = ${nf(4).format(L)} kg m²/s stays fixed, so ω = ω₀ (r₀/r)² = ${nf(2).format(w)} rad/s (${nf(2).format(w / (2 * Math.PI))} rev/s). Speed ${nf(2).format(v.r * w)} m/s, string tension ${nf(1).format(m * v.r * w * w)} N. Kinetic energy ${nf(2).format(T)} J, up from ${nf(2).format(T0)} J: the work done pulling the string.`);
  },
});

// 07.08 four-bar linkage with velocities and Grashof check
def('fourbar', {
  controls: [{ k: 'th', label: 'Crank angle (°)', min: 0, max: 360, step: 2, v: 60, f: 0 }, { k: 'b', label: 'Coupler b (mm)', min: 20, max: 110, step: 1, v: 70, f: 0 }, { k: 'c', label: 'Rocker c (mm)', min: 20, max: 110, step: 1, v: 45, f: 0 }, { k: 'd', label: 'Ground d (mm)', min: 20, max: 110, step: 1, v: 70, f: 0 }],
  draw(p, v, out) {
    const a = 20, b = v.b, c = v.c, d = v.d, th = v.th * Math.PI / 180, w2 = 2 * Math.PI;
    const L = [a, b, c, d].sort((x, y) => x - y), gr = L[0] + L[3] <= L[1] + L[2];
    fitAt(p, d / 2, 20, Math.max(d, 60) / 2 + 60, 70, 'x, mm', 'y, mm');
    const A = [a * Math.cos(th), a * Math.sin(th)], e = [d - A[0], -A[1]], LL = Math.hypot(...e);
    p.dots([0, d], [0, 0], C.grey, 6).line([0, A[0]], [0, A[1]], C.lime, 4);
    if (LL > b + c || LL < Math.abs(b - c)) { out(`At ${v.th}° the coupler and rocker can't reach each other: the crank can't get here. Links sorted ${L.join(', ')}: s + l = ${L[0] + L[3]} ${gr ? '≤' : '>'} p + q = ${L[1] + L[2]}, ${gr ? 'Grashof' : 'non-Grashof, so no link turns fully'}.`); return; }
    const x = (b * b - c * c + LL * LL) / (2 * LL), h = Math.sqrt(Math.max(b * b - x * x, 0)), u = [e[0] / LL, e[1] / LL], B = [A[0] + x * u[0] - h * u[1], A[1] + x * u[1] + h * u[0]];
    const rAB = [B[0] - A[0], B[1] - A[1]], rO4B = [B[0] - d, B[1]], vA = [-w2 * A[1], w2 * A[0]];
    const det = -rAB[1] * -rO4B[0] - rO4B[1] * rAB[0], w3 = ((-vA[0]) * -rO4B[0] - rO4B[1] * (-vA[1])) / det, w4 = (-rAB[1] * (-vA[1]) - rAB[0] * (-vA[0])) / det;
    const vB = [-w4 * rO4B[1], w4 * rO4B[0]], k = 0.15;
    p.line([A[0], B[0]], [A[1], B[1]], C.paper, 3).line([d, B[0]], [0, B[1]], C.cyan, 4).dots([A[0], B[0]], [A[1], B[1]], C.paper, 4);
    arrow(p, A[0], A[1], A[0] + k * vA[0], A[1] + k * vA[1], C.amber); arrow(p, B[0], B[1], B[0] + k * vB[0], B[1] + k * vB[1], C.amber);
    out(`Crank 20 mm at 60 rpm. ω₃ = ${nf(3).format(w3)}, ω₄ = ${nf(3).format(w4)} rad/s; |v_A| = ${nf(1).format(Math.hypot(...vA))}, |v_B| = ${nf(1).format(Math.hypot(...vB))} mm/s (amber). s + l = ${L[0] + L[3]} ${gr ? '≤' : '>'} p + q = ${L[1] + L[2]}: ${gr ? (L[0] === a ? 'Grashof with the crank shortest, so it turns fully' : 'Grashof, but the crank is not the shortest link') : 'non-Grashof: no link can turn fully'}.`);
  },
});

// 07.09 rolling race down a ramp
def('rollrace', {
  controls: [{ k: 'th', label: 'Ramp angle (°)', min: 2, max: 30, step: 1, v: 10, f: 0 }, { k: 'mu', label: 'Friction coefficient μ', min: 0, max: 0.5, step: 0.01, v: 0.3, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, th = v.th * Math.PI / 180, L = 2, shapes = [['sphere', 0.4, C.cyan], ['disc', 0.5, C.lime], ['ring', 1, C.amber]];
    const res = shapes.map(([n, k, col]) => { const aRoll = g * Math.sin(th) / (1 + k), F = aRoll * k, slip = F > v.mu * g * Math.cos(th); const a = slip ? g * (Math.sin(th) - v.mu * Math.cos(th)) : aRoll; return { n, a, col, slip, t: Math.sqrt(2 * L / a) }; });
    const tmax = Math.max(...res.map((r) => r.t)) * 1.05;
    p.frame({ x: [0, tmax], y: [0, 2.1], xlabel: 'time, s', ylabel: 'distance down the ramp, m' });
    res.forEach((r) => { const ts = linspace(0, r.t, 60); p.line(ts, ts.map((t) => 0.5 * r.a * t * t), r.col, 2.5); });
    const blk = Math.sqrt(2 * L / (g * Math.sin(th))); const tb = linspace(0, blk, 60); p.line(tb, tb.map((t) => 0.5 * g * Math.sin(th) * t * t), C.grey, 1.5, [5, 4]);
    out(res.map((r) => `${r.n} ${nf(3).format(r.t)} s${r.slip ? ' (slips)' : ''}`).join(', ') + `; frictionless block (dashed) ${nf(3).format(blk)} s. Rolling: a = g sinθ/(1 + I/mr²), so 5/7, 2/3 and 1/2 of g sinθ. Steepen the ramp or cut μ and they start to slip.`);
  },
});

// 07.10 flywheel profile editor
def('flywheelprof', {
  controls: [{ k: 'ri', label: 'Rim inner radius (mm)', min: 80, max: 190, step: 5, v: 160, f: 0 }, { k: 'tr', label: 'Rim width (mm)', min: 20, max: 100, step: 5, v: 60, f: 0 }, { k: 'tw', label: 'Web thickness (mm)', min: 5, max: 60, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const rho = 7850, R = 200, ri = v.ri, rows = [[15, 30, 60], [30, ri, v.tw], [ri, R, v.tr]];
    let m = 0, I = 0, mr = 0, Ir = 0;
    rows.forEach(([a, b, t], k) => { const dm = rho * (t / 1e3) * Math.PI * ((b / 1e3) ** 2 - (a / 1e3) ** 2), dI = rho * (t / 1e3) * Math.PI / 2 * ((b / 1e3) ** 4 - (a / 1e3) ** 4); m += dm; I += dI; if (k === 2) { mr = dm; Ir = dI; } });
    fitAt(p, 100, 0, 115, 60, 'radius, mm', 'axial, mm');
    rows.forEach(([a, b, t]) => p.rect(a, b, -t / 2, t / 2, 'rgba(238,255,65,0.55)'));
    p.line([0, 0], [-60, 60], C.grey, 1, [4, 4]);
    const w = 3000 * Math.PI / 30;
    out(`Mass ${nf(2).format(m)} kg, I = ${nf(4).format(I)} kg m², radius of gyration ${nf(0).format(Math.sqrt(I / m) * 1000)} mm. The rim holds ${nf(0).format(100 * mr / m)} % of the mass and ${nf(0).format(100 * Ir / I)} % of the inertia. Energy at 3000 rpm: ${nf(2).format(0.5 * I * w * w / 1e3)} kJ. Mass far from the axis counts with r².`);
  },
});

// 07.11 rotor balancing, end view of the m r vectors
def('rotorbal', {
  controls: [{ k: 'm2', label: 'Middle unbalance mass (g)', min: 0, max: 40, step: 1, v: 15, f: 0 }, { k: 'a2', label: 'Its angle (°)', min: 0, max: 360, step: 5, v: 160, f: 0 }, { type: 'select', k: 'fix', label: 'Correction', options: ['none', 'static (one plane)', 'dynamic (two planes)'], v: 'none' }],
  draw(p, v, out) {
    const d2r = Math.PI / 180, rot = [[0.020, 0.10, 30, 0.10], [v.m2 / 1000, 0.12, v.a2, 0.30], [0.010, 0.08, 270, 0.50]];
    const sum = (ms) => { let F = [0, 0], M = [0, 0]; ms.forEach(([m, r, a, z]) => { const u = [m * r * Math.cos(a * d2r), m * r * Math.sin(a * d2r)]; F = [F[0] + u[0], F[1] + u[1]]; M = [M[0] + u[0] * z, M[1] + u[1] * z]; }); return [F, M]; };
    let [F, M] = sum(rot), corr = [];
    if (v.fix.startsWith('static')) corr = [[Math.hypot(...F) / 0.1, 0.1, Math.atan2(-F[1], -F[0]) / d2r, 0.3]];
    if (v.fix.startsWith('dynamic')) { const uR = [(-M[0] + F[0] * 0) / 0.6, (-M[1] + F[1] * 0) / 0.6], uL = [-F[0] - uR[0], -F[1] - uR[1]]; corr = [[Math.hypot(...uL) / 0.1, 0.1, Math.atan2(uL[1], uL[0]) / d2r, 0], [Math.hypot(...uR) / 0.1, 0.1, Math.atan2(uR[1], uR[0]) / d2r, 0.6]]; }
    const [F2, M2] = sum(rot.concat(corr)), s = 1000;
    fitAt(p, 0, 0, 3.2, 3.2, 'm r, g m (end view)', '');
    const ring = linspace(0, 2 * Math.PI, 97); p.line(ring.map((q) => 2.5 * Math.cos(q)), ring.map((q) => 2.5 * Math.sin(q)), C.rule, 1.5);
    rot.forEach(([m, r, a]) => { const u = m * r * s; if (u > 1e-6) arrow(p, 0, 0, u * Math.cos(a * d2r), u * Math.sin(a * d2r), C.cyan, 2); });
    corr.forEach(([m, r, a]) => arrow(p, 0, 0, m * r * s * Math.cos(a * d2r), m * r * s * Math.sin(a * d2r), C.amber, 2));
    if (Math.hypot(...F2) > 1e-7) arrow(p, 0, 0, F2[0] * s, F2[1] * s, C.red, 3);
    const w = 100 * Math.PI;
    out(`Residual force ${nf(3).format(Math.hypot(...F2) * 1e3)} g m (red; ${nf(1).format(Math.hypot(...F2) * w * w)} N at 3000 rpm) and moment ${nf(3).format(Math.hypot(...M2) * 1e3)} g m². ${v.fix === 'none' ? 'Cyan: the three unbalances.' : v.fix.startsWith('static') ? 'One mass (amber) kills the force, but a couple remains: the rotor still rocks in its bearings.' : 'Two masses in the end planes (amber) cancel force and moment together.'}`);
  },
});

// 07.12 ball on a carousel, inertial vs rotating view
def('carousel', {
  controls: [{ k: 't', label: 'Time (s)', min: 0, max: 1.5, step: 0.01, v: 1.2, f: 2 }, { k: 'u', label: 'Rolling speed (m/s)', min: 0.5, max: 4, step: 0.1, v: 2, f: 1 }, { type: 'select', k: 'view', label: 'View', options: ['rotating (riding the carousel)', 'inertial (from above, standing still)'], v: 'rotating (riding the carousel)' }, { type: 'check', k: 'cw', label: 'Turn clockwise instead', v: 0 }],
  draw(p, v, out) {
    const Om = (v.cw ? -1 : 1) * 2 * Math.PI / 6, R = 3, ts = linspace(0, v.t, 150);
    const rotView = v.view.startsWith('rotating');
    const X = ts.map((t) => Math.min(v.u * t, R)), pts = ts.map((t, i) => rotView ? [X[i] * Math.cos(Om * t), -X[i] * Math.sin(Om * t)] : [X[i], 0]);
    fitAt(p, 0, 0, 3.4, 3.4, 'x, m', 'y, m');
    const ring = linspace(0, 2 * Math.PI, 121); p.line(ring.map((q) => R * Math.cos(q)), ring.map((q) => R * Math.sin(q)), C.grey, 2);
    const ang = rotView ? 0 : Om * v.t; p.line([0, R * Math.cos(ang)], [0, R * Math.sin(ang)], C.rule, 2, [5, 4]);
    p.line(pts.map((q) => q[0]), pts.map((q) => q[1]), C.lime, 2.5).dots([pts[pts.length - 1][0]], [pts[pts.length - 1][1]], C.cyan, 6);
    const e = pts[pts.length - 1];
    out(rotView ? `Riding along, the ball curves to the ${v.cw ? 'left' : 'right'} (it ends at (${nf(2).format(e[0])}, ${nf(2).format(e[1])}) m), as if pushed by the Coriolis force 2Ωv = ${nf(2).format(2 * Math.abs(Om) * v.u)} m/s² plus the centrifugal force. The dashed line is where it was aimed.` : `From outside, no force acts and the ball rolls dead straight. The carousel (dashed radius) simply turns underneath it. Same motion, different frame.`);
  },
});

// 07.13 gimbal lock: Euler-angle rates against quaternion rates
def('gimbal', {
  controls: [{ k: 'th', label: 'Pitch angle θ (°)', min: 0, max: 89.5, step: 0.5, v: 60, f: 1 }],
  draw(p, v, out) {
    const phi = 0.3, rate = (th) => { const t = th * Math.PI / 180; const c = Math.cos(phi), s = Math.sin(phi); return Math.hypot(c * Math.tan(t), -s, c / Math.cos(t)); };
    const ths = linspace(0, 89.5, 180);
    p.frame({ x: [0, 90], y: [0.1, 1000], ylog: true, xlabel: 'pitch θ, degrees', ylabel: 'rate needed, rad/s' });
    p.line(ths, ths.map(rate), C.red, 2.5).line([0, 90], [0.5, 0.5], C.lime, 2.5);
    p.dots([v.th], [rate(v.th)], C.red, 6).dots([v.th], [0.5], C.lime, 6);
    out(`A body yawing at 1 rad/s about its own axis. The roll-pitch-yaw angles must change at ${nf(2).format(rate(v.th))} rad/s (red), heading to infinity at θ = 90° where two gimbal axes line up. The quaternion (lime) changes at a steady |q̇| = |ω|/2 = 0.50 for any orientation.`);
  },
});

// 07.14 inertia tensor and principal axes of a tilted plate
def('principal', {
  controls: [{ k: 'th', label: 'Tilt of the plate (°)', min: 0, max: 180, step: 1, v: 30, f: 0 }, { k: 'a', label: 'Length a (m)', min: 0.1, max: 0.6, step: 0.01, v: 0.4, f: 2 }, { k: 'b', label: 'Width b (m)', min: 0.05, max: 0.6, step: 0.01, v: 0.2, f: 2 }],
  draw(p, v, out) {
    const M = 8, t = v.th * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
    const Ia = M * v.b * v.b / 12, Ib = M * v.a * v.a / 12;
    // in-plane tensor of the rotated plate: R diag(Ia, Ib) R^T, with Ixy as the product of inertia (sign convention: I = [[Ixx, -Pxy], ...])
    const Ixx = Ia * c * c + Ib * s * s, Iyy = Ia * s * s + Ib * c * c, Ixy = (Ia - Ib) * s * c;
    const Cn = (Ixx + Iyy) / 2, Rr = Math.hypot((Ixx - Iyy) / 2, Ixy), l1 = Cn - Rr, l2 = Cn + Rr, ang = 0.5 * Math.atan2(2 * Ixy, Ixx - Iyy);
    fitAt(p, 0, 0, 0.4, 0.4, 'x, m', 'y, m');
    const corners = [[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([u, w]) => [u * v.a / 2 * c - w * v.b / 2 * s, u * v.a / 2 * s + w * v.b / 2 * c]);
    poly(p, corners, C.paper, 'rgba(238,255,65,0.25)', 1.5);
    const L = 0.38; p.line([-L * Math.cos(ang), L * Math.cos(ang)], [-L * Math.sin(ang), L * Math.sin(ang)], C.cyan, 2).line([L * Math.sin(ang), -L * Math.sin(ang)], [-L * Math.cos(ang), L * Math.cos(ang)], C.amber, 2);
    out(`In x-y axes: Ixx = ${nf(5).format(Ixx)}, Iyy = ${nf(5).format(Iyy)}, product term ${nf(5).format(Ixy)} kg m². Eigenvalues ${nf(5).format(l1)} (cyan axis) and ${nf(5).format(l2)} (amber axis): always m b²/12 = ${nf(5).format(Ia)} and m a²/12 = ${nf(5).format(Ib)}, whatever the tilt. The eigenvectors follow the plate's edges.`);
  },
});

// 07.15 the tennis racket theorem
def('racket', {
  controls: [{ type: 'select', k: 'ax', label: 'Spin about', options: ['smallest axis', 'intermediate axis', 'largest axis'], v: 'intermediate axis' }, { k: 'e', label: 'Initial wobble (log10 rad/s)', min: -5, max: -1, step: 0.5, v: -3, f: 1 }],
  draw(p, v, out) {
    const I = [1.0, 2.5, 3.3], k = ['smallest axis', 'intermediate axis', 'largest axis'].indexOf(v.ax), eps = 10 ** v.e;
    let w = [eps, eps, eps]; w[k] = 10;
    const f = (w) => [(I[1] - I[2]) * w[1] * w[2] / I[0], (I[2] - I[0]) * w[2] * w[0] / I[1], (I[0] - I[1]) * w[0] * w[1] / I[2]];
    const dt = 0.002, n = 5000, ts = [0], W = [[w[0]], [w[1]], [w[2]]];
    for (let i = 0; i < n; i++) {
      const k1 = f(w), k2 = f(w.map((q, j) => q + dt / 2 * k1[j])), k3 = f(w.map((q, j) => q + dt / 2 * k2[j])), k4 = f(w.map((q, j) => q + dt * k3[j]));
      w = w.map((q, j) => q + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]));
      if (i % 5 === 4) { ts.push((i + 1) * dt); W.forEach((a, j) => a.push(w[j])); }
    }
    p.frame({ x: [0, 10], y: [-12, 12], xlabel: 'time, s', ylabel: 'ω about each body axis, rad/s' });
    [C.cyan, C.lime, C.amber].forEach((col, j) => p.line(ts, W[j], col, 2));
    const flips = W[k].slice(1).filter((x, i) => Math.sign(x) !== Math.sign(W[k][i])).length;
    out(k === 1 ? `Spinning about the intermediate axis (lime), a wobble of ${eps.toExponential(0)} rad/s grows like e^(6.03 t) until the body flips over, ${flips} times in 10 s. Smaller wobbles only delay the flip.` : `About the ${v.ax}, the wobble stays tiny: rotation about the smallest and largest axes is stable. Cyan, lime, amber: smallest, intermediate, largest axis.`);
  },
});

// 07.16 gyroscope precession: simulation against m g l / (I3 w)
def('gyro', {
  controls: [{ k: 'w', label: 'Spin (rad/s)', min: 60, max: 2000, step: 10, v: 300, f: 0 }, { k: 'l', label: 'Pivot to centre of mass (mm)', min: 10, max: 80, step: 1, v: 40, f: 0 }],
  draw(p, v, out) {
    const m = 0.15, g = 9.81, l = v.l / 1000, I1 = 4e-5 * (l / 0.04) ** 2 + 1e-5, I3 = 6e-5, w3 = v.w, th0 = Math.PI / 2, pphi = I3 * w3 * Math.cos(th0), dt = 2e-4, T = 3;
    const f = (s) => { const [th, thd] = s, sn = Math.sin(th), phd = (pphi - I3 * w3 * Math.cos(th)) / (I1 * sn * sn); return [thd, (phd * phd * sn * Math.cos(th) * I1 - I3 * w3 * phd * sn + m * g * l * sn) / I1, phd]; };
    let s = [th0, 0, 0]; const ts = [0], ph = [0], tl = [0];
    for (let i = 1; i <= T / dt; i++) { const k1 = f(s), k2 = f(s.map((q, j) => q + dt / 2 * k1[j])), k3 = f(s.map((q, j) => q + dt / 2 * k2[j])), k4 = f(s.map((q, j) => q + dt * k3[j])); s = s.map((q, j) => q + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])); if (i % 25 === 0) { ts.push(i * dt); ph.push(s[2] * 180 / Math.PI); tl.push((s[0] - th0) * 180 / Math.PI); } }
    const Om = m * g * l / (I3 * w3), top = Math.max(30, ph[ph.length - 1] * 1.1);
    p.frame({ x: [0, T], y: [0, top], xlabel: 'time, s', ylabel: 'precession angle, degrees' });
    p.line([0, T], [0, Om * T * 180 / Math.PI], C.grey, 1.5, [5, 4]).line(ts, ph, C.lime, 2.5);
    out(`Simulated precession ${nf(3).format(s[2] / T)} rad/s; fast-top formula Ω = mgl/(I₃ω) = ${nf(3).format(Om)} rad/s (dashed), one turn every ${nf(1).format(2 * Math.PI / Om)} s. The axis dips and wobbles (nutation) by ${nf(2).format(Math.max(...tl.map(Math.abs)))}°. Spin faster: slower precession, smaller wobble, closer to the formula.`);
  },
});

// 07.17 flywheel spin-up with burst warning
def('flyburst', {
  controls: [{ k: 'rpm', label: 'Speed (rpm)', min: 0, max: 40000, step: 500, v: 15000, f: 0 }, { k: 'R', label: 'Rim mean radius (m)', min: 0.1, max: 1, step: 0.05, v: 0.25, f: 2 }, { type: 'select', k: 'mat', label: 'Rim material', options: ['steel (800 MPa)', 'carbon fibre (1500 MPa)'], v: 'carbon fibre (1500 MPa)' }],
  draw(p, v, out) {
    const steel = v.mat.startsWith('steel'), rho = steel ? 7850 : 1600, sl = steel ? 800 : 1500, m = 60;
    const rpms = linspace(0, 40000, 200), sig = (n) => rho * (n * Math.PI / 30 * v.R) ** 2 / 1e6;
    p.frame({ x: [0, 40000], y: [0, 2500], xlabel: 'speed, rpm', ylabel: 'rim hoop stress, MPa' });
    p.line([0, 40000], [sl, sl], C.red, 1.5, [5, 4]).line([0, 40000], [sl / 1.5, sl / 1.5], C.amber, 1, [2, 4]);
    p.line(rpms, rpms.map(sig), C.lime, 2.5);
    const s = sig(v.rpm), w = v.rpm * Math.PI / 30, E = 0.5 * m * v.R * v.R * w * w / 3.6e6, burst = Math.sqrt(sl * 1e6 / rho) / v.R * 30 / Math.PI;
    p.dots([v.rpm], [s], s > sl ? C.red : s > sl / 1.5 ? C.amber : C.cyan, 6);
    out(`${s > sl ? 'BURST: the rim stress exceeds the material strength. ' : s > sl / 1.5 ? 'Warning: inside the 1.5 safety margin. ' : ''}Rim speed ${nf(0).format(w * v.R)} m/s, hoop stress ρv² = ${nf(0).format(s)} MPa. A 60 kg rim stores ${nf(3).format(E)} kWh. Burst at ${nf(0).format(burst)} rpm, which is ρv² = σ at v = ${nf(0).format(Math.sqrt(sl * 1e6 / rho))} m/s, the same rim speed for any radius.`);
  },
});

// 07.18 double pendulum chaos
def('dpend', {
  controls: [{ k: 'a', label: 'Upper arm start angle (°)', min: 0, max: 170, step: 1, v: 115, f: 0 }, { k: 'b', label: 'Lower arm start angle (°)', min: 0, max: 170, step: 1, v: 143, f: 0 }, { k: 't', label: 'Time (s)', min: 0, max: 20, step: 0.1, v: 8, f: 1 }],
  draw(p, v, out) {
    const g = 9.81, d2r = Math.PI / 180, dt = 0.002;
    const f = ([a, b, wa, wb]) => { const d = a - b, den = 3 - Math.cos(2 * d); return [wa, wb, (-3 * g * Math.sin(a) - g * Math.sin(a - 2 * b) - 2 * Math.sin(d) * (wb * wb + wa * wa * Math.cos(d))) / den, (2 * Math.sin(d) * (2 * wa * wa + 2 * g * Math.cos(a) + wb * wb * Math.cos(d))) / den]; };
    const E = ([a, b, wa, wb]) => wa * wa + 0.5 * wb * wb + wa * wb * Math.cos(a - b) - 2 * g * Math.cos(a) - g * Math.cos(b);
    const run = (s) => { const tr = [[], []]; const n = Math.round(v.t / dt); for (let i = 0; i < n; i++) { const k1 = f(s), k2 = f(s.map((q, j) => q + dt / 2 * k1[j])), k3 = f(s.map((q, j) => q + dt / 2 * k2[j])), k4 = f(s.map((q, j) => q + dt * k3[j])); s = s.map((q, j) => q + dt / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])); if (i % 5 === 0 && i > n - 1500) { tr[0].push(Math.sin(s[0]) + Math.sin(s[1])); tr[1].push(-Math.cos(s[0]) - Math.cos(s[1])); } } return { s, tr }; };
    const s0 = [v.a * d2r, v.b * d2r, 0, 0], A = run(s0), B = run([s0[0] + 1e-6, s0[1], 0, 0]);
    fitAt(p, 0, 0, 2.2, 2.2, 'x, m', 'y, m');
    p.line(B.tr[0], B.tr[1], 'rgba(255,90,54,0.45)', 1).line(A.tr[0], A.tr[1], 'rgba(238,255,65,0.6)', 1.2);
    const draw = (s, col) => { const x1 = Math.sin(s[0]), y1 = -Math.cos(s[0]), x2 = x1 + Math.sin(s[1]), y2 = y1 - Math.cos(s[1]); p.line([0, x1, x2], [0, y1, y2], col, 3).dots([x1, x2], [y1, y2], col, 5); };
    draw(B.s, C.red); draw(A.s, C.paper);
    out(`Two 1 kg, 1 m pendulums from Lagrange's equations, RK4. The red one started 0.000001 rad different. Energy drift ${nf(1).format(Math.abs(E(A.s) / E(s0) - 1) * 1e6)} ppm. Small starting angles: they stay together. Large ones: within seconds they swing completely differently. That is chaos.`);
  },
});

// 07.19 train on a canted curve
def('railcant', {
  controls: [{ k: 'kmh', label: 'Speed (km/h)', min: 0, max: 250, step: 5, v: 160, f: 0 }, { k: 'R', label: 'Curve radius (m)', min: 300, max: 4000, step: 50, v: 1200, f: 0 }, { k: 'c', label: 'Cant (mm)', min: 0, max: 180, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const g = 9.81, S = 1.5, phi = Math.asin(v.c / 1000 / S), vv = v.kmh / 3.6, an = vv * vv / v.R, a = an * Math.cos(phi) - g * Math.sin(phi), vb = Math.sqrt(g * v.R * Math.tan(phi)) * 3.6;
    fitAt(p, 0, 1.4, 2.2, 1.9, 'm (looking along the track, curve centre to the left)', '');
    const rot = ([x, y]) => [x * Math.cos(phi) - y * Math.sin(phi), x * Math.sin(phi) + y * Math.cos(phi)];
    poly(p, [[-1.6, -0.15], [1.6, -0.15], [1.6, 0], [-1.6, 0]].map(rot), C.grey, 'rgba(154,157,147,0.4)', 1);
    poly(p, [[-1.4, 0.3], [1.4, 0.3], [1.4, 3.2], [-1.4, 3.2]].map(rot), C.paper, 'rgba(242,243,236,0.08)', 1.5);
    const cg = rot([0, 1.7]), k = 0.12;
    // resultant of gravity and the inertial (centrifugal) load, as felt by the coach
    const Fx = an, Fy = -g;
    arrow(p, cg[0], cg[1], cg[0] + k * Fx, cg[1] + k * Fy, C.amber);
    const nrm = rot([0, -1]); p.line([cg[0], cg[0] + 1.3 * nrm[0]], [cg[1], cg[1] + 1.3 * nrm[1]], C.grey, 1, [4, 4]);
    out(`Tilt ${nf(2).format(phi * 180 / Math.PI)}°. Balance speed ${nf(1).format(vb)} km/h. At ${v.kmh} km/h: lateral acceleration along the floor ${nf(3).format(a)} m/s² (${a > 0 ? 'outwards' : 'inwards'}), cant deficiency ${nf(0).format(S * 1000 * an / g - v.c)} mm. The amber arrow (gravity plus the centrifugal load) lines up with the dashed floor normal only at the balance speed. Comfort limit about 1.0 m/s², tilting trains 2.0.`);
  },
});

// 07.20 slider-crank: piston motion and the constraint forces
def('engine', {
  controls: [{ k: 'th', label: 'Crank angle (°)', min: 0, max: 360, step: 2, v: 60, f: 0 }, { k: 'rpm', label: 'Engine speed (rpm)', min: 600, max: 7000, step: 100, v: 3000, f: 0 }],
  draw(p, v, out) {
    const r = 0.05, l = 0.15, m3 = 0.5, w = v.rpm * Math.PI / 30;
    const kin = (t) => { const s = r * Math.sin(t), c = Math.sqrt(l * l - s * s), x = r * Math.cos(t) + c, xd = -r * w * Math.sin(t) - r * r * w * Math.sin(t) * Math.cos(t) / c;
      const xdd = -r * w * w * Math.cos(t) - (r * r * w * w * (Math.cos(t) ** 2 - Math.sin(t) ** 2) * c * c + (r * r * Math.sin(t) * Math.cos(t)) ** 2 * w * w) / (c ** 3); return { x, xd, xdd, s, c }; };
    const ths = linspace(0, 2 * Math.PI, 181), acc = ths.map((t) => kin(t).xdd);
    const top = Math.max(...acc.map(Math.abs)) * 1.1;
    p.frame({ x: [0, 360], y: [-top, top], xlabel: 'crank angle, degrees', ylabel: 'piston acceleration, m/s²' });
    p.line(ths.map((t) => t * 180 / Math.PI), acc, C.lime, 2).line(ths.map((t) => t * 180 / Math.PI), ths.map((t) => -r * w * w * Math.cos(t)), C.grey, 1, [4, 4]);
    const K = kin(v.th * Math.PI / 180); p.dots([v.th], [K.xdd], C.cyan, 6);
    const rodF = m3 * K.xdd / (K.c / l);
    out(`Piston at ${nf(1).format(K.x * 1000)} mm, velocity ${nf(2).format(K.xd)} m/s, acceleration ${nf(0).format(K.xdd)} m/s² (${nf(0).format(K.xdd / 9.81)} g). The rod (a constraint) pushes on the 0.5 kg piston with ${nf(0).format(Math.abs(rodF))} N: in a multibody solver this force is the Lagrange multiplier. Dashed: pure r ω² cos θ; the rod's angle adds the second harmonic.`);
  },
});

// ---------- Phase 08 ----------
// 08.01 mass-spring lab
def('springlab', {
  controls: [{ k: 'm', label: 'Mass (kg)', min: 50, max: 1000, step: 10, v: 300, f: 0 }, { k: 'k', label: 'Spring stiffness (kN/m)', min: 5, max: 100, step: 1, v: 30, f: 0 }, { k: 'x0', label: 'Release from (mm)', min: 5, max: 100, step: 5, v: 50, f: 0 }],
  draw(p, v, out) {
    const m = v.m, k = v.k * 1e3, wn = Math.sqrt(k / m), T = 2 * Math.PI / wn, dt = 1e-3, n = 3000;
    let x = v.x0 / 1000, u = 0, a = -k / m * x; const ts = [0], xs = [x * 1000]; let last = null; const cross = [];
    for (let i = 1; i <= n; i++) { const xn = x + dt * u + 0.5 * dt * dt * a, an = -k / m * xn; u += 0.5 * dt * (a + an); if (x < 0 && xn >= 0) cross.push((i - 1) * dt - x * dt / (xn - x)); x = xn; a = an; ts.push(i * dt); xs.push(x * 1000); }
    const Tm = cross.length > 1 ? (cross[cross.length - 1] - cross[0]) / (cross.length - 1) : NaN;
    p.frame({ x: [0, 3], y: [-110, 110], xlabel: 'time, s', ylabel: 'displacement, mm' }).line(ts, xs, C.lime, 2);
    cross.forEach((c) => p.line([c, c], [-110, 110], C.grey, 1, [3, 4]));
    out(`ω_n = √(k/m) = ${nf(2).format(wn)} rad/s, f_n = ${nf(3).format(wn / 2 / Math.PI)} Hz. Measured period ${isNaN(Tm) ? 'needs two crossings' : nf(4).format(Tm) + ' s'}; 2π√(m/k) = ${nf(4).format(T)} s. Change the release height: the period stays the same.`);
  },
});

// 08.02 free decay with envelope
def('decay', {
  controls: [{ k: 'z', label: 'Damping ratio ζ', min: 0, max: 1.2, step: 0.01, v: 0.1, f: 2 }, { k: 'fn', label: 'Natural frequency (Hz)', min: 0.5, max: 4, step: 0.1, v: 1.6, f: 1 }],
  draw(p, v, out) {
    const wn = 2 * Math.PI * v.fn, z = v.z, ts = linspace(0, 4, 800), x0 = 50;
    let xs;
    if (z < 1) { const wd = wn * Math.sqrt(1 - z * z); xs = ts.map((t) => x0 * Math.exp(-z * wn * t) * (Math.cos(wd * t) + z * wn / wd * Math.sin(wd * t))); }
    else if (z === 1) xs = ts.map((t) => x0 * Math.exp(-wn * t) * (1 + wn * t));
    else { const s = Math.sqrt(z * z - 1), r1 = -wn * (z - s), r2 = -wn * (z + s); xs = ts.map((t) => x0 * (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r2 - r1)); }
    p.frame({ x: [0, 4], y: [-55, 55], xlabel: 'time, s', ylabel: 'displacement, mm' });
    if (z < 1) { const env = ts.map((t) => x0 * Math.exp(-z * wn * t) / Math.sqrt(1 - z * z)); p.line(ts, env, C.amber, 1, [4, 4]).line(ts, env.map((e) => -e), C.amber, 1, [4, 4]); }
    p.line(ts, xs, C.lime, 2);
    if (z > 0 && z < 1) { const d = 2 * Math.PI * z / Math.sqrt(1 - z * z); out(`Underdamped. Each cycle the amplitude falls by e^(−δ) = ${nf(3).format(Math.exp(-d))}, log decrement δ = ${nf(3).format(d)}, period ${nf(3).format(2 * Math.PI / (wn * Math.sqrt(1 - z * z)))} s. Amber: envelope e^(−ζω_n t).`); }
    else if (z === 0) out('No damping: it oscillates for ever with constant amplitude.');
    else out(z === 1 ? 'Critically damped: the fastest return to zero without overshoot.' : 'Overdamped: no oscillation, and a slower return than critical damping.');
  },
});

// 08.03 shaker sweep: amplitude and phase
def('shaker', {
  controls: [{ k: 'r', label: 'Forcing frequency / natural frequency', min: 0.05, max: 3, step: 0.01, v: 0.9, f: 2 }, { k: 'z', label: 'Damping ratio ζ', min: 0.01, max: 0.7, step: 0.01, v: 0.05, f: 2 }],
  draw(p, v, out) {
    const rs = linspace(0.01, 3, 600), z = v.z, amp = (r) => 1 / Math.sqrt((1 - r * r) ** 2 + (2 * z * r) ** 2), ph = (r) => Math.atan2(2 * z * r, 1 - r * r) * 180 / Math.PI;
    p.frame({ x: [0, 3], y: [0, 12], xlabel: 'ω / ω_n', ylabel: 'amplitude / static deflection' });
    p.line(rs, rs.map((r) => Math.min(12, amp(r))), C.lime, 2.5).line(rs, rs.map((r) => ph(r) / 15), C.cyan, 1.5, [5, 3]);
    p.text('cyan: phase lag, 180° at top', 1.3, 8.5, C.cyan);
    const rp = z < 0.7071 ? Math.sqrt(1 - 2 * z * z) : 0;
    if (rp > 0) p.dots([rp], [Math.min(12, amp(rp))], C.amber, 5);
    p.dots([v.r], [Math.min(12, amp(v.r))], C.red, 6);
    out(`At ω/ω_n = ${nf(2).format(v.r)}: amplitude ${nf(2).format(amp(v.r))} × static, lagging the force by ${nf(1).format(ph(v.r))}°. ${rp > 0 ? `Peak ${nf(2).format(amp(rp))} × static at ω/ω_n = √(1 − 2ζ²) = ${nf(3).format(rp)} (amber).` : 'No resonant peak: ζ > 0.707.'}`);
  },
});

// 08.04 bike on cobbles: transmissibility
def('bikebump', {
  controls: [{ k: 'v', label: 'Riding speed (m/s)', min: 0.5, max: 8, step: 0.1, v: 2, f: 1 }, { k: 'z', label: 'Damping ratio ζ', min: 0.05, max: 0.8, step: 0.01, v: 0.3, f: 2 }, { k: 'fn', label: 'Suspension natural frequency (Hz)', min: 1.5, max: 6, step: 0.1, v: 2.8, f: 1 }],
  draw(p, v, out) {
    const T = (r, z) => Math.sqrt((1 + (2 * z * r) ** 2) / ((1 - r * r) ** 2 + (2 * z * r) ** 2)), fs = linspace(0.05, 25, 500), f = v.v / 0.25, r = f / v.fn;
    p.frame({ x: [0, 25], y: [0, 4], xlabel: 'cobble frequency, Hz (cobbles 0.25 m apart)', ylabel: 'transmissibility X / Y' });
    p.rect(Math.SQRT2 * v.fn, 25, 0, 4, 'rgba(238,255,65,0.07)').line([0, 25], [1, 1], C.grey, 1, [4, 4]).line([Math.SQRT2 * v.fn, Math.SQRT2 * v.fn], [0, 4], C.grey, 1, [2, 4]);
    p.line(fs, fs.map((x) => Math.min(4, T(x / v.fn, 0.05))), C.grey, 1).line(fs, fs.map((x) => Math.min(4, T(x / v.fn, v.z))), C.lime, 2.5);
    const Tv = T(r, v.z); p.dots([Math.min(25, f)], [Math.min(4, Tv)], Tv > 1 ? C.red : C.cyan, 6);
    out(`${nf(1).format(v.v)} m/s over cobbles 0.25 m apart shakes the wheel at ${nf(1).format(f)} Hz, r = ${nf(2).format(r)}. The rider moves ${nf(2).format(Tv)} times the cobble height: ${Tv > 1 ? 'amplified, below √2 f_n' : 'isolated, above √2 f_n (shaded)'}. Grey curve: ζ = 0.05 for comparison.`);
  },
});

// 08.05 washing machine spin-up
def('washer', {
  controls: [{ k: 'rpm', label: 'Drum speed (rpm)', min: 0, max: 1600, step: 10, v: 1400, f: 0 }, { k: 'z', label: 'Damping ratio ζ', min: 0.02, max: 0.5, step: 0.01, v: 0.1, f: 2 }, { k: 'm', label: 'Unbalanced laundry (kg)', min: 0.1, max: 2, step: 0.1, v: 0.5, f: 1 }],
  draw(p, v, out) {
    const M = 40, e = 0.25, k = 40e3, wn = Math.sqrt(k / M), X = (n) => { const r = n * Math.PI / 30 / wn; return v.m * e / M * r * r / Math.sqrt((1 - r * r) ** 2 + (2 * v.z * r) ** 2) * 1000; };
    const ns = linspace(0, 1600, 800);
    p.frame({ x: [0, 1600], y: [0, Math.max(10, Math.min(60, 1.15 * X(wn * 30 / Math.PI)))], xlabel: 'drum speed, rpm', ylabel: 'drum amplitude, mm' });
    p.line([0, 1600], [v.m * e / M * 1000, v.m * e / M * 1000], C.amber, 1, [4, 4]).line(ns, ns.map(X), C.lime, 2.5).dots([v.rpm], [X(v.rpm)], C.red, 6);
    const r = v.rpm * Math.PI / 30 / wn, FT = k * X(v.rpm) / 1000 * Math.sqrt(1 + (2 * v.z * r) ** 2);
    out(`At ${v.rpm} rpm the drum moves ±${nf(2).format(X(v.rpm))} mm and pushes ${nf(0).format(FT)} N into the floor. Resonance is at ${nf(0).format(wn * 30 / Math.PI)} rpm (±${nf(1).format(X(wn * 30 / Math.PI))} mm); the machine passes through it quickly. At high speed the amplitude settles at m e / M = ${nf(2).format(v.m * e / M * 1000)} mm (amber).`);
  },
});

// 08.06 coupled pendulums: beats
def('coupled', {
  controls: [{ k: 'ks', label: 'Coupling spring (N/m)', min: 0.05, max: 3, step: 0.05, v: 0.5, f: 2 }, { k: 'mode', label: 'Start', type: 'select', options: ['one pendulum pulled aside', 'in phase (mode 1)', 'opposite (mode 2)'], v: 'one pendulum pulled aside' }],
  draw(p, v, out) {
    const g = 9.81, w1 = Math.sqrt(g), w2 = Math.sqrt(g + 2 * v.ks), ts = linspace(0, 60, 2400);
    const [a, b] = v.mode.startsWith('one') ? [0.05, 0.05] : v.mode.startsWith('in') ? [0.1, 0] : [0, 0.1];
    const t1 = ts.map((t) => a * Math.cos(w1 * t) + b * Math.cos(w2 * t)), t2 = ts.map((t) => a * Math.cos(w1 * t) - b * Math.cos(w2 * t));
    p.frame({ x: [0, 60], y: [-0.25, 0.25], xlabel: 'time, s', ylabel: 'angle, rad (pendulum 2 offset down)' });
    p.line(ts, t1.map((x) => x + 0.11), C.lime, 1.5).line(ts, t2.map((x) => x - 0.11), C.cyan, 1.5);
    p.text('pendulum 1', 1, 0.235, C.lime).text('pendulum 2', 1, -0.235, C.cyan);
    const Tb = 2 * Math.PI / (w2 - w1);
    out(`Modes: in phase at ${nf(4).format(w1)} rad/s (the spring never stretches), opposite at ${nf(4).format(w2)} rad/s. ${v.mode.startsWith('one') ? `Starting one pendulum excites both modes equally, so the motion beats: all the energy passes to pendulum 2 and back every ${nf(1).format(Tb)} s.` : 'Started in a mode shape, the motion stays in that mode for ever.'}`);
  },
});

// 08.07 tuned mass damper on a footbridge
def('tmdbridge', {
  controls: [{ k: 'mu', label: 'TMD mass / bridge modal mass (%)', min: 0.5, max: 8, step: 0.5, v: 2, f: 1 }, { k: 'f', label: 'TMD tuning (frequency ratio)', min: 0.8, max: 1.2, step: 0.005, v: 0.98, f: 3 }, { k: 'z', label: 'TMD damping ratio', min: 0.01, max: 0.3, step: 0.005, v: 0.085, f: 3 }],
  draw(p, v, out) {
    const mu = v.mu / 100, zs = 0.005, rs = linspace(0.75, 1.25, 700);
    const X = (r, on) => { if (!on) return 1 / Math.hypot(1 - r * r, 2 * zs * r); const k2 = mu * v.f * v.f, c2 = 2 * v.z * mu * v.f;
      // complex 2x2 solve, first unknown: X1 = a22 / (a11 a22 - a12^2)
      const a11 = [1 + k2 - r * r, r * (2 * zs + c2)], a12 = [-k2, -r * c2], a22 = [k2 - mu * r * r, r * c2];
      const mul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]], d1 = mul(a11, a22), d2 = mul(a12, a12), det = [d1[0] - d2[0], d1[1] - d2[1]];
      return Math.hypot(...a22) / Math.hypot(...det); };
    const on = rs.map((r) => X(r, 1)), pk = Math.max(...on), fdh = 1 / (1 + mu), zdh = Math.sqrt(3 * mu / (8 * (1 + mu) ** 3));
    p.frame({ x: [0.75, 1.25], y: [0, 40], xlabel: 'forcing frequency / bridge frequency', ylabel: 'amplitude / static deflection' });
    p.line(rs, rs.map((r) => Math.min(40, X(r, 0))), C.red, 1.5).line(rs, on, C.lime, 2.5);
    p.text('no TMD (peak 100)', 1.03, 37, C.red);
    out(`With the TMD the worst-case amplification is ${nf(1).format(pk)}, down from 100 without it. Den Hartog's recipe for ${nf(1).format(v.mu)} %: tuning ${nf(3).format(fdh)}, damping ${nf(3).format(zdh)}. Too little TMD damping splits the peak into two tall ones; too much locks the TMD to the bridge.`);
  },
});

// 08.08 five-storey shear building modes
def('building5', {
  controls: [{ k: 'mode', label: 'Mode', min: 1, max: 5, step: 1, v: 1, f: 0 }, { k: 'ph', label: 'Phase of the swing (°)', min: 0, max: 360, step: 5, v: 90, f: 0 }],
  draw(p, v, out) {
    const n = 5, m = 20e3, k = 40e6, i = v.mode, w = 2 * Math.sqrt(k / m) * Math.sin((2 * i - 1) * Math.PI / (2 * (2 * n + 1)));
    // shear building with fixed base and free top: mode shapes sin((2i-1) j pi / (2n+1))
    const sh = range(0, n).map((j) => Math.sin((2 * i - 1) * j * Math.PI / (2 * n + 1))), top = sh[n], s = Math.sin(v.ph * Math.PI / 180) * 0.9 / Math.abs(top) * Math.sign(top);
    fitAt(p, 0, 2.6, 2.3, 2.9, 'sway (exaggerated)', 'floor');
    p.line([-2, 2], [0, 0], C.grey, 2);
    for (let j = 1; j <= n; j++) { const x0 = sh[j - 1] * s, x1 = sh[j] * s; p.line([x0 - 1, x1 - 1], [j - 1, j], C.paper, 2).line([x0 + 1, x1 + 1], [j - 1, j], C.paper, 2).line([x1 - 1.1, x1 + 1.1], [j, j], C.lime, 4); }
    p.line(sh.map((y) => y * 0.9 / Math.abs(top) * Math.sign(top)), range(0, n), C.amber, 1, [3, 4]);
    const L = sh.slice(1).reduce((a, b) => a + b, 0) * m, Mn = sh.slice(1).reduce((a, b) => a + b * b, 0) * m;
    out(`Mode ${i}: ${nf(3).format(w / 2 / Math.PI)} Hz, ${i === 1 ? 'all floors sway the same way' : `with ${i - 1} point${i === 2 ? '' : 's'} up the height where the sway changes sign`}. It carries ${nf(1).format(L * L / Mn / (n * m) * 100)} % of the building's mass in an earthquake, so mode 1 dominates. Amber: the mode shape.`);
  },
});

// 08.09 plucked string: shape and harmonics
def('pluck', {
  controls: [{ k: 'xp', label: 'Pluck position (fraction of length)', min: 0.05, max: 0.5, step: 0.01, v: 0.2, f: 2 }, { k: 't', label: 'Time (fraction of a period)', min: 0, max: 1, step: 0.01, v: 0.15, f: 2 }],
  draw(p, v, out) {
    const N = 60, xp = v.xp, b = range(1, N).map((n) => 2 / (n * n * Math.PI * Math.PI * xp * (1 - xp)) * Math.sin(n * Math.PI * xp)), xs = linspace(0, 1, 300);
    const y = xs.map((x) => b.reduce((s, bn, i) => s + bn * Math.sin((i + 1) * Math.PI * x) * Math.cos((i + 1) * 2 * Math.PI * v.t), 0));
    p.frame({ x: [0, 1], y: [-1.6, 1.15], xlabel: 'position along the string; bars: harmonic amplitude', ylabel: '' });
    p.line(xs, y, C.lime, 2.5).dots([xp], [1], C.amber, 5);
    const bmax = Math.abs(b[0]);
    for (let n = 1; n <= 12; n++) { const h = Math.abs(b[n - 1]) / bmax * 0.4, x0 = (n - 0.8) / 12.5, x1 = (n - 0.2) / 12.5; p.rect(x0, x1, -1.55, -1.55 + h, Math.abs(b[n - 1]) / bmax < 1e-6 ? C.red : 'rgba(92,200,255,0.8)'); }
    const miss = range(1, 12).filter((n) => Math.abs(b[n - 1]) / bmax < 1e-6);
    out(`Plucked at ${nf(2).format(xp)} of the length. Bars: amplitudes of harmonics 1 to 12 (frequencies f, 2f, 3f, …). ${miss.length ? `Harmonic${miss.length > 1 ? 's' : ''} ${miss.join(', ')} ${miss.length > 1 ? 'are' : 'is'} missing: their nodes sit at the pluck point.` : 'No harmonic up to 12 has a node exactly at the pluck point.'} Plucking near the middle sounds round; near the bridge, bright.`);
  },
});

// 08.10 rod modes: axial or torsional
def('rodmode', {
  controls: [{ k: 'n', label: 'Mode number', min: 1, max: 5, step: 1, v: 1, f: 0 }, { k: 'L', label: 'Rod length (m)', min: 0.5, max: 10, step: 0.5, v: 2, f: 1 }, { type: 'select', k: 'bc', label: 'Ends', options: ['fixed-free', 'fixed-fixed'], v: 'fixed-free' }, { type: 'select', k: 'kind', label: 'Motion (steel)', options: ['axial (c = √(E/ρ))', 'torsional (c = √(G/ρ))'], v: 'axial (c = √(E/ρ))' }],
  draw(p, v, out) {
    const c = v.kind.startsWith('axial') ? Math.sqrt(210e9 / 7850) : Math.sqrt(81e9 / 7850), ff = v.bc === 'fixed-free', n = v.n;
    const k = ff ? (2 * n - 1) * Math.PI / (2 * v.L) : n * Math.PI / v.L, f = c * k / (2 * Math.PI), xs = linspace(0, v.L, 300);
    p.frame({ x: [0, v.L], y: [-1.3, 1.3], xlabel: 'position along the rod, m', ylabel: v.kind.startsWith('axial') ? 'axial displacement' : 'twist angle' });
    p.line(xs, xs.map((x) => Math.sin(k * x)), C.lime, 2.5).line([0, v.L], [0, 0], C.grey, 1);
    const nodes = []; for (let j = 0; j <= 2 * n; j++) { const x = j * Math.PI / k; if (x <= v.L + 1e-9) nodes.push(x); }
    p.dots(nodes, nodes.map(() => 0), C.amber, 5);
    out(`${v.bc}, mode ${n}: f = ${nf(1).format(f)} Hz with c = ${nf(0).format(c)} m/s. ${ff ? `Fixed-free modes are odd multiples of c/(4L) = ${nf(1).format(c / (4 * v.L))} Hz: 1, 3, 5, …` : `Fixed-fixed modes are whole multiples of c/(2L) = ${nf(1).format(c / (2 * v.L))} Hz.`} Amber: nodes (no motion).`);
  },
});

// 08.11 cantilever bending modes
def('cantimode', {
  controls: [{ k: 'n', label: 'Mode', min: 1, max: 4, step: 1, v: 1, f: 0 }, { k: 'L', label: 'Overhang (mm)', min: 100, max: 400, step: 10, v: 300, f: 0 }, { k: 't', label: 'Thickness (mm)', min: 0.5, max: 3, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const bl = [1.875104, 4.694091, 7.854757, 10.995541][v.n - 1], L = v.L / 1000, t = v.t / 1000, E = 200e9, rho = 7850;
    const f = bl * bl / (2 * Math.PI) * Math.sqrt(E * t * t / 12 / (rho * L ** 4)), s = (Math.cosh(bl) + Math.cos(bl)) / (Math.sinh(bl) + Math.sin(bl));
    const xs = linspace(0, 1, 300), ph = (x) => Math.cosh(bl * x) - Math.cos(bl * x) - s * (Math.sinh(bl * x) - Math.sin(bl * x)), tip = ph(1);
    p.frame({ x: [-0.08, 1], y: [-1.4, 1.4], xlabel: 'x / L (clamped at 0)', ylabel: 'deflection (normalised)' });
    p.rect(-0.08, 0, -1.4, 1.4, 'rgba(154,157,147,0.35)');
    p.line(xs, xs.map((x) => ph(x) / tip), C.lime, 2.5).line(xs, xs.map((x) => -ph(x) / tip), C.lime, 1, [3, 4]).line([0, 1], [0, 0], C.grey, 1);
    out(`Steel ruler, ${v.L} mm overhang, ${nf(1).format(v.t)} mm thick: mode ${v.n} at ${nf(2).format(f)} Hz (β L = ${nf(4).format(bl)}). Higher modes go as (βL)²: 1, 6.27, 17.5, 34.4 times f₁, not whole multiples. Frequency ∝ t / L²: halve the overhang and it rises 4 times.`);
  },
});

// 08.12 Chladni patterns on a square plate (classic approximation)
def('chladni', {
  controls: [{ k: 'm', label: 'm', min: 1, max: 8, step: 1, v: 4, f: 0 }, { k: 'n', label: 'n', min: 0, max: 8, step: 1, v: 1, f: 0 }, { type: 'select', k: 'sg', label: 'Combination', options: ['plus', 'minus'], v: 'plus' }],
  draw(p, v, out) {
    const sgn = v.sg === 'plus' ? 1 : -1, F = (x, y) => Math.cos(v.n * Math.PI * x) * Math.cos(v.m * Math.PI * y) + sgn * Math.cos(v.m * Math.PI * x) * Math.cos(v.n * Math.PI * y);
    sqAt(p, 0.5, 0.5, 0.52, '', '');
    const e = 1e-4, dist = (x, y) => Math.abs(F(x, y)) / (Math.hypot(F(x + e, y) - F(x - e, y), F(x, y + e) - F(x, y - e)) / (2 * e) + 1e-9);
    bands(p, (x, y) => (x < 0 || x > 1 || y < 0 || y > 1) ? 0 : Math.max(0, 1 - dist(x, y) / 0.012), 0, 1, 6, 260);
    poly(p, [[0, 0], [1, 0], [1, 1], [0, 1]], C.grey, null, 1);
    const zero = v.m === v.n && sgn < 0;
    out(zero ? 'With m = n the minus combination cancels everywhere: no vibration. Pick different m and n.' : `Bright lines: where sand gathers, the nodal lines of cos(${v.n}πx)cos(${v.m}πy) ${sgn > 0 ? '+' : '−'} cos(${v.m}πx)cos(${v.n}πy). Two modes of the same frequency combine, so a square plate shows patterns neither shows alone.`);
  },
});

// 08.13 hammer test FRF of a 3-storey frame
def('frfhammer', {
  controls: [{ type: 'select', k: 'tap', label: 'Tap at floor', options: ['1', '2', '3'], v: '3' }, { type: 'select', k: 'meas', label: 'Measure at floor', options: ['1', '2', '3'], v: '3' }, { k: 'z', label: 'Damping ratio ζ (%)', min: 0.2, max: 10, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const n = 3, m = 2, k = 8000, z = v.z / 100, i = +v.tap, j = +v.meas, modes = [];
    for (let r = 1; r <= n; r++) { const w = 2 * Math.sqrt(k / m) * Math.sin((2 * r - 1) * Math.PI / (2 * (2 * n + 1))), sh = range(1, n).map((q) => Math.sin((2 * r - 1) * q * Math.PI / (2 * n + 1))), nm = Math.sqrt(m * sh.reduce((a, b) => a + b * b, 0)); modes.push({ w, ph: sh.map((s) => s / nm) }); }
    const fs = linspace(0.5, 25, 1200), H = (f) => { const w = 2 * Math.PI * f; let re = 0, im = 0; for (const md of modes) { const a = md.ph[i - 1] * md.ph[j - 1], dr = md.w * md.w - w * w, di = 2 * z * md.w * w, d = dr * dr + di * di; re += a * dr / d; im -= a * di / d; } return Math.hypot(re, im); };
    p.frame({ x: [0.5, 25], y: [1e-6, 1e-1], ylog: true, xlabel: 'frequency, Hz', ylabel: '|H|, m/N' });
    p.line(fs, fs.map((f) => Math.max(1e-6, H(f))), C.lime, 2);
    modes.forEach((md) => p.line([md.w / 2 / Math.PI, md.w / 2 / Math.PI], [1e-6, 1e-1], C.grey, 1, [3, 4]));
    const weak = modes.map((md, r) => Math.abs(md.ph[i - 1] * md.ph[j - 1]) < 0.15 * Math.max(...modes.map((q) => Math.abs(q.ph[i - 1] * q.ph[j - 1]))) ? r + 1 : 0).filter(Boolean);
    out(`Modes at ${modes.map((md) => nf(2).format(md.w / 2 / Math.PI)).join(', ')} Hz (dashed). Each peak's height is set by the mode shape at the tap and sensor points times 1/(2ζω²). ${weak.length ? `Mode ${weak.join(' and ')} is weak here: tap or sensor sits near its node, so test at more than one point.` : ''} Half-power width of each peak ≈ 2ζf.`);
  },
});

// 08.14 Duffing response curve and jumps
def('duffjump', {
  controls: [{ k: 'F', label: 'Forcing amplitude F', min: 0.01, max: 0.2, step: 0.005, v: 0.1, f: 3 }, { k: 'b', label: 'Hardening β', min: -0.2, max: 2, step: 0.05, v: 1, f: 2 }, { type: 'select', k: 'dir', label: 'Sweep', options: ['up', 'down'], v: 'up' }],
  draw(p, v, out) {
    const z = 0.02, F = v.F, b = v.b, ws = linspace(0.5, 2.2, 400);
    const G = (A, w) => ((1 - w * w) * A + 0.75 * b * A ** 3) ** 2 + (2 * z * w * A) ** 2 - F * F;
    const roots = (w) => { const r = []; const N = 900, Amax = 4; let a0 = 1e-6, g0 = G(a0, w); for (let s = 1; s <= N; s++) { const a1 = Amax * s / N, g1 = G(a1, w); if (g0 * g1 < 0) { let lo = a0, hi = a1; for (let it = 0; it < 50; it++) { const mid = 0.5 * (lo + hi); if (G(lo, w) * G(mid, w) <= 0) hi = mid; else lo = mid; } r.push(0.5 * (lo + hi)); } a0 = a1; g0 = g1; } return r; };
    const R = ws.map(roots);
    p.frame({ x: [0.5, 2.2], y: [0, 3], xlabel: 'forcing frequency ω / ω_n', ylabel: 'amplitude' });
    const lo = [], hi = [], mid = [];
    R.forEach((r, q) => { if (r.length === 1) { lo.push([ws[q], r[0]]); hi.push([ws[q], r[0]]); } else if (r.length >= 3) { lo.push([ws[q], r[0]]); mid.push([ws[q], r[1]]); hi.push([ws[q], r[2]]); } });
    p.dots(mid.map((a) => a[0]), mid.map((a) => a[1]), C.grey, 1.2);
    // sweep path: up follows the highest stable branch until it ends; down follows the lowest
    const path = []; let jump = null;
    if (v.dir === 'up') { let on = 'hi'; ws.forEach((w, q) => { const r = R[q]; if (!r.length) return; let a = r.length === 1 ? r[0] : on === 'hi' ? r[r.length - 1] : r[0]; if (r.length === 1 && path.length && path[path.length - 1][1] - a > 0.3) { jump = [w, path[path.length - 1][1], a]; on = 'lo'; } path.push([w, a]); }); }
    else { for (let q = ws.length - 1; q >= 0; q--) { const r = R[q]; if (!r.length) continue; const a = r[0]; if (path.length && a - path[path.length - 1][1] > 0.3) jump = [ws[q], path[path.length - 1][1], a]; path.push([ws[q], a]); } }
    p.dots(lo.map((a) => a[0]), lo.map((a) => a[1]), C.cyan, 1.2).dots(hi.map((a) => a[0]), hi.map((a) => a[1]), C.cyan, 1.2);
    p.line(path.map((a) => a[0]), path.map((a) => a[1]), C.lime, 2.5);
    if (jump) arrow(p, jump[0], jump[1], jump[0], jump[2], C.red, 2);
    out(`${jump ? `Sweeping ${v.dir}, the amplitude jumps ${v.dir === 'up' ? 'down' : 'up'} at ω ≈ ${nf(2).format(jump[0])} (red arrow). Between the two jump frequencies there are three solutions; the middle one (grey) is unstable, so up and down sweeps follow different branches: hysteresis.` : 'No jump at this forcing: the curve is single-valued, as for a linear system. Increase F or |β|.'} ${b < 0 ? 'Negative β softens the spring and bends the peak to the left.' : ''}`);
  },
});

// 08.15 Van der Pol phase plane
def('vdpplane', {
  controls: [{ k: 'mu', label: 'Nonlinear damping μ', min: 0.05, max: 5, step: 0.05, v: 1, f: 2 }, { k: 'T', label: 'Time simulated', min: 2, max: 40, step: 1, v: 25, f: 0 }],
  draw(p, v, out) {
    const mu = v.mu, dt = 0.005, f = ([x, y]) => [y, mu * (1 - x * x) * y - x], starts = [[0.05, 0], [3.5, 0], [-3, 3], [0, -4]], cols = [C.lime, C.cyan, C.amber, C.red];
    fitAt(p, 0, 0, 4.2, Math.max(4.5, 2.2 * mu + 2.5), 'x', 'dx/dt');
    let A = 0, Tp = NaN;
    starts.forEach((s0, q) => { let s = s0.slice(); const xs = [s[0]], ys = [s[1]]; const cr = []; let px = s[0]; for (let i = 1; i <= v.T / dt; i++) { const k1 = f(s), k2 = f([s[0] + dt / 2 * k1[0], s[1] + dt / 2 * k1[1]]), k3 = f([s[0] + dt / 2 * k2[0], s[1] + dt / 2 * k2[1]]), k4 = f([s[0] + dt * k3[0], s[1] + dt * k3[1]]); const xn = s[0] + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); s = [xn, s[1] + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])]; if (i % 2 === 0) { xs.push(s[0]); ys.push(s[1]); } if (q === 0 && i * dt > v.T / 2) { A = Math.max(A, s[0]); if (px < 0 && s[0] >= 0) cr.push(i * dt); } px = s[0]; }
      p.line(xs, ys, cols[q], 1.5).dots([s0[0]], [s0[1]], cols[q], 4); if (q === 0 && cr.length > 1) Tp = (cr[cr.length - 1] - cr[0]) / (cr.length - 1); });
    out(`Four starts, inside and outside. All spiral onto the same closed loop, the limit cycle${A ? `: amplitude ≈ ${nf(2).format(A)}` : ''}${isNaN(Tp) ? '' : `, period ≈ ${nf(2).format(Tp)}`}. Inside |x| < 1 the damping is negative and pumps energy in; outside it removes energy. ${mu > 2.5 ? 'Large μ: a relaxation oscillation, slow creeps and fast snaps, like brake squeal or a squeaky door.' : ''}`);
  },
});

// 08.16 striker hits a bar: stress waves
def('rodimpact', {
  controls: [{ k: 't', label: 'Time (ms)', min: 0, max: 1.2, step: 0.01, v: 0.25, f: 2 }, { k: 'L1', label: 'Striker length (m)', min: 0.2, max: 1.5, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const c = Math.sqrt(210e9 / 7850), Z = 7850 * c, v0 = 5, npm = 100, dx = 1 / npm, dt = dx / c, n1 = Math.round(v.L1 * npm), n2 = 2 * npm, N = n1 + n2;
    let f = new Float64Array(N), g = new Float64Array(N); for (let q = 0; q < n1; q++) { f[q] = g[q] = v0 / 2; } let contact = true;
    const steps = Math.round(v.t * 1e-3 / dt);
    for (let s = 0; s < steps; s++) { if (contact && Z * (g[n1] - f[n1 - 1]) > 0) contact = false; const fn = new Float64Array(N), gn = new Float64Array(N); for (let q = 1; q < N; q++) fn[q] = f[q - 1]; for (let q = 0; q < N - 1; q++) gn[q] = g[q + 1]; fn[0] = g[0]; gn[N - 1] = f[N - 1]; if (!contact) { gn[n1 - 1] = f[n1 - 1]; fn[n1] = g[n1]; } f = fn; g = gn; }
    const xs = [], ss = []; for (let q = 0; q < N; q++) { xs.push(-v.L1 + (q + 0.5) * dx); ss.push(Z * (g[q] - f[q]) / 1e6); }
    p.frame({ x: [-1.5, 2], y: [-130, 130], xlabel: 'position, m (striker left of 0, bar right)', ylabel: 'stress, MPa (tension +)' });
    p.rect(-v.L1, 0, -130, 130, 'rgba(154,157,147,0.12)').line([-1.5, 2], [0, 0], C.grey, 1);
    p.line(xs.slice(0, n1), ss.slice(0, n1), C.cyan, 2).line(xs.slice(n1), ss.slice(n1), C.lime, 2.5);
    out(`t = ${nf(2).format(v.t)} ms. Impact at 5 m/s sends a −${nf(1).format(Z * v0 / 2 / 1e6)} MPa compression pulse (ρcv/2) into each rod. The striker's pulse reflects from its free end and unloads it after 2L₁/c = ${nf(3).format(2 * v.L1 / c * 1e3)} ms, so the bar carries a pulse 2L₁ long. At the bar's free end the compression reflects as tension. ${contact ? '' : 'The rods have separated.'}`);
  },
});

// ---------- Phase 09 ----------
// 09.01 Lennard-Jones well, force and harmonic fit
def('ljwell', {
  controls: [{ k: 'r', label: 'Separation r / r₀', min: 0.9, max: 1.6, step: 0.005, v: 1.05, f: 3 }, { k: 'show', label: 'Show the parabola fitted at r₀', type: 'check', v: 1 }],
  draw(p, v, out) {
    const r0 = Math.pow(2, 1 / 6), V = (x) => { const r = x * r0; return 4 * (r ** -12 - r ** -6); }, Fo = (x) => { const r = x * r0; return 24 / r * (2 * r ** -12 - r ** -6); };
    const S = 72 / Math.pow(2, 1 / 3), xs = linspace(0.88, 1.8, 400);
    p.frame({ x: [0.88, 1.8], y: [-1.6, 1.2], xlabel: 'separation r / r₀', ylabel: 'energy / ε (lime), force (cyan)' });
    p.line([0.88, 1.8], [0, 0], C.grey, 1);
    if (v.show) p.line(xs, xs.map((x) => -1 + 0.5 * S * ((x - 1) * r0) ** 2), C.amber, 1, [4, 4]);
    p.line(xs, xs.map((x) => Math.min(1.2, V(x))), C.lime, 2.5).line(xs, xs.map((x) => Math.max(-1.6, Math.min(1.2, Fo(x) / 3))), C.cyan, 1.5);
    p.dots([v.r], [Math.min(1.2, V(v.r))], C.red, 6);
    const F = Fo(v.r), lin = -S * (v.r - 1) * r0;
    out(`At r = ${nf(3).format(v.r)} r₀ the bond force is ${nf(3).format(F)} ε/σ (${F > 0 ? 'repulsive' : 'attractive'}); a linear spring of stiffness V''(r₀) = ${nf(2).format(S)} ε/σ² would give ${nf(3).format(lin)}. Near r₀ they agree: Hooke's law. The attraction peaks at 1.109 r₀, the bond's theoretical strength. The well is lopsided, so hot atoms sit further apart: thermal expansion.`);
  },
});

// 09.02 cubic unit cells
def('unitcell', {
  controls: [{ type: 'select', k: 'kind', label: 'Lattice', options: ['SC', 'BCC', 'FCC'], v: 'FCC' }, { k: 'rot', label: 'Rotate (°)', min: 0, max: 90, step: 1, v: 30, f: 0 }, { k: 'size', label: 'Atom size (fraction of touching)', min: 0.2, max: 1, step: 0.05, v: 0.55, f: 2 }],
  draw(p, v, out) {
    const B = { SC: [[0, 0, 0]], BCC: [[0, 0, 0], [0.5, 0.5, 0.5]], FCC: [[0, 0, 0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]] }[v.kind];
    const R = { SC: 0.5, BCC: Math.sqrt(3) / 4, FCC: Math.sqrt(2) / 4 }[v.kind], z = { SC: 6, BCC: 8, FCC: 12 }[v.kind];
    const th = v.rot * Math.PI / 180, el = 0.45, proj = ([x, y, zz]) => { x -= 0.5; y -= 0.5; zz -= 0.5; const X = x * Math.cos(th) - y * Math.sin(th), Y = x * Math.sin(th) + y * Math.cos(th); return [X, zz * Math.cos(el) + Y * Math.sin(el), Y * Math.cos(el) - zz * Math.sin(el)]; };
    fitAt(p, 0, 0, 1.0, 1.0, '', '');
    const corners = []; for (const a of [0, 1]) for (const b of [0, 1]) for (const c of [0, 1]) corners.push([a, b, c]);
    for (const a of corners) for (const b of corners) { const d = Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]); if (d === 1 && a < b) { const P = proj(a), Q = proj(b); p.line([P[0], Q[0]], [P[1], Q[1]], C.grey, 1); } }
    const atoms = []; for (const b of B) for (const i of [0, 1]) for (const j of [0, 1]) for (const k of [0, 1]) { const q = [b[0] + i, b[1] + j, b[2] + k]; if (q.every((c) => c <= 1 + 1e-9)) atoms.push(q); }
    const uniq = [...new Map(atoms.map((a) => [a.join(','), a])).values()].map(proj).sort((a, b) => b[2] - a[2]);
    const g = p.g, rp = Math.abs(p.X(R * v.size) - p.X(0));
    for (const [X, Y, D] of uniq) { g.save(); g.beginPath(); g.arc(p.X(X), p.Y(Y), rp, 0, 2 * Math.PI); g.fillStyle = `rgba(238,255,65,${0.25 + 0.5 * (0.9 - D) / 1.8})`; g.strokeStyle = C.ink; g.lineWidth = 1; g.fill(); g.stroke(); g.restore(); }
    const n = B.length, apf = n * 4 / 3 * Math.PI * R ** 3;
    out(`${v.kind}: ${n} atom${n > 1 ? 's' : ''} per cell (corners count 1/8, faces 1/2), each touching ${z} neighbours. Atoms touch along the ${v.kind === 'SC' ? 'cube edge' : v.kind === 'BCC' ? 'body diagonal' : 'face diagonal'}, so R = ${nf(4).format(R)} a and the packing factor is ${nf(4).format(apf)}.`);
  },
});

// 09.03 Frenkel-Kontorova chain: a kink glides
def('fkchain', {
  controls: [{ k: 'F', label: 'Push per atom (fraction of rigid-slip force)', min: 0, max: 0.05, step: 0.001, v: 0.02, f: 3 }, { k: 't', label: 'Time', min: 0, max: 400, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const N = 40, k = 4, V0 = 0.2, Fr = V0 * Math.PI, F = v.F * Fr, dt = 0.4 / (k + 2 * Math.PI ** 2 * V0);
    const x = Array.from({ length: N + 1 }, (_, i) => i - (2 / Math.PI) * Math.atan(Math.exp((i - 12) / 2))); x[N] = N - 1;
    const step = (FF) => { const f = x.map((xi) => FF - V0 * Math.PI * Math.sin(2 * Math.PI * xi)); for (let i = 0; i < N; i++) { const s = x[i + 1] - x[i] - 1; f[i] += k * s; f[i + 1] -= k * s; } f[0] = 0; f[N] = 0; for (let i = 0; i <= N; i++) x[i] += dt * f[i]; };
    for (let i = 0; i < 3000; i++) step(0);
    for (let i = 0; i < v.t / dt; i++) step(F);
    const xs = linspace(-0.5, N - 0.5, 2400);
    p.frame({ x: [-0.5, N - 0.5], y: [-1.2, 1.6], xlabel: 'position (lattice spacings)', ylabel: '' });
    p.line(xs, xs.map((q) => -0.5 - 0.35 * Math.cos(2 * Math.PI * q)), C.grey, 1);
    const w = x.slice(0, -1).map((xi, i) => Math.max(0, 1 - (x[i + 1] - xi))), cen = w.reduce((a, b, i) => a + b * i, 0) / Math.max(1e-9, w.reduce((a, b) => a + b, 0));
    p.dots(x, x.map((xi) => -0.5 - 0.35 * Math.cos(2 * Math.PI * xi)), C.lime, 4);
    p.line(x.slice(0, -1).map((xi, i) => 0.5 * (xi + x[i + 1])), w.map((q) => 0.6 + 2.5 * q), C.amber, 2);
    out(`Lime: atoms on the grey substrate wells. Amber: squeeze between neighbours, which marks the kink (an extra atom, like the extra half-plane of an edge dislocation). Pushing with ${nf(1).format(v.F * 100)} % of the force needed to slide a perfect row, the kink ${Math.abs(cen - 12) > 3 ? `has glided to site ${nf(0).format(cen)}` : 'is held by the lattice'}. A kink moves at about 1.2 % here: that's why real metals yield at a tiny fraction of the ideal strength.`);
  },
});

// 09.04 tensile curve: engineering and true, 0.2 % offset, necking
def('tensilecurve', {
  controls: [{ k: 'n', label: 'Strain-hardening exponent n', min: 0.03, max: 0.4, step: 0.01, v: 0.06, f: 2 }, { k: 'K', label: 'Strength coefficient K (MPa)', min: 200, max: 1200, step: 10, v: 380, f: 0 }, { k: 'tr', label: 'Show true stress-strain', type: 'check', v: 1 }],
  draw(p, v, out) {
    const E = 69e3, K = v.K, n = v.n, ss = linspace(1, K * n ** n, 600), et = ss.map((s) => s / E + (s / K) ** (1 / n)), ee = et.map((e) => Math.exp(e) - 1), se = ss.map((s, i) => s / (1 + ee[i]));
    const xmax = Math.max(0.05, 1.3 * (Math.exp(n) - 1)), ymax = 1.15 * K * n ** n;
    p.frame({ x: [0, xmax * 100], y: [0, ymax], xlabel: 'strain, %', ylabel: 'stress, MPa' });
    // after necking the engineering curve falls: sketch as a smooth drop over a further 40 % of the uniform strain
    const eu = ee[ee.length - 1], su = se[se.length - 1], tail = linspace(0, 1, 40).map((q) => [eu * (1 + 0.4 * q), su * (1 - 0.18 * q * q)]);
    p.line(ee.map((e) => e * 100), se, C.lime, 2.5).line(tail.map((a) => a[0] * 100), tail.map((a) => a[1]), C.lime, 2.5, [5, 3]);
    if (v.tr) p.line(et.map((e) => e * 100), ss, C.cyan, 1.5);
    const sy = K * 0.002 ** n; p.line([0.2, 0.2 + ymax / E * 100], [0, ymax], C.grey, 1, [3, 4]).dots([0.2 + sy / E * 100], [sy], C.amber, 5).dots([eu * 100], [su], C.red, 5);
    out(`0.2 % offset yield ${nf(0).format(sy)} MPa (amber). UTS ${nf(0).format(su)} MPa at ${nf(1).format(eu * 100)} % strain (red): necking starts where the true stress equals its slope, at true plastic strain = n. ${v.tr ? 'Cyan: true stress keeps rising; the engineering curve falls only because the neck shrinks.' : ''} Higher n: more uniform stretch before necking, good for forming.`);
  },
});

// 09.05 Hall-Petch
def('hallpetch', {
  controls: [{ k: 'ld', label: 'Grain size, log₁₀(µm)', min: -0.5, max: 2.7, step: 0.05, v: 1.3, f: 2 }, { k: 'k', label: 'Hall-Petch k (MPa √m)', min: 0.05, max: 1, step: 0.01, v: 0.74, f: 2 }],
  draw(p, v, out) {
    const s0 = 70, d = 10 ** v.ld, sy = (dd) => s0 + v.k / Math.sqrt(dd * 1e-6), ds = logspace(-0.5, 2.7, 200);
    p.frame({ x: [10 ** -0.5, 10 ** 2.7], y: [0, 1400], xlog: true, xlabel: 'grain size d, µm', ylabel: 'yield strength, MPa' });
    p.line(ds, ds.map(sy), C.lime, 2.5).line([10 ** -0.5, 10 ** 2.7], [s0, s0], C.grey, 1, [4, 4]).dots([d], [sy(d)], C.red, 6);
    out(`d = ${nf(d < 10 ? 1 : 0).format(d)} µm: σ_y = σ₀ + k/√d = ${nf(0).format(s0)} + ${nf(0).format(v.k / Math.sqrt(d * 1e-6))} = ${nf(0).format(sy(d))} MPa. Grain boundaries block dislocations; smaller grains mean more boundaries. Refining grains is the one mechanism that raises strength and toughness together. Below about 20 nm the trend reverses.`);
  },
});

// 09.06 ideal Cu-Ni phase diagram and the lever rule
def('leverrule', {
  controls: [{ k: 'x', label: 'Overall Ni content (%)', min: 0, max: 100, step: 1, v: 40, f: 0 }, { k: 'T', label: 'Temperature (°C)', min: 1000, max: 1500, step: 1, v: 1235, f: 0 }],
  draw(p, v, out) {
    const R = 8.314, TA = 1358, HA = 13050, TB = 1728, HB = 17480;
    const sl = (T) => { const kA = Math.exp(HA / R * (1 / TA - 1 / T)), kB = Math.exp(HB / R * (1 / TB - 1 / T)), xs = (1 - kA) / (kB - kA); return [xs, kB * xs]; };
    const Ts = linspace(TA + 0.01, TB - 0.01, 200), S = Ts.map(sl);
    p.frame({ x: [0, 100], y: [1000, 1500], xlabel: 'Ni, % (atomic)', ylabel: 'temperature, °C' });
    p.line(S.map((a) => a[0] * 100), Ts.map((T) => T - 273.15), C.cyan, 2).line(S.map((a) => a[1] * 100), Ts.map((T) => T - 273.15), C.amber, 2);
    p.text('liquid', 15, 1450, C.amber).text('solid', 70, 1080, C.cyan);
    const T = v.T + 273.15, x0 = v.x / 100; p.dots([v.x], [v.T], C.red, 6);
    let msg;
    if (T <= TA || T >= TB) msg = T >= TB ? 'Above both melting points: all liquid.' : 'Below both melting points: all solid.';
    else { const [xs, xl] = sl(T); if (x0 <= xl) msg = `All liquid (the liquidus is at ${nf(1).format(xl * 100)} % Ni here).`; else if (x0 >= xs) msg = `All solid (the solidus is at ${nf(1).format(xs * 100)} % Ni here).`; else { const fl = (xs - x0) / (xs - xl); p.line([xl * 100, xs * 100], [v.T, v.T], C.lime, 2.5); msg = `Two phases. Tie line from liquid at ${nf(1).format(xl * 100)} % Ni to solid at ${nf(1).format(xs * 100)} % Ni. Lever rule: ${nf(1).format(fl * 100)} % liquid, ${nf(1).format((1 - fl) * 100)} % solid; the fraction of each phase is the length of the opposite lever arm.`; } }
    out(msg + ' (Ideal-solution model from the melting data of Cu and Ni; the real diagram is a little wider.)');
  },
});

// 09.07 Fe-C steel corner: microstructure from the lever rule
def('ironcarbon', {
  controls: [{ k: 'c', label: 'Carbon content (wt%)', min: 0.02, max: 1.6, step: 0.01, v: 0.45, f: 2 }],
  draw(p, v, out) {
    const ce = 0.76, ca = 0.022, cc = 6.7, c = v.c;
    p.frame({ x: [0, 1.6], y: [500, 1000], xlabel: 'carbon, wt%', ylabel: 'temperature, °C' });
    p.line([0, ce], [912, 727], C.cyan, 2).line([ce, 1.6], [727, 727 + (1148 - 727) * (1.6 - ce) / (2.11 - ce)], C.amber, 2).line([ca, 1.6], [727, 727], C.grey, 1.5).line([0.022, 0.008, 0], [727, 600, 500], C.grey, 1);
    p.text('austenite γ', 0.3, 940, C.paper).text('γ + α', 0.08, 770, C.cyan).text('γ + Fe₃C', 1.1, 790, C.amber).text('α + pearlite', 0.12, 640, C.cyan).text('pearlite + Fe₃C', 0.95, 640, C.amber);
    const A = c <= ce ? 912 - (912 - 727) * c / ce : 727 + (1148 - 727) * (c - ce) / (2.11 - ce);
    p.line([c, c], [500, 1000], C.lime, 2, [5, 4]).dots([c], [A], C.red, 5).dots([c], [727], C.red, 5);
    const pro = c <= ce ? (ce - c) / (ce - ca) : (c - ce) / (cc - ce), pe = 1 - pro;
    // bar along the bottom showing proeutectoid vs pearlite
    p.rect(0.05, 0.05 + 1.5 * pro, 515, 545, c <= ce ? C.cyan : C.amber).rect(0.05 + 1.5 * pro, 1.55, 515, 545, C.lime);
    out(`${nf(2).format(c)} % C. Cooling slowly, ${c <= ce ? 'ferrite' : 'cementite'} starts to form at ${nf(0).format(A)} °C (upper red dot). At 727 °C the remaining austenite, now at 0.76 % C, turns into pearlite. Room temperature: ${nf(1).format(pro * 100)} % proeutectoid ${c <= ce ? 'ferrite' : 'cementite'} and ${nf(1).format(pe * 100)} % pearlite (lime bar). ${c < 0.3 ? 'Mild steel: soft, weldable.' : c <= 0.6 ? 'Medium carbon: shafts, gears; heat treatable.' : 'High carbon: springs, tools, knives.'}`);
  },
});

// 09.08 carburising: erf profile against depth
def('carburise', {
  controls: [{ k: 'T', label: 'Temperature (°C)', min: 850, max: 1050, step: 5, v: 927, f: 0 }, { k: 'h', label: 'Time (h)', min: 0.5, max: 16, step: 0.5, v: 4, f: 1 }],
  draw(p, v, out) {
    const erf = (x) => { const t = 1 / (1 + 0.3275911 * Math.abs(x)), y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : -y; };
    const D = (T) => 2.3e-5 * Math.exp(-148000 / (8.314 * (T + 273.15))), d = D(v.T), t = v.h * 3600, L = 2 * Math.sqrt(d * t);
    const xs = linspace(0, 2.5, 200), prof = (x) => 1 - 0.8 * erf(x * 1e-3 / L);
    p.frame({ x: [0, 2.5], y: [0, 1.1], xlabel: 'depth, mm', ylabel: 'carbon, wt%' });
    p.line(xs, xs.map((x) => 1 - 0.8 * erf(x * 1e-3 / (2 * Math.sqrt(D(927) * 4 * 3600)))), C.grey, 1, [4, 4]).line(xs, xs.map(prof), C.lime, 2.5).line([0, 2.5], [0.4, 0.4], C.amber, 1, [3, 3]);
    const xc = 0.8134 * L * 1e3; p.dots([xc], [0.4], C.red, 5);
    out(`D = ${d.toExponential(2)} m²/s. Case depth to 0.4 % C: ${nf(2).format(xc)} mm. Depth grows with √(Dt): double the depth needs four times the time. A hotter furnace is far quicker, since D rises exponentially with temperature. Grey dashed: 4 h at 927 °C.`);
  },
});

// 09.09 viscoelastic models
def('creeprelax', {
  controls: [{ type: 'select', k: 'm', label: 'Test', options: ['Maxwell: hold strain (relaxation)', 'Kelvin-Voigt: hold stress (creep)', 'Standard linear solid: creep', 'Maxwell: hold stress (creep)'], v: 'Maxwell: hold strain (relaxation)' }, { k: 'tau', label: 'Time constant τ = η/E (s)', min: 100, max: 3000, step: 50, v: 1000, f: 0 }],
  draw(p, v, out) {
    const sel = ['Maxwell: hold strain (relaxation)', 'Kelvin-Voigt: hold stress (creep)', 'Standard linear solid: creep', 'Maxwell: hold stress (creep)'].indexOf(v.m);
    const ts = linspace(0, 5000, 300), tau = v.tau, m = sel;
    let ys, yl, msg;
    if (m === 0) { ys = ts.map((t) => 20 * Math.exp(-t / tau)); yl = 'stress, MPa'; msg = `Held at 1 % strain, the stress decays as e^(−t/τ): ${nf(1).format(20 * Math.exp(-1))} MPa after τ, ${nf(2).format(20 * Math.exp(-3))} after 3τ. This is why plastic snap fits and bolted gaskets lose their grip.`; }
    else if (m === 1) { ys = ts.map((t) => 0.5 * (1 - Math.exp(-t / tau))); yl = 'strain, %'; msg = 'Under 10 MPa the strain creeps up to σ/E = 0.5 % but there is no instant stretch: the dashpot holds the spring back.'; }
    else if (m === 2) { ys = ts.map((t) => 0.5 + 0.25 * (1 - Math.exp(-t / tau))); yl = 'strain, %'; msg = 'Instant elastic strain (0.5 %), then delayed creep towards 0.75 %. This is the simplest model that looks like a real polymer.'; }
    else { ys = ts.map((t) => 0.5 + 0.5 * t / tau); yl = 'strain, %'; msg = 'A Maxwell model under constant stress flows forever, like a liquid: instant 0.5 %, then a steady creep rate.'; }
    p.frame({ x: [0, 5000], y: [0, Math.max(...ys) * 1.15], xlabel: 'time, s', ylabel: yl });
    p.line(ts, ys, C.lime, 2.5).line([tau, tau], [0, Math.max(...ys) * 1.15], C.grey, 1, [4, 4]);
    out(msg + ` (τ = ${nf(0).format(tau)} s marked.)`);
  },
});

// 09.10 laminate stiffness in polar form
def('laminate', {
  controls: [{ type: 'select', k: 'L', label: 'Layup', options: ['Unidirectional [0]', 'Cross-ply [0/90]s', 'Angle-ply [±45]s', 'Quasi-isotropic [0/±45/90]s'], v: 'Unidirectional [0]' }, { k: 'vf', label: 'Fibre volume fraction', min: 0.3, max: 0.7, step: 0.01, v: 0.6, f: 2 }],
  draw(p, v, out) {
    const sel = ['Unidirectional [0]', 'Cross-ply [0/90]s', 'Angle-ply [±45]s', 'Quasi-isotropic [0/±45/90]s'].indexOf(v.L);
    const vf = v.vf, E1 = vf * 230 + (1 - vf) * 3.5, E2 = 1 / (vf / 230 + (1 - vf) / 3.5), G = 1 / (vf / 15 + (1 - vf) / 1.3), nu = vf * 0.2 + (1 - vf) * 0.35, nu21 = nu * E2 / E1, d = 1 - nu * nu21;
    const Q11 = E1 / d, Q22 = E2 / d, Q12 = nu * E2 / d, Q66 = G;
    const qb = (t) => { const c = Math.cos(t), s = Math.sin(t), c2 = c * c, s2 = s * s; return [Q11 * c2 * c2 + 2 * (Q12 + 2 * Q66) * s2 * c2 + Q22 * s2 * s2, (Q11 + Q22 - 4 * Q66) * s2 * c2 + Q12 * (s2 * s2 + c2 * c2), Q11 * s2 * s2 + 2 * (Q12 + 2 * Q66) * s2 * c2 + Q22 * c2 * c2, (Q11 - Q12 - 2 * Q66) * s * c2 * c + (Q12 - Q22 + 2 * Q66) * s2 * s * c, (Q11 - Q12 - 2 * Q66) * s2 * s * c + (Q12 - Q22 + 2 * Q66) * s * c2 * c, (Q11 + Q22 - 2 * Q12 - 2 * Q66) * s2 * c2 + Q66 * (s2 * s2 + c2 * c2)]; };
    const lay = [[0], [0, 90], [45, -45], [0, 45, -45, 90]][sel];
    const A = [0, 0, 0, 0, 0, 0]; lay.forEach((a) => qb(a * Math.PI / 180).forEach((q, i) => (A[i] += q / lay.length)));
    // E along direction phi: rotate the laminate by -phi and take 1/inv(A)[0][0]
    const Ephi = (phi) => { const rot = [0, 0, 0, 0, 0, 0]; lay.forEach((a) => qb((a - phi) * Math.PI / 180).forEach((q, i) => (rot[i] += q / lay.length))); const [a11, a12, a22, a16, a26, a66] = rot; const det = a11 * (a22 * a66 - a26 * a26) - a12 * (a12 * a66 - a26 * a16) + a16 * (a12 * a26 - a22 * a16); return det / (a22 * a66 - a26 * a26); };
    const ph = linspace(0, 360, 361), Es = ph.map(Ephi), R = 150;
    p.frame({ x: [-R, R], y: [-R * 0.8, R * 0.8], xlabel: 'E along x, GPa', ylabel: 'E along y, GPa' });
    p.line(ph.map((a, i) => Es[i] * Math.cos(a * Math.PI / 180)), ph.map((a, i) => Es[i] * Math.sin(a * Math.PI / 180)), C.lime, 2.5);
    p.line(ph.map((a) => 70 * Math.cos(a * Math.PI / 180)), ph.map((a) => 70 * Math.sin(a * Math.PI / 180)), C.grey, 1, [4, 4]);
    out(`Lime: modulus in each direction. E at 0° = ${nf(1).format(Es[0])} GPa, at 45° = ${nf(1).format(Es[45])} GPa, at 90° = ${nf(1).format(Es[90])} GPa. Grey: aluminium, 70 GPa in every direction (and 1.7 times denser). ${sel === 3 ? 'Quasi-isotropic: a circle, the same stiffness every way.' : sel === 0 ? 'Very stiff along the fibres, weak a few degrees off.' : ''}`);
  },
});

// 09.11 bamboo culm against a solid rod of the same mass
def('culm', {
  controls: [{ k: 'D', label: 'Outer diameter (mm)', min: 40, max: 160, step: 1, v: 100, f: 0 }, { k: 'g', label: 'Fibre grading (outer minus inner fraction)', min: 0, max: 0.6, step: 0.01, v: 0.45, f: 2 }],
  draw(p, v, out) {
    const A = 2827.4, D = v.D, ri = Math.sqrt(Math.max(0, D * D / 4 - A / Math.PI)), ro = D / 2, t = ro - ri, ds = Math.sqrt(4 * A / Math.PI);
    const vm = 0.383, n = 400; let EI = 0, F = 0, Ar = 0;
    // choose the inner value so the mean fibre fraction stays at vm
    const rr = linspace(ri, ro, n + 1); let w1 = 0, w2 = 0; for (let i = 0; i < n; i++) { const r = (rr[i] + rr[i + 1]) / 2, dr = rr[i + 1] - rr[i]; w1 += 2 * Math.PI * r * dr; w2 += 2 * Math.PI * r * dr * (r - ri) / t; }
    const vin = vm - v.g * w2 / w1;
    for (let i = 0; i < n; i++) { const r = (rr[i] + rr[i + 1]) / 2, dr = rr[i + 1] - rr[i], vf = vin + v.g * (r - ri) / t, E = vf * 40 + (1 - vf) * 2; EI += E * Math.PI * r ** 3 * dr; F += vf * 2 * Math.PI * r * dr; Ar += 2 * Math.PI * r * dr; }
    const EIs = (vm * 40 + (1 - vm) * 2) * Math.PI * ds ** 4 / 64;
    p.frame({ x: [-95, 95], y: [-85, 85], xlabel: 'mm', ylabel: 'mm' });
    for (let k = 0; k < 12; k++) { const r = ri + (k + 0.5) * t / 12, vf = vin + v.g * (k + 0.5) / 12, th = linspace(0, 2 * Math.PI, 90); p.line(th.map((a) => r * Math.cos(a) - (D < 120 ? 25 : 0)), th.map((a) => r * Math.sin(a)), vf > 0.45 ? C.lime : vf > 0.3 ? C.amber : C.grey, Math.max(1, t / 12 * 1.4)); }
    const th = linspace(0, 2 * Math.PI, 90); p.line(th.map((a) => (ds / 2) * Math.cos(a) + 56), th.map((a) => (ds / 2) * Math.sin(a) - 50), C.cyan, 2);
    out(`Same material and mass (2827 mm²). Culm ${nf(0).format(D)} mm, wall ${nf(1).format(t)} mm: EI = ${nf(1).format(EI / 1e6)} kN m², versus ${nf(1).format(EIs / 1e6)} for the solid ${nf(0).format(ds)} mm rod (cyan): ${nf(1).format(EI / EIs)} times stiffer. Lime rings are fibre-rich. Too thin a wall would buckle locally, which is why bamboo has nodes.`);
  },
});

// 09.12 stress intensity against crack length
def('crackk', {
  controls: [{ type: 'select', k: 'm', label: 'Material', options: ['Glass (K_IC 0.75)', '7075-T6 aluminium (25)', 'Structural steel (50)', 'Pressure-vessel steel (150)'], v: 'Structural steel (50)' }, { k: 's', label: 'Stress (MPa)', min: 10, max: 500, step: 5, v: 300, f: 0 }, { k: 'a', label: 'Edge crack depth (mm)', min: 0.1, max: 40, step: 0.1, v: 5, f: 1 }],
  draw(p, v, out) {
    const sel = ['Glass (K_IC 0.75)', '7075-T6 aluminium (25)', 'Structural steel (50)', 'Pressure-vessel steel (150)'].indexOf(v.m);
    const KIC = [0.75, 25, 50, 150][sel], Y = 1.12, as = linspace(0.01, 40, 300), Kf = (a) => Y * v.s * Math.sqrt(Math.PI * a * 1e-3);
    const ymax = Math.max(KIC * 1.6, Kf(40) * 1.05);
    p.frame({ x: [0, 40], y: [0, ymax], xlabel: 'crack depth a, mm', ylabel: 'K, MPa √m' });
    p.line(as, as.map(Kf), C.lime, 2.5).line([0, 40], [KIC, KIC], C.red, 1.5, [5, 4]).dots([v.a], [Kf(v.a)], Kf(v.a) >= KIC ? C.red : C.cyan, 6);
    const ac = (KIC / (Y * v.s)) ** 2 / Math.PI * 1e3;
    out(`K = 1.12 σ √(πa) = ${nf(1).format(Kf(v.a))} MPa √m against K_IC = ${KIC}. ${Kf(v.a) >= KIC ? 'Fast fracture.' : 'Safe for now.'} Critical depth at this stress: ${ac < 0.1 ? nf(3).format(ac) : nf(1).format(ac)} mm. Halving the stress quadruples the tolerable crack.`);
  },
});

// 09.13 S-N curve with Goodman mean-stress correction
def('sncurve', {
  controls: [{ k: 'sa', label: 'Stress amplitude (MPa)', min: 150, max: 600, step: 5, v: 250, f: 0 }, { k: 'sm', label: 'Mean stress (MPa)', min: -200, max: 500, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const sf = 1225, b = -0.095, su = 725, life = (s) => 0.5 * (s / sf) ** (1 / b);
    const Ns = logspace(2, 8, 200);
    p.frame({ x: [1e2, 1e8], y: [100, 1000], xlog: true, ylog: true, xlabel: 'cycles to failure N', ylabel: 'amplitude, MPa' });
    p.line(Ns, Ns.map((N) => sf * (2 * N) ** b), C.lime, 2.5);
    const seq = v.sm >= 0 ? (v.sm < su ? v.sa / (1 - v.sm / su) : 1e9) : v.sa;
    const N = seq < 1e8 ? life(seq) : 0;
    p.dots([Math.min(1e8, Math.max(1e2, life(v.sa)))], [v.sa], C.grey, 4);
    if (seq < 1000 && N > 100) p.dots([Math.min(1e8, N)], [seq], C.red, 6).line([Math.min(1e8, N), Math.min(1e8, N)], [100, seq], C.red, 1, [3, 3]);
    const fmt = (x) => x >= 1e8 ? 'over 10⁸' : x.toExponential(2).replace('e+', ' × 10^');
    out(seq >= 1000 || v.sa + v.sm >= su ? 'Peak stress exceeds the tensile strength: static failure.' : `Goodman: σ_a/(1 − σ_m/σ_u) = ${nf(0).format(seq)} MPa equivalent fully reversed amplitude. Life ${fmt(N)} cycles (grey dot: ${fmt(life(v.sa))} with zero mean). ${v.sm < 0 ? 'Compressive mean stress is conservatively ignored; shot peening exploits it.' : 'Tensile mean stress shortens life.'}`);
  },
});

// 09.14 galvanic corrosion: thinning against time
def('galvanic', {
  controls: [{ k: 'la', label: 'Anode area, log₁₀(cm²)', min: 0, max: 3.5, step: 0.05, v: 1, f: 2 }, { k: 'I', label: 'Couple current (mA)', min: 0.2, max: 10, step: 0.1, v: 2, f: 1 }],
  draw(p, v, out) {
    const A = 10 ** v.la, i = v.I * 1e-3 / A * 1e6, rate = i * 0.0116, yrs = linspace(0, 20, 100);
    p.frame({ x: [0, 20], y: [0, 3.2], xlabel: 'years', ylabel: 'steel wall left, mm' });
    p.line(yrs, yrs.map((y) => Math.max(0, 3 - 0.0116 * 0.5 * y)), C.grey, 1.5, [4, 4]).line(yrs, yrs.map((y) => Math.max(0, 3 - rate * y)), C.lime, 2.5);
    const life = 3 / rate;
    out(`Anode ${nf(0).format(A)} cm²: ${nf(1).format(i)} µA/cm², ${nf(3).format(rate)} mm/year by Faraday's law. A 3 mm wall is gone in ${life > 1000 ? 'over 1000' : nf(1).format(life)} years. Same current through a smaller anode: faster attack. Never put small steel fasteners in a big copper or stainless sheet; the reverse is fine. Grey: free corrosion at 0.5 µA/cm².`);
  },
});

// 09.15 Ashby chart: modulus against density
def('ashbychart', {
  controls: [{ type: 'select', k: 'ix', label: 'Design', options: ['Light stiff tie: E/ρ', 'Light stiff beam: E^1/2/ρ', 'Light stiff panel: E^1/3/ρ'], v: 'Light stiff beam: E^1/2/ρ' }, { k: 'c', label: 'Move the guideline', min: -1, max: 1, step: 0.02, v: 0, f: 2 }],
  draw(p, v, out) {
    const db = [['steel', 210, 7850, 0.5, 1.15], ['aluminium', 70, 2700, 1.08, 0.8], ['titanium', 115, 4500, 1.08, 1.05], ['CFRP', 70, 1560, 0.62, 1.2], ['GFRP', 25, 1900, 0.72, 0.68], ['bamboo', 18, 700, 1.08, 1.05], ['spruce', 12, 450, 1.08, 0.75], ['concrete', 30, 2400, 1.08, 1.0], ['ABS', 2.3, 1050, 1.08, 1.0]];
    const sel = ['Light stiff tie: E/ρ', 'Light stiff beam: E^1/2/ρ', 'Light stiff panel: E^1/3/ρ'].indexOf(v.ix), n = [1, 2, 3][sel];
    const M = (E, r) => (E * 1e9) ** (1 / n) / r, ref = M(70, 2700) * 10 ** v.c;
    p.frame({ x: [300, 1.2e4], y: [1, 500], xlog: true, ylog: true, xlabel: 'density, kg/m³', ylabel: 'Young’s modulus, GPa' });
    const rs = logspace(Math.log10(300), Math.log10(1.2e4), 80).filter((r) => (ref * r) ** n / 1e9 <= 500 && (ref * r) ** n / 1e9 >= 1); p.line(rs, rs.map((r) => (ref * r) ** n / 1e9), C.amber, 2, [6, 4]);
    const better = [];
    db.forEach(([nm, E, r, fx, fy]) => { const good = M(E, r) >= ref * (1 - 1e-9); if (good) better.push(nm); p.dots([r], [E], good ? C.lime : C.grey, 5).text(nm, r * fx, E * fy, good ? C.lime : C.grey); });
    out(`Slope ${n} guideline: every material on it is equally good. Above it (lime) is better: ${better.length ? better.join(', ') : 'none'}. Rank by the index ${v.ix.split(': ')[1]}.`);
  },
});

// 09.16 embodied energy of the 09.15 beam
def('embodied', {
  controls: [{ type: 'select', k: 'q', label: 'Show', options: ['Mass (kg)', 'Embodied energy (MJ)', 'Carbon (kg CO₂)'], v: 'Embodied energy (MJ)' }],
  draw(p, v, out) {
    const db = [['steel', 210, 7850, 25, 2], ['aluminium', 70, 2700, 200, 12], ['recycled Al', 70, 2700, 30, 2], ['titanium', 115, 4500, 600, 40], ['CFRP', 70, 1560, 270, 25], ['bamboo', 18, 700, 3, 0.4], ['spruce', 12, 450, 8, 0.5]];
    const sel = ['Mass (kg)', 'Embodied energy (MJ)', 'Carbon (kg CO₂)'].indexOf(v.q);
    const rows = db.map(([nm, E, r, H, c]) => { const m = r * Math.sqrt(12 * 1000 / (3 * E * 1e9 * 0.005)); return [nm, [m, m * H, m * c][sel]]; });
    const mx = Math.max(...rows.map((r) => r[1])), lg = sel > 0;
    p.frame({ x: [lg ? 1 : 0, lg ? mx * 40 : mx * 1.45], y: [0, rows.length], xlog: lg, xlabel: v.q + (lg ? ', log scale' : ''), ylabel: '' });
    rows.forEach(([nm, val], i) => { const y = rows.length - i - 0.5; p.rect(lg ? 1 : 0, val, y - 0.3, y + 0.3, i === 0 ? C.grey : val <= rows[0][1] ? C.lime : C.red).text(`${nm} ${nf(val < 10 ? 1 : 0).format(val)}`, lg ? Math.max(val * 1.1, 1.2) : val + mx * 0.02, y - 0.1, C.paper); });
    out(`The 1 m cantilever from 09.15 (5 mm under 1 kN). Lime: better than steel, red: worse. ${sel === 0 ? 'Lightest is not the same as greenest.' : 'Primary aluminium, titanium and carbon fibre are energy-hungry; wood and bamboo store carbon instead. Recycling aluminium cuts its energy by about 85 %.'}`);
  },
});

// 09.17 unit cost against batch size
def('processcost', {
  controls: [{ k: 'ln', label: 'Batch size, log₁₀(n)', min: 0, max: 5, step: 0.05, v: 3, f: 2 }, { k: 'tool', label: 'Die-casting tooling (kUSD)', min: 10, max: 100, step: 1, v: 40, f: 0 }],
  draw(p, v, out) {
    const pr = [['CNC machining', 0.6, 300, 80, 4, C.cyan], ['sand casting', 0.3, 2000, 50, 10, C.amber], ['die casting', 0.1, v.tool * 1000, 120, 120, C.lime], ['metal 3D print', 0.05, 0, 60, 0.5, C.red]];
    const cost = (q, n) => 0.75 / (1 - q[1]) + q[2] / n + q[3] / q[4], ns = logspace(0, 5, 150), n = 10 ** v.ln;
    p.frame({ x: [1, 1e5], y: [1, 1e4], xlog: true, ylog: true, xlabel: 'batch size n', ylabel: 'cost per part, USD' });
    pr.forEach((q) => p.line(ns, ns.map((x) => cost(q, x)), q[5], 2.2));
    p.line([n, n], [1, 1e4], C.grey, 1, [4, 4]);
    const c = pr.map((q) => [q[0], cost(q, n)]).sort((a, b) => a[1] - b[1]);
    out(`n = ${nf(0).format(n)}: cheapest is ${c[0][0]} at ${nf(2).format(c[0][1])} USD per part (then ${c[1][0]}, ${nf(2).format(c[1][1])}). Tooling is spread over the batch (falling part of each curve); the flat floor is material plus machine time. Cyan CNC, amber sand casting, lime die casting, red 3D printing.`);
  },
});

// 09.18 Merchant orthogonal cutting
def('merchant', {
  controls: [{ k: 'a', label: 'Rake angle α (°)', min: -5, max: 25, step: 1, v: 10, f: 0 }, { k: 'mu', label: 'Friction coefficient μ on the rake face', min: 0.2, max: 1.2, step: 0.05, v: 0.5, f: 2 }],
  draw(p, v, out) {
    const al = v.a * Math.PI / 180, be = Math.atan(v.mu), ph = Math.PI / 4 + al / 2 - be / 2, t0 = 1, tc = t0 * Math.cos(ph - al) / Math.sin(ph);
    const d = [Math.sin(al), Math.cos(al)], nn = [-Math.cos(al), Math.sin(al)], B = [-t0 / Math.tan(ph), t0], L = 3.2;
    p.frame({ x: [-5, 4], y: [-1.5, 4], xlabel: '', ylabel: '' });
    p.rect(-5, 4, -1.5, 0, 'rgba(242,243,236,0.18)');
    poly(p, [[-5, 0], [0, 0], B, [-5, t0]], null, 'rgba(242,243,236,0.28)');
    const s = (t0 - tc * Math.sin(al)) / Math.cos(al), top = [L * d[0], L * d[1]];
    poly(p, [[0, 0], top, [top[0] + tc * nn[0], top[1] + tc * nn[1]], B], C.amber, 'rgba(255,170,60,0.35)');
    poly(p, [[0, 0], top, [3.8, top[1]], [3.8, 0.35]], C.cyan, 'rgba(90,200,250,0.25)');
    p.line([0, B[0]], [0, B[1]], C.red, 2.5).text('shear plane', B[0] - 0.4, B[1] + 0.25, C.red).text('chip', top[0] - 2.3, top[1] - 0.3, C.amber).text('tool', 2.2, 1.5, C.cyan);
    arrow(p, -3.5, -0.8, -1.5, -0.8, C.grey, 2); p.text('work moves', -4.6, -0.45, C.grey);
    const ratio = Math.sin(ph) / Math.cos(ph - al), Fc = 550 * 0.2 * 2 / Math.sin(ph) / Math.cos(ph + be - al) * Math.cos(be - al);
    out(`Merchant: φ = 45° + α/2 − β/2 = ${nf(1).format(ph * 180 / Math.PI)}°. The chip is ${nf(2).format(1 / ratio)} times thicker than the cut. For 0.2 mm × 2 mm in steel (τ = 550 MPa): cutting force ${nf(0).format(Fc)} N, ${nf(2).format(Fc * 200 / 60 / 1000)} kW at 200 m/min. More rake or less friction: steeper shear plane, thinner chip, less force.`);
  },
});

// 09.19 Taylor tool life and economic cutting speed
def('taylorcost', {
  controls: [{ k: 'n', label: 'Taylor exponent n', min: 0.1, max: 0.5, step: 0.01, v: 0.25, f: 2 }, { k: 'Ct', label: 'Cost per cutting edge (USD)', min: 1, max: 30, step: 0.5, v: 6, f: 1 }],
  draw(p, v, out) {
    const n = v.n, CT = 400, Co = 1.5, tch = 2, Vs = linspace(80, 400, 300);
    const parts = (V) => { const tm = Math.PI * 60 * 200 / (1000 * V * 0.25), T = (CT / V) ** (1 / n); return [Co, Co * tm, (Co * tch + v.Ct) * tm / T]; };
    const tot = Vs.map((V) => parts(V).reduce((a, b) => a + b, 0));
    p.frame({ x: [80, 400], y: [0, 8], xlabel: 'cutting speed V, m/min', ylabel: 'cost per part, USD' });
    p.line(Vs, Vs.map((V) => parts(V)[1]), C.cyan, 1.5, [4, 3]).line(Vs, Vs.map((V) => parts(V)[2]), C.amber, 1.5, [4, 3]).line(Vs, tot, C.lime, 2.5);
    const To = (1 / n - 1) * (tch + v.Ct / Co), Vo = CT / To ** n, cmin = parts(Vo).reduce((a, b) => a + b, 0);
    p.dots([Vo], [cmin], C.red, 6);
    out(`Minimum cost at V = ${nf(0).format(Vo)} m/min, where each edge lasts T = (1/n − 1)(t_change + C_tool/C_machine) = ${nf(1).format(To)} min. Cost ${nf(2).format(cmin)} USD per part. Cyan: machine time (falls with speed). Amber: tool wear (rises steeply). Cheaper edges or a larger n push the optimum faster.`);
  },
});

// 09.20 pocket toolpath and coverage
def('pocketpath', {
  controls: [{ k: 'so', label: 'Stepover (% of tool diameter)', min: 20, max: 110, step: 1, v: 50, f: 0 }, { k: 'D', label: 'Tool diameter (mm)', min: 3, max: 12, step: 0.5, v: 8, f: 1 }, { k: 'fin', label: 'Finishing contour pass', type: 'check', v: 1 }],
  draw(p, v, out) {
    const W = 40, H = 25, r = v.D / 2, so = v.so / 100 * v.D, x0 = r, x1 = W - r, y0 = r, y1 = H - r, pts = [];
    let y = y0, k = 0;
    while (y < y1 - 1e-9) { if (k % 2 === 0) pts.push([x0, y], [x1, y]); else pts.push([x1, y], [x0, y]); y = Math.min(y + so, y1); k++; }
    if (k % 2 === 0) pts.push([x0, y1], [x1, y1]); else pts.push([x1, y1], [x0, y1]);
    if (v.fin) pts.push([x0, y1], [x0, y0], [x1, y0], [x1, y1], [x0, y1]);
    p.frame({ x: [-2, 42], y: [-2, 27], xlabel: 'x, mm', ylabel: 'y, mm' });
    // coverage on a 0.5 mm grid
    let un = 0, tot = 0;
    for (let gx = 0.25; gx < W; gx += 0.5) for (let gy = 0.25; gy < H; gy += 0.5) {
      tot++; let hit = false;
      for (let i = 0; i < pts.length - 1 && !hit; i++) { const [ax, ay] = pts[i], [bx, by] = pts[i + 1], dx = bx - ax, dy = by - ay, L2 = dx * dx + dy * dy, t = L2 ? Math.max(0, Math.min(1, ((gx - ax) * dx + (gy - ay) * dy) / L2)) : 0; hit = (gx - ax - t * dx) ** 2 + (gy - ay - t * dy) ** 2 <= r * r; }
      if (!hit) { un++; p.rect(gx - 0.25, gx + 0.25, gy - 0.25, gy + 0.25, 'rgba(255,90,54,0.8)'); }
    }
    p.line([0, W, W, 0, 0], [0, 0, H, H, 0], C.paper, 1.5).line(pts.map((q) => q[0]), pts.map((q) => q[1]), C.lime, 1.8);
    const th = linspace(0, 2 * Math.PI, 40); p.line(th.map((a) => pts[0][0] + r * Math.cos(a)), th.map((a) => pts[0][1] + r * Math.sin(a)), C.cyan, 1.5);
    let L = 0; for (let i = 0; i < pts.length - 1; i++) L += Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
    out(`Path ${nf(0).format(L)} mm per layer, ${nf(2).format(L / 600)} min at 600 mm/min. Uncut (red): ${nf(1).format(un / tot * 100)} % of the pocket. ${v.so > 100 ? 'Stepover above the diameter leaves ridges between passes.' : 'Only the corners remain, with radius equal to the tool radius.'} Cyan circle: the tool.`);
  },
});

// 09.21 turned surface profile
def('roughprofile', {
  controls: [{ k: 'f', label: 'Feed f (mm/rev)', min: 0.02, max: 0.5, step: 0.01, v: 0.2, f: 2 }, { k: 'r', label: 'Tool nose radius r (mm)', min: 0.2, max: 2.4, step: 0.1, v: 0.8, f: 1 }],
  draw(p, v, out) {
    const f = v.f, r = v.r, xs = linspace(0, 4 * f, 800), z = xs.map((x) => { const xc = (Math.floor(x / f) + 0.5) * f; return (r - Math.sqrt(Math.max(0, r * r - (x - xc) ** 2))) * 1000; });
    const m = z.reduce((a, b) => a + b, 0) / z.length, Ra = z.reduce((a, b) => a + Math.abs(b - m), 0) / z.length, Rt = Math.max(...z);
    p.frame({ x: [0, 4 * f], y: [-0.1 * Math.max(Rt, 1), 1.2 * Math.max(Rt, 1)], xlabel: 'along the axis, mm', ylabel: 'height, µm' });
    p.line(xs, z, C.lime, 2).line([0, 4 * f], [m, m], C.grey, 1, [4, 4]).line([0, 4 * f], [m + Ra, m + Ra], C.amber, 1, [2, 3]).line([0, 4 * f], [m - Ra, m - Ra], C.amber, 1, [2, 3]);
    out(`Ra = ${nf(3).format(Ra)} µm (formula f²/(32r) = ${nf(3).format(f * f / (32 * r) * 1000)}); peak to valley ${nf(2).format(Rt)} µm (f²/(8r) = ${nf(2).format(f * f / (8 * r) * 1000)}). Halving the feed quarters the roughness; a bigger nose radius helps linearly but raises chatter risk. Amber: mean ± Ra.`);
  },
});

// 09.22 bend allowance and springback
def('bendflat', {
  controls: [{ k: 'R', label: 'Inside bend radius R (mm)', min: 0.5, max: 10, step: 0.5, v: 3, f: 1 }, { k: 't', label: 'Thickness t (mm)', min: 0.5, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'K', label: 'K-factor', min: 0.25, max: 0.5, step: 0.01, v: 0.33, f: 2 }, { type: 'select', k: 'm', label: 'Material', options: ['5052-H32 aluminium', 'Mild steel', 'Spring steel'], v: '5052-H32 aluminium' }],
  draw(p, v, out) {
    const sel = ['5052-H32 aluminium', 'Mild steel', 'Spring steel'].indexOf(v.m), Y = [193, 350, 1000][sel], E = [70000, 210000, 210000][sel];
    const R = v.R, t = v.t, BA = Math.PI / 2 * (R + v.K * t), sb = R + t, flats = (30 - sb) + (50 - 2 * sb) + (30 - sb), L = flats + 2 * BA;
    const x = R * Y / (E * t), ratio = 4 * x ** 3 - 3 * x + 1, thf = 90 * (R + t / 2) / (R / ratio + t / 2);
    p.frame({ x: [-5, 60], y: [-8, 36], xlabel: 'mm', ylabel: 'mm' });
    // U channel: draw inner and outer contours with rounded corners (outside 50 wide, 30 tall)
    const ro = R + t, rn = R + v.K * t, arc = (cx, cy, r, a0, a1) => linspace(a0, a1, 30).map((a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)]);
    const path = (r, off) => [[off, 30], [off, ro], ...arc(ro, ro, r, Math.PI, 1.5 * Math.PI), [50 - ro, ro - r], ...arc(50 - ro, ro, r, 1.5 * Math.PI, 2 * Math.PI), [50 - off, 30]];
    const outer = path(ro, 0), inner = path(R, t), neut = path(rn, ro - rn);
    p.line(outer.map((q) => q[0]), outer.map((q) => q[1]), C.paper, 2).line(inner.map((q) => q[0]), inner.map((q) => q[1]), C.paper, 2).line(neut.map((q) => q[0]), neut.map((q) => q[1]), C.lime, 1.5, [4, 3]);
    p.line([0, L * 50 / 110], [-5, -5], C.cyan, 4).text(`flat blank ${nf(2).format(L)} mm (scaled)`, 0, -2.5, C.cyan);
    out(`Bend allowance (π/2)(R + Kt) = ${nf(3).format(BA)} mm per bend. Blank for the 30 × 50 × 30 channel: ${nf(2).format(L)} mm. Dashed lime: the neutral axis, which keeps its length. Springback (${v.m}): R_i/R_f = ${nf(4).format(ratio)}, so a 90° bend opens to ${nf(2).format(thf)}°; overbend to ${nf(2).format(8100 / thf)}°.`);
  },
});

// 09.23 extrusion ram force against stroke
def('extrudeforce', {
  controls: [{ k: 'R', label: 'Extrusion ratio A₀/A', min: 5, max: 100, step: 1, v: 40, f: 0 }, { k: 's', label: 'Flow stress at temperature (MPa)', min: 20, max: 120, step: 1, v: 40, f: 0 }, { k: 'm', label: 'Container friction factor m', min: 0, max: 1, step: 0.05, v: 1, f: 2 }],
  draw(p, v, out) {
    const D0 = 0.1, Lb = 0.3, A0 = Math.PI * D0 * D0 / 4, s = v.s * 1e6, Fd = s * (0.8 + 1.5 * Math.log(v.R)) * A0 / 1e6, Ff = (L) => v.m * s / Math.sqrt(3) * Math.PI * D0 * L / 1e6;
    const st = linspace(0, 280, 100);
    p.frame({ x: [0, 300], y: [0, 12], xlabel: 'ram stroke, mm', ylabel: 'force, MN' });
    p.line(st, st.map((x) => Fd + Ff(Lb - x / 1000)), C.lime, 2.5).line(st, st.map(() => Fd), C.cyan, 1.5, [4, 3]).line([0, 300], [8, 8], C.red, 1.5, [6, 4]).text('8 MN press', 200, 8.4, C.red);
    const Fmax = Fd + Ff(Lb);
    out(`Peak ${nf(2).format(Fmax)} MN at the start: die ${nf(2).format(Fd)} MN (cyan, Johnson p = σ(0.8 + 1.5 ln R)) plus container friction ${nf(2).format(Ff(Lb))} MN, which falls as the billet shortens. Profile area ${nf(0).format(A0 / v.R * 1e6)} mm². ${Fmax > 8 ? 'Too much for the press: heat the billet more, or use a lower ratio.' : 'Within the press capacity.'}`);
  },
});

// 09.24 Chvorinov: freezing time against modulus
def('chvorinov', {
  controls: [{ k: 'D', label: 'Riser diameter = height (mm)', min: 20, max: 100, step: 1, v: 56, f: 0 }, { k: 'B', label: 'Mould constant B (min/cm²)', min: 1, max: 5, step: 0.05, v: 2.96, f: 2 }],
  draw(p, v, out) {
    const shapes = [['plate', 7.69], ['bar', 9.375], ['cube/sphere', 16.67]], Mr = v.D / 6, t = (M) => v.B * (M / 10) ** 2, Ms = linspace(0, 20, 100);
    p.frame({ x: [0, 20], y: [0, 12], xlabel: 'modulus V/A, mm', ylabel: 'freezing time, min' });
    p.line(Ms, Ms.map(t), C.grey, 1.5);
    shapes.forEach(([n, M]) => p.dots([M], [t(M)], C.cyan, 5).text(n, M > 12 ? M - 6.2 : M + 0.4, M > 12 ? t(M) + 0.3 : t(M) - 0.5, C.cyan));
    const ok = Mr >= 1.2 * 7.69; p.dots([Mr], [t(Mr)], ok ? C.lime : C.red, 7).text('riser', Mr - 1.5, t(Mr) + 0.6, ok ? C.lime : C.red);
    out(`Chvorinov: t = B (V/A)². The plate (V/A = 7.69 mm) freezes in ${nf(1).format(t(7.69))} min. Riser V/A = D/6 = ${nf(2).format(Mr)} mm, freezing in ${nf(1).format(t(Mr))} min: ${ok ? 'it stays liquid long enough to feed the shrinking plate.' : 'too small; it needs V/A at least 1.2 × the casting\u2019s (D ≥ 55.4 mm).'}`);
  },
});

// 09.25 injection moulding: centre temperature of the wall against time
def('mouldcool', {
  controls: [{ k: 's', label: 'Wall thickness (mm)', min: 0.5, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'Tw', label: 'Mould temperature (°C)', min: 20, max: 80, step: 1, v: 60, f: 0 }],
  draw(p, v, out) {
    const a = 8.095e-8, Tm = 240, Te = 90, s = v.s / 1000, Tw = v.Tw;
    const Tc = (t, ss) => { let sum = 0; for (let k = 0; k < 40; k++) { const m = 2 * k + 1; sum += (4 / (m * Math.PI)) * Math.sin(m * Math.PI / 2) * Math.exp(-((m * Math.PI / ss) ** 2) * a * t); } return Tw + (Tm - Tw) * sum; };
    const ts = linspace(0.01, 60, 300);
    p.frame({ x: [0, 60], y: [0, 260], xlabel: 'time, s', ylabel: 'centre temperature, °C' });
    p.line(ts, ts.map((t) => Tc(t, 0.002)), C.grey, 1, [4, 4]).line(ts, ts.map((t) => Tc(t, s)), C.lime, 2.5).line([0, 60], [Te, Te], C.amber, 1, [3, 3]).text('eject at 90 °C', 40, 100, C.amber);
    const tc = s * s / (Math.PI ** 2 * a) * Math.log(4 / Math.PI * (Tm - Tw) / (Te - Tw));
    if (tc < 60) p.dots([tc], [Te], C.red, 6);
    out(`Cooling time t = s²/(π²α) ln[(4/π)(T_melt − T_mould)/(T_eject − T_mould)] = ${nf(1).format(tc)} s. Cycle about ${nf(1).format(tc + 5)} s, ${nf(0).format(3600 / (tc + 5))} shots per hour. Twice the wall, four times the wait: keep walls thin and even. Grey: 2 mm.`);
  },
});

// 09.26 Rosenthal weld: top-view isotherms
def('weldpool', {
  controls: [{ k: 'I', label: 'Current (A)', min: 80, max: 300, step: 5, v: 200, f: 0 }, { k: 'v', label: 'Travel speed (mm/s)', min: 1, max: 15, step: 0.5, v: 5, f: 1 }, { k: 'T0', label: 'Preheat (°C)', min: 20, max: 250, step: 5, v: 20, f: 0 }],
  draw(p, v, out) {
    const k = 40, al = 40 / (7850 * 600), q = 0.8 * 25 * v.I, vv = v.v / 1000;
    const T = (x, y) => { const xi = x / 1000, yy = y / 1000, r = Math.max(1e-5, Math.hypot(xi, yy)); return v.T0 + q / (2 * Math.PI * k * r) * Math.exp(-vv * (xi + r) / (2 * al)); };
    p.frame({ x: [-30, 8], y: [-12, 12], xlabel: 'along the weld, mm (arc at 0, moving right)', ylabel: 'mm' });
    bands(p, (x, y) => Math.min(T(x, y), 1600), 0, 1600, 16, 140);
    // pool boundary: scan each column for the melt width
    const xs = linspace(-30, 8, 300), w = xs.map((x) => { let lo = 0, hi = 12; if (T(x, 0.001) < 1510) return NaN; for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2; if (T(x, m) > 1510) lo = m; else hi = m; } return lo; });
    const ok = xs.map((x, i) => [x, w[i]]).filter((q) => !isNaN(q[1]));
    if (ok.length) p.line(ok.map((q) => q[0]), ok.map((q) => q[1]), C.red, 2).line(ok.map((q) => q[0]), ok.map((q) => -q[1]), C.red, 2);
    const t85 = q / vv / (2 * Math.PI * k) * (1 / (500 - v.T0) - 1 / (800 - v.T0)), L = ok.length ? ok[ok.length - 1][0] - ok[0][0] : 0;
    out(`Heat input ${nf(2).format(q / vv / 1e6)} kJ/mm. Melt pool (red) about ${nf(1).format(L)} mm long, a teardrop trailing the arc. Cooling 800 → 500 °C takes ${nf(2).format(t85)} s: ${t85 < 3 ? 'fast, so hard, brittle martensite risks cracking in the heat-affected zone; preheat or slow down.' : 'slow enough for most structural steels.'}`);
  },
});

// 09.27 slicing a sphere into layers
def('slicelayers', {
  controls: [{ k: 'h', label: 'Layer height (mm)', min: 0.05, max: 3, step: 0.05, v: 2, f: 2 }, { type: 'select', k: 'sh', label: 'Shape', options: ['Sphere, 40 mm', 'Cone, 40 mm', 'Vase (vertical walls)'], v: 'Sphere, 40 mm' }],
  draw(p, v, out) {
    const sel = ['Sphere, 40 mm', 'Cone, 40 mm', 'Vase (vertical walls)'].indexOf(v.sh), R = 20, H = 40;
    const rad = (z) => sel === 0 ? Math.sqrt(Math.max(0, R * R - (z - R) ** 2)) : sel === 1 ? R * (1 - z / H) : 12 + 4 * Math.sin(z / 6);
    p.frame({ x: [-25, 25], y: [0, 42], xlabel: 'mm', ylabel: 'height, mm' });
    const zs = linspace(0, H, 200); p.line(zs.map(rad), zs, C.grey, 1.5).line(zs.map((z) => -rad(z)), zs, C.grey, 1.5);
    let V = 0, n = 0, per = 0;
    for (let z = 0; z < H - 1e-9; z += v.h) { const zm = Math.min(z + v.h / 2, H), r = rad(zm), h = Math.min(v.h, H - z); V += Math.PI * r * r * h; per += 2 * Math.PI * r; n++; p.rect(-r, r, z, z + h, n % 2 ? 'rgba(238,255,65,0.45)' : 'rgba(238,255,65,0.3)'); }
    const Vex = sel === 0 ? 4 / 3 * Math.PI * R ** 3 : sel === 1 ? Math.PI * R * R * H / 3 : (() => { let s = 0; for (let i = 0; i < 4000; i++) { const z = (i + 0.5) * H / 4000; s += Math.PI * rad(z) ** 2 * H / 4000; } return s; })();
    const tmin = (2 * per + 0.2 * V / 0.4) / 40 / 60;
    out(`${n} layers. Sliced volume ${nf(0).format(V)} mm³ vs ${nf(0).format(Vex)} exact (${nf(2).format((V / Vex - 1) * 100)} %). About ${nf(0).format(tmin)} min at 40 mm/s (two perimeters, 20 % infill). Steps are worst where the surface is nearly flat (top of the sphere) and vanish on vertical walls. Thinner layers: smoother but slower.`);
  },
});

// small deterministic normal generator for the statistics widgets
function gaussSeq(seed) { let s = seed >>> 0; const u = () => ((s = (s * 1664525 + 1013904223) >>> 0) + 0.5) / 4294967296; return () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u()); }

// 09.28 uncertainty budget for a micrometer reading
def('ubudget', {
  controls: [{ k: 'n', label: 'Number of readings', min: 1, max: 30, step: 1, v: 10, f: 0 }, { k: 'dT', label: 'Temperature band ± (°C)', min: 0, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'ab', label: 'Abbe offset (mm) at 50 µrad tilt', min: 0, max: 60, step: 1, v: 0, f: 0 }],
  draw(p, v, out) {
    const rows = [['repeatability', 1.197 / Math.sqrt(v.n)], ['resolution', 1 / Math.sqrt(12)], ['calibration', 1.0], ['temperature', 25 * 11.5e-6 * v.dT / Math.sqrt(3) * 1000], ['Abbe', v.ab * 50e-6 / Math.sqrt(3)]];
    const uc = Math.sqrt(rows.reduce((a, r) => a + r[1] * r[1], 0));
    p.frame({ x: [0, 3], y: [0, rows.length + 1], xlabel: 'standard uncertainty, µm', ylabel: '' });
    rows.forEach(([nm, u], i) => { const y = rows.length - i + 0.5; p.rect(0, Math.min(u, 3), y - 0.3, y + 0.3, u * u / (uc * uc) > 0.4 ? C.amber : C.lime).text(`${nm} ${nf(2).format(u)}`, Math.min(u, 2.2) + 0.05, y - 0.1, C.paper); });
    p.rect(0, Math.min(uc, 3), 0.2, 0.8, C.cyan).text(`combined ${nf(2).format(uc)}`, Math.min(uc, 2) + 0.05, 0.4, C.paper);
    out(`Combined u_c = √(Σu²) = ${nf(2).format(uc)} µm; report 25.0049 mm ± ${nf(1).format(2 * uc)} µm (k = 2, about 95 %). Amber marks the dominant term: improve that one first. More readings only shrink repeatability, as 1/√n.`);
  },
});

// 09.29 X-bar control chart with a mean shift
def('spcchart', {
  controls: [{ k: 'sh', label: 'Mean shift after subgroup 20 (µm)', min: 0, max: 10, step: 0.5, v: 4, f: 1 }, { k: 'sg', label: 'Process σ (µm)', min: 1, max: 8, step: 0.1, v: 4, f: 1 }],
  draw(p, v, out) {
    const g = gaussSeq(11), mu = 4, xb = [], R = [];
    for (let i = 0; i < 40; i++) { const xs = []; for (let k = 0; k < 5; k++) xs.push(mu + (i >= 20 ? v.sh : 0) + v.sg * g()); xb.push(xs.reduce((a, b) => a + b) / 5); R.push(Math.max(...xs) - Math.min(...xs)); }
    const xbb = xb.slice(0, 20).reduce((a, b) => a + b) / 20, Rb = R.slice(0, 20).reduce((a, b) => a + b) / 20, ucl = xbb + 0.577 * Rb, lcl = xbb - 0.577 * Rb, s = Rb / 2.326;
    p.frame({ x: [0, 41], y: [-20, 25], xlabel: 'subgroup', ylabel: 'mean − 25.000 mm, µm' });
    p.line([0, 41], [20, 20], C.red, 1, [2, 2]).line([0, 41], [-20, -20], C.red, 1, [2, 2]).line([0, 41], [ucl, ucl], C.amber, 1.5, [5, 4]).line([0, 41], [lcl, lcl], C.amber, 1.5, [5, 4]).line([0, 41], [xbb, xbb], C.grey, 1);
    p.line(xb.map((_, i) => i + 1), xb, C.lime, 1.5);
    xb.forEach((x, i) => p.dots([i + 1], [x], x > ucl || x < lcl ? C.red : C.lime, 3.5));
    const first = xb.findIndex((x, i) => i >= 20 && (x > ucl || x < lcl)), cpk = Math.min(20 - xbb, xbb + 20) / (3 * s), cp = 40 / (6 * s);
    out(`Limits from the first 20 subgroups: x̄̄ ± A₂R̄ (amber). Tolerance ±20 µm (red). σ̂ = R̄/d₂ = ${nf(2).format(s)} µm, Cp = ${nf(2).format(cp)}, Cpk = ${nf(2).format(cpk)}. ${v.sh > 0 ? (first >= 0 ? `The shift is flagged at subgroup ${first + 1}.` : 'The shift is not flagged yet: small shifts need run rules or CUSUM.') : 'In control.'}`);
  },
});

// 09.30 characteristic value from a sample
def('charvalue', {
  controls: [{ k: 'n', label: 'Culms tested', min: 5, max: 100, step: 1, v: 30, f: 0 }, { k: 'cv', label: 'Coefficient of variation (%)', min: 5, max: 30, step: 1, v: 15, f: 0 }],
  draw(p, v, out) {
    const g = gaussSeq(21), cov = v.cv / 100, sl = Math.sqrt(Math.log(1 + cov * cov)), ml = Math.log(55) - sl * sl / 2, x = [];
    for (let i = 0; i < v.n; i++) x.push(Math.exp(ml + sl * g()));
    const m = x.reduce((a, b) => a + b) / v.n, s = Math.sqrt(x.reduce((a, b) => a + (b - m) ** 2, 0) / (v.n - 1)), p5 = m - 1.645 * s, fk = p5 * (1 - 2.7 * (s / m) / Math.sqrt(v.n)), tru = Math.exp(ml - 1.6449 * sl);
    const bins = 16, lo = 20, hi = 100, w = (hi - lo) / bins, hist = new Array(bins).fill(0); x.forEach((xi) => { const b = Math.floor((xi - lo) / w); if (b >= 0 && b < bins) hist[b]++; });
    const top = Math.max(...hist) / (v.n * w) * 1.3;
    p.frame({ x: [lo, hi], y: [0, top], xlabel: 'compressive strength, MPa', ylabel: 'density' });
    hist.forEach((c, i) => p.rect(lo + i * w, lo + (i + 0.92) * w, 0, c / (v.n * w), 'rgba(238,255,65,0.45)'));
    const xs = linspace(lo, hi, 200); p.line(xs, xs.map((t) => Math.exp(-((t - m) ** 2) / (2 * s * s)) / (s * Math.sqrt(2 * Math.PI))), C.cyan, 1.5);
    p.line([tru, tru], [0, top], C.grey, 1, [4, 4]).line([p5, p5], [0, top], C.amber, 1.5).line([fk, fk], [0, top], C.red, 2);
    out(`Sample mean ${nf(1).format(m)} MPa, s ${nf(1).format(s)}. 5th percentile m − 1.645s = ${nf(1).format(p5)} (amber); with the small-sample factor f_k = ${nf(1).format(fk)} MPa (red). True 5th percentile ${nf(1).format(tru)} (grey). Design value 0.8 f_k/1.3 = ${nf(1).format(0.8 * fk / 1.3)} MPa. More tests or less scatter: a higher, more honest design value.`);
  },
});

// 10.01 system boundaries
def('sysboundary', {
  controls: [{ type: 'select', k: 'ex', label: 'What are you analysing?', options: ['Gas in a piston-cylinder', 'Steam turbine', 'Sealed vacuum flask', 'Kettle boiling with the lid open'], v: 'Gas in a piston-cylinder' }],
  draw(p, v, out) {
    const sel = ['Gas in a piston-cylinder', 'Steam turbine', 'Sealed vacuum flask', 'Kettle boiling with the lid open'].indexOf(v.ex);
    p.frame({ x: [0, 10], y: [0, 7], xlabel: '', ylabel: '' });
    const box = (x0, x1, y0, y1, c, d) => p.line([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], c, 2, d);
    let msg;
    if (sel === 0) { box(3, 7, 1, 5, C.paper); p.rect(3.1, 6.9, 3.6, 4.0, C.grey); p.line([5, 5], [4, 6.5], C.grey, 3); box(3.05, 6.95, 1.05, 3.6, C.lime, [5, 4]); p.text('gas', 4.6, 2.2, C.lime); arrow(p, 1, 2.3, 2.9, 2.3, C.red); p.text('Q', 1.2, 2.7, C.red); arrow(p, 5.3, 4.2, 5.3, 6.3, C.cyan); p.text('W (boundary moves)', 5.5, 5.5, C.cyan); msg = 'Closed system: no mass crosses the dashed boundary, but heat and work can. The boundary moves with the piston.'; }
    else if (sel === 1) { poly(p, [[3, 3], [7, 1.5], [7, 5.5], [3, 4]], C.paper, null, 2); box(2.8, 7.2, 1.3, 5.7, C.lime, [5, 4]); arrow(p, 0.8, 3.5, 2.9, 3.5, C.amber); p.text('steam in', 0.5, 4, C.amber); arrow(p, 7.1, 2.5, 9.3, 2.5, C.amber); p.text('steam out', 7.6, 1.9, C.amber); arrow(p, 5, 5.6, 5, 6.8, C.cyan); p.text('shaft work', 5.2, 6.4, C.cyan); msg = 'Open system (control volume): mass flows in and out across a fixed boundary. Steady flow, so the energy stored inside does not change.'; }
    else if (sel === 2) { box(3.5, 6.5, 1, 5.5, C.paper); box(3.8, 6.2, 1.3, 5.2, C.grey); box(3.4, 6.6, 0.9, 5.6, C.lime, [5, 4]); p.text('coffee', 4.4, 3, C.amber); msg = 'Isolated (approximately): no mass, no heat, no work cross the boundary. Its energy is constant; its entropy can only grow (10.09).'; }
    else { box(3, 7, 1, 4, C.paper); box(3, 7, 1, 5.2, C.lime, [5, 4]); arrow(p, 5, 0, 5, 0.95, C.red); p.text('Q from the element', 5.2, 0.4, C.red); arrow(p, 4.5, 4.3, 4.5, 6.7, C.amber); p.text('vapour leaves', 4.7, 6.2, C.amber); msg = 'Open and unsteady: heat enters, vapour leaves, and the mass inside falls with time.'; }
    out(msg);
  },
});

// 10.02 molecules in a box
def('gasbox', {
  controls: [{ k: 'T', label: 'Temperature (K)', min: 50, max: 1000, step: 10, v: 300, f: 0 }, { k: 'N', label: 'Molecules in the box (thousands)', min: 1, max: 4, step: 0.5, v: 2, f: 1 }],
  draw(p, v, out) {
    const g = gaussSeq(5), kB = 1.380649e-23, m = 4.6518e-26, s = Math.sqrt(kB * v.T / m), N = 300;
    p.frame({ x: [0, 2.2], y: [0, 1], xlabel: 'left: snapshot (300 shown); right: speed distribution', ylabel: '' });
    p.line([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], C.paper, 1.5);
    const speeds = [];
    for (let i = 0; i < N; i++) { const vx = s * g(), vy = s * g(), vz = s * g(), sp = Math.hypot(vx, vy, vz); speeds.push(sp); const x = 0.03 + 0.94 * ((i * 0.618034) % 1), y = 0.03 + 0.94 * ((i * 0.414214 + 0.37 * ((i * 7) % 11) / 11) % 1); p.dots([x], [y], sp > 2.2 * s ? C.red : sp > 1.6 * s ? C.amber : C.cyan, 2.2); }
    const vmax = 2500, fT = (c, T) => 4 * Math.PI * (m / (2 * Math.PI * kB * T)) ** 1.5 * c * c * Math.exp(-m * c * c / (2 * kB * T)), f = (c) => fT(c, v.T), cs = linspace(0, vmax, 150), fmax = fT(Math.sqrt(2 * kB * 100 / m), 100);
    p.line(cs.map((c) => 1.15 + c / vmax), cs.map((c) => 0.05 + 0.9 * Math.min(1, f(c) / fmax)), C.lime, 2).text('0', 1.14, 0.0, C.grey).text('2500 m/s', 1.85, 0.0, C.grey);
    const pr = v.N * 1000 * kB * v.T / 1e-21, vrms = Math.sqrt(3) * s;
    out(`N₂ at ${v.T} K: rms speed √(3kT/m) = ${nf(0).format(vrms)} m/s. ${nf(1).format(v.N)}k molecules in a 100 nm cube: p = NkT/V = ${nf(0).format(pr)} Pa. Pressure is momentum delivered to the walls: faster molecules hit harder and more often, so p ∝ T.`);
  },
});

// 10.03 p-V work along a polytropic path
def('pvpath', {
  controls: [{ k: 'n', label: 'Polytropic exponent n (pVⁿ = const)', min: 0, max: 1.67, step: 0.01, v: 1.4, f: 2 }, { k: 'V2', label: 'Final volume (L)', min: 1, max: 20, step: 0.5, v: 2, f: 1 }],
  draw(p, v, out) {
    const p1 = 100, V1 = 10, V2 = v.V2, n = v.n, pf = (V) => p1 * (V1 / V) ** n, Vs = linspace(Math.min(V1, V2), Math.max(V1, V2), 120);
    const ymax = Math.max(1100, pf(1) * 1.05 > 1100 ? 1100 : 0);
    p.frame({ x: [0, 21], y: [0, ymax], xlabel: 'V, L', ylabel: 'p, kPa' });
    [0, 1, 1.4].forEach((nn) => p.line(linspace(1, 20, 100), linspace(1, 20, 100).map((V) => p1 * (V1 / V) ** nn), C.grey, 1, [3, 4]));
    poly(p, [[Vs[0], 0], ...Vs.map((V) => [V, pf(V)]), [Vs[Vs.length - 1], 0]], null, V2 < V1 ? 'rgba(255,90,54,0.25)' : 'rgba(238,255,65,0.25)');
    p.line(Vs, Vs.map(pf), C.lime, 2.5).dots([V1, V2], [p1, pf(V2)], C.red, 5);
    const W = Math.abs(n - 1) < 1e-9 ? p1 * V1 * Math.log(V2 / V1) : (pf(V2) * V2 - p1 * V1) / (1 - n);
    out(`W = ∫p dV = ${nf(0).format(W)} J (kPa·L = J) ${W < 0 ? 'done on the gas (compression)' : 'done by the gas (expansion)'}. n = 0 isobaric, 1 isothermal, 1.4 adiabatic for air. Final pressure ${nf(0).format(pf(V2))} kPa. The shaded area is the work; it depends on the path, not just the end states.`);
  },
});

// 10.04 first-law energy flow
def('energysankey', {
  controls: [{ k: 'T2', label: 'Heat at constant pressure up to (K)', min: 300, max: 800, step: 10, v: 500, f: 0 }, { k: 'T3', label: 'Then at constant volume up to (K)', min: 300, max: 1000, step: 10, v: 700, f: 0 }],
  draw(p, v, out) {
    const m = 150e3 * 2e-3 / (287 * 300), T2 = v.T2, T3 = Math.max(v.T3, T2), W = m * 287 * (T2 - 300), dU = m * 718 * (T3 - 300), Q = dU + W;
    const sc = 3 / Math.max(Q, 1);
    p.frame({ x: [0, 10], y: [-2, 4], xlabel: '', ylabel: '' });
    const hq = Q * sc, hw = W * sc, hu = dU * sc;
    poly(p, [[0.5, 1 - hq / 2], [4, 1 - hq / 2], [4, 1 + hq / 2], [0.5, 1 + hq / 2]], null, 'rgba(255,90,54,0.6)');
    poly(p, [[4, 1 + hq / 2 - hw], [7, 3.4 - hw], [7, 3.4], [4, 1 + hq / 2]], null, 'rgba(90,200,250,0.6)');
    poly(p, [[4, 1 - hq / 2], [7, -1.2], [7, -1.2 + hu], [4, 1 - hq / 2 + hu]], null, 'rgba(238,255,65,0.55)');
    p.text(`Q in ${nf(0).format(Q)} J`, 0.6, 1 + hq / 2 + 0.25, C.red).text(`W out ${nf(0).format(W)} J`, 7.1, 3.4 - hw / 2, C.cyan).text(`ΔU ${nf(0).format(dU)} J`, 7.1, -1.2 + hu / 2, C.lime);
    out(`2 L of air (${nf(2).format(m * 1000)} g) at 150 kPa, 300 K. Heat in = work out + rise in internal energy: ${nf(0).format(Q)} = ${nf(0).format(W)} + ${nf(0).format(dU)} J. Only the constant-pressure step does work (piston rises); the constant-volume step puts all the heat into U. Residual: 0.`);
  },
});

// 10.05 steady-flow devices
def('sfeedevice', {
  controls: [{ type: 'select', k: 'dev', label: 'Device', options: ['Nozzle', 'Turbine', 'Compressor', 'Throttle valve'], v: 'Nozzle' }, { k: 'T1', label: 'Inlet temperature (K)', min: 250, max: 1500, step: 10, v: 500, f: 0 }, { k: 'r', label: 'Pressure ratio (high/low)', min: 1, max: 20, step: 0.1, v: 3, f: 1 }],
  draw(p, v, out) {
    const sel = ['Nozzle', 'Turbine', 'Compressor', 'Throttle valve'].indexOf(v.dev), cp = 1005, k = 1.4, e = (k - 1) / k, T1 = v.T1, r = v.r;
    const T2 = sel === 2 ? T1 * r ** e : sel === 3 ? T1 : T1 * r ** -e;
    p.frame({ x: [0, 10], y: [0, 6], xlabel: '', ylabel: '' });
    const shape = [[[1, 2], [5, 2.5], [9, 2.8], [9, 3.2], [5, 3.5], [1, 4]], [[2, 2.5], [8, 1], [8, 5], [2, 3.5]], [[2, 1], [8, 2.5], [8, 3.5], [2, 5]], [[1, 2.6], [4.6, 2.6], [5, 3.2], [5.4, 2.6], [9, 2.6], [9, 3.4], [5.4, 3.4], [5, 2.8], [4.6, 3.4], [1, 3.4]]][sel];
    poly(p, shape, C.paper, 'rgba(242,243,236,0.12)', 2);
    arrow(p, 0.1, 3, 1.4, 3, C.amber); arrow(p, 8.6, 3, 9.9, 3, C.amber);
    p.text(`${nf(0).format(T1)} K`, 0.1, 3.5, C.amber).text(`${nf(0).format(T2)} K`, 8.7, 3.5, C.amber);
    let msg;
    if (sel === 0) { const V2 = Math.sqrt(900 + 2 * cp * (T1 - T2)); msg = `No work, no heat: the enthalpy drop becomes kinetic energy. V₂ = √(V₁² + 2c_p ΔT) = ${nf(0).format(V2)} m/s (inlet 30 m/s).`; }
    else if (sel === 1) msg = `Shaft work out = c_p (T₁ − T₂) = ${nf(1).format(cp * (T1 - T2) / 1000)} kJ per kg of air (isentropic). At 2 kg/s: ${nf(0).format(2 * cp * (T1 - T2) / 1000)} kW.`;
    else if (sel === 2) msg = `Work in = c_p (T₂ − T₁) = ${nf(1).format(cp * (T2 - T1) / 1000)} kJ per kg (isentropic); the air leaves hotter.`;
    else msg = 'No work, no heat, little change in velocity: h₂ = h₁. For an ideal gas that means T₂ = T₁, although the pressure falls (real gases and refrigerants do cool, 10.15).';
    out(msg + ' Steady flow: energy in = energy out, Q − W = ṁ[Δh + ΔV²/2 + gΔz].');
  },
});

// 10.06 T-v diagram of water
def('tvdiagram', {
  controls: [{ k: 'T', label: 'Temperature (°C)', min: 10, max: 300, step: 1, v: 100, f: 0 }, { k: 'lv', label: 'Specific volume, log₁₀(m³/kg)', min: -3.2, max: 2.2, step: 0.02, v: 0, f: 2 }],
  draw(p, v, out) {
    const tab = [[10, 1.2282, 0.001, 106.3032], [20, 2.3393, 0.001002, 57.7567], [30, 4.247, 0.001004, 32.8783], [40, 7.3849, 0.001008, 19.5151], [50, 12.3519, 0.001012, 12.0269], [60, 19.9464, 0.001017, 7.6672], [70, 31.2009, 0.001023, 5.0395], [80, 47.4145, 0.001029, 3.4052], [90, 70.1818, 0.001036, 2.3591], [100, 101.418, 0.001043, 1.6718], [120, 198.6744, 0.00106, 0.8912], [140, 361.5391, 0.00108, 0.5085], [160, 618.2346, 0.001102, 0.3068], [180, 1002.8105, 0.001127, 0.1938], [200, 1554.9279, 0.001157, 0.1272], [250, 3976.1749, 0.001252, 0.0501], [300, 8587.9049, 0.001404, 0.0217]];
    const sat = (T) => { for (let i = 0; i < tab.length - 1; i++) { const a = tab[i], b = tab[i + 1]; if (T >= a[0] && T <= b[0]) { const x0 = 1 / (a[0] + 273.15), x1 = 1 / (b[0] + 273.15), x = 1 / (T + 273.15), q = (x - x0) / (x1 - x0), t = (T - a[0]) / (b[0] - a[0]); return [Math.exp(Math.log(a[1]) + q * Math.log(b[1] / a[1])), a[2] + t * (b[2] - a[2]), Math.exp(Math.log(a[3]) + q * Math.log(b[3] / a[3]))]; } } return null; };
    p.frame({ x: [10 ** -3.2, 10 ** 2.2], y: [0, 320], xlog: true, xlabel: 'specific volume v, m³/kg', ylabel: 'T, °C' });
    p.line(tab.map((r) => r[2]), tab.map((r) => r[0]), C.cyan, 2).line(tab.map((r) => r[3]), tab.map((r) => r[0]), C.amber, 2);
    const s = sat(v.T), vv = 10 ** v.lv; p.line([s[1], s[2]], [v.T, v.T], C.grey, 1, [4, 3]).dots([vv], [v.T], C.red, 6);
    let msg;
    if (vv < s[1]) msg = `Compressed liquid (v below v_f = ${s[1].toFixed(6)}).`;
    else if (vv > s[2]) msg = `Superheated vapour (v above v_g = ${nf(4).format(s[2])}).`;
    else { const x = (vv - s[1]) / (s[2] - s[1]); msg = `Wet mixture at p_sat = ${nf(2).format(s[0])} kPa. Quality x = (v − v_f)/(v_g − v_f) = ${nf(4).format(x)}: ${nf(1).format(x * 100)} % of the mass is vapour.`; }
    out(`${v.T} °C, v = ${vv < 0.01 ? vv.toExponential(3) : nf(4).format(vv)} m³/kg. ${msg} Cyan: saturated liquid line; amber: saturated vapour line.`);
  },
});

// 10.07 pumped storage reservoirs
def('pumpstore', {
  controls: [{ k: 'f', label: 'Upper reservoir level (fraction full)', min: 0, max: 1, step: 0.01, v: 0.7, f: 2 }, { k: 'h', label: 'Head (m)', min: 50, max: 1000, step: 10, v: 300, f: 0 }, { k: 'V', label: 'Upper reservoir capacity (million m³)', min: 1, max: 50, step: 1, v: 25, f: 0 }],
  draw(p, v, out) {
    const E = 1000 * 9.81 * v.h * v.V * 1e6 * v.f, Eh = E / 3.6e12, rt = 0.791, Pmw = 900;
    p.frame({ x: [0, 10], y: [0, 12], xlabel: '', ylabel: 'height (schematic)' });
    const top = 2 + 8 * v.h / 1000;
    poly(p, [[0.5, top], [3.5, top], [3.5, top + 1.6], [0.5, top + 1.6]], C.paper, null, 1.5); p.rect(0.55, 3.45, top, top + 1.6 * v.f, 'rgba(90,200,250,0.7)');
    poly(p, [[6.5, 0.4], [9.5, 0.4], [9.5, 2], [6.5, 2]], C.paper, null, 1.5); p.rect(6.55, 9.45, 0.4, 0.4 + 1.6 * (1 - v.f), 'rgba(90,200,250,0.7)');
    p.line([3.5, 5, 6.5], [top + 0.2, top * 0.5, 1.2], C.grey, 3).dots([5], [top * 0.5], C.amber, 7).text('turbine / pump', 5.3, top * 0.5, C.amber);
    p.line([4, 4], [1.2, top], C.lime, 1, [3, 3]).text(`h = ${v.h} m`, 1.0, (top + 1.2) / 2, C.lime);
    out(`Stored: ρghV = ${nf(2).format(Eh)} GWh in ${nf(1).format(v.V * v.f)} million m³. Generating at 89.4 % returns ${nf(2).format(Eh * 0.894)} GWh, ${nf(1).format(Eh * 0.894 * 1000 / Pmw)} h at 900 MW, and pumping at 88.5 % took ${nf(2).format(Eh / 0.885)} GWh: a 79 % round trip. Energy scales linearly with both head and volume, so high Alpine heads make compact stores.`);
  },
});

// 10.08 heat engine between two reservoirs
def('carnotengine', {
  controls: [{ k: 'Th', label: 'Hot reservoir (K)', min: 350, max: 2500, step: 10, v: 900, f: 0 }, { k: 'Tc', label: 'Cold reservoir (K)', min: 250, max: 400, step: 5, v: 300, f: 0 }, { k: 'eta', label: 'Claimed efficiency (%)', min: 5, max: 95, step: 1, v: 50, f: 0 }],
  draw(p, v, out) {
    const ec = 1 - v.Tc / v.Th, e = v.eta / 100, ok = e <= ec + 1e-12;
    p.frame({ x: [0, 10], y: [0, 10], xlabel: '', ylabel: '' });
    p.rect(1, 9, 8.6, 9.6, 'rgba(255,90,54,0.6)').text(`hot reservoir ${v.Th} K`, 3.2, 9.0, C.paper);
    p.rect(1, 9, 0.4, 1.4, 'rgba(90,200,250,0.6)').text(`cold reservoir ${v.Tc} K`, 3.2, 0.8, C.paper);
    const th = linspace(0, 2 * Math.PI, 60); p.line(th.map((a) => 5 + 1.2 * Math.cos(a)), th.map((a) => 5 + 1.2 * Math.sin(a)), ok ? C.lime : C.red, 2.5).text('engine', 4.3, 4.9, ok ? C.lime : C.red);
    const w = (x) => 1 + 5 * x;
    p.line([5, 5], [8.6, 6.2], C.red, w(1)); p.line([5, 5], [3.8, 1.4], C.cyan, w(1 - e)); p.line([6.2, 9.2], [5, 5], C.amber, w(e));
    p.text('Q_h = 100', 5.3, 7.4, C.red).text(`Q_c = ${nf(0).format(100 * (1 - e))}`, 5.3, 2.6, C.cyan).text(`W = ${nf(0).format(100 * e)}`, 7.2, 5.6, C.amber);
    out(`Carnot limit 1 − T_c/T_h = ${nf(1).format(ec * 100)} %. ${ok ? 'The claim is allowed by the second law.' : `The claim of ${v.eta} % is impossible: combined with a reversed Carnot engine it would turn heat from one reservoir entirely into work (Kelvin-Planck violation).`} Raise T_h or lower T_c to push the limit up.`);
  },
});

// 10.09 mixing water streams
def('mixlab', {
  controls: [{ k: 'm1', label: 'Hot flow (kg/min)', min: 0.5, max: 10, step: 0.1, v: 4.8, f: 1 }, { k: 'T1', label: 'Hot temperature (°C)', min: 20, max: 95, step: 1, v: 60, f: 0 }, { k: 'm2', label: 'Cold flow (kg/min)', min: 0.5, max: 10, step: 0.1, v: 2.4, f: 1 }, { k: 'T2', label: 'Cold temperature (°C)', min: 2, max: 40, step: 1, v: 15, f: 0 }],
  draw(p, v, out) {
    const c = 4186, m1 = v.m1 / 60, m2 = v.m2 / 60, T1 = v.T1 + 273.15, T2 = v.T2 + 273.15, T3 = (m1 * T1 + m2 * T2) / (m1 + m2);
    const s1 = m1 * c * Math.log(T3 / T1), s2 = m2 * c * Math.log(T3 / T2), Sg = s1 + s2;
    const L = Math.max(0.5, Math.abs(s1), s2) * 1.25; p.frame({ x: [0, 4], y: [-L, L], xlabel: '', ylabel: 'entropy change rate, W/K' });
    p.rect(0.3, 1.1, 0, s1, C.red).rect(1.5, 2.3, 0, s2, C.cyan).rect(2.7, 3.5, 0, Sg, C.lime).line([0, 4], [0, 0], C.grey, 1);
    p.text('hot', 0.45, s1 - 0.08 * L, C.paper).text('cold', 1.6, s2 + 0.05 * L, C.paper).text('total', 2.8, Sg + 0.05 * L, C.paper);
    out(`Mixed at ${nf(2).format(T3 - 273.15)} °C. The hot stream loses ${nf(3).format(-s1)} W/K, the cold gains ${nf(3).format(s2)} W/K: net generation S_gen = ${nf(4).format(Sg)} W/K ≥ 0. Lost work potential T₀S_gen = ${nf(1).format(288.15 * Sg)} W. Mixing at different temperatures is irreversible; S_gen is zero only when they are equal.`);
  },
});

// 10.10 compressor on an h-s diagram
def('hscompressor', {
  controls: [{ k: 'rp', label: 'Pressure ratio', min: 1.5, max: 30, step: 0.5, v: 8, f: 1 }, { k: 'eta', label: 'Isentropic efficiency', min: 0.5, max: 1, step: 0.01, v: 0.85, f: 2 }, { k: 'T1', label: 'Inlet temperature (°C)', min: -20, max: 50, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const cp = 1.005, R = 0.287, k = cp / (cp - R), T1 = v.T1 + 273.15, T2s = T1 * v.rp ** ((k - 1) / k), T2 = T1 + (T2s - T1) / v.eta;
    const s = (T, pr) => cp * Math.log(T / 273.15) - R * Math.log(pr);
    const ym = Math.max(1200, cp * T2 * 1.1); p.frame({ x: [-1.1, 1.5], y: [0, ym], xlabel: 's, kJ/(kg K) (relative to 0 °C, 1 bar)', ylabel: 'h, kJ/kg (relative to 0 K)' });
    const Ts = linspace(200, ym / cp, 80);
    p.line(Ts.map((T) => s(T, 1)), Ts.map((T) => cp * T), C.cyan, 1.5).line(Ts.map((T) => s(T, v.rp)), Ts.map((T) => cp * T), C.red, 1.5);
    p.text('p₁', s(0.9 * ym / cp, 1) + 0.04, 0.9 * ym, C.cyan).text('p₂', s(0.9 * ym / cp, v.rp) - 0.18, 0.9 * ym, C.red);
    const s1 = s(T1, 1), s2 = s(T2, v.rp);
    p.line([s1, s1], [cp * T1, cp * T2s], C.grey, 1, [4, 4]).line([s1, s2], [cp * T1, cp * T2], C.lime, 2.5);
    p.dots([s1, s1, s2], [cp * T1, cp * T2s, cp * T2], C.amber, 6).text('1', s1 + 0.06, cp * T1, C.paper).text('2s', s1 - 0.2, cp * T2s, C.paper).text('2', s2 + 0.06, cp * T2, C.paper);
    out(`T₂s = ${nf(1).format(T2s - 273.15)} °C, actual T₂ = ${nf(1).format(T2 - 273.15)} °C. Work ${nf(1).format(cp * (T2 - T1))} kJ/kg against ${nf(1).format(cp * (T2s - T1))} ideal. Entropy generated ${nf(4).format(s2 - s1)} kJ/(kg K); at η = 1 point 2 lands on 2s.`);
  },
});

// 10.11 heat exchanger exergy bars
def('exergybars', {
  controls: [{ k: 'Th', label: 'Hot inlet (°C)', min: 40, max: 200, step: 1, v: 90, f: 0 }, { k: 'mc', label: 'Cold flow (kg/s), hot is 1 kg/s', min: 0.5, max: 5, step: 0.1, v: 1.5, f: 1 }, { k: 'Tc', label: 'Cold inlet (°C)', min: 5, max: 35, step: 1, v: 10, f: 0 }],
  draw(p, v, out) {
    const c = 4.186, T0 = 288.15, Thi = v.Th + 273.15, Tho = Thi - 40, Tci = v.Tc + 273.15, Q = c * 40, Tco = Tci + Q / (v.mc * c);
    const psi = (T) => c * (T - T0) - T0 * c * Math.log(T / T0);
    const dh = psi(Thi) - psi(Tho), dc = v.mc * (psi(Tco) - psi(Tci)), Sg = c * Math.log(Tho / Thi) + v.mc * c * Math.log(Tco / Tci);
    p.frame({ x: [0, 4], y: [0, Math.max(dh, 1) * 1.2], xlabel: '', ylabel: 'exergy rate, kW' });
    p.rect(0.3, 1.1, 0, dh, C.red).rect(1.5, 2.3, 0, dc, C.cyan).rect(2.7, 3.5, 0, dh - dc, C.grey);
    p.text('given', 0.4, dh * 1.05, C.paper).text('gained', 1.5, dc + dh * 0.05, C.paper).text('destroyed', 2.6, (dh - dc) + dh * 0.05, C.paper);
    out(`Hot stream cools by 40 K (${nf(1).format(Q)} kW); cold leaves at ${nf(1).format(Tco - 273.15)} °C. Exergy destroyed ${nf(2).format(dh - dc)} kW = T₀S_gen = ${nf(2).format(T0 * Sg)} kW. Second-law efficiency ${nf(0).format(100 * dc / dh)} %, though the first law counts it as 100 %. Closer temperatures destroy less.${Tco > Thi ? ' (Cold outlet above hot inlet: not achievable in a real exchanger.)' : ''}`);
  },
});

// 10.12 Otto and Diesel p-V loops
def('pvcycle', {
  controls: [{ type: 'select', k: 'k', label: 'Cycle', options: ['Otto', 'Diesel'], v: 'Otto' }, { k: 'r', label: 'Compression ratio', min: 4, max: 24, step: 0.5, v: 10, f: 1 }, { k: 'rc', label: 'Diesel cutoff ratio', min: 1.2, max: 3.5, step: 0.1, v: 2, f: 1 }],
  draw(p, v, out) {
    const sel = ['Otto', 'Diesel'].indexOf(v.k), cv = 0.718, R = 0.287, k = (cv + R) / cv, T1 = 300, p1 = 100, v1 = R * T1 / p1, v2 = v1 / v.r;
    const vc = linspace(v1, v2, 80), pc = vc.map((x) => p1 * (v1 / x) ** k), p2 = pc[pc.length - 1], T2 = T1 * v.r ** (k - 1);
    let v3, p3, eta, T3;
    if (sel === 0) { T3 = T2 + 1200 / cv; p3 = p2 * T3 / T2; v3 = v2; eta = 1 - v.r ** (1 - k); }
    else { v3 = v.rc * v2; p3 = p2; T3 = T2 * v.rc; eta = 1 - v.r ** (1 - k) * (v.rc ** k - 1) / (k * (v.rc - 1)); }
    const ve = linspace(v3, v1, 80), pe = ve.map((x) => p3 * (v3 / x) ** k);
    p.frame({ x: [0, v1 * 1.05], y: [0, 15], xlabel: 'v, m³/kg', ylabel: 'p, MPa' });
    p.line(vc, pc.map((x) => x / 1000), C.cyan, 2).line([v2, v3], [p2 / 1000, p3 / 1000], C.red, 2.5).line(ve, pe.map((x) => x / 1000), C.amber, 2).line([v1, v1], [pe[pe.length - 1] / 1000, p1 / 1000], C.grey, 2);
    out(`${v.k}: η = ${nf(1).format(eta * 100)} %, peak ${nf(0).format(T3)} K at ${nf(2).format(p3 / 1000)} MPa${p3 > 15000 ? ' (off the chart)' : ''}. ${sel === 0 ? 'Heat added at constant volume (1200 kJ/kg); efficiency depends only on r.' : 'Heat added at constant pressure; a larger cutoff ratio lowers efficiency at the same r.'} Air-standard values; real engines reach roughly 60 % of these.`);
  },
});

// 10.13 Brayton T-s loop
def('braytonts', {
  controls: [{ k: 'rp', label: 'Pressure ratio', min: 2, max: 40, step: 0.5, v: 8, f: 1 }, { k: 'ec', label: 'Compressor efficiency', min: 0.6, max: 1, step: 0.01, v: 0.85, f: 2 }, { k: 'et', label: 'Turbine efficiency', min: 0.6, max: 1, step: 0.01, v: 0.9, f: 2 }, { k: 'T3', label: 'Turbine inlet (K)', min: 900, max: 1800, step: 10, v: 1400, f: 0 }],
  draw(p, v, out) {
    const cp = 1.005, R = 0.287, k = cp / (cp - R), T1 = 300, e = v.rp ** ((k - 1) / k);
    const T2 = T1 + T1 * (e - 1) / v.ec, T4 = v.T3 - v.et * (v.T3 - v.T3 / e);
    const s = (T, pr) => cp * Math.log(T / T1) - R * Math.log(pr);
    const wc = cp * (T2 - T1), wt = cp * (v.T3 - T4), q = cp * (v.T3 - T2), eta = (wt - wc) / q, ei = 1 - 1 / e;
    p.frame({ x: [-0.3, 1.6], y: [0, 2000], xlabel: 's, kJ/(kg K) (relative to inlet)', ylabel: 'T, K' });
    const hi = linspace(T2, v.T3, 40), lo = linspace(T4, T1, 40);
    p.line([s(T1, 1), s(T2, v.rp)], [T1, T2], C.cyan, 2.5).line(hi.map((T) => s(T, v.rp)), hi, C.red, 2.5).line([s(v.T3, v.rp), s(T4, 1)], [v.T3, T4], C.amber, 2.5).line(lo.map((T) => s(T, 1)), lo, C.grey, 2);
    p.dots([s(T1, 1), s(T2, v.rp), s(v.T3, v.rp), s(T4, 1)], [T1, T2, v.T3, T4], C.paper, 5);
    p.text('1', s(T1, 1) - 0.08, T1, C.paper).text('2', s(T2, v.rp) - 0.08, T2, C.paper).text('3', s(v.T3, v.rp) + 0.03, v.T3 + 40, C.paper).text('4', s(T4, 1) + 0.04, T4, C.paper);
    out(`Efficiency ${nf(1).format(eta * 100)} % (ideal ${nf(1).format(ei * 100)} %). Net work ${nf(0).format(wt - wc)} kJ/kg; the compressor eats ${nf(0).format(100 * wc / wt)} % of the turbine output (back-work ratio).${wt <= wc ? ' The turbine no longer drives the compressor: no net output.' : ''}`);
  },
});

// 10.14 Rankine T-s with the steam dome
def('rankinets', {
  controls: [{ type: 'select', k: 'k', label: 'Cycle', options: ['Simple superheat', 'With reheat at 2 MPa'], v: 'Simple superheat' }, { k: 'T', label: 'Steam temperature (°C)', min: 350, max: 650, step: 10, v: 500, f: 0 }, { k: 'et', label: 'Turbine efficiency', min: 0.7, max: 1, step: 0.01, v: 1, f: 2 }],
  draw(p, v, out) {
    const sel = ['Simple superheat', 'With reheat at 2 MPa'].indexOf(v.k);
    const dome = [[10, 0.1511, 8.8998], [45.81, 0.6492, 8.1488], [100, 1.3072, 7.3541], [150, 1.8418, 6.8371], [200, 2.3305, 6.4302], [250, 2.7935, 6.0721], [300, 3.2552, 5.7059], [330, 3.5518, 5.4422], [350, 3.7784, 5.211], [365, 4.0014, 4.9497], [373.9, 4.3402, 4.4831]];
    const S10 = [[311.0, 2725.49, 5.6160], [350, 2924.02, 5.9459], [400, 3097.45, 6.2141], [450, 3242.34, 6.4219], [500, 3375.13, 6.5995], [550, 3501.96, 6.7585], [600, 3625.76, 6.9045], [650, 3748.12, 7.0408]];
    const S2 = [[212.38, 2798.29, 6.3390], [250, 2903.24, 6.5475], [300, 3024.18, 6.7684], [350, 3137.65, 6.9583], [400, 3248.34, 7.1292], [450, 3358.22, 7.2866], [500, 3468.24, 7.4337], [550, 3578.97, 7.5725], [600, 3690.74, 7.7043], [650, 3803.75, 7.8302]];
    const ip = (rows, a, b, x) => { let i = 1; while (i < rows.length - 1 && rows[i][a] < x) i++; const r0 = rows[i - 1], r1 = rows[i]; return r0[b] + (x - r0[a]) / (r1[a] - r0[a]) * (r1[b] - r0[b]); };
    const hf = 191.81, hg = 2583.86, sf = 0.6492, sg = 8.1488, wp = 10.09;
    const expand = (h, s0) => { const x = (s0 - sf) / (sg - sf), hs = hf + x * (hg - hf), h6 = h - v.et * (h - hs), xx = (h6 - hf) / (hg - hf); return [h6, xx, sf + xx * (sg - sf)]; };
    p.frame({ x: [0, 9], y: [0, 700], xlabel: 's, kJ/(kg K)', ylabel: 'T, °C' });
    p.line(dome.map((d) => d[1]).concat(dome.map((d) => d[2]).reverse()), dome.map((d) => d[0]).concat(dome.map((d) => d[0]).reverse()), C.grey, 1.5);
    const liq = dome.filter((d) => d[0] <= 311); const h3 = ip(S10, 0, 1, v.T), s3 = ip(S10, 0, 2, v.T);
    const sup = S10.filter((r) => r[0] < v.T).concat([[v.T, h3, s3]]);
    p.line(liq.map((d) => d[1]).concat([3.3606]), liq.map((d) => d[0]).concat([311]), C.red, 2.5).line([3.3606, 5.616], [311, 311], C.red, 2.5).line(sup.map((r) => r[2]), sup.map((r) => r[0]), C.red, 2.5);
    let wt, qin = h3 - hf - wp, ex;
    if (sel === 1) {
      const h4s = ip(S2, 2, 1, s3), h4 = h3 - v.et * (h3 - h4s), T4 = Math.max(212.38, ip(S2, 1, 0, h4)), s4 = ip(S2, 1, 2, h4);
      const h5 = ip(S2, 0, 1, v.T), s5 = ip(S2, 0, 2, v.T); ex = expand(h5, s5);
      const rh = S2.filter((r) => r[0] > T4 && r[0] < v.T);
      p.line([s3, s4], [v.T, T4], C.amber, 2.5).line([s4].concat(rh.map((r) => r[2]), [s5]), [T4].concat(rh.map((r) => r[0]), [v.T]), C.red, 2.5).line([s5, ex[2]], [v.T, 45.81], C.amber, 2.5);
      wt = h3 - h4 + h5 - ex[0]; qin += h5 - h4;
    } else { ex = expand(h3, s3); p.line([s3, ex[2]], [v.T, 45.81], C.amber, 2.5); wt = h3 - ex[0]; }
    p.line([sf, ex[2]], [45.81, 45.81], C.cyan, 2.5);
    const eta = (wt - wp) / qin;
    out(`10 MPa boiler, 10 kPa condenser. Efficiency ${nf(1).format(eta * 100)} %, turbine exit quality ${nf(3).format(Math.min(ex[1], 1))}${ex[1] < 0.88 ? ' (too wet: droplets erode the last blades)' : ''}. Heat in ${nf(0).format(qin)} = work ${nf(0).format(wt - wp)} + heat out ${nf(0).format(ex[0] - hf)} kJ/kg.`);
  },
});

// 10.15 heat pump COP against outdoor temperature
def('heatpumpcop', {
  controls: [{ k: 'Ts', label: 'Supply water (°C)', min: 30, max: 60, step: 1, v: 35, f: 0 }, { k: 'To', label: 'Outdoor air (°C)', min: -20, max: 20, step: 1, v: 2, f: 0 }, { k: 'ec', label: 'Compressor efficiency', min: 0.5, max: 1, step: 0.01, v: 0.7, f: 2 }],
  draw(p, v, out) {
    const SAT = [[-25, 546.28, 2.4090, 139.60, 1.546], [-20, 552.13, 2.3999, 151.36, 1.580], [-15, 557.93, 2.3918, 163.28, 1.616], [-10, 563.65, 2.3846, 175.35, 1.655], [-5, 569.30, 2.3781, 187.59, 1.695], [0, 574.87, 2.3724, 200.00, 1.739], [5, 580.33, 2.3672, 212.60, 1.785], [10, 585.67, 2.3626, 225.40, 1.835], [15, 590.89, 2.3583, 238.40, 1.890], [20, 595.95, 2.3544, 251.64, 1.949], [25, 600.84, 2.3507, 265.11, 2.015], [30, 605.54, 2.3471, 278.83, 2.088], [35, 610.01, 2.3436, 292.84, 2.170], [40, 614.21, 2.3399, 307.15, 2.263], [45, 618.12, 2.3360, 321.79, 2.371], [50, 621.66, 2.3317, 336.80, 2.499], [55, 624.77, 2.3268, 352.23, 2.652], [60, 627.36, 2.3210, 368.14, 2.841], [65, 629.29, 2.3139, 384.60, 3.086]];
    const sat = (T) => { const i = Math.min(Math.max(Math.floor((T + 25) / 5), 0), SAT.length - 2), a = SAT[i], b = SAT[i + 1], t = (T - a[0]) / 5; return a.map((x, j) => x + t * (b[j] - x)); };
    const cop = (To) => { const Te = To - 5, Tc = v.Ts + 5, A = sat(Te), B = sat(Tc), h1 = A[1], s1 = A[2]; const T2s = (Tc + 273.15) * Math.exp(Math.max(s1 - B[2], 0) / B[4]); const h2s = B[1] + B[4] * (T2s - Tc - 273.15), h2 = h1 + (h2s - h1) / v.ec; return (h2 - B[3]) / (h2 - h1); };
    const carnot = (To) => (v.Ts + 5 + 273.15) / (v.Ts - To + 10);
    const xs = linspace(-20, 20, 81);
    p.frame({ x: [-20, 20], y: [0, 12], xlabel: 'outdoor temperature, °C', ylabel: 'heating COP' });
    p.line(xs, xs.map(carnot), C.grey, 1.5, [5, 4]).line(xs, xs.map(cop), C.lime, 2.5).dots([v.To], [cop(v.To)], C.amber, 7);
    p.text('Carnot', -18, Math.min(11.3, carnot(-18) + 0.6), C.grey).text('R290 cycle', 8, Math.max(0.6, cop(8) - 1.0), C.lime);
    const c = cop(v.To);
    out(`At ${v.To} °C outdoors, supplying ${v.Ts} °C water: COP ${nf(2).format(c)} (Carnot ${nf(2).format(carnot(v.To))}). Each kWh of electricity delivers ${nf(1).format(c)} kWh of heat. Lower supply temperatures (floor heating) raise the COP; so does milder weather.`);
  },
});

// 10.16 van der Waals isotherms and the Maxwell construction
def('vdwiso', {
  controls: [{ k: 'T', label: 'Temperature (K)', min: 240, max: 400, step: 1, v: 280, f: 0 }],
  draw(p, v, out) {
    const R = 8.314462618, A = 0.3640, B = 4.267e-5, T = v.T, pf = (x) => R * T / (x - B) - A / (x * x);
    const vs = logspace(Math.log10(1.15 * B), Math.log10(60 * B), 400);
    p.frame({ x: [1.15 * B * 1e6, 60 * B * 1e6], xlog: true, y: [0, 14], xlabel: 'v, cm³/mol (log)', ylabel: 'p, MPa' });
    p.line(vs.map((x) => x * 1e6), vs.map((x) => Math.min(Math.max(pf(x) / 1e6, -1), 15)), C.cyan, 2);
    p.line(vs.map((x) => x * 1e6), vs.map((x) => Math.min(R * T / x / 1e6, 15)), C.grey, 1, [4, 4]);
    let msg = `Above T_c = 304.0 K the isotherm has no loop: a single fluid phase.`;
    if (T < 304) {
      const roots = (pp) => { const r = []; let prev = pf(vs[0]) - pp; for (let i = 1; i < vs.length; i++) { const cur = pf(vs[i]) - pp; if (prev * cur <= 0) { let a = vs[i - 1], b = vs[i]; for (let k = 0; k < 60; k++) { const m = (a + b) / 2; ((pf(a) - pp) * (pf(m) - pp) <= 0) ? (b = m) : (a = m); } r.push((a + b) / 2); } prev = cur; } return r; };
      const ex = []; for (let i = 1; i < vs.length - 1; i++) { const d0 = pf(vs[i]) - pf(vs[i - 1]), d1 = pf(vs[i + 1]) - pf(vs[i]); if (d0 * d1 < 0) ex.push(pf(vs[i])); }
      let lo = Math.max(ex[0], 1), hi = ex[1], ps = 0, rr = [];
      for (let k = 0; k < 60; k++) { ps = (lo + hi) / 2; rr = roots(ps); if (rr.length < 3) break; const vl = rr[0], vg = rr[rr.length - 1]; const I = R * T * Math.log((vg - B) / (vl - B)) + A * (1 / vg - 1 / vl) - ps * (vg - vl); I > 0 ? (lo = ps) : (hi = ps); }
      if (rr.length >= 3) { const vl = rr[0], vg = rr[rr.length - 1]; p.line([vl * 1e6, vg * 1e6], [ps / 1e6, ps / 1e6], C.lime, 2.5).dots([vl * 1e6, vg * 1e6], [ps / 1e6, ps / 1e6], C.amber, 5);
        msg = `Maxwell construction: saturation at ${nf(3).format(ps / 1e6)} MPa, where the loop's two areas match. Liquid ${nf(1).format(vl * 1e6)}, vapour ${nf(1).format(vg * 1e6)} cm³/mol. The wiggle between them is unstable.`; }
    }
    out(`${msg} Dashed: ideal gas. At large volume (low pressure) the two curves merge and Z → 1.`);
  },
});

// 10.17 psychrometric chart
def('psychart', {
  controls: [{ type: 'select', k: 'k', label: 'Site', options: ['Bali, sea level (101.3 kPa)', 'Zurich, 408 m (96.6 kPa)'], v: 'Bali, sea level (101.3 kPa)' }, { k: 'T', label: 'Air temperature (°C)', min: -10, max: 45, step: 0.5, v: 31, f: 1 }, { k: 'RH', label: 'Relative humidity (%)', min: 5, max: 100, step: 1, v: 75, f: 0 }],
  draw(p, v, out) {
    const P = [101.3e3, 96.6e3][['Bali, sea level (101.3 kPa)', 'Zurich, 408 m (96.6 kPa)'].indexOf(v.k)];
    const ps = (T) => 610.94 * Math.exp(17.625 * T / (T + 243.04)), W = (T, rh) => 622 * rh * ps(T) / (P - rh * ps(T));
    const Ts = linspace(-10, 45, 111);
    p.frame({ x: [-10, 45], y: [0, 40], xlabel: 'dry-bulb temperature, °C', ylabel: 'humidity ratio, g/kg' });
    [0.2, 0.4, 0.6, 0.8].forEach((rh) => p.line(Ts, Ts.map((T) => Math.min(W(T, rh), 40)), C.grey, 1, [3, 3]));
    p.line(Ts, Ts.map((T) => Math.min(W(T, 1), 40)), C.cyan, 2).text('100 %', 30, 36, C.cyan);
    const w = W(v.T, v.RH / 100), g = Math.log(v.RH / 100 * ps(v.T) / 610.94), Td = 243.04 * g / (17.625 - g), h = 1.006 * v.T + w / 1000 * (2501 + 1.86 * v.T);
    p.line([Td, v.T], [w, w], C.amber, 1.5, [4, 3]).dots([v.T], [w], C.lime, 7).dots([Td], [w], C.amber, 5);
    out(`Humidity ratio ${nf(2).format(w)} g/kg, dew point ${nf(2).format(Td)} °C (cool the air horizontally to the saturation curve), enthalpy ${nf(1).format(h)} kJ/kg. At RH 100 % the dew point equals the air temperature.`);
  },
});

// 10.18 adiabatic flame temperature against equivalence ratio
def('flametemp', {
  controls: [{ k: 'phi', label: 'Equivalence ratio φ', min: 0.5, max: 1.5, step: 0.01, v: 1, f: 2 }, { k: 'T0', label: 'Reactant temperature (K)', min: 250, max: 800, step: 10, v: 300, f: 0 }],
  draw(p, v, out) {
    const RU = 8.314462618;
    const N = {
      CH4: [[0.074851495, 0.0133909467, -5.73285809e-06, 1.22292535e-09, -1.0181523e-13, -9468.34459, 18.437318], [5.14987613, -0.0136709788, 4.91800599e-05, -4.84743026e-08, 1.66693956e-11, -10246.6476, -4.64130376]],
      O2: [[3.28253784, 0.00148308754, -7.57966669e-07, 2.09470555e-10, -2.16717794e-14, -1088.45772, 5.45323129], [3.78245636, -0.00299673416, 9.84730201e-06, -9.68129509e-09, 3.24372837e-12, -1063.94356, 3.65767573]],
      N2: [[2.92664, 0.0014879768, -5.68476e-07, 1.0097038e-10, -6.753351e-15, -922.7977, 5.980528], [3.298677, 0.0014082404, -3.963222e-06, 5.641515e-09, -2.444854e-12, -1020.8999, 3.950372]],
      CO2: [[3.85746029, 0.00441437026, -2.21481404e-06, 5.23490188e-10, -4.72084164e-14, -48759.166, 2.27163806], [2.35677352, 0.00898459677, -7.12356269e-06, 2.45919022e-09, -1.43699548e-13, -48371.9697, 9.90105222]],
      H2O: [[3.03399249, 0.00217691804, -1.64072518e-07, -9.7041987e-11, 1.68200992e-14, -30004.2971, 4.9667701], [4.19864056, -0.0020364341, 6.52040211e-06, -5.48797062e-09, 1.77197817e-12, -30293.7267, -0.849032208]],
      CO: [[2.71518561, 0.00206252743, -9.98825771e-07, 2.30053008e-10, -2.03647716e-14, -14151.8724, 7.81868772], [3.57953347, -0.00061035368, 1.01681433e-06, 9.07005884e-10, -9.04424499e-13, -14344.086, 3.50840928]],
      H2: [[3.3372792, -4.94024731e-05, 4.99456778e-07, -1.79566394e-10, 2.00255376e-14, -950.158922, -3.20502331], [2.34433112, 0.00798052075, -1.9478151e-05, 2.01572094e-08, -7.37611761e-12, -917.935173, 0.683010238]],
    };
    const co = (sp, T) => (T > 1000 ? N[sp][0] : N[sp][1]);
    const h = (sp, T) => { const a = co(sp, T); return RU * T * (a[0] + a[1] * T / 2 + a[2] * T * T / 3 + a[3] * T ** 3 / 4 + a[4] * T ** 4 / 5 + a[5] / T); };
    const s = (sp, T) => { const a = co(sp, T); return RU * (a[0] * Math.log(T) + a[1] * T + a[2] * T * T / 2 + a[3] * T ** 3 / 3 + a[4] * T ** 4 / 4 + a[6]); };
    // rich mixtures: water-gas shift CO2 + H2 <-> CO + H2O in equilibrium, as in the lesson
    const prod = (ph, T) => {
      const o2 = 2 / ph; if (ph <= 1) return { CO2: 1, H2O: 2, O2: o2 - 2, N2: 3.76 * o2 };
      const g = h('CO', T) + h('H2O', T) - h('CO2', T) - h('H2', T) - T * (s('CO', T) + s('H2O', T) - s('CO2', T) - s('H2', T)), K = Math.exp(-g / (RU * T)), O = 2 * o2;
      let lo = Math.max(0, 2 - O + 1e-12), hi = Math.min(1, 4 - O), x = 0;
      for (let k = 0; k < 60; k++) { x = (lo + hi) / 2; (x * (O - 2 + x) - K * (1 - x) * (4 - O - x) > 0) ? (hi = x) : (lo = x); }
      return { CO2: 1 - x, CO: x, H2O: O - 2 + x, H2: 4 - O - x, N2: 3.76 * o2 };
    };
    const Tad = (ph) => { const Hr = h('CH4', v.T0) + 2 / ph * (h('O2', v.T0) + 3.76 * h('N2', v.T0)); let lo = 300, hi = 3800; for (let k = 0; k < 45; k++) { const T = (lo + hi) / 2, pr = prod(ph, T); let Hp = 0; for (const sp in pr) Hp += pr[sp] * h(sp, T); Hp > Hr ? (hi = T) : (lo = T); } return (lo + hi) / 2; };
    const phis = linspace(0.5, 1.5, 81), Ts = phis.map(Tad);
    p.frame({ x: [0.5, 1.5], y: [1000, 3000], xlabel: 'equivalence ratio φ', ylabel: 'adiabatic flame temperature, K' });
    p.line(phis, Ts, C.amber, 2.5).line([1, 1], [1000, 3000], C.grey, 1, [4, 4]).dots([v.phi], [Tad(v.phi)], C.lime, 7);
    out(`φ = ${nf(2).format(v.phi)}: T_ad ≈ ${nf(0).format(Tad(v.phi))} K (no dissociation). ${v.phi < 1 ? 'Lean: excess air soaks up heat.' : v.phi > 1 ? 'Rich: not enough oxygen to release all the fuel energy; CO and H₂ leave unburnt.' : 'Stoichiometric: the peak.'} Preheating the reactants raises every point.`);
  },
});

// 10.19 Gibbs energy against extent of CO2 dissociation
def('gibbsmin', {
  controls: [{ k: 'T', label: 'Temperature (K)', min: 1500, max: 3500, step: 50, v: 2500, f: 0 }, { k: 'lp', label: 'Pressure (atm, log scale)', min: -2, max: 2, step: 0.1, v: 0, f: 1 }],
  draw(p, v, out) {
    const RU = 8.314462618, T = v.T, P = 10 ** v.lp * 101325;
    const N = { CO2: [[3.85746029, 0.00441437026, -2.21481404e-06, 5.23490188e-10, -4.72084164e-14, -48759.166, 2.27163806]], CO: [[2.71518561, 0.00206252743, -9.98825771e-07, 2.30053008e-10, -2.03647716e-14, -14151.8724, 7.81868772]], O2: [[3.28253784, 0.00148308754, -7.57966669e-07, 2.09470555e-10, -2.16717794e-14, -1088.45772, 5.45323129]] };
    const g0 = (sp) => { const a = N[sp][0]; const h = RU * T * (a[0] + a[1] * T / 2 + a[2] * T * T / 3 + a[3] * T ** 3 / 4 + a[4] * T ** 4 / 5 + a[5] / T); const s = RU * (a[0] * Math.log(T) + a[1] * T + a[2] * T * T / 2 + a[3] * T ** 3 / 3 + a[4] * T ** 4 / 4 + a[6]); return h - T * s; };
    const G = (x) => { const n = { CO2: 1 - x, CO: x, O2: x / 2 }, Nt = 1 + x / 2; let g = 0; for (const sp in n) if (n[sp] > 0) g += n[sp] * (g0(sp) + RU * T * Math.log(n[sp] / Nt * P / 1e5)); return g; };
    let a = 1e-9, b = 1 - 1e-9; const r = (Math.sqrt(5) - 1) / 2; for (let k = 0; k < 80; k++) { const c = b - r * (b - a), d = a + r * (b - a); G(c) < G(d) ? (b = d) : (a = c); } const xe = (a + b) / 2;
    const xs = linspace(0.001, 0.999, 200), G0 = G(0.001), gs = xs.map((x) => (G(x) - G0) / 1000);
    const lo = Math.min(...gs), hi = Math.max(...gs);
    p.frame({ x: [0, 1], y: [lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo)], xlabel: 'extent of dissociation ξ', ylabel: 'G − G(ξ≈0), kJ' });
    p.line(xs, gs, C.cyan, 2.5).dots([xe], [(G(xe) - G0) / 1000], C.lime, 7);
    out(`Minimum at ξ = ${nf(4).format(xe)}: ${nf(1).format(100 * xe)} % of the CO2 dissociated at ${T} K and ${nf(2).format(10 ** v.lp)} atm (mole fraction CO ${nf(3).format(xe / (1 + xe / 2))}). Hotter shifts the minimum right; higher pressure shifts it left, because dissociation increases the number of moles.`);
  },
});

// 10.20 Swiss seasonal balance (assumed data)
def('swissseason', {
  controls: [{ k: 'pv', label: 'Solar PV (TWh/year)', min: 0, max: 45, step: 1, v: 24, f: 0 }, { type: 'select', k: 'k', label: 'Nuclear', options: ['Off (phased out)', 'On (18 TWh/year)'], v: 'Off (phased out)' }],
  draw(p, v, out) {
    const nuc = ['Off (phased out)', 'On (18 TWh/year)'].indexOf(v.k);
    const sh = (A, pk) => Array.from({ length: 12 }, (_, m) => 1 + A * Math.cos(2 * Math.PI * (m - pk) / 12));
    const mon = (tot, A, pk) => sh(A, pk).map((w) => tot / 12 * w);
    const D = mon(60, 0.15, 0), RR = mon(18, 0.45, 6), LI = mon(20, 0.8, 6), NU = mon(nuc ? 18 : 0, 0.1, 0), OT = mon(4, 0, 0), PV = mon(v.pv, 0.6, 6);
    const net = D.map((d, m) => RR[m] + LI[m] + NU[m] + OT[m] + PV[m] - d), ann = net.reduce((s, x) => s + x, 0);
    let L = 0; const lev = net.map((x) => (L += x - ann / 12));
    const st = Math.max(...lev) - Math.min(...lev), win = [0, 1, 2, 9, 10, 11].reduce((s, m) => s + net[m], 0);
    p.frame({ x: [0, 12], y: [-14, 14], xlabel: 'month (Jan to Dec)', ylabel: 'TWh' });
    net.forEach((x, m) => p.rect(m + 0.15, m + 0.85, 0, x, x >= 0 ? C.lime : C.red));
    p.line(lev.map((_, m) => m + 0.5), lev, C.cyan, 2.5).line([0, 12], [0, 0], C.grey, 1);
    p.text('monthly surplus / deficit', 0.3, 12.6, C.paper).text('storage level', 0.3, 11, C.cyan);
    out(`Assumed data, not official statistics. Annual balance ${ann >= 0 ? '+' : ''}${nf(1).format(ann)} TWh; winter half (Oct–Mar) ${nf(1).format(win)} TWh. Shifting surpluses into the deficits takes ${nf(1).format(st)} TWh of seasonal storage, ${st > 8.8 ? `${nf(1).format(st - 8.8)} TWh more than the roughly 8.8 TWh of storage lakes` : 'within the roughly 8.8 TWh of storage lakes'}. More solar improves the year but deepens the summer surplus that must be carried to winter.`);
  },
});

// 11.01 Couette shear between plates
def('couette', {
  controls: [{ k: 'U', label: 'Top plate speed (m/s)', min: 0, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'h', label: 'Gap (mm)', min: 0.2, max: 5, step: 0.1, v: 1, f: 1 }, { type: 'select', k: 'k', label: 'Fluid', options: ['Water (1.0 mPa s)', 'SAE 30 oil (0.29 Pa s)', 'Honey (10 Pa s)'], v: 'SAE 30 oil (0.29 Pa s)' }, { k: 'G', label: 'Pressure gradient −dp/dx (MPa/m)', min: -4, max: 4, step: 0.1, v: 0, f: 1 }],
  draw(p, v, out) {
    const sel = ['Water (1.0 mPa s)', 'SAE 30 oil (0.29 Pa s)', 'Honey (10 Pa s)'].indexOf(v.k), mu = [1e-3, 0.29, 10][sel], h = v.h / 1000;
    const u = (y) => v.U * y / h + (-v.G * 1e6) / (2 * mu) * (y * y - h * y);
    const ys = linspace(0, h, 41), us = ys.map(u), um = Math.max(1, ...us.map(Math.abs)) * 1.15;
    p.frame({ x: [-um * 0.3, um], y: [-0.1, 1.15], xlabel: 'u, m/s', ylabel: 'y / h' });
    p.rect(-um * 0.3, um, -0.1, 0, C.grey).rect(-um * 0.3, um, 1, 1.06, C.amber);
    arrow(p, um * 0.5, 1.1, um * 0.5 + Math.max(0.05, v.U / um) * um * 0.3, 1.1, C.amber, 2);
    for (let i = 0; i <= 40; i += 4) arrow(p, 0, ys[i] / h, us[i], ys[i] / h, C.cyan, 1.5);
    p.line(us, ys.map((y) => y / h), C.lime, 2.5);
    const tauTop = mu * (v.U / h + (-v.G * 1e6) / (2 * mu) * h);
    out(`Wall shear on the moving plate τ = μ du/dy = ${nf(1).format(tauTop)} Pa${v.G === 0 ? ', the same everywhere: the profile is linear, u = Uy/h.' : '. A pressure gradient adds a parabola on top of the linear Couette profile.'} Viscosity ${mu} Pa s.`);
  },
});

// 11.02 manometer and pressure with depth
def('manometer', {
  controls: [{ k: 'h', label: 'Manometer reading h (mm)', min: 0, max: 400, step: 1, v: 120, f: 0 }, { type: 'select', k: 'k', label: 'Manometer fluid', options: ['Mercury (13 546 kg/m³)', 'Water (998 kg/m³)', 'Oil (850 kg/m³)'], v: 'Mercury (13 546 kg/m³)' }, { type: 'select', k: 'f', label: 'Fluid in the pipe', options: ['Water', 'Air'], v: 'Water' }],
  draw(p, v, out) {
    const rm = [13546, 998, 850][['Mercury (13 546 kg/m³)', 'Water (998 kg/m³)', 'Oil (850 kg/m³)'].indexOf(v.k)], rf = v.f === 'Water' ? 998 : 1.2;
    const dp = (rm - rf) * 9.81 * v.h / 1000, H = v.h / 1000;
    p.frame({ x: [0, 10], y: [-0.3, 0.7], xlabel: '', ylabel: 'height, m' });
    p.rect(2, 3, -0.25, 0.6, 'rgba(90,200,250,0.25)').rect(7, 8, -0.25, 0.6, 'rgba(90,200,250,0.25)').rect(2, 8, -0.3, -0.25, 'rgba(90,200,250,0.25)');
    const mc = rm > 5000 ? 'rgba(200,200,210,0.9)' : rm > 900 && rm < 1000 ? 'rgba(90,150,250,0.9)' : 'rgba(255,190,60,0.9)';
    p.rect(2, 3, -0.25, 0.1 - H / 2, mc).rect(7, 8, -0.25, 0.1 + H / 2, mc).rect(2, 8, -0.3, -0.25, mc);
    p.line([3.2, 3.2], [0.1 - H / 2, 0.1 + H / 2], C.lime, 1.5).text(`h = ${v.h} mm`, 3.4, 0.1, C.lime);
    p.text('high p', 1.4, 0.65, C.paper).text('low p', 7.1, 0.65, C.paper);
    out(`Δp = (ρ_m − ρ_f) g h = (${rm} − ${rf}) × 9.81 × ${nf(3).format(H)} = ${nf(2).format(dp / 1000)} kPa. ${rm === 998 && v.f === 'Water' ? 'Same fluid on both sides: no reading is possible.' : rm < rf ? 'Negative: a manometer fluid lighter than the pipe fluid must be used in an inverted U-tube.' : ''} For reference, 10 m of water is 98.1 kPa.`);
  },
});

// 11.03 tilting hull with metacentre
def('tilthull', {
  controls: [{ k: 'th', label: 'Heel angle (°)', min: 0, max: 25, step: 0.5, v: 10, f: 1 }, { k: 'KG', label: 'Centre of gravity above keel KG (m)', min: 0.5, max: 4.5, step: 0.05, v: 1.8, f: 2 }, { k: 'm', label: 'Displacement (t)', min: 60, max: 280, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const B = 6, D = 2.5, L = 20, T = v.m * 1000 / (1025 * L * B), th = v.th * Math.PI / 180, bm = B * B / (12 * T), GM = T / 2 + bm - v.KG;
    const GZ = Math.sin(th) * (GM + bm / 2 * Math.tan(th) ** 2);
    const rot = (x, y) => [x * Math.cos(th) - (y - T) * Math.sin(th), x * Math.sin(th) + (y - T) * Math.cos(th)];
    p.frame({ x: [-5, 5], y: [-3, 5], xlabel: 'm', ylabel: 'm (waterline at 0)' });
    p.rect(-5, 5, -3, 0, 'rgba(90,200,250,0.25)');
    poly(p, [[-B / 2, 0], [B / 2, 0], [B / 2, D], [-B / 2, D]].map(([x, y]) => rot(x, y)), C.paper, 'rgba(255,190,60,0.25)', 2);
    const yb = T / 2 + bm / 2 * Math.tan(th) ** 2, xb = -(B * B / (12 * T)) * Math.tan(th);     // wall-sided centre of buoyancy, ship frame
    const Gp = rot(0, v.KG), Bp = rot(xb, yb), Mp = rot(0, T / 2 + bm);
    p.dots([Gp[0]], [Gp[1]], C.red, 6).dots([Bp[0]], [Bp[1]], C.cyan, 6).dots([Mp[0]], [Mp[1]], C.lime, 6);
    p.text('G', Gp[0] + 0.15, Gp[1], C.red).text('B', Bp[0] + 0.15, Bp[1], C.cyan).text('M', Mp[0] + 0.15, Mp[1], C.lime);
    arrow(p, Gp[0], Gp[1], Gp[0], Gp[1] - 1.2, C.red, 2); arrow(p, Bp[0], Bp[1], Bp[0], Bp[1] + 1.2, C.cyan, 2);
    out(`Draft ${nf(3).format(T)} m, BM = B²/12T = ${nf(3).format(bm)} m, GM = ${nf(3).format(GM)} m: ${GM > 0 ? 'stable, the metacentre is above G.' : 'unstable, G is above the metacentre and the barge capsizes.'} Righting arm GZ = ${nf(3).format(GZ)} m, moment ${nf(0).format(v.m * 9.81 * GZ)} kN m${GZ < 0 ? ' (heeling, not righting)' : ''}. Box hull, wall-sided formula; valid until the deck edge goes under.`);
  },
});

// 11.04 streamlines, pathlines, streaklines
def('flowlines', {
  controls: [{ type: 'select', k: 'k', label: 'Show', options: ['All three', 'Streamline', 'Pathline', 'Streakline'], v: 'All three' }, { k: 'w', label: 'Oscillation frequency ω (rad/s), 0 = steady', min: 0, max: 2, step: 0.05, v: 1, f: 2 }, { k: 't', label: 'Time now (s)', min: 0.5, max: 9, step: 0.1, v: 6.3, f: 1 }],
  draw(p, v, out) {
    const sel = ['All three', 'Streamline', 'Pathline', 'Streakline'].indexOf(v.k), U0 = 1, V0 = 0.5, w = v.w, t = v.t;
    const vy = (tt) => (w === 0 ? V0 * 0.6 : V0 * Math.sin(w * tt));
    const Y = (t0, tt) => (w === 0 ? V0 * 0.6 * (tt - t0) : V0 * (Math.cos(w * t0) - Math.cos(w * tt)) / w);       // exact particle y
    p.frame({ x: [0, 9], y: [-3, 3], xlabel: 'x, m', ylabel: 'y, m' });
    const ts = linspace(0, t, 120);
    if (sel === 0 || sel === 2) p.line(ts.map((tt) => U0 * tt), ts.map((tt) => Y(0, tt)), C.lime, 2.5);
    if (sel === 0 || sel === 3) p.line(ts.map((t0) => U0 * (t - t0)), ts.map((t0) => Y(t0, t)), C.amber, 2.5);
    if (sel === 0 || sel === 1) { const xe = U0 * t; p.line([xe - 3, xe + 3], [Y(0, t) - 3 * vy(t) / U0, Y(0, t) + 3 * vy(t) / U0], C.cyan, 2, [6, 4]); }
    p.dots([0], [0], C.paper, 5).dots([U0 * t], [Y(0, t)], C.lime, 6);
    p.text('pathline', 0.3, 2.6, C.lime).text('streakline', 3.2, 2.6, C.amber).text('streamline now', 6.0, 2.6, C.cyan);
    out(`${w === 0 ? 'Steady field: all three lines lie on top of each other.' : `Unsteady field u = 1, v = 0.5 sin(${nf(2).format(w)} t). The pathline is one particle's history, the streakline joins every particle released from the origin (dye from a nozzle), and the streamline is tangent to the velocity at this instant only.`}`);
  },
});

// 11.05 material acceleration arrows
def('materialacc', {
  controls: [{ type: 'select', k: 'k', label: 'Field', options: ['Stagnation point u = ax, v = −ay', 'Solid-body rotation u = −Ωy, v = Ωx', 'Uniform flow'], v: 'Stagnation point u = ax, v = −ay' }, { k: 'a', label: 'Strength a or Ω (1/s)', min: 0.1, max: 1.5, step: 0.05, v: 0.5, f: 2 }],
  draw(p, v, out) {
    const sel = ['Stagnation point u = ax, v = −ay', 'Solid-body rotation u = −Ωy, v = Ωx', 'Uniform flow'].indexOf(v.k), a = v.a;
    const U = (x, y) => [[a * x, -a * y], [-a * y, a * x], [0.8, 0]][sel];
    const Acc = (x, y) => [[a * a * x, a * a * y], [-a * a * x, -a * a * y], [0, 0]][sel];
    p.frame({ x: [-2.2, 2.2], y: [-2.2, 2.2], xlabel: 'x, m', ylabel: 'y, m' });
    const g = linspace(-1.6, 1.6, 5);
    for (const x of g) for (const y of g) { const [u, w] = U(x, y), [ax, ay] = Acc(x, y); arrow(p, x, y, x + 0.25 * u, y + 0.25 * w, C.cyan, 1.2); if (sel !== 2) arrow(p, x, y, x + 0.25 * ax, y + 0.25 * ay, C.red, 1.6); }
    out(`${['The flow is steady, yet parcels speed up along x and slow down along y: Du/Dt = (u·∇)u = (a²x, a²y), pointing away from the origin.', 'Steady again, but every parcel turns: the convective acceleration (−Ω²x, −Ω²y) is the centripetal acceleration of circular motion.', 'Uniform, steady flow: zero material acceleration everywhere.'][sel]} Blue: velocity, red: acceleration (both scaled by 0.25).`);
  },
});

// 11.06 pipe contraction with flow-rate counter
def('contraction', {
  controls: [{ k: 'Q', label: 'Flow rate (L/s)', min: 5, max: 150, step: 1, v: 70, f: 0 }, { k: 'D2', label: 'Throat diameter (mm)', min: 60, max: 300, step: 5, v: 150, f: 0 }],
  draw(p, v, out) {
    const D1 = 300, D3 = 200, Q = v.Q / 1000;
    const prof = (x) => (x < 3 ? D1 : x < 4 ? D1 + (v.D2 - D1) * (x - 3) : x < 6 ? v.D2 : x < 7 ? v.D2 + (D3 - v.D2) * (x - 6) : D3);
    const xs = linspace(0, 10, 101);
    p.frame({ x: [0, 10], y: [-200, 200], xlabel: 'distance along pipe, m', ylabel: 'radius, mm' });
    p.line(xs, xs.map((x) => prof(x) / 2), C.paper, 2).line(xs, xs.map((x) => -prof(x) / 2), C.paper, 2);
    [1.5, 5, 8.5].forEach((x) => { const D = prof(x) / 1000, A = Math.PI * D * D / 4, V = Q / A; p.line([x, x], [-prof(x) / 2, prof(x) / 2], C.grey, 1, [3, 3]); arrow(p, x - 0.15 * Math.min(V, 12), 0, x + 0.15 * Math.min(V, 12), 0, C.cyan, 2.5); p.text(`${nf(2).format(V)} m/s`, x - 0.7, prof(x) / 2 + 22, C.cyan).text(`${nf(1).format(A * V * 1000)} L/s`, x - 0.6, -prof(x) / 2 - 30, C.lime); });
    out(`Incompressible: Q = AV is the same at every section (${v.Q} L/s). The speed in the throat is (D₁/D₂)² = ${nf(2).format((D1 / v.D2) ** 2)} times the inlet speed.`);
  },
});

// 11.07 venturi: speed and pressure along a contraction
def('venturipipe', {
  controls: [{ k: 'Q', label: 'Flow rate (L/s)', min: 1, max: 25, step: 0.5, v: 12, f: 1 }, { k: 'd', label: 'Throat diameter (mm)', min: 30, max: 95, step: 1, v: 50, f: 0 }],
  draw(p, v, out) {
    const rho = 998, D = 0.1, d = v.d / 1000, Q = v.Q / 1000, p1 = 200;     // kPa at the inlet
    const Dx = (x) => (x < 1 ? D : x < 2 ? D - (D - d) * 0.5 * (1 - Math.cos(Math.PI * (x - 1))) : x < 2.5 ? d : x < 4.5 ? d + (D - d) * 0.5 * (1 - Math.cos(Math.PI * (x - 2.5) / 2)) : D);
    const xs = linspace(0, 5.5, 221), u = xs.map((x) => Q / (Math.PI * Dx(x) ** 2 / 4)), pr = u.map((uu) => p1 + 0.5 * rho * (u[0] ** 2 - uu * uu) / 1000);
    const pmin = Math.min(...pr);
    p.frame({ x: [0, 5.5], y: [Math.min(0, pmin - 20), 270], xlabel: 'distance, m', ylabel: 'pressure, kPa (pipe outline above)' });
    p.line(xs, xs.map((x) => 245 + Dx(x) * 120), C.paper, 1.5).line(xs, xs.map((x) => 245 - Dx(x) * 120), C.paper, 1.5);
    p.line(xs, pr, C.cyan, 2.5);
    [0.5, 2.25, 5].forEach((x) => { const i = Math.round(x / 5.5 * 220); p.dots([x], [pr[i]], C.amber, 5).text(`${nf(2).format(u[i])} m/s`, x - 0.3, pr[i] - 12, C.amber); });
    const dp = pr[0] - pmin;
    out(`Bernoulli: p + ½ρV² is constant along the streamline. The throat speed is ${nf(2).format(Math.max(...u))} m/s and the pressure drops by ${nf(2).format(dp)} kPa, a ${nf(0).format(dp * 1e6 / ((13546 - 998) * 9.81))} mm mercury reading. Ideal flow recovers it fully downstream; a real venturi loses 10–20 % of it.${pmin < 2.3 ? ' Throat pressure below vapour pressure: the water would cavitate.' : ''}`);
  },
});

// 11.08 draining tank
def('draintank', {
  controls: [{ type: 'select', k: 'k', label: 'Tank shape', options: ['Cylinder', 'Inverted cone'], v: 'Cylinder' }, { k: 'dh', label: 'Outlet diameter (mm)', min: 10, max: 60, step: 1, v: 25, f: 0 }, { k: 't', label: 'Time (min)', min: 0, max: 40, step: 0.5, v: 10, f: 1 }],
  draw(p, v, out) {
    const sel = ['Cylinder', 'Inverted cone'].indexOf(v.k), R = 0.6, H = 1.5, a = Math.PI * (v.dh / 1000) ** 2 / 4, k = 0.61 * a * Math.sqrt(2 * 9.81);
    const Tcyl = Math.PI * R * R / k * 2 * Math.sqrt(H), Tcone = 0.4 * Math.PI * R * R / k * Math.sqrt(H) / (H * H) * H * H;
    // closed forms for h(t): cylinder sqrt(h) = sqrt(H) - k t / (2 A); cone h^2.5 = H^2.5 - 2.5 k H^2 t / (pi R^2)
    const hc = (t) => Math.max(0, Math.sqrt(H) - k * t / (2 * Math.PI * R * R)) ** 2, hk = (t) => Math.max(0, H ** 2.5 - 2.5 * k * H * H * t / (Math.PI * R * R)) ** 0.4;
    const hf = sel === 0 ? hc : hk, T = sel === 0 ? Tcyl : Tcone, t = v.t * 60, h = hf(t);
    p.frame({ x: [0, 45], y: [0, 1.7], xlabel: 'time, min', ylabel: 'water depth, m' });
    const ts = linspace(0, 45, 181);
    p.line(ts, ts.map((m) => hf(m * 60)), C.cyan, 2.5).dots([v.t], [h], C.lime, 7);
    const x0 = 36, w = 7; if (sel === 0) { poly(p, [[x0, 0], [x0 + w, 0], [x0 + w, H], [x0, H]], C.paper, null, 1.5); p.rect(x0, x0 + w, 0, h, 'rgba(90,200,250,0.6)'); }
    else { poly(p, [[x0 + w / 2, 0], [x0 + w, H], [x0, H]], C.paper, null, 1.5); poly(p, [[x0 + w / 2, 0], [x0 + w / 2 + w / 2 * h / H, h], [x0 + w / 2 - w / 2 * h / H, h]], 'rgba(90,200,250,0.9)', 'rgba(90,200,250,0.6)', 1); }
    out(`Depth ${nf(3).format(h)} m, outflow speed √(2gh) = ${nf(2).format(Math.sqrt(2 * 9.81 * h))} m/s. Empty after ${nf(1).format(T / 60)} min. The level falls slower and slower in the cylinder because the driving head shrinks; the cone speeds up at the end because its area shrinks too.`);
  },
});

// 11.09 jet on a vane
def('jetvane', {
  controls: [{ k: 'th', label: 'Turning angle (°)', min: 0, max: 180, step: 5, v: 90, f: 0 }, { k: 'V', label: 'Jet speed (m/s)', min: 2, max: 40, step: 1, v: 20, f: 0 }, { k: 'u', label: 'Vane speed (m/s)', min: 0, max: 20, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const rho = 998, A = Math.PI * 0.03 ** 2 / 4, Vr = Math.max(v.V - v.u, 0), m = rho * A * Vr, th = v.th * Math.PI / 180;
    const Fx = m * Vr * (1 - Math.cos(th)), Fy = -m * Vr * Math.sin(th);
    p.frame({ x: [-5, 5], y: [-4, 4], xlabel: '', ylabel: '' });
    arrow(p, -4.5, 0, 0, 0, C.cyan, 4);
    const R = 1.2, arc = linspace(0, th, 30);
    p.line(arc.map((a) => R * Math.sin(a)), arc.map((a) => R - R * Math.cos(a)), C.paper, 3);
    arrow(p, R * Math.sin(th), R - R * Math.cos(th), R * Math.sin(th) + 2.5 * Math.cos(th), R - R * Math.cos(th) + 2.5 * Math.sin(th), C.cyan, 4);
    const s = 3 / Math.max(1, 2 * rho * A * 40 * 40) * 1;
    arrow(p, 0.5, -0.5, 0.5 + Fx * s * 3, -0.5 + Fy * s * 3, C.red, 3);
    p.text('force on vane', 0.6 + Fx * s * 3, -0.9 + Fy * s * 3, C.red);
    out(`Mass flow meeting the vane ${nf(2).format(m)} kg/s at relative speed ${nf(1).format(Vr)} m/s. Force on the vane F_x = ṁV_r(1 − cos θ) = ${nf(1).format(Fx)} N, F_y = ${nf(1).format(Fy)} N. A flat plate (90°) feels ṁV; turning the jet right back (180°) doubles it, the idea behind the Pelton bucket.`);
  },
});

// 11.10 Pelton runner: power against bucket speed
def('peltonrun', {
  controls: [{ k: 'H', label: 'Net head (m)', min: 100, max: 1900, step: 50, v: 800, f: 0 }, { k: 'r', label: 'Bucket speed / jet speed', min: 0, max: 1, step: 0.01, v: 0.5, f: 2 }, { k: 'b', label: 'Bucket turning angle (°)', min: 90, max: 180, step: 1, v: 165, f: 0 }],
  draw(p, v, out) {
    const Q = 2, V = 0.98 * Math.sqrt(2 * 9.81 * v.H), Ph = 1000 * 9.81 * Q * v.H;
    const P = (x) => { const u = x * V, w1 = V - u, cu2 = u - w1 * Math.cos((180 - v.b) * Math.PI / 180); return 1000 * Q * u * (V - cu2); };
    const xs = linspace(0, 1, 101);
    p.frame({ x: [0, 1], y: [0, 1.05], xlabel: 'bucket speed u / jet speed V', ylabel: 'efficiency P / ρgQH' });
    p.line(xs, xs.map((x) => P(x) / Ph), C.lime, 2.5).dots([v.r], [P(v.r) / Ph], C.amber, 7).line([0.5, 0.5], [0, 1.05], C.grey, 1, [4, 4]);
    // runner sketch
    const cx = 0.83, cy = 0.82, R = 0.11;
    for (let k = 0; k < 12; k++) { const a = k * Math.PI / 6; p.line([cx + 0.6 * R * Math.cos(a), cx + R * Math.cos(a)], [cy + 0.6 * R * Math.sin(a) * 1.6, cy + R * Math.sin(a) * 1.6], C.paper, 2); }
    arrow(p, cx - 0.32, cy + R * 1.6, cx - 0.02, cy + R * 1.6, C.cyan, 3);
    out(`Jet speed ${nf(1).format(V)} m/s. At u/V = ${nf(2).format(v.r)} the runner makes ${nf(2).format(P(v.r) / 1e6)} MW of the ${nf(2).format(Ph / 1e6)} MW available (${nf(1).format(100 * P(v.r) / Ph)} %). The ideal optimum is u = V/2, where the water leaves the bucket with almost no absolute speed.`);
  },
});

// 11.11 Reynolds number from honey to the Rhine
def('reslider', {
  controls: [{ type: 'select', k: 'k', label: 'Case', options: ['Honey dripping off a spoon', 'Blood in a capillary', 'Bacterium swimming', 'Water from a tap', 'Cyclist in air', 'Limmat in Zurich', 'Rhine at Basel', 'Airliner wing'], v: 'Water from a tap' }],
  draw(p, v, out) {
    const cases = { 'Honey dripping off a spoon': [0.01, 0.005, 7e-3], 'Blood in a capillary': [1e-3, 8e-6, 3.3e-6], 'Bacterium swimming': [3e-5, 2e-6, 1e-6], 'Water from a tap': [1.5, 0.01, 1e-6], 'Cyclist in air': [12, 1.7, 1.5e-5], 'Limmat in Zurich': [1.0, 3, 1.3e-6], 'Rhine at Basel': [2.0, 8, 1.3e-6], 'Airliner wing': [250, 5, 3.5e-5] };
    const [U, L, nu] = cases[v.k], Re = U * L / nu, lg = Math.log10(Re);
    p.frame({ x: [-8, 9], y: [0, 3], xlabel: 'log₁₀ Re', ylabel: '' });
    p.rect(-8, 0, 0.5, 1.0, 'rgba(90,200,250,0.35)').rect(0, 3.3, 0.5, 1.0, 'rgba(255,190,60,0.35)').rect(3.3, 9, 0.5, 1.0, 'rgba(255,90,54,0.35)');
    p.text('creeping, viscous', -7.5, 1.3, C.cyan).text('laminar', 0.3, 1.3, C.amber).text('mostly turbulent', 4, 1.3, C.red);
    Object.entries(cases).forEach(([n, c]) => { const x = Math.log10(c[0] * c[1] / c[2]); p.dots([x], [0.75], n === v.k ? C.lime : C.grey, n === v.k ? 8 : 4); });
    p.line([lg, lg], [0.5, 2.3], C.lime, 1.5).text(`Re = ${Re < 1 ? Re.toExponential(1) : nf(0).format(Re)}`, Math.min(lg, 5.5) - 0.5, 2.5, C.lime);
    out(`${v.k}: U = ${U} m/s, L = ${L} m, ν = ${nu.toExponential(1)} m²/s, so Re = UL/ν = ${Re < 1 ? Re.toExponential(2) : nf(0).format(Re)}. Inertia beats viscosity by that factor. The thresholds are rough: pipe flow turns turbulent near Re ≈ 2300 based on diameter.`);
  },
});

// 11.12 Froude model vs prototype
def('froudemodel', {
  controls: [{ k: 'lam', label: 'Length scale λ (prototype/model)', min: 5, max: 100, step: 1, v: 50, f: 0 }, { k: 'Q', label: 'Prototype discharge (m³/s)', min: 100, max: 3000, step: 50, v: 1500, f: 0 }],
  draw(p, v, out) {
    const L = v.lam, items = [['length', 1], ['velocity', 0.5], ['time', 0.5], ['flow', 2.5], ['force', 3], ['power', 3.5]];
    p.frame({ x: [0, 6], y: [0, 7.5], xlabel: '', ylabel: 'log₁₀ (prototype / model)' });
    items.forEach(([n, e], i) => { const r = Math.log10(L ** e); p.rect(i + 0.15, i + 0.85, 0, r, C.cyan).text(n, i + 0.1, r + 0.25, C.paper); });
    const Qm = v.Q / L ** 2.5, Vp = 8, Vm = Vp / Math.sqrt(L), Rer = L ** 1.5;
    out(`Model discharge ${nf(2).format(Qm * 1000)} L/s for ${v.Q} m³/s at full scale. Water at 8 m/s on the prototype moves at ${nf(3).format(Vm)} m/s in the model, and the model runs ${nf(2).format(Math.sqrt(L))} times faster in time. Froude matches; Reynolds is ${nf(0).format(Rer)} times smaller in the model, so it must stay well turbulent (Re above about 10⁴) for friction to be modelled acceptably.`);
  },
});

// 11.13 Navier-Stokes term explorer (x-momentum)
def('nsterms', {
  controls: [{ type: 'select', k: 'k', label: 'Flow', options: ['Plane Poiseuille', 'Taylor-Green vortex', 'Taylor-Green with p = 0 (wrong)'], v: 'Taylor-Green vortex' }, { k: 'x', label: 'Position x (along y = 0.5)', min: 0, max: 6.28, step: 0.02, v: 0.6, f: 2 }, { k: 't', label: 'Time t', min: 0, max: 10, step: 0.1, v: 1, f: 1 }],
  draw(p, v, out) {
    const sel = ['Plane Poiseuille', 'Taylor-Green vortex', 'Taylor-Green with p = 0 (wrong)'].indexOf(v.k), rho = 1, mu = 0.1, U = 1, y = 0.5, x = v.x;
    let T;
    if (sel === 0) { const G = 1; T = [0, 0, -G, G]; }
    else { const F = Math.exp(-2 * mu / rho * v.t), u = U * Math.sin(x) * Math.cos(y) * F; const half = 0.5 * rho * U * U * F * F * Math.sin(2 * x); T = [-2 * mu * u, half, sel === 1 ? -half : 0, 2 * mu * u]; }
    const S = T.reduce((a, b) => a + b, 0), names = ['ρ ∂u/∂t', 'ρ(u·∇)u', '∂p/∂x', '−μ∇²u', 'sum'], vals = T.concat([S]);
    const L = Math.max(0.2, ...vals.map(Math.abs)) * 1.3;
    p.frame({ x: [0, 5], y: [-L, L], xlabel: '', ylabel: 'term (x-momentum)' });
    vals.forEach((val, i) => { p.rect(i + 0.15, i + 0.85, 0, val, i === 4 ? (Math.abs(S) < 1e-9 ? C.lime : C.red) : C.cyan); p.text(names[i], i + 0.1, (val >= 0 ? -0.12 : 0.06) * L, C.paper); });
    p.line([0, 5], [0, 0], C.grey, 1);
    out(`${['Steady parallel flow: no acceleration at all. The pressure gradient is balanced entirely by viscous friction.', 'Every term changes with x and t, yet they always sum to zero: an exact solution. Convection is balanced by the pressure gradient, and the decay in time by viscosity.', 'Without its pressure field the vortex fails: the convective term is left unbalanced, so this is not a solution.'][sel]} Sum = ${nf(4).format(S)}.`);
  },
});

// 11.14 Hagen-Poiseuille profile
def('pipeprofile', {
  controls: [{ k: 'dp', label: 'Pressure drop per metre (Pa/m)', min: 10, max: 2000, step: 10, v: 400, f: 0 }, { k: 'D', label: 'Pipe diameter (mm)', min: 2, max: 40, step: 1, v: 20, f: 0 }, { type: 'select', k: 'k', label: 'Fluid', options: ['Olive oil (84 mPa s)', 'Glycerol (1.4 Pa s)', 'Water (1.0 mPa s)'], v: 'Olive oil (84 mPa s)' }],
  draw(p, v, out) {
    const sel = ['Olive oil (84 mPa s)', 'Glycerol (1.4 Pa s)', 'Water (1.0 mPa s)'].indexOf(v.k), mu = [0.084, 1.4, 1e-3][sel], rho = [910, 1260, 998][sel], R = v.D / 2000;
    const umax = v.dp * R * R / (4 * mu), Q = Math.PI * R ** 4 * v.dp / (8 * mu), um = umax / 2, Re = rho * um * 2 * R / mu;
    const rs = linspace(-R, R, 81);
    p.frame({ x: [0, umax * 1.25], y: [-R * 1e3 * 1.2, R * 1e3 * 1.2], xlabel: 'u, m/s', ylabel: 'r, mm' });
    p.line([0, umax * 1.25], [R * 1e3, R * 1e3], C.paper, 2).line([0, umax * 1.25], [-R * 1e3, -R * 1e3], C.paper, 2);
    for (let i = 4; i <= 76; i += 8) arrow(p, 0, rs[i] * 1e3, v.dp * (R * R - rs[i] ** 2) / (4 * mu), rs[i] * 1e3, C.cyan, 1.4);
    p.line(rs.map((r) => v.dp * (R * R - r * r) / (4 * mu)), rs.map((r) => r * 1e3), C.lime, 2.5).line([um, um], [-R * 1e3, R * 1e3], C.amber, 1.5, [5, 4]);
    out(`Centre speed ${umax < 0.01 ? umax.toExponential(2) : nf(3).format(umax)} m/s, mean (dashed) exactly half. Q = πR⁴Δp/(8μL) = ${nf(2).format(Q * 1e6)} mL/s. Re = ${nf(0).format(Re)}: ${Re < 2300 ? 'laminar, the parabola holds.' : 'too high, the real flow would be turbulent and this profile is invalid.'}`);
  },
});

// 11.15 Rankine vortex with a coconut
def('rankinevortex', {
  controls: [{ k: 'G', label: 'Circulation Γ (m²/s)', min: 0.2, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'a', label: 'Core radius (m)', min: 0.1, max: 1, step: 0.05, v: 0.4, f: 2 }, { k: 'r', label: 'Coconut radius (m)', min: 0.05, max: 1.5, step: 0.05, v: 1, f: 2 }],
  draw(p, v, out) {
    const ut = (r) => (r < v.a ? v.G * r / (2 * Math.PI * v.a * v.a) : v.G / (2 * Math.PI * r));
    const rs = linspace(0, 1.6, 161), umax = v.G / (2 * Math.PI * v.a);
    p.frame({ x: [0, 1.6], y: [0, umax * 1.25], xlabel: 'radius r, m', ylabel: 'swirl speed, m/s' });
    p.rect(0, v.a, 0, umax * 1.25, 'rgba(255,90,54,0.15)').text('core: vorticity 2Ω', 0.02, umax * 1.17, C.red).text('outside: irrotational', Math.min(v.a + 0.05, 1.0), umax * 1.05, C.cyan);
    p.line(rs, rs.map(ut), C.cyan, 2.5).dots([v.r], [ut(v.r)], C.amber, 8).text('coconut', v.r + 0.03, ut(v.r) + umax * 0.06, C.amber);
    const T = 2 * Math.PI * v.r / ut(v.r);
    out(`Coconut at r = ${nf(2).format(v.r)} m moves at ${nf(3).format(ut(v.r))} m/s and circles once every ${nf(1).format(T)} s. ${v.r < v.a ? 'Inside the core it turns like a solid body: the same period at every radius.' : 'Outside the core, speed falls as 1/r; the fluid parcels orbit without spinning about their own axes.'} Circulation around any loop enclosing the core is Γ = ${nf(1).format(v.G)} m²/s.`);
  },
});

// 11.16 potential flow past a cylinder with circulation
def('potentialcyl', {
  controls: [{ k: 'g', label: 'Clockwise circulation, Γ/(4πUa)', min: 0, max: 1.4, step: 0.02, v: 0.4, f: 2 }],
  draw(p, v, out) {
    const g = v.g, G = g * 4 * Math.PI;                       // U = 1, a = 1
    const vel = (x, y) => { const r2 = x * x + y * y, re = (x * x - y * y) / (r2 * r2), im = -2 * x * y / (r2 * r2);
      // dw/dz = 1 - 1/z^2 + i G/(2 pi z);  u = Re, v = -Im
      const dRe = 1 - re + G / (2 * Math.PI) * (y / r2), dIm = -im + G / (2 * Math.PI) * (x / r2);
      return [dRe, -dIm]; };
    sqframe(p, 2.4, 'x / a', 'y / a');
    for (const y0 of linspace(-2.6, 2.6, 19)) {
      let x = -4, y = y0; const xs = [x], ys = [y];
      for (let k = 0; k < 700; k++) {
        let [u1, v1] = vel(x, y); let s = Math.hypot(u1, v1); if (s < 1e-6) break;
        const xm = x + 0.015 * u1 / s, ym = y + 0.015 * v1 / s; [u1, v1] = vel(xm, ym); s = Math.hypot(u1, v1); if (s < 1e-6) break;
        x += 0.03 * u1 / s; y += 0.03 * v1 / s; if (x * x + y * y < 1.0 || x > 4) { xs.push(x); ys.push(y); break; }
        xs.push(x); ys.push(y);
      }
      p.line(xs, ys, C.cyan, 1.3);
    }
    const th = linspace(0, 2 * Math.PI, 90);
    poly(p, th.map((t) => [Math.cos(t), Math.sin(t)]), C.paper, 'rgba(200,200,200,0.25)', 2);
    if (g <= 1) { const t1 = Math.asin(-g), t2 = Math.PI - t1; p.dots([Math.cos(t1), Math.cos(t2)], [Math.sin(t1), Math.sin(t2)], C.amber, 6); }
    else { const yy = -(g + Math.sqrt(g * g - 1)); p.dots([0], [yy], C.amber, 6); }
    arrow(p, 0, 0, 0, Math.min(2, 0.4 + g * 1.2), C.lime, 3);
    const L = 1.2 * 10 * g * 4 * Math.PI * 10 * 0.5;
    out(`${g === 0 ? 'No circulation: the flow is symmetric, the pressure forces cancel and there is no lift and no drag (d\'Alembert\'s paradox).' : g <= 1 ? `Circulation speeds the flow over the top and slows it underneath; the stagnation points (amber) slide down to ${nf(1).format(Math.asin(-g) * 180 / Math.PI)}° and ${nf(1).format(180 + Math.asin(g) * 180 / Math.PI)}°.` : 'The circulation is so strong that the stagnation point leaves the surface; a ring of fluid circulates with the cylinder.'} For a 1 m cylinder in a 10 m/s wind, lift = ρUΓ = ${nf(0).format(L)} N per metre; drag stays zero.`);
  },
});

// 11.17 specific energy diagram
def('specenergy', {
  controls: [{ k: 'q', label: 'Discharge per unit width q (m²/s)', min: 0.5, max: 5, step: 0.1, v: 2, f: 1 }, { k: 'y', label: 'Flow depth y (m)', min: 0.15, max: 3, step: 0.01, v: 1.5, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, q = v.q, E = (y) => y + q * q / (2 * g * y * y), yc = Math.cbrt(q * q / g), ys = linspace(0.08, 3.2, 300);
    p.frame({ x: [0, 4], y: [0, 3.2], xlabel: 'specific energy E, m', ylabel: 'depth y, m' });
    p.line([0, 3.2], [0, 3.2], C.grey, 1, [4, 4]).text('E = y', 2.75, 3.0, C.grey);
    p.line(ys.map(E), ys, C.lime, 2.5).line([0, 1.5 * yc], [yc, yc], C.amber, 1, [4, 4]).dots([1.5 * yc], [yc], C.amber, 6).text('critical, Fr = 1', 1.5 * yc + 0.08, yc - 0.12, C.amber);
    const Ey = E(v.y), Fr = q / (v.y * Math.sqrt(g * v.y));
    let lo = 1e-4, hi = yc; const target = Ey, other = v.y > yc;
    if (!other) { lo = yc; hi = 20; }
    for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; ((E(m) - target) * (E(lo) - target) <= 0) ? (hi = m) : (lo = m); }
    const ya = (lo + hi) / 2;
    p.dots([Ey], [v.y], C.cyan, 7);
    if (Ey < 4) { p.line([Ey, Ey], [v.y, ya], C.cyan, 1, [3, 3]); if (ya < 3.2) p.dots([Ey], [ya], C.red, 5); }
    out(`Depth ${nf(2).format(v.y)} m: V = ${nf(2).format(q / v.y)} m/s, Fr = ${nf(2).format(Fr)} (${Fr < 1 ? 'subcritical, slow and deep' : 'supercritical, fast and shallow'}), E = ${nf(3).format(Ey)} m. Alternate depth with the same energy: ${nf(3).format(ya)} m (red). Critical depth ${nf(3).format(yc)} m, minimum energy ${nf(3).format(1.5 * yc)} m.`);
  },
});

// 11.18 subak terrace cascade
def('subakcascade', {
  controls: [{ k: 'Q', label: 'Inflow from the canal (L/s)', min: 2, max: 30, step: 1, v: 10, f: 0 }, { k: 'b', label: 'Notch width (m)', min: 0.1, max: 0.6, step: 0.05, v: 0.3, f: 2 }, { k: 't', label: 'Time since the gate opened (h)', min: 0, max: 12, step: 0.1, v: 3, f: 1 }],
  draw(p, v, out) {
    const n = 5, A = 400, crest = 0.05, Qin0 = v.Q / 1000, k = v.b * (2 / 3) ** 1.5 * Math.sqrt(9.81), dt = 5, h = new Array(n).fill(0);
    let Qend = 0;
    for (let s = 0; s < Math.round(v.t * 3600 / dt); s++) { let Qi = Qin0; for (let i = 0; i < n; i++) { const Qo = h[i] > crest ? k * (h[i] - crest) ** 1.5 : 0; h[i] += (Qi - Qo) / A * dt; Qi = Qo; } Qend = Qi; }
    p.frame({ x: [0, n], y: [0, n * 0.6 + 1.0], xlabel: 'terrace', ylabel: '', noy: true });
    const sc = 4;                                                   // vertical exaggeration of water depth
    for (let i = 0; i < n; i++) {
      const bed = (n - i) * 0.6 - 0.3;
      p.rect(i, i + 1, 0, bed, 'rgba(140,100,60,0.55)');
      if (h[i] > 0) p.rect(i, i + 0.97, bed, bed + h[i] * sc, 'rgba(41,182,246,0.7)');
      p.line([i + 0.97, i + 0.97], [bed, bed + crest * sc], C.paper, 3);
      p.text(`${nf(1).format(h[i] * 100)} cm`, i + 0.12, bed + 0.62, C.cyan);
    }
    arrow(p, 0.05, n * 0.6 + 0.88, 0.5, n * 0.6 + 0.88, C.cyan, 2); p.text('canal', 0.55, n * 0.6 + 0.84, C.cyan);
    const Hs = Math.pow(Qin0 / k, 2 / 3);
    out(`After ${nf(1).format(v.t)} h: outflow from the last terrace ${nf(2).format(Qend * 1000)} L/s of ${v.Q} L/s in. Each terrace holds 5 cm before spilling; at steady state the head over every notch is (Q/k)²ᐟ³ = ${nf(2).format(Hs * 100)} cm, so each holds ${nf(2).format((crest + Hs) * 100)} cm. Depths drawn ×4.`);
  },
});

// 11.19 hydraulic jump profile
def('hydjump', {
  controls: [{ k: 'F', label: 'Upstream Froude number Fr₁', min: 1, max: 9, step: 0.1, v: 5.1, f: 1 }, { k: 'y1', label: 'Upstream depth y₁ (m)', min: 0.05, max: 0.6, step: 0.01, v: 0.25, f: 2 }],
  draw(p, v, out) {
    const g = 9.81, F = v.F, y1 = v.y1, r = (Math.sqrt(1 + 8 * F * F) - 1) / 2, y2 = r * y1, V1 = F * Math.sqrt(g * y1), q = V1 * y1, V2 = q / y2;
    const E = (y) => y + q * q / (2 * g * y * y), dE = E(y1) - E(y2), Ltop = Math.max(6, y2 * 1.4);
    const Lj = 6 * y2, x0 = 2;
    p.frame({ x: [0, x0 + Lj + 3], y: [0, Ltop], xlabel: 'distance, m', ylabel: 'height, m' });
    const xs = linspace(0, x0 + Lj + 3, 200), surf = xs.map((x) => (x < x0 ? y1 : x > x0 + Lj ? y2 : y1 + (y2 - y1) * (1 - Math.exp(-4 * (x - x0) / Lj)) / (1 - Math.exp(-4))));
    poly(p, xs.map((x, i) => [x, surf[i]]).concat([[xs[xs.length - 1], 0], [0, 0]]), C.cyan, 'rgba(41,182,246,0.35)', 1);
    p.line(xs, surf, C.cyan, 2.5);
    p.line([0, x0 + Lj + 3], [E(y1), E(y1)], C.amber, 1.5, [5, 4]).line([0, x0 + Lj + 3], [E(y2), E(y2)], C.lime, 1.5, [5, 4]);
    if (E(y1) < Ltop) p.text('energy line before', 0.1, Math.min(E(y1), Ltop) - 0.25 * Ltop / 6, C.amber);
    p.text('energy line after', 0.1, E(y2) + 0.12 * Ltop / 6, C.lime);
    if (F > 1.05) for (let i = 0; i < 3; i++) { const cx = x0 + Lj * (0.15 + 0.2 * i), cy = y1 + (y2 - y1) * (0.55 + 0.1 * i), rr = (y2 - y1) * 0.18; p.line(linspace(0, 5.5, 30).map((t) => cx + rr * Math.cos(t)), linspace(0, 5.5, 30).map((t) => cy + rr * Math.sin(t)), C.paper, 1.2); }
    const kind = F < 1.7 ? 'undular jump, a train of standing waves' : F < 2.5 ? 'weak jump' : F < 4.5 ? 'oscillating jump, which shakes stilling basins' : F < 9 ? 'steady jump, the design range for stilling basins' : 'strong, rough jump';
    out(`V₁ = ${nf(2).format(V1)} m/s into a ${kind}. Conjugate depth y₂ = ${nf(3).format(y2)} m (×${nf(2).format(r)}), V₂ = ${nf(2).format(V2)} m/s, Fr₂ = ${nf(3).format(V2 / Math.sqrt(g * y2))}. Head lost ${nf(3).format(dE)} m, ${nf(0).format(100 * dE / E(y1))}% of the incoming energy, ${nf(1).format(9.81 * q * dE)} kW per metre width.`);
  },
});

// 11.20 water hammer at a penstock valve (method of characteristics)
def('hammerpen', {
  controls: [{ k: 'tc', label: 'Valve closing time (s)', min: 0, max: 12, step: 0.1, v: 3, f: 1 }, { k: 'V0', label: 'Initial flow speed (m/s)', min: 0.5, max: 4, step: 0.1, v: 2, f: 1 }, { k: 'a', label: 'Wave speed a (m/s)', min: 300, max: 1400, step: 50, v: 1000, f: 0 }],
  draw(p, v, out) {
    const g = 9.81, L = 600, H0 = 100, a = v.a, V0 = v.V0, N = 30, dt = L / N / a, B = a / g, T = 14;
    let H = new Array(N + 1).fill(H0), V = new Array(N + 1).fill(V0); const ts = [0], hv = [H0];
    for (let t = dt; t <= T; t += dt) {
      const Hn = H.slice(), Vn = V.slice();
      for (let i = 1; i < N; i++) { const cp = H[i - 1] + B * V[i - 1], cm = H[i + 1] - B * V[i + 1]; Hn[i] = (cp + cm) / 2; Vn[i] = (cp - cm) / (2 * B); }
      Hn[0] = H0; Vn[0] = (H0 - (H[1] - B * V[1])) / B;
      const tau = v.tc > 0 ? Math.max(0, 1 - t / v.tc) : 0, cpv = H[N - 1] + B * V[N - 1];
      if (tau === 0) Vn[N] = 0; else { const Cv = (tau * V0) ** 2 / H0; Vn[N] = (-B * Cv + Math.sqrt((B * Cv) ** 2 + 4 * Cv * Math.max(cpv, 0))) / 2; }
      Hn[N] = cpv - B * Vn[N]; H = Hn; V = Vn; ts.push(t); hv.push(H[N]);
    }
    const dJ = a * V0 / g, top = H0 + dJ * 1.15;
    p.frame({ x: [0, T], y: [H0 - dJ * 1.15, top], xlabel: 'time, s', ylabel: 'head at the valve, m' });
    if (H0 - dJ * 1.15 < -10) p.rect(0, T, H0 - dJ * 1.15, -10, 'rgba(255,90,54,0.15)');
    p.line([0, T], [H0 + dJ, H0 + dJ], C.amber, 1.5, [5, 4]).text('Joukowsky H₀ + aV₀/g', 0.2, H0 + dJ + dJ * 0.05, C.amber).line([0, T], [H0, H0], C.grey, 1);
    if (v.tc > 0) p.line([v.tc, v.tc], [H0 - dJ * 1.15, top], C.grey, 1, [3, 3]);
    p.line(ts, hv, C.cyan, 2);
    const mx = Math.max(...hv), mn = Math.min(...hv), tr = 2 * L / a;
    out(`Round trip 2L/a = ${nf(2).format(tr)} s. Peak head rise ${nf(1).format(mx - H0)} m (${nf(1).format((mx - H0) * 9.81 / 100)} bar)${v.tc <= tr ? ', the full Joukowsky value: the valve shut before the relief wave came back.' : `, below Joukowsky's ${nf(1).format(dJ)} m because reflected waves arrive while the valve is still closing.`} ${mn < -10 ? `The head falls to ${nf(0).format(mn)} m, below vapour pressure (red band): in reality the column would separate and cavitate.` : ''}`);
  },
});

// Phase 12 helpers
function erfc12(x) { const t = 1 / (1 + 0.3275911 * Math.abs(x)), y = ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x); return x >= 0 ? y : 2 - y; }
const BLASIUS12 = (() => {
  const h = 0.005, n = 2000, eta = [0], fp = [0]; let s = [0, 0, 0.332057];
  const r = (q) => [q[1], q[2], -0.5 * q[0] * q[2]];
  for (let i = 0; i < n; i++) {
    const k1 = r(s), k2 = r(s.map((z, j) => z + h / 2 * k1[j])), k3 = r(s.map((z, j) => z + h / 2 * k2[j])), k4 = r(s.map((z, j) => z + h * k3[j]));
    s = s.map((z, j) => z + h / 6 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])); eta.push((i + 1) * h); fp.push(s[1]);
  }
  return { eta, fp };
})();

// 12.01 Stokes' first problem: the growing diffusion layer
def('stokeslayer', {
  controls: [{ type: 'select', k: 'k', label: 'Fluid', options: ['Water (ν = 1.0 mm²/s)', 'Olive oil (ν = 92 mm²/s)', 'Honey (ν = 7000 mm²/s)'], v: 'Water (ν = 1.0 mm²/s)' }, { k: 't', label: 'Time since the plate started (s)', min: 0.5, max: 60, step: 0.5, v: 10, f: 1 }],
  draw(p, v, out) {
    const sel = ['Water (ν = 1.0 mm²/s)', 'Olive oil (ν = 92 mm²/s)', 'Honey (ν = 7000 mm²/s)'].indexOf(v.k), nu = [1e-6, 9.2e-5, 7e-3][sel];
    const ymax = 3.643 * Math.sqrt(nu * 60) * 1.15 * 1000, ys = linspace(0, ymax, 160);
    p.frame({ x: [0, 1.05], y: [0, ymax], xlabel: 'u / U', ylabel: 'height above the plate, mm' });
    [v.t / 4, v.t / 16].forEach((tt) => p.line(ys.map((y) => erfc12(y / 1000 / (2 * Math.sqrt(nu * tt)))), ys, C.grey, 1.2, [4, 3]));
    p.line(ys.map((y) => erfc12(y / 1000 / (2 * Math.sqrt(nu * v.t)))), ys, C.lime, 2.5);
    const d = 3.643 * Math.sqrt(nu * v.t) * 1000;
    p.line([0, 1.05], [d, d], C.amber, 1.5, [5, 4]).text(`δ₉₉ = ${d < 10 ? nf(2).format(d) : d < 100 ? nf(1).format(d) : nf(0).format(d)} mm`, 0.55, d + ymax * 0.03, C.amber);
    out(`After ${nf(1).format(v.t)} s the moving fluid reaches ${d < 10 ? nf(2).format(d) : d < 100 ? nf(1).format(d) : nf(0).format(d)} mm. The dashed grey profiles are at t/4 and t/16: each quartering of the time halves the layer, because δ = 3.64 √(νt).`);
  },
});

// 12.02 settling velocity of a grain
def('settlegrain', {
  controls: [{ k: 'ld', label: 'Grain diameter, log₁₀ of µm', min: 0, max: 3.3, step: 0.05, v: 1.3, f: 2 }, { type: 'select', k: 'k', label: 'Grain', options: ['Quartz (2650 kg/m³)', 'Microplastic (1050 kg/m³)'], v: 'Quartz (2650 kg/m³)' }],
  draw(p, v, out) {
    const rp = [2650, 1050][['Quartz (2650 kg/m³)', 'Microplastic (1050 kg/m³)'].indexOf(v.k)], rho = 1000, mu = 1e-3, g = 9.81;
    const st = (d) => (rp - rho) * g * d * d / (18 * mu);
    const term = (d) => { let U = st(d); for (let i = 0; i < 200; i++) { const Re = rho * U * d / mu, cd = 24 / Re * (1 + 0.15 * Re ** 0.687); U = 0.5 * (U + Math.sqrt(4 * (rp - rho) * g * d / (3 * rho * cd))); } return U; };
    const ds = logspace(0, 3.3, 120).map((x) => x * 1e-6);
    p.frame({ x: [1, 2000], y: [1e-7, 10], xlog: true, ylog: true, xlabel: 'grain diameter, µm', ylabel: 'settling speed, m/s' });
    p.line(ds.map((d) => d * 1e6), ds.map(st), C.grey, 1.5, [5, 4]).line(ds.map((d) => d * 1e6), ds.map(term), C.lime, 2.5);
    const d = 10 ** v.ld * 1e-6, U = term(d), Re = rho * U * d / mu;
    p.dots([d * 1e6], [U], C.cyan, 7).text('Stokes law', 2, 3e-1, C.grey).text('with drag correlation', 2, 1.0, C.lime);
    const tset = 3 / U, ts = tset < 120 ? `${nf(0).format(tset)} s` : tset < 7200 ? `${nf(1).format(tset / 60)} min` : tset < 172800 ? `${nf(1).format(tset / 3600)} h` : `${nf(1).format(tset / 86400)} days`;
    out(`d = ${nf(d * 1e6 < 10 ? 1 : 0).format(d * 1e6)} µm: settles at ${U < 1e-3 ? U.toExponential(2) : nf(4).format(U)} m/s, Re = ${Re < 0.01 ? Re.toExponential(1) : nf(2).format(Re)}. ${Re < 0.5 ? 'Stokes law is accurate here.' : 'Stokes overestimates: inertia adds drag.'} To sink through 3 m of still river: ${ts}.`);
  },
});

// 12.03 Blasius layer along a plate
def('blasiusplate', {
  controls: [{ k: 'U', label: 'Air speed U (m/s)', min: 1, max: 20, step: 0.5, v: 5, f: 1 }, { k: 'x', label: 'Position along the plate x (m)', min: 0.05, max: 1.9, step: 0.05, v: 1, f: 2 }],
  draw(p, v, out) {
    const nu = 1.5e-5, del = (x) => 4.91 * Math.sqrt(nu * x / v.U) * 1000, top = del(2) * 1.6, xs = linspace(0.001, 2, 150);
    p.frame({ x: [0, 2.4], y: [0, top], xlabel: 'distance along the plate, m', ylabel: 'height, mm' });
    p.line([0, 2], [0, 0], C.paper, 4).line(xs, xs.map(del), C.amber, 1.8, [5, 4]).text('δ₉₉', 1.6, del(1.6) + top * 0.04, C.amber);
    const sc = Math.sqrt(nu * v.x / v.U) * 1000, E = BLASIUS12.eta.filter((e) => e <= top / sc), w = 0.4;
    p.line(E.map((e, i) => v.x + w * BLASIUS12.fp[i]), E.map((e) => e * sc), C.lime, 2.5).line([v.x, v.x], [0, top], C.grey, 1);
    for (let k = 1; k <= 6; k++) { const yy = top * k / 7, e = yy / sc, i = Math.min(BLASIUS12.eta.length - 1, Math.round(e / 0.005)); arrow(p, v.x, yy, v.x + w * BLASIUS12.fp[i], yy, C.cyan, 1.3); }
    const Re = v.U * v.x / nu, cf = 0.664 / Math.sqrt(Re);
    out(`At x = ${nf(2).format(v.x)} m: Re_x = ${Re.toExponential(2)}, δ₉₉ = ${nf(2).format(del(v.x))} mm, C_f = ${nf(5).format(cf)}, wall shear ${nf(4).format(cf * 0.6 * v.U * v.U)} Pa. ${Re > 5e5 ? 'Beyond Re_x ≈ 5 × 10⁵ the real layer would usually turn turbulent; Blasius no longer applies.' : 'Laminar: the profile has the same shape everywhere, only stretched by √(νx/U).'}`);
  },
});

// 12.04 Thwaites separation on a cylinder
def('cylsep', {
  controls: [{ type: 'select', k: 'k', label: 'Outer velocity', options: ['Ideal flow, 2U sin θ', 'Measured pressures (Hiemenz fit)'], v: 'Ideal flow, 2U sin θ' }, { k: 'a', label: 'Probe angle from the front (°)', min: 5, max: 150, step: 1, v: 60, f: 0 }],
  draw(p, v, out) {
    const sel = ['Ideal flow, 2U sin θ', 'Measured pressures (Hiemenz fit)'].indexOf(v.k);
    const ue = (a) => (sel === 0 ? 2 * Math.sin(a) : 1.814 * a - 0.271 * a ** 3 - 0.0471 * a ** 5);
    const n = 3000, A = linspace(1e-4, 2.9, n), U = A.map(ue), lam = new Array(n); let I = 0;
    for (let i = 0; i < n; i++) { if (i > 0) I += 0.5 * (U[i] ** 5 + U[i - 1] ** 5) * (A[i] - A[i - 1]); const d = i === 0 ? (U[1] - U[0]) / (A[1] - A[0]) : (U[Math.min(i + 1, n - 1)] - U[i - 1]) / (A[Math.min(i + 1, n - 1)] - A[i - 1]); lam[i] = i === 0 ? 0.075 : 0.45 * I / U[i] ** 6 * d; }
    let is = lam.findIndex((l) => l < -0.09); const sep = A[is - 1] + (-0.09 - lam[is - 1]) * (A[is] - A[is - 1]) / (lam[is] - lam[is - 1]);
    sqframe(p, 2.2, 'x / R', 'y / R');
    for (const y0 of [-1.6, -1.2, 0.0, 1.2, 1.6]) p.line([-4, -1.3], [y0, y0], C.grey, 1);
    arrow(p, -3, 0, -1.6, 0, C.cyan, 2);
    // the front stagnation point is at angle pi in plot coordinates
    const P = (a, r = 1) => [-r * Math.cos(a), r * Math.sin(a)];
    const th = linspace(0, 2 * Math.PI, 90);
    poly(p, th.map((t) => [Math.cos(t), Math.sin(t)]), C.paper, 'rgba(200,200,200,0.25)', 2);
    const att = linspace(0, sep, 40);
    [1, -1].forEach((sg) => { p.line(att.map((a) => P(a, 1.08)[0]), att.map((a) => sg * P(a, 1.08)[1]), C.lime, 3); const [sx, sy] = P(sep); p.line([sx, sx + 2.2], [sg * sy, sg * (Math.abs(sy) + 0.35)], C.red, 1.5, [5, 4]); p.dots([sx], [sg * sy], C.red, 6); });
    const ap = v.a * Math.PI / 180, [px, py] = P(ap), li = Math.min(n - 1, Math.round((ap - 1e-4) / (2.9 - 1e-4) * (n - 1)));
    p.dots([px], [py], C.amber, 6);
    out(`Laminar separation (red) at ${nf(1).format(sep * 180 / Math.PI)}° from the front stagnation point; the boundary layer stays attached along the lime arc. At the probe (${v.a}°): Uₑ/U = ${nf(3).format(ue(ap))}, λ = ${nf(3).format(lam[li])}, ${ap < sep ? (lam[li] > 0 ? 'favourable pressure gradient, the flow accelerates.' : 'adverse pressure gradient, the layer is slowing down.') : 'past separation: the wake.'}`);
  },
});

// 12.05 cyclist power
def('cyclistpower', {
  controls: [{ type: 'select', k: 'k', label: 'Riding position', options: ['Upright (C_D A 0.50)', 'Hoods (0.32)', 'Drops (0.28)', 'Time trial (0.22)'], v: 'Hoods (0.32)' }, { k: 'P', label: 'Rider power (W)', min: 50, max: 500, step: 5, v: 200, f: 0 }, { k: 'w', label: 'Headwind (m/s, negative = tailwind)', min: -5, max: 10, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const CdA = [0.5, 0.32, 0.28, 0.22][['Upright (C_D A 0.50)', 'Hoods (0.32)', 'Drops (0.28)', 'Time trial (0.22)'].indexOf(v.k)], rho = 96600 / (287.05 * 288.15);
    const pw = (s) => { const va = s + v.w, a = 0.5 * rho * CdA * va * Math.abs(va) * s, r = 0.004 * 80 * 9.81 * s; return [(a + r) / 0.97, a / 0.97, r / 0.97]; };
    const vs = linspace(0, 60 / 3.6, 120);
    p.frame({ x: [0, 60], y: [0, 600], xlabel: 'speed, km/h', ylabel: 'power, W' });
    p.line(vs.map((s) => s * 3.6), vs.map((s) => pw(s)[2]), C.grey, 1.5, [4, 3]).line(vs.map((s) => s * 3.6), vs.map((s) => Math.max(0, pw(s)[1])), C.cyan, 1.5).line(vs.map((s) => s * 3.6), vs.map((s) => pw(s)[0]), C.lime, 2.5);
    let lo = 0, hi = 30; for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; pw(m)[0] < v.P ? (lo = m) : (hi = m); } const s = lo;
    p.line([0, 60], [v.P, v.P], C.amber, 1, [5, 4]).dots([s * 3.6], [v.P], C.amber, 7).text('total', 52, Math.min(580, pw(52 / 3.6)[0]) - 40, C.lime).text('aero', 50, Math.min(560, pw(50 / 3.6)[1]) - 70, C.cyan).text('rolling', 46, pw(46 / 3.6)[2] + 15, C.grey);
    const [Pt, Pa] = pw(s);
    out(`${v.P} W gives ${nf(1).format(s * 3.6)} km/h${v.w ? ` with a ${Math.abs(v.w)} m/s ${v.w > 0 ? 'headwind' : 'tailwind'}` : ''}. Aerodynamic drag takes ${nf(0).format(100 * Math.max(0, Pa) / Pt)}% of the effort. In still air the aero part grows as v³, so 10% more speed costs about 33% more aero power.`);
  },
});

// 12.06 thin airfoil at angle of attack
def('airfoilaoa', {
  controls: [{ k: 'a', label: 'Angle of attack α (°)', min: -4, max: 18, step: 0.5, v: 4, f: 1 }, { k: 'm', label: 'Maximum camber (% chord)', min: 0, max: 6, step: 0.5, v: 2, f: 1 }],
  draw(p, v, out) {
    const m = v.m / 100, pp = 0.4, t = 0.12, n = 400;
    const zc = (x) => (m === 0 ? 0 : x < pp ? m / pp ** 2 * (2 * pp * x - x * x) : m / (1 - pp) ** 2 * (1 - 2 * pp + 2 * pp * x - x * x));
    const dz = (x) => (m === 0 ? 0 : x < pp ? 2 * m / pp ** 2 * (pp - x) : 2 * m / (1 - pp) ** 2 * (pp - x));
    let s0 = 0; for (let i = 0; i < n; i++) { const th = (i + 0.5) * Math.PI / n; s0 += dz((1 - Math.cos(th)) / 2) * (Math.cos(th) - 1) * Math.PI / n; }
    const aL0 = -s0 / Math.PI, a = v.a * Math.PI / 180, CL = 2 * Math.PI * (a - aL0);
    const yt = (x) => 5 * t * (0.2969 * Math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4);
    const xs = linspace(0, 1, 80), up = xs.map((x) => [x, zc(x) + yt(x)]), lo = xs.slice().reverse().map((x) => [x, zc(x) - yt(x)]);
    const rot = ([x, y]) => [(x - 0.25) * Math.cos(a) + y * Math.sin(a), -(x - 0.25) * Math.sin(a) + y * Math.cos(a)];
    sqframe(p, 0.7, 'x / c', 'y / c');
    for (const y0 of [-0.45, -0.25, 0.25, 0.45]) arrow(p, -1.1, y0, -0.75, y0, C.grey, 1.2);
    poly(p, up.concat(lo).map(rot), C.paper, 'rgba(200,200,200,0.3)', 2);
    const stall = v.a > 13;
    arrow(p, 0, 0, 0, Math.max(-0.6, Math.min(0.62, CL * 0.38)), stall ? C.red : C.lime, 3);
    out(`Thin airfoil theory: C_L = 2π(α − α_L0) = ${nf(3).format(CL)}, with zero-lift angle α_L0 = ${nf(2).format(aL0 * 180 / Math.PI)}° from the camber. ${stall ? 'Above about 13° a real airfoil stalls: the flow separates from the upper surface and lift drops. Thin theory no longer applies (red).' : 'Camber shifts the lift line; the slope stays 2π per radian (0.110 per degree).'}`);
  },
});

// 12.07 Hess-Smith panel method: pressure distribution
function hessSmith12(m, t, alpha, nh) {
  const pp = 0.4, X = [], Y = [], xs = [], yu = [], yl = [];
  for (let i = 0; i <= nh; i++) {
    const x = (1 - Math.cos(Math.PI * i / nh)) / 2, yt = 5 * t * (0.2969 * Math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4);
    const yc = m === 0 ? 0 : x < pp ? m / pp ** 2 * (2 * pp * x - x * x) : m / (1 - pp) ** 2 * (1 - 2 * pp + 2 * pp * x - x * x);
    xs.push(x); yu.push(yc + yt); yl.push(yc - yt);
  }
  for (let i = nh; i >= 0; i--) { X.push(xs[i]); Y.push(yl[i]); }
  for (let i = 1; i <= nh; i++) { X.push(xs[i]); Y.push(yu[i]); }
  Y[0] = Y[Y.length - 1] = (Y[0] + Y[Y.length - 1]) / 2;
  const N = X.length - 1, xc = [], yc = [], L = [], th = [];
  for (let j = 0; j < N; j++) { xc.push((X[j] + X[j + 1]) / 2); yc.push((Y[j] + Y[j + 1]) / 2); L.push(Math.hypot(X[j + 1] - X[j], Y[j + 1] - Y[j])); th.push(Math.atan2(Y[j + 1] - Y[j], X[j + 1] - X[j])); }
  const An = [], At = [], Bn = new Array(N).fill(0), Bt = new Array(N).fill(0);
  for (let i = 0; i < N; i++) {
    An.push(new Array(N)); At.push(new Array(N));
    const nx = -Math.sin(th[i]), ny = Math.cos(th[i]), tx = Math.cos(th[i]), ty = Math.sin(th[i]);
    for (let j = 0; j < N; j++) {
      let us, vs;
      if (i === j) { us = 0; vs = 0.5; } else {
        const dx = xc[i] - X[j], dy = yc[i] - Y[j], c = Math.cos(th[j]), s = Math.sin(th[j]), xp = dx * c + dy * s, yp = -dx * s + dy * c;
        us = Math.log(Math.hypot(xp, yp) / Math.hypot(xp - L[j], yp)) / (2 * Math.PI); vs = (Math.atan2(yp, xp - L[j]) - Math.atan2(yp, xp)) / (2 * Math.PI);
      }
      const c = Math.cos(th[j]), s = Math.sin(th[j]), ug = us * c - vs * s, vg = us * s + vs * c, ugv = vs * c + us * s, vgv = vs * s - us * c;
      An[i][j] = ug * nx + vg * ny; At[i][j] = ug * tx + vg * ty; Bn[i] += ugv * nx + vgv * ny; Bt[i] += ugv * tx + vgv * ty;
    }
  }
  const U = Math.cos(alpha), V = Math.sin(alpha), M = [];
  for (let i = 0; i < N; i++) M.push(An[i].concat([Bn[i], -(U * -Math.sin(th[i]) + V * Math.cos(th[i]))]));
  M.push(At[0].map((a, j) => a + At[N - 1][j]).concat([Bt[0] + Bt[N - 1], -(U * (Math.cos(th[0]) + Math.cos(th[N - 1])) + V * (Math.sin(th[0]) + Math.sin(th[N - 1])))]));
  const n = N + 1;
  for (let k = 0; k < n; k++) { let piv = k; for (let r = k + 1; r < n; r++) if (Math.abs(M[r][k]) > Math.abs(M[piv][k])) piv = r; [M[k], M[piv]] = [M[piv], M[k]]; for (let r = k + 1; r < n; r++) { const f = M[r][k] / M[k][k]; for (let c2 = k; c2 <= n; c2++) M[r][c2] -= f * M[k][c2]; } }
  const sol = new Array(n); for (let k = n - 1; k >= 0; k--) { let s = M[k][n]; for (let c2 = k + 1; c2 < n; c2++) s -= M[k][c2] * sol[c2]; sol[k] = s / M[k][k]; }
  const gam = sol[N], Cp = [];
  for (let i = 0; i < N; i++) { let vt = gam * Bt[i] + U * Math.cos(th[i]) + V * Math.sin(th[i]); for (let j = 0; j < N; j++) vt += At[i][j] * sol[j]; Cp.push(1 - vt * vt); }
  return { xc, Cp, N, CL: 2 * gam * L.reduce((a, b) => a + b, 0) };
}
def('panelcp', {
  controls: [{ k: 'a', label: 'Angle of attack α (°)', min: -4, max: 12, step: 0.5, v: 4, f: 1 }, { k: 't', label: 'Thickness (% chord)', min: 2, max: 20, step: 1, v: 12, f: 0 }, { k: 'm', label: 'Maximum camber (% chord)', min: 0, max: 6, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const r = hessSmith12(v.m / 100, v.t / 100, v.a * Math.PI / 180, 40), h = r.N / 2;
    const lower = r.Cp.slice(0, h), upper = r.Cp.slice(h), xl = r.xc.slice(0, h), xu = r.xc.slice(h);
    const top = Math.max(1.2, ...r.Cp.map((c) => -c)) * 1.1;
    p.frame({ x: [0, 1], y: [-1.1, top], xlabel: 'x / c', ylabel: '−C_p (suction up)' });
    p.line([0, 1], [0, 0], C.grey, 1).line(xu, upper.map((c) => -c), C.lime, 2.5).line(xl, lower.map((c) => -c), C.cyan, 2.5);
    p.text('upper surface', 0.55, top * 0.85, C.lime).text('lower surface', 0.55, -0.85, C.cyan);
    const thin = 2 * Math.PI * v.a * Math.PI / 180;
    out(`Hess-Smith with ${r.N} panels: C_L = ${nf(3).format(r.CL)}. ${v.m === 0 ? `Thin airfoil theory gives 2πα = ${nf(3).format(thin)}; thickness adds about ${nf(0).format(77 * v.t / 100)}% (1 + 0.77 t/c).` : 'Camber adds lift at every angle, spread along the chord.'} The area between the two curves is the lift; the suction peak near the leading edge does most of the work.`);
  },
});

// 12.08 model turbulence energy spectrum
def('kspectrum', {
  controls: [{ k: 'le', label: 'Dissipation rate, log₁₀ ε (W/kg)', min: -6, max: 0, step: 0.1, v: -2.9, f: 1 }, { k: 'L', label: 'Large-eddy size L (m)', min: 0.1, max: 10, step: 0.1, v: 6, f: 1 }],
  draw(p, v, out) {
    const nu = 1e-6, eps = 10 ** v.le, L = v.L, eta = (nu ** 3 / eps) ** 0.25;
    const E = (k) => { const kL = k * L, ke = k * eta; return 1.5 * eps ** (2 / 3) * k ** (-5 / 3) * (kL / Math.sqrt(kL * kL + 6.78)) ** (11 / 3) * Math.exp(-5.2 * ((ke ** 4 + 0.4 ** 4) ** 0.25 - 0.4)); };
    const ks = logspace(-2, 5, 300), Es = ks.map(E), ymax = Math.max(...Es) * 30;
    p.frame({ x: [1e-2, 1e5], y: [ymax * 1e-12, ymax], xlog: true, ylog: true, xlabel: 'wavenumber k, 1/m', ylabel: 'E(k), m³/s²' });
    p.line(ks, Es, C.lime, 2.5);
    const k1 = 8 / L, k2 = 0.1 / eta; if (k2 > k1) p.line([k1, k2], [E(k1) * 4, E(k1) * 4 * (k2 / k1) ** (-5 / 3)], C.amber, 1.5, [5, 4]);
    p.line([1 / L, 1 / L], [ymax * 1e-12, ymax], C.grey, 1, [3, 3]).line([1 / eta, 1 / eta], [ymax * 1e-12, ymax], C.red, 1, [3, 3]).text('1/L', 1.15 / L, ymax * 0.05, C.grey).text('1/η', 1.15 / eta, ymax * 0.05, C.red).text('−5/3', Math.sqrt(k1 * k2), E(Math.sqrt(k1 * k2)) * 12, C.amber);
    const u = (eps * L) ** (1 / 3);
    out(`Kolmogorov length η = (ν³/ε)¹ᐟ⁴ = ${nf(3).format(eta * 1000)} mm, time ${nf(1).format(Math.sqrt(nu / eps) * 1000)} ms. Large eddies of ${nf(1).format(L)} m carry u' ≈ (εL)¹ᐟ³ = ${nf(3).format(u)} m/s, so L/η = ${nf(0).format(L / eta)}. Energy enters at the left, cascades along the −5/3 line, and is dissipated near 1/η.`);
  },
});

// 12.09 Reynolds decomposition of a velocity record
def('reynoldsdecomp', {
  controls: [{ k: 'I', label: 'Turbulence intensity (%)', min: 0, max: 30, step: 1, v: 10, f: 0 }, { k: 'r', label: "Correlation of u' and v'", min: -0.8, max: 0.8, step: 0.05, v: -0.4, f: 2 }, { k: 'T', label: 'Averaging window (s)', min: 0.2, max: 20, step: 0.2, v: 20, f: 1 }],
  draw(p, v, out) {
    let seed = 12345; const rnd = () => { seed = (seed + 0x6d2b79f5) | 0; let z = Math.imul(seed ^ (seed >>> 15), 1 | seed); z = (z + Math.imul(z ^ (z >>> 7), 61 | z)) ^ z; return ((z ^ (z >>> 14)) >>> 0) / 4294967296; };
    const gauss = () => Math.sqrt(-2 * Math.log(rnd() + 1e-12)) * Math.cos(2 * Math.PI * rnd());
    const n = 2000, dt = 0.01, U0 = 1.5, su = v.I / 100 * U0, sv = 0.55 * su, a = [], b = [];
    let fa = 0, fb = 0; const ph = 0.9;                              // a little memory, so the trace looks like turbulence
    for (let i = 0; i < n; i++) { fa = ph * fa + Math.sqrt(1 - ph * ph) * gauss(); fb = ph * fb + Math.sqrt(1 - ph * ph) * gauss(); a.push(fa); b.push(fb); }
    const ts = a.map((_, i) => i * dt), u = a.map((x) => U0 + su * x), w = a.map((x, i) => sv * (v.r * x + Math.sqrt(1 - v.r * v.r) * b[i]));
    const m = Math.min(n, Math.max(2, Math.round(v.T / dt))), Um = u.slice(0, m).reduce((s, x) => s + x, 0) / m;
    const up = u.slice(0, m).map((x) => x - Um), wm = w.slice(0, m).reduce((s, x) => s + x, 0) / m, vp = w.slice(0, m).map((x) => x - wm);
    const mean = (q) => q.reduce((s, x) => s + x, 0) / q.length, uu = mean(up.map((x) => x * x)), uv = mean(up.map((x, i) => x * vp[i]));
    p.frame({ x: [0, 20], y: [U0 * 0.4, U0 * 1.6], xlabel: 'time, s', ylabel: 'streamwise velocity u, m/s' });
    p.rect(0, m * dt, U0 * 0.4, U0 * 1.6, 'rgba(238,255,65,0.06)');
    p.line(ts, u, C.cyan, 1).line([0, m * dt], [Um, Um], C.lime, 2.5).text(`U = ${nf(3).format(Um)} m/s`, 0.3, U0 * 1.5, C.lime);
    out(`Over the ${nf(1).format(m * dt)} s window: mean U = ${nf(4).format(Um)} m/s, mean of u' = ${Math.abs(mean(up)) < 1e-12 ? '0' : mean(up).toExponential(1)} (always zero by construction), ⟨u'u'⟩ = ${nf(5).format(uu)} m²/s², Reynolds shear stress −ρ⟨u'v'⟩ = ${nf(2).format(-1000 * uv)} Pa. ${v.T < 3 ? 'A short window gives a noisy mean: averages need many eddy lifetimes.' : ''}`);
  },
});

// 12.10 Moody chart
function colebrook12(Re, e) { if (Re < 2300) return 64 / Re; let x = 1 / Math.sqrt((-1.8 * Math.log10((e / 3.7) ** 1.11 + 6.9 / Re)) ** -2); for (let i = 0; i < 60; i++) x = -2 * Math.log10(e / 3.7 + 2.51 * x / Re); return 1 / (x * x); }
def('moodychart', {
  controls: [{ k: 'lr', label: 'Reynolds number, log₁₀ Re', min: 2.7, max: 8, step: 0.05, v: 5.5, f: 2 }, { k: 'le', label: 'Relative roughness, log₁₀ ε/D (−6 = smooth)', min: -6, max: -1.3, step: 0.1, v: -2.9, f: 1 }],
  draw(p, v, out) {
    const Res = logspace(3.61, 8, 120), e = v.le <= -5.95 ? 0 : 10 ** v.le, Re = 10 ** v.lr;
    p.frame({ x: [500, 1e8], y: [0.006, 0.12], xlog: true, ylog: true, xlabel: 'Reynolds number', ylabel: 'friction factor f' });
    const lam = logspace(2.7, 3.36, 20); p.line(lam, lam.map((r) => 64 / r), C.amber, 2).text('64/Re', 700, 0.1, C.amber);
    p.rect(2300, 4000, 0.006, 0.12, 'rgba(154,157,147,0.12)');
    [0, 1e-5, 1e-4, 1e-3, 5e-3, 0.02, 0.05].forEach((ee) => p.line(Res, Res.map((r) => colebrook12(r, ee)), C.grey, 1));
    if (Re >= 2300) p.line(Res, Res.map((r) => colebrook12(r, e)), C.lime, 2.5);
    const f = colebrook12(Re, e); p.dots([Re], [f], C.cyan, 7);
    out(`Re = ${Re.toExponential(2)}, ε/D = ${e === 0 ? '0 (smooth)' : e.toExponential(1)}: f = ${nf(5).format(f)}. ${Re < 2300 ? 'Laminar: f = 64/Re, roughness is irrelevant.' : Re < 4000 ? 'Transitional (grey band): the real friction factor jumps unpredictably.' : (e > 0 && Re * e > 200 ? 'Fully rough: f hardly depends on Re any more.' : 'Turbulent: Colebrook, solved by iteration.')}`);
  },
});

// 12.11 Hardy Cross network
def('hardycrossnet', {
  controls: [{ k: 'it', label: 'Hardy Cross sweeps', min: 0, max: 8, step: 1, v: 0, f: 0 }, { k: 'd5', label: 'Demand at the far corner (L/s)', min: 5, max: 40, step: 1, v: 15, f: 0 }],
  draw(p, v, out) {
    const P = [[0, 1, 400, 0.2], [1, 2, 400, 0.15], [0, 3, 300, 0.2], [1, 4, 300, 0.15], [2, 5, 300, 0.1], [3, 4, 400, 0.15], [4, 5, 400, 0.1]];
    const K = P.map(([, , L, D]) => 8 * 0.02 * L / (9.81 * Math.PI ** 2 * D ** 5)), extra = (v.d5 - 15) / 1000;
    const Q = [0.03, 0.012, 0.03 + extra, 0.008, 0.002, 0.02 + extra, 0.013 + extra];
    const loops = [[[0, 1], [3, 1], [5, -1], [2, -1]], [[1, 1], [4, 1], [6, -1], [3, -1]]];
    const imb = () => loops.map((lp) => lp.reduce((s, [k, sg]) => s + sg * K[k] * Q[k] * Math.abs(Q[k]), 0));
    for (let it = 0; it < v.it; it++) loops.forEach((lp) => { const num = lp.reduce((s, [k, sg]) => s + sg * K[k] * Q[k] * Math.abs(Q[k]), 0), den = lp.reduce((s, [k]) => s + 2 * K[k] * Math.abs(Q[k]), 0), dQ = -num / den; lp.forEach(([k, sg]) => { Q[k] += sg * dQ; }); });
    const N = [[-1, 0.6], [0, 0.6], [1, 0.6], [-1, -0.6], [0, -0.6], [1, -0.6]], dem = [0, 10, 10, 10, 15, v.d5];
    sqframe(p, 1.2, '', '');
    P.forEach(([a, b], k) => { const q = Q[k], [x1, y1] = N[q >= 0 ? a : b], [x2, y2] = N[q >= 0 ? b : a], w = 1 + Math.abs(q) * 1000 / 4;
      p.line([x1, x2], [y1, y2], C.grey, 1); arrow(p, x1 + (x2 - x1) * 0.2, y1 + (y2 - y1) * 0.2, x1 + (x2 - x1) * 0.75, y1 + (y2 - y1) * 0.75, C.cyan, w);
      const mx = (x1 + x2) / 2, my = (y1 + y2) / 2; p.text(`${nf(1).format(Math.abs(q) * 1000)}`, mx + (y1 === y2 ? -0.12 : 0.06), my + (y1 === y2 ? 0.1 : 0), C.paper); });
    N.forEach(([x, y], i) => { p.dots([x], [y], i === 0 ? C.lime : C.amber, 7); p.text(i === 0 ? `in ${nf(0).format(45 + v.d5)}` : `−${dem[i]}`, x - 0.12, y + (y > 0 ? 0.17 : -0.24), i === 0 ? C.lime : C.amber); });
    const [e1, e2] = imb();
    out(`After ${v.it} sweep${v.it === 1 ? '' : 's'}: head imbalance around the left loop ${nf(4).format(e1)} m, right loop ${nf(4).format(e2)} m (flows in L/s). Every correction adds the same ΔQ all round a loop, so continuity at every node holds from the first guess onwards. ${Math.abs(e1) + Math.abs(e2) < 1e-4 ? 'Converged.' : ''}`);
  },
});

// 12.12 pump and system curves
def('pumpsystem', {
  controls: [{ k: 'N', label: 'Pump speed (rpm)', min: 700, max: 1800, step: 10, v: 1450, f: 0 }, { k: 'Hs', label: 'Static lift (m)', min: 0, max: 35, step: 0.5, v: 15, f: 1 }],
  draw(p, v, out) {
    const ph = (Q, N) => 40 * (N / 1450) ** 2 - 4000 * Q * Q, sh = (Q) => v.Hs + 3000 * Q * Q;
    const eff = (Q, N) => { const q = Q / (0.06 * N / 1450); return Math.max(0, 0.78 * (2 * q - q * q)); };
    const Qs = linspace(0, 0.14, 120);
    p.frame({ x: [0, 140], y: [0, 70], xlabel: 'flow Q, L/s', ylabel: 'head H, m' });
    p.line(Qs.map((q) => q * 1000), Qs.map((q) => ph(q, 1450)), C.grey, 1.2, [5, 4]).line(Qs.map((q) => q * 1000), Qs.map((q) => ph(q, v.N)), C.lime, 2.5).line(Qs.map((q) => q * 1000), Qs.map(sh), C.cyan, 2);
    p.text('pump', 4, ph(0, v.N) + 2, C.lime).text('system', 100, Math.min(66, sh(0.1)) - 4, C.cyan);
    if (ph(0, v.N) <= v.Hs) { out(`At ${v.N} rpm the pump's shut-off head ${nf(1).format(ph(0, v.N))} m is below the static lift: no flow at all.`); return; }
    let lo = 0, hi = 0.2; for (let i = 0; i < 80; i++) { const m = (lo + hi) / 2; ph(m, v.N) > sh(m) ? (lo = m) : (hi = m); }
    const Q = lo, H = sh(Q), e = eff(Q, v.N), P = 1000 * 9.81 * Q * H / Math.max(e, 0.05);
    p.dots([Q * 1000], [H], C.amber, 7);
    out(`Operating point: Q = ${nf(1).format(Q * 1000)} L/s at H = ${nf(1).format(H)} m, efficiency ${nf(0).format(e * 100)}%, shaft power ${nf(2).format(P / 1000)} kW. Affinity: the pump curve scales by (N/1450)² in head and N/1450 in flow; ${v.Hs > 0 ? 'with static lift the operating flow falls faster than the speed.' : 'with no static lift the operating flow scales exactly with speed.'}`);
  },
});

// 12.13 isentropic ratios against Mach number
def('machslider', {
  controls: [{ k: 'M', label: 'Mach number', min: 0, max: 3, step: 0.01, v: 0.82, f: 2 }, { type: 'select', k: 'k', label: 'Where', options: ['Cruise at 11 km (−56.5 °C)', 'Sea level (15 °C)', 'Hot day in Bali (32 °C)'], v: 'Cruise at 11 km (−56.5 °C)' }],
  draw(p, v, out) {
    const sel = ['Cruise at 11 km (−56.5 °C)', 'Sea level (15 °C)', 'Hot day in Bali (32 °C)'].indexOf(v.k), T = [216.65, 288.15, 305.15][sel], P = [22.632, 101.325, 100.9][sel], k = 1.4;
    const tr = (M) => 1 + 0.2 * M * M, Ms = linspace(0, 3, 150);
    p.frame({ x: [0, 3], y: [0, 1.05], xlabel: 'Mach number', ylabel: 'static / stagnation' });
    p.line(Ms, Ms.map((M) => 1 / tr(M)), C.amber, 2).line(Ms, Ms.map((M) => tr(M) ** -3.5), C.lime, 2.5).line(Ms, Ms.map((M) => tr(M) ** -2.5), C.cyan, 2);
    p.line([v.M, v.M], [0, 1.05], C.grey, 1, [4, 3]).line([1, 1], [0, 1.05], C.red, 1, [2, 3]);
    p.text('T/T₀', 2.4, 1 / tr(2.4) + 0.05, C.amber).text('p/p₀', 2.4, tr(2.4) ** -3.5 - 0.06, C.lime).text('ρ/ρ₀', 1.55, tr(1.55) ** -2.5 + 0.08, C.cyan);
    const a = Math.sqrt(k * 287.05 * T), V = v.M * a, pr = tr(v.M) ** 3.5, err = v.M > 0 ? 100 * (0.7 * v.M * v.M / (pr - 1) - 1) : 0;
    out(`a = √(kRT) = ${nf(1).format(a)} m/s, so V = ${nf(0).format(V)} m/s (${nf(0).format(V * 3.6)} km/h). Stagnation temperature ${nf(1).format(T * tr(v.M))} K (${nf(1).format(T * tr(v.M) - 273.15)} °C), stagnation pressure ${nf(2).format(P * pr)} kPa. ${v.M > 0 && v.M < 1 ? `Incompressible Bernoulli would be off by ${nf(1).format(Math.abs(err))}%.` : v.M >= 1 ? 'Supersonic: Bernoulli is meaningless here and shocks can form.' : ''}`);
  },
});

// 12.14 converging-diverging nozzle with back pressure
function nozzleState12(pbr) {
  const k = 1.4, ar = (M) => (1 / M) * ((2 / (k + 1)) * (1 + 0.2 * M * M)) ** 3, pr = (M) => (1 + 0.2 * M * M) ** -3.5;
  const mfa = (A, sup) => { let lo = sup ? 1 : 1e-9, hi = sup ? 50 : 1; for (let i = 0; i < 100; i++) { const m = (lo + hi) / 2, big = ar(m) > A; if (sup) big ? (hi = m) : (lo = m); else big ? (lo = m) : (hi = m); } return (lo + hi) / 2; };
  const sh = (M1) => { const M2 = Math.sqrt((1 + 0.2 * M1 * M1) / (k * M1 * M1 - 0.2)), p21 = 1 + 2 * k / (k + 1) * (M1 * M1 - 1); return [M2, p21, p21 * pr(M1) / pr(M2)]; };
  const Ae = 2, xt = 0.4, A = (x) => (x < xt ? 1 + 2 * ((x - xt) / xt) ** 2 : 1 + (Ae - 1) * ((x - xt) / (1 - xt)) ** 2);
  const pc1 = pr(mfa(Ae, false)), Msup = mfa(Ae, true), pc2 = pr(Msup) * sh(Msup)[1], xs = linspace(0, 1, 201);
  let ps, regime, mdot, xsh = null;
  if (pbr >= 0.9999) { ps = xs.map(() => 1); regime = 'no flow'; mdot = 0; }
  else if (pbr >= pc1) { const Me = Math.sqrt(5 * (pbr ** (-1 / 3.5) - 1)), As = Ae / ar(Me); ps = xs.map((x) => pr(mfa(A(x) / As, false))); regime = 'subsonic everywhere, not choked'; mdot = As; }
  else {
    mdot = 1;
    const isen = (x) => pr(mfa(A(x), x > xt));
    if (pbr >= pc2) {
      const exitp = (as) => { const [, , p0r] = sh(mfa(as, true)), Me = mfa(Ae * p0r, false); return p0r * pr(Me); };
      let lo = 1.0000001, hi = Ae; for (let i = 0; i < 60; i++) { const m = (lo + hi) / 2; exitp(m) > pbr ? (lo = m) : (hi = m); }
      const As = (lo + hi) / 2, p0r = sh(mfa(As, true))[2]; xsh = xt + (1 - xt) * Math.sqrt((As - 1) / (Ae - 1));
      ps = xs.map((x) => (x <= xsh ? isen(x) : p0r * pr(mfa(A(x) * p0r, false)))); regime = 'choked, normal shock inside the nozzle';
    } else { ps = xs.map(isen); regime = pbr > pr(Msup) + 1e-3 ? 'choked, supersonic exit, over-expanded (oblique shocks outside)' : pbr < pr(Msup) - 1e-3 ? 'choked, supersonic exit, under-expanded (expansion fans outside)' : 'choked, design condition: exit pressure matches'; }
  }
  return { xs, ps, A, regime, mdot, xsh, pc1, pc2, pd: pr(Msup) };
}
def('cdnozzle', {
  controls: [{ k: 'pb', label: 'Back pressure p_b / p₀', min: 0, max: 1, step: 0.005, v: 0.75, f: 3 }],
  draw(p, v, out) {
    const s = nozzleState12(v.pb);
    p.frame({ x: [0, 1.1], y: [0, 1.6], xlabel: 'position along the nozzle', ylabel: 'p / p₀' });
    const sc = 0.12; p.line(s.xs, s.xs.map((x) => 1.38 + sc * Math.sqrt(s.A(x))), C.paper, 1.5).line(s.xs, s.xs.map((x) => 1.38 - sc * Math.sqrt(s.A(x))), C.paper, 1.5);
    p.line(s.xs, s.ps, C.lime, 2.5).line([1, 1.1], [v.pb, v.pb], C.amber, 2).text('p_b', 1.02, v.pb + 0.05, C.amber);
    if (s.xsh) { p.line([s.xsh, s.xsh], [0, 1.25], C.red, 2, [4, 3]); p.line([s.xsh, s.xsh], [1.38 - sc * Math.sqrt(s.A(s.xsh)), 1.38 + sc * Math.sqrt(s.A(s.xsh))], C.red, 3); }
    out(`${s.regime[0].toUpperCase() + s.regime.slice(1)}. Mass flow ${nf(4).format(s.mdot)} of the choked value. Critical back pressures for this nozzle: chokes below ${nf(4).format(s.pc1)} p₀, shock reaches the exit at ${nf(4).format(s.pc2)} p₀, design exit pressure ${nf(4).format(s.pd)} p₀. Below the first, lowering p_b doesn't change the mass flow at all.`);
  },
});

// 12.15 Sod-type shock tube, exact solution
def('shocktube', {
  controls: [{ k: 't', label: 'Time after the diaphragm bursts', min: 0, max: 0.25, step: 0.005, v: 0.2, f: 3 }, { k: 'pL', label: 'Left pressure (right = 0.1)', min: 0.2, max: 10, step: 0.1, v: 1, f: 1 }, { type: 'select', k: 'k', label: 'Show', options: ['Density', 'Pressure', 'Velocity'], v: 'Density' }],
  draw(p, v, out) {
    const k = 1.4, rL = 1, pL = v.pL, rR = 0.125, pR = 0.1, aL = Math.sqrt(k * pL / rL), aR = Math.sqrt(k * pR / rR), g = (k - 1) / (k + 1);
    const f = (pp, r, pk, a) => (pp > pk ? (pp - pk) * Math.sqrt(2 / ((k + 1) * r) / (pp + g * pk)) : 2 * a / (k - 1) * ((pp / pk) ** ((k - 1) / (2 * k)) - 1));
    let lo = 1e-8, hi = 10 * pL; for (let i = 0; i < 100; i++) { const m = (lo + hi) / 2; f(m, rL, pL, aL) + f(m, rR, pR, aR) < 0 ? (lo = m) : (hi = m); }
    const ps = (lo + hi) / 2, us = 0.5 * (f(ps, rR, pR, aR) - f(ps, rL, pL, aL)), rsL = rL * (ps / pL) ** (1 / k), asL = aL * (ps / pL) ** ((k - 1) / (2 * k));
    const r2 = rR * (ps / pR + g) / (g * ps / pR + 1), S = us * r2 / (r2 - rR);
    const sample = (x) => { if (v.t === 0) return x < 0.5 ? [rL, 0, pL] : [rR, 0, pR]; const s = (x - 0.5) / v.t;
      if (s < -aL) return [rL, 0, pL];
      if (s < us - asL) { const u = 2 / (k + 1) * (aL + s), a = 2 / (k + 1) * (aL - (k - 1) / 2 * s); return [rL * (a / aL) ** (2 / (k - 1)), u, pL * (a / aL) ** (2 * k / (k - 1))]; }
      if (s < us) return [rsL, us, ps]; if (s < S) return [r2, us, ps]; return [rR, 0, pR]; };
    const sel = ['Density', 'Pressure', 'Velocity'].indexOf(v.k), xs = linspace(0, 1, 400), ys = xs.map((x) => sample(x)[sel]);
    const top = [Math.max(rL, r2), pL, Math.max(0.5, us)][sel] * 1.15;
    p.frame({ x: [0, 1], y: [0, top], xlabel: 'position in the tube', ylabel: ['density', 'pressure', 'velocity'][sel] });
    p.line(xs, ys, C.lime, 2.5).line([0.5, 0.5], [0, top], C.grey, 1, [3, 3]);
    if (v.t > 0) { const xS = 0.5 + S * v.t, xC = 0.5 + us * v.t; p.text('shock', Math.min(0.9, xS - 0.03), top * 0.93, C.red).text('contact', Math.max(0.02, xC - 0.08), top * 0.8, C.cyan).text('expansion', Math.max(0.02, 0.5 - aL * v.t - 0.02), top * 0.93, C.amber); }
    const Ms = S / aR, ds = 717.6 * Math.log((ps / pR) / ((r2 / rR) ** k));
    out(`Shock Mach ${nf(3).format(Ms)}, pressure ratio ${nf(3).format(ps / pR)} across it, gas behind moving at ${nf(3).format(us)} (units of the initial state). Entropy rises across the shock by ${nf(1).format(ds)} J/(kg K) for air, but not across the smooth expansion or the contact surface.`);
  },
});

// 12.16 Karman vortex street behind a cable
def('karmanstreet', {
  controls: [{ k: 'U', label: 'Wind speed (m/s)', min: 1, max: 25, step: 0.5, v: 10, f: 1 }, { k: 'D', label: 'Cable diameter (mm)', min: 10, max: 80, step: 1, v: 40, f: 0 }, { k: 't', label: 'Time (ms)', min: 0, max: 100, step: 1, v: 0, f: 0 }],
  draw(p, v, out) {
    const D = v.D / 1000, f = 0.2 * v.U / D, Uc = 0.85 * v.U, lam = Uc / f, hs = 0.281 * lam;   // street spacing ratio h/l = 0.281 (von Karman)
    const R = 1;                                                   // plot in units of the cable diameter
    p.frame({ x: [-2, 30], y: [-6, 6], xlabel: 'distance downstream / D', ylabel: '' , noy: true });
    poly(p, linspace(0, 2 * Math.PI, 40).map((a) => [0.5 * Math.cos(a), 0.5 * Math.sin(a)]), C.paper, 'rgba(200,200,200,0.4)', 2);
    const shift = (Uc * v.t / 1000) / D, L = lam / D, H = hs / D;
    for (let n = -1; n < 12; n++) {
      [0, 1].forEach((side) => { const x = 1.5 + (n + side / 2) * L + (shift % L); if (x < 1 || x > 30) return; const y = side ? -H / 2 : H / 2, r = 0.45 + 0.02 * x;
        const th = linspace(0, 4 * Math.PI, 50); p.line(th.map((a) => x + r * (a / (4 * Math.PI)) * Math.cos(side ? -a : a)), th.map((a) => y + r * (a / (4 * Math.PI)) * Math.sin(side ? -a : a)), side ? C.cyan : C.amber, 1.6); });
    }
    arrow(p, -1.8, 4.8, 0.4, 4.8, C.grey, 1.5);
    out(`Strouhal 0.2: the cable sheds ${nf(1).format(f)} Hz (one vortex from each side per cycle), Re = ${nf(0).format(v.U * D / 1.5e-5)}. Vortices drift at about 0.85 U and sit ${nf(2).format(lam)} m apart, rows ${nf(2).format(hs)} m apart. ${f > 20 && f < 20000 ? 'Audible: this is the cable singing.' : 'Below the audible range, but it can still shake a structure whose natural frequency matches.'}`);
  },
});

// 12.17 wind load on a signboard
def('signwind', {
  controls: [{ k: 'V', label: 'Mean wind speed at the sign (m/s)', min: 5, max: 40, step: 0.5, v: 22, f: 1 }, { k: 'b', label: 'Sign width (m)', min: 1, max: 6, step: 0.5, v: 3, f: 1 }, { type: 'select', k: 'k', label: 'Terrain', options: ['Open coast (z₀ = 0.01 m)', 'Village (z₀ = 0.3 m)', 'Lakeside (z₀ = 0.05 m)'], v: 'Village (z₀ = 0.3 m)' }],
  draw(p, v, out) {
    const z0 = [0.01, 0.3, 0.05][['Open coast (z₀ = 0.01 m)', 'Village (z₀ = 0.3 m)', 'Lakeside (z₀ = 0.05 m)'].indexOf(v.k)], Iv = 1 / Math.log(4 / z0), A = v.b * 1.5;
    const Fz = (V) => 1.8 * (1 + 7 * Iv) * 0.6 * V * V * A, Vs = linspace(0, 40, 100), W = 139.1e-6;
    p.frame({ x: [0, 40], y: [0, Fz(40) / 1000 * 1.05], xlabel: 'mean wind speed, m/s', ylabel: 'force on the sign, kN' });
    p.line(Vs, Vs.map((V) => Fz(V) / 1000), C.lime, 2.5);
    const Vy = Math.sqrt(355e6 * W / 4 / (1.8 * (1 + 7 * Iv) * 0.6 * A));
    if (Vy < 40) p.line([Vy, Vy], [0, Fz(40) / 1000], C.red, 1.5, [5, 4]).text('post yields', Vy + 0.5, Fz(40) / 1000 * 0.9, C.red);
    const F = Fz(v.V); p.dots([v.V], [F / 1000], C.amber, 7);
    out(`Peak pressure ${nf(0).format((1 + 7 * Iv) * 0.6 * v.V * v.V)} Pa (gust factor 1 + 7I = ${nf(2).format(1 + 7 * Iv)}, a labelled simplification). Force ${nf(2).format(F / 1000)} kN on ${nf(1).format(A)} m², base moment ${nf(1).format(F * 4 / 1000)} kN m, stress ${nf(0).format(F * 4 / W / 1e6)} MPa in a 168.3 × 7.1 mm post. Double the wind and the load is four times bigger.`);
  },
});

// 12.18 dye release in the Limmat
def('dyerelease', {
  controls: [{ k: 't', label: 'Time since release (min)', min: 2, max: 180, step: 1, v: 30, f: 0 }, { k: 'D', label: 'Longitudinal dispersion D (m²/s)', min: 10, max: 300, step: 5, v: 88, f: 0 }, { k: 'U', label: 'Mean velocity U (m/s)', min: 0.3, max: 2, step: 0.05, v: 1, f: 2 }],
  draw(p, v, out) {
    const A = 100, M = 10, t = v.t * 60, xs = linspace(0, 15000, 400);
    const c = (x, tt) => M / (A * Math.sqrt(4 * Math.PI * v.D * tt)) * Math.exp(-((x - v.U * tt) ** 2) / (4 * v.D * tt)) * 1e6;
    const top = c(v.U * 240, 240) * 1.1;
    p.frame({ x: [0, 15], y: [0, top], xlabel: 'distance downstream, km', ylabel: 'dye concentration, µg/L' });
    [600, 3600, 7200].forEach((tt) => p.line(xs.map((x) => x / 1000), xs.map((x) => c(x, tt)), C.grey, 1, [4, 3]));
    p.line(xs.map((x) => x / 1000), xs.map((x) => c(x, t)), C.lime, 2.5);
    const dx = xs[1] - xs[0], mass = xs.reduce((s, x) => s + c(x, t), 0) * dx * A / 1e6;
    out(`After ${v.t} min the cloud is centred ${nf(1).format(v.U * t / 1000)} km downstream with a peak of ${nf(1).format(c(v.U * t, t))} µg/L and a width (4σ) of ${nf(0).format(4 * Math.sqrt(2 * v.D * t))} m. Area under the curve × cross-section = ${nf(2).format(mass)} kg${v.U * t + 3 * Math.sqrt(2 * v.D * t) > 15000 ? ' within the plotted reach (some dye has already passed 15 km)' : ' of the 10 kg released: the mass is conserved while the peak falls as 1/√t'}.`);
  },
});

// 13.01 conduction through a wall
def('wallprofile', {
  controls: [{ k: 'k', label: 'Thermal conductivity k (W/(m K))', min: 0.03, max: 2.5, step: 0.01, v: 1.4, f: 2 }, { k: 'L', label: 'Wall thickness (cm)', min: 5, max: 40, step: 1, v: 20, f: 0 }, { k: 'To', label: 'Outside surface (°C)', min: 26, max: 50, step: 0.5, v: 34, f: 1 }],
  draw(p, v, out) {
    const Ti = 26, L = v.L / 100, q = v.k * (v.To - Ti) / L;
    p.frame({ x: [-10, 50], y: [20, 52], xlabel: 'position, cm (outside on the left)', ylabel: 'temperature, °C' });
    p.rect(0, v.L, 20, 52, 'rgba(154,157,147,0.25)').text('wall', v.L / 2 - 2, 50, C.paper).text('sun side', -9, 50, C.amber).text('room', v.L + 1, 50, C.cyan);
    p.line([-10, 0, v.L, 50], [v.To, v.To, Ti, Ti], C.lime, 2.5);
    for (let i = 1; i <= 3; i++) arrow(p, v.L * (i / 4) - 2, 22.5, v.L * (i / 4) + 2, 22.5, C.red, 1 + Math.min(4, q / 40));
    out(`Fourier's law: q = k ΔT / L = ${nf(2).format(v.k)} × ${nf(1).format(v.To - Ti)} / ${nf(2).format(L)} = ${nf(1).format(q)} W/m², the same at every depth, so the profile is a straight line. A 12 m² wall lets ${nf(0).format(q * 12)} W into the room${v.k < 0.1 ? ', insulation-level conductivity.' : '.'}`);
  },
});

// 13.02 alpine hut wall builder
def('hutbuilder', {
  controls: [{ k: 'ins', label: 'Mineral wool (cm)', min: 0, max: 30, step: 1, v: 12, f: 0 }, { k: 'To', label: 'Outside air (°C)', min: -25, max: 10, step: 1, v: -10, f: 0 }, { k: 'win', label: 'Window share of a 12 m² wall (%)', min: 0, max: 50, step: 1, v: 17, f: 0 }],
  draw(p, v, out) {
    const Ti = 20, hi = 7.7, ho = 25, lay = [['spruce', 0.02, 0.13, 'rgba(255,181,71,0.45)'], ['wool', v.ins / 100, 0.035, 'rgba(238,255,65,0.25)'], ['larch', 0.024, 0.13, 'rgba(255,181,71,0.45)']];
    const R = [1 / hi].concat(lay.map(([, L, k]) => L / k), [1 / ho]), Rt = R.reduce((a, b) => a + b, 0), U = 1 / Rt, q = (Ti - v.To) * U;
    p.frame({ x: [0, 40], y: [-26, 22], xlabel: 'through the wall, cm (inside on the left)', ylabel: 'temperature, °C' });
    const xs = [0], Ts = [Ti]; let x = 0, T = Ti; const film = 2;
    T -= q * R[0]; xs.push(film); Ts.push(T); x = film;
    lay.forEach(([, L, k], i) => { p.rect(x, x + L * 100, -26, 22, lay[i][3]); x += L * 100; T -= q * R[i + 1]; xs.push(x); Ts.push(T); });
    T -= q * R[4]; xs.push(x + film); Ts.push(T);
    p.line(xs, Ts, C.lime, 2.5).dots(xs, Ts, C.lime, 3).text('in', 0.3, 20, C.cyan).text('out', Math.min(37, x + 2.2), 20, C.cyan);
    const Aw = 12 * v.win / 100, Q = (Ti - v.To) * (U * (12 - Aw) + 1.1 * Aw);
    out(`R_total = ${nf(3).format(Rt)} m² K/W, U = ${nf(3).format(U)} W/(m² K): ${nf(2).format(q)} W/m² through the wall. With ${nf(1).format(Aw)} m² of window (U = 1.1) the 12 m² wall loses ${nf(0).format(Q)} W, ${Q > 0 ? nf(0).format(100 * 1.1 * Aw * (Ti - v.To) / Q) : 0}% through the glass. Nearly all the temperature drop sits across the insulation.`);
  },
});

// 13.03 critical insulation radius
def('critradius', {
  controls: [{ k: 'r2', label: 'Outer radius of the insulation (mm)', min: 2, max: 60, step: 0.5, v: 10, f: 1 }, { k: 'k', label: 'Insulation k (W/(m K))', min: 0.03, max: 0.4, step: 0.01, v: 0.19, f: 2 }, { k: 'h', label: 'Surface coefficient h (W/(m² K))', min: 3, max: 50, step: 1, v: 10, f: 0 }],
  draw(p, v, out) {
    const r1 = 0.002, dT = 40, Q = (r2) => dT / (Math.log(r2 / r1) / (2 * Math.PI * v.k) + 1 / (2 * Math.PI * r2 * v.h)), rs = linspace(r1, 0.06, 300), rc = v.k / v.h;
    const top = Math.max(...rs.map(Q)) * 1.15;
    p.frame({ x: [0, 60], y: [0, top], xlabel: 'outer radius r₂, mm (wire radius 2 mm)', ylabel: 'heat loss, W per metre' });
    p.line(rs.map((r) => r * 1000), rs.map(Q), C.lime, 2.5);
    if (rc > r1 && rc < 0.06) p.line([rc * 1000, rc * 1000], [0, top], C.amber, 1.5, [5, 4]).text('r_c = k/h', rc * 1000 + 1, top * 0.93, C.amber);
    const q = Q(v.r2 / 1000); p.dots([v.r2], [q], C.cyan, 7);
    out(`Critical radius k/h = ${nf(1).format(rc * 1000)} mm. At r₂ = ${nf(1).format(v.r2)} mm the wire loses ${nf(2).format(q)} W/m (bare: ${nf(2).format(Q(r1))} W/m). ${rc <= r1 ? 'r_c is below the wire radius: any insulation reduces the loss.' : v.r2 / 1000 < rc ? 'Below r_c, adding insulation increases the loss: the extra surface area wins over the extra resistance.' : 'Beyond r_c, more insulation reduces the loss.'}`);
  },
});

// 13.04 fin temperature profile
def('finprofile', {
  controls: [{ k: 'L', label: 'Fin length (mm)', min: 5, max: 150, step: 1, v: 30, f: 0 }, { k: 'h', label: 'h (W/(m² K)), fan off to fan on', min: 5, max: 150, step: 1, v: 40, f: 0 }, { type: 'select', k: 'k', label: 'Material', options: ['Aluminium (200)', 'Copper (390)', 'Stainless steel (15)'], v: 'Aluminium (200)' }],
  draw(p, v, out) {
    const k = [200, 390, 15][['Aluminium (200)', 'Copper (390)', 'Stainless steel (15)'].indexOf(v.k)], d = 0.003, P = Math.PI * d, A = Math.PI * d * d / 4, L = v.L / 1000, tb = 40;
    const m = Math.sqrt(v.h * P / (k * A)), a = v.h / (k * m), den = Math.cosh(m * L) + a * Math.sinh(m * L), th = (x) => (Math.cosh(m * (L - x)) + a * Math.sinh(m * (L - x))) / den;
    const xs = linspace(0, L, 120), M = Math.sqrt(v.h * P * k * A) * tb, q = M * (Math.sinh(m * L) + a * Math.cosh(m * L)) / den, eta = q / (v.h * (P * L + A) * tb);
    p.frame({ x: [0, 150], y: [0, 42], xlabel: 'distance from the base, mm', ylabel: 'excess temperature T − T∞, K' });
    p.rect(0, v.L, 0, 3, 'rgba(154,157,147,0.4)').text('the fin', Math.max(v.L / 2, 12), 5, C.grey, 'center');
    p.line(xs.map((x) => x * 1000), xs.map((x) => th(x) * tb), C.lime, 2.5).line([0, 150], [tb, tb], C.grey, 1, [4, 3]);
    out(`3 mm pin, base 40 K above the air: mL = ${nf(2).format(m * L)}, tip at ${nf(1).format(th(L) * tb)} K. Heat rate ${nf(3).format(q)} W, ${nf(0).format(100 * q / M)}% of the infinitely long fin's √(hPkA)θ_b = ${nf(3).format(M)} W. Fin efficiency ${nf(0).format(eta * 100)}%. ${m * L > 2.5 ? 'Past mL ≈ 2.5 extra length adds almost nothing.' : ''}`);
  },
});

// 13.05 lumped versus exact cooling of a sphere
function sphereRoots13(Bir, n) { const r = []; const g = (z) => 1 - z / Math.tan(z) - Bir; for (let k = 1; k <= n; k++) { let a = (k - 1) * Math.PI + 1e-9, b = k * Math.PI - 1e-9, ga = g(a); for (let i = 0; i < 60; i++) { const c = 0.5 * (a + b), gc = g(c); if ((ga < 0) === (gc < 0)) { a = c; ga = gc; } else b = c; } r.push(0.5 * (a + b)); } return r; }
function sphereExact13(roots, Fo) { let cen = 0, mean = 0; for (const z of roots) { const Cn = 4 * (Math.sin(z) - z * Math.cos(z)) / (2 * z - Math.sin(2 * z)), e = Math.exp(-z * z * Fo); cen += Cn * e; mean += Cn * e * 3 * (Math.sin(z) - z * Math.cos(z)) / z ** 3; } return [cen, mean]; }
def('lumpedbiot', {
  controls: [{ k: 'lb', label: 'log₁₀ of the Biot number hL_c/k', min: -3, max: 0.7, step: 0.05, v: -0.5, f: 2 }],
  draw(p, v, out) {
    const Bi = 10 ** v.lb, roots = sphereRoots13(3 * Bi, 30), ts = linspace(0.02, 4, 160);
    p.frame({ x: [0, 4], y: [0, 1.05], xlabel: 'time / lumped time constant τ = ρcV/(hA)', ylabel: '(T − T∞)/(Tᵢ − T∞)' });
    p.line(ts, ts.map((t) => Math.exp(-t)), C.lime, 2.5);
    p.line(ts, ts.map((t) => sphereExact13(roots, t / (9 * Bi))[1]), C.cyan, 2, [6, 4]);
    p.line(ts, ts.map((t) => sphereExact13(roots, t / (9 * Bi))[0]), C.red, 2, [2, 3]);
    p.text('lumped', 2.6, 0.17, C.lime).text('exact mean', 2.6, 0.27, C.cyan).text('exact centre', 2.6, 0.37, C.red);
    const [c1, m1] = sphereExact13(roots, 1 / (9 * Bi));
    out(`Sphere, Bi = ${nf(3).format(Bi)}. After one τ the lumped model says 0.368; the exact mean is ${nf(3).format(m1)} and the centre ${nf(3).format(c1)}. ${Bi < 0.1 ? 'Bi < 0.1: the lumped model is fine.' : 'Warning: Bi > 0.1, so the inside lags the surface and the lumped model is too optimistic.'}`);
  },
});

// 13.06 2D transient in a square bar
def('heatsquare', {
  controls: [{ k: 't', label: 'Time in the 60 °C bath (min)', min: 0, max: 90, step: 1, v: 10, f: 0 }],
  draw(p, v, out) {
    const L = 0.02, al = 1.4e-7, t = v.t * 60, Ti = 5, Tb = 60;
    const th = (x) => { if (t === 0) return 1; let s = 0; for (let n = 0; n < 60; n++) { const lam = (2 * n + 1) * Math.PI / (2 * L); s += 4 * (n % 2 ? -1 : 1) / ((2 * n + 1) * Math.PI) * Math.cos(lam * x) * Math.exp(-lam * lam * al * t); } return s; };
    const N = 20, d = 2 * L / N, cols = [[92, 200, 255], [238, 255, 65], [255, 181, 71], [255, 90, 54]];
    const col = (T) => { const u = Math.min(Math.max((T - Ti) / (Tb - Ti), 0), 1) * 3, i = Math.min(Math.floor(u), 2), f = u - i, a = cols[i], b = cols[i + 1]; return `rgb(${a.map((q, j) => Math.round(q + (b[j] - q) * f)).join(',')})`; };
    sqframe(p, 24, 'x, mm', 'y, mm');
    const tx = []; for (let i = 0; i < N; i++) tx.push(th(-L + (i + 0.5) * d));
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) p.rect((-L + i * d) * 1000, (-L + (i + 1) * d) * 1000, (-L + j * d) * 1000, (-L + (j + 1) * d) * 1000, col(Tb + (Ti - Tb) * tx[i] * tx[j]));
    const c2 = Tb + (Ti - Tb) * th(0) ** 2, c1 = Tb + (Ti - Tb) * th(0);
    out(`4 × 4 cm bar of meat from 5 °C into a 60 °C bath (faces held at 60 °C). After ${v.t} min the centre is at ${nf(1).format(c2)} °C (product of two slab solutions; a 4 cm slab's centre would be ${nf(1).format(c1)} °C). Blue is 5 °C, lime and amber in between, red is 60 °C.`);
  },
});

// 13.07 local h along a flat plate
def('platebl', {
  controls: [{ k: 'U', label: 'Air speed (m/s)', min: 0.5, max: 30, step: 0.5, v: 3, f: 1 }],
  draw(p, v, out) {
    const nu = 1.608e-5, k = 0.02588, Pr = 0.7282, L = 1, xt = Math.min(5e5 * nu / v.U, L), xs = linspace(0.005, L, 300);
    const hl = (x) => 0.332 * Math.sqrt(v.U * x / nu) * Pr ** (1 / 3) * k / x, ht = (x) => 0.0296 * (v.U * x / nu) ** 0.8 * Pr ** (1 / 3) * k / x;
    p.frame({ x: [0, 100], y: [0, 120], xlabel: 'distance from the leading edge, cm', ylabel: 'local h, W/(m² K)' });
    p.line(xs.map((x) => x * 100), xs.map((x) => (x <= xt ? hl(x) : NaN)), C.lime, 2.5);
    if (xt < L) { p.line(xs.map((x) => x * 100), xs.map((x) => (x >= xt ? ht(x) : NaN)), C.amber, 2.5).line([xt * 100, xt * 100], [0, 120], C.grey, 1, [4, 3]).text('Re = 5 × 10⁵', xt * 100 + 1.5, 112, C.grey); }
    const ReL = v.U * L / nu, h05 = 0.664 * Math.sqrt(v.U * 0.5 / nu) * Pr ** (1 / 3) * k / 0.5;
    out(`Air at 30 °C. Over a 0.5 m plate Re_L = ${nf(0).format(v.U * 0.5 / nu)}${v.U * 0.5 / nu < 5e5 ? `, laminar: average h = ${nf(2).format(h05)} W/(m² K)` : ', past transition: the laminar formula no longer applies to the whole plate'}. On this 1 m plate ${xt < L ? `the boundary layer turns turbulent at ${nf(0).format(xt * 100)} cm (amber, 0.0296 Re^0.8 Pr^⅓), and h jumps.` : `Re_L = ${nf(0).format(ReL)} stays laminar (lime) all the way.`}`);
  },
});

// 13.08 pipe convection calculator
def('pipecalc', {
  controls: [{ k: 'U', label: 'Mean velocity (m/s)', min: 0.05, max: 3, step: 0.05, v: 1, f: 2 }, { k: 'D', label: 'Tube diameter (mm)', min: 4, max: 50, step: 1, v: 10, f: 0 }, { type: 'select', k: 'fl', label: 'Fluid at 40 °C', options: ['Water (Pr 4.32)', 'Air (Pr 0.71)', 'Engine oil (Pr 2870)'], v: 'Water (Pr 4.32)' }],
  draw(p, v, out) {
    const i = ['Water (Pr 4.32)', 'Air (Pr 0.71)', 'Engine oil (Pr 2870)'].indexOf(v.fl), nu = [0.658e-6, 1.70e-5, 2.42e-4][i], k = [0.631, 0.0271, 0.144][i], Pr = [4.32, 0.71, 2870][i], D = v.D / 1000;
    const db = (Re) => 0.023 * Re ** 0.8 * Pr ** 0.4, gn = (Re) => { const f = (0.790 * Math.log(Re) - 1.64) ** -2; return (f / 8) * (Re - 1000) * Pr / (1 + 12.7 * Math.sqrt(f / 8) * (Pr ** (2 / 3) - 1)); };
    const Res = logspace(1, 6, 300);
    p.frame({ x: [10, 1e6], y: [1, 1e4], xlog: true, ylog: true, xlabel: 'Reynolds number', ylabel: 'Nusselt number' });
    p.rect(2300, 3000, 1, 1e4, 'rgba(255,181,71,0.12)');
    p.line(Res, Res.map((R) => (R < 2300 ? 3.66 : NaN)), C.cyan, 2.5).line(Res, Res.map((R) => (R >= 3000 ? gn(R) : NaN)), C.lime, 2.5).line(Res, Res.map((R) => (R >= 1e4 ? db(R) : NaN)), C.red, 1.5, [5, 4]);
    const Re = v.U * D / nu, mode = Re < 2300 ? 'laminar' : Re < 3000 ? 'transitional' : 'turbulent';
    const Nu = Re < 2300 ? 3.66 : Re < 3000 ? NaN : gn(Re); p.dots([Re], [isFinite(Nu) ? Nu : 3.66], C.paper, 6);
    const warn = Re < 2300 ? ` Thermal entry length about 0.05 Re Pr D = ${nf(1).format(0.05 * Re * Pr * D)} m: in a shorter tube the flow is not yet fully developed and Nu is higher.` : Pr > 2000 ? ' Warning: Pr is outside Gnielinski (0.5 to 2000) and Dittus-Boelter (0.6 to 160) ranges.' : Re >= 3000 && Re < 1e4 ? ' Dittus-Boelter is outside its range here (needs Re > 10⁴); use Gnielinski.' : '';
    out(`Re = ${nf(0).format(Re)}, ${mode}. ${Re < 2300 ? `Fully developed laminar flow, constant wall temperature: Nu = 3.66, h = ${nf(0).format(3.66 * k / D)} W/(m² K).` : Re < 3000 ? 'Between 2300 and 3000 no correlation is reliable.' : `Gnielinski Nu = ${nf(1).format(gn(Re))}, h = ${nf(0).format(gn(Re) * k / D)} W/(m² K)${Re >= 1e4 ? `; Dittus-Boelter ${nf(1).format(db(Re))}` : ''}.`}${warn}`);
  },
});

// 13.09 natural convection on a vertical plate
def('natplate', {
  controls: [{ k: 'lr', label: 'log₁₀ of the Rayleigh number', min: 4, max: 13, step: 0.1, v: 8.8, f: 1 }],
  draw(p, v, out) {
    const Pr = 0.71, cc = (Ra) => (0.825 + 0.387 * Ra ** (1 / 6) / (1 + (0.492 / Pr) ** (9 / 16)) ** (8 / 27)) ** 2, Ras = logspace(4, 13, 200), Ra = 10 ** v.lr;
    p.frame({ x: [1e4, 1e13], y: [1, 1e4], xlog: true, ylog: true, xlabel: 'Rayleigh number Ra = gβΔT L³/(να)', ylabel: 'average Nusselt number' });
    p.line([1e9, 1e9], [1, 1e4], C.grey, 1, [4, 3]).text('transition', 1.4e9, 2, C.grey);
    p.line(Ras, Ras.map((R) => 0.59 * R ** 0.25), C.cyan, 1.5, [5, 4]).line(Ras, Ras.map((R) => 0.10 * R ** (1 / 3)), C.amber, 1.5, [5, 4]).line(Ras, Ras.map(cc), C.lime, 2.5);
    p.dots([Ra], [cc(Ra)], C.paper, 6);
    const L = Math.cbrt(Ra * 1.70e-5 * (1.70e-5 / Pr) / (9.81 / 313.15 * 40));
    out(`Ra = ${Ra.toExponential(2)}: Churchill-Chu Nu = ${nf(1).format(cc(Ra))} (lime). Laminar 0.59 Ra^¼ (cyan) gives ${nf(1).format(0.59 * Ra ** 0.25)}, turbulent 0.10 Ra^⅓ (amber) ${nf(1).format(0.10 * Ra ** (1 / 3))}. ${Ra < 1e9 ? 'Laminar.' : 'Past Ra ≈ 10⁹ the boundary layer is turbulent.'} For a surface 40 K above 20 °C air, this Ra is a plate ${nf(2).format(L)} m tall.`);
  },
});

// 13.10 roof heat balance in the tropical sun
def('roofbalance', {
  controls: [{ k: 'a', label: 'Solar absorptivity', min: 0.05, max: 0.95, step: 0.01, v: 0.65, f: 2 }, { k: 'e', label: 'Thermal emissivity', min: 0.03, max: 0.95, step: 0.01, v: 0.25, f: 2 }],
  draw(p, v, out) {
    const S = 5.670374e-8, Tsky = 294.15, Ta = 304.15, h = 10, G = 1000;
    const roof = (a, e) => { let lo = 250, hi = 450; for (let i = 0; i < 50; i++) { const m = 0.5 * (lo + hi); if (a * G - e * S * (m ** 4 - Tsky ** 4) - h * (m - Ta) > 0) lo = m; else hi = m; } return 0.5 * (lo + hi) - 273.15; };
    const as = linspace(0.05, 0.95, 60);
    p.frame({ x: [0, 1], y: [20, 110], xlabel: 'solar absorptivity', ylabel: 'roof temperature, °C' });
    p.line(as, as.map((a) => roof(a, 0.9)), C.grey, 1.5, [5, 4]).line(as, as.map((a) => roof(a, 0.05)), C.grey, 1.5, [2, 3]);
    p.text('dashed: ε = 0.9 (paint)', 0.04, 104, C.grey).text('dotted: ε = 0.05 (polished metal)', 0.04, 96, C.grey);
    p.line(as, as.map((a) => roof(a, v.e)), C.lime, 2.5);
    const T = roof(v.a, v.e), Tk = T + 273.15; p.dots([v.a], [T], C.paper, 6);
    out(`Bali at noon (1000 W/m², air 31 °C, sky 21 °C, h = 10): roof at ${nf(1).format(T)} °C. It absorbs ${nf(0).format(v.a * G)} W/m², radiates away a net ${nf(0).format(v.e * S * (Tk ** 4 - Tsky ** 4))} W/m² and convects ${nf(0).format(h * (Tk - Ta))} W/m². White cool-roof paint (0.20, 0.90) sits near 40 °C; galvanised steel (0.65, 0.25) near 84 °C.`);
  },
});

// 13.11 sun path for Bali and Zurich
def('sunpath', {
  controls: [{ k: 'n', label: 'Day of the year', min: 1, max: 365, step: 1, v: 172, f: 0 }, { type: 'select', k: 'pl', label: 'Place', options: ['Bali (8.65° S)', 'Zürich (47.37° N)'], v: 'Bali (8.65° S)' }],
  draw(p, v, out) {
    const lats = [-8.65, 47.37], i = ['Bali (8.65° S)', 'Zürich (47.37° N)'].indexOf(v.pl), d2r = Math.PI / 180;
    const dec = (n) => 23.45 * Math.sin(d2r * 360 * (284 + n) / 365);
    const el = (lat, n, hr) => Math.asin(Math.sin(lat * d2r) * Math.sin(dec(n) * d2r) + Math.cos(lat * d2r) * Math.cos(dec(n) * d2r) * Math.cos(15 * (hr - 12) * d2r)) / d2r;
    const day = (lat, n) => { let s = 0; for (let k = 0; k < 288; k++) { const a = el(lat, n, (k + 0.5) / 12); if (a > 0) { const sn = Math.sin(a * d2r); s += 1.1 * 1353 * 0.7 ** ((1 / sn) ** 0.678) * sn; } } return s / 12 / 1000; };
    const hs = linspace(0, 24, 241);
    p.frame({ x: [0, 24], y: [-10, 90], xlabel: 'solar time, h', ylabel: 'sun elevation, °' });
    p.line([0, 24], [0, 0], C.grey, 1);
    p.line(hs, hs.map((h) => el(lats[1 - i], v.n, h)), C.grey, 1.5, [5, 4]);
    p.line(hs, hs.map((h) => el(lats[i], v.n, h)), C.lime, 2.5);
    const noon = 90 - Math.abs(lats[i] - dec(v.n));
    p.dots([12], [noon], C.paper, 6);
    out(`${v.pl}, day ${v.n}: declination ${nf(2).format(dec(v.n))}°, noon elevation 90 − |lat − decl| = ${nf(1).format(noon)}°. Clear-sky energy on a flat panel: ${nf(2).format(day(lats[i], v.n))} kWh/m² (the other city, dashed grey: ${nf(2).format(day(lats[1 - i], v.n))}).`);
  },
});

// 13.12 parallel flow versus counterflow profiles
def('hxprofile', {
  controls: [{ k: 'UA', label: 'UA (W/K)', min: 20, max: 1500, step: 10, v: 300, f: 0 }, { type: 'select', k: 'ar', label: 'Arrangement', options: ['Counterflow', 'Parallel flow'], v: 'Counterflow' }],
  draw(p, v, out) {
    const Thi = 110, Tci = 25, Ch = 420, Cc = 418, cnt = v.ar === 'Counterflow', xs = linspace(0, 1, 101);
    let Th, Tc;
    if (!cnt) { const k = v.UA * (1 / Ch + 1 / Cc), dT = (x) => (Thi - Tci) * Math.exp(-k * x), Tm = (Ch * Thi + Cc * Tci) / (Ch + Cc); Th = xs.map((x) => Tm + Cc / (Ch + Cc) * dT(x)); Tc = xs.map((x) => Tm - Ch / (Ch + Cc) * dT(x)); }
    else { const k = v.UA * (1 / Ch - 1 / Cc), cr = Ch / Cc, e = Math.abs(k) < 1e-9 ? v.UA / Ch / (1 + v.UA / Ch) : (1 - Math.exp(-k)) / (1 - cr * Math.exp(-k)), Q = e * Ch * (Thi - Tci), Tco = Tci + Q / Cc;
      const dT0 = Thi - Tco, I = (x) => (Math.abs(k) < 1e-9 ? x : (1 - Math.exp(-k * x)) / k); Th = xs.map((x) => Thi - v.UA / Ch * dT0 * I(x)); Tc = xs.map((x, j) => Th[j] - dT0 * Math.exp(-k * x)); }
    p.frame({ x: [0, 1], y: [20, 115], xlabel: 'position along the exchanger, fraction of length', ylabel: 'temperature, °C' });
    p.line(xs, Th, C.red, 2.5).line(xs, Tc, C.cyan, 2.5);
    p.text(cnt ? 'water flows ←' : 'water flows →', 0.62, cnt ? Tc[62] + 6 : Tc[62] - 7, C.cyan).text('oil flows →', 0.05, Th[5] + 5, C.red);
    const Q = Ch * (Thi - Th[100]), Tco = cnt ? Tc[0] : Tc[100];
    out(`${v.ar}: oil 110 → ${nf(1).format(Th[100])} °C, water 25 → ${nf(1).format(Tco)} °C, Q = ${nf(2).format(Q / 1000)} kW. ${cnt ? (Tco > Th[100] ? 'The water leaves hotter than the oil leaves: only counterflow can do that.' : 'Push UA up: counterflow can heat the water above the oil outlet temperature.') : 'In parallel flow the water can never get hotter than the oil outlet.'}`);
  },
});

// 13.13 effectiveness against NTU
def('ntucurve', {
  controls: [{ k: 'ntu', label: 'NTU = UA/C_min', min: 0.1, max: 6, step: 0.05, v: 0.72, f: 2 }, { k: 'cr', label: 'Capacity ratio C_min/C_max', min: 0, max: 1, step: 0.01, v: 1, f: 2 }],
  draw(p, v, out) {
    const par = (n, c) => (1 - Math.exp(-n * (1 + c))) / (1 + c), cnt = (n, c) => (Math.abs(1 - c) < 1e-9 ? n / (1 + n) : (1 - Math.exp(-n * (1 - c))) / (1 - c * Math.exp(-n * (1 - c))));
    const ns = linspace(0, 6, 200);
    p.frame({ x: [0, 6], y: [0, 1], xlabel: 'NTU = UA / C_min', ylabel: 'effectiveness ε = Q / Q_max' });
    p.line(ns, ns.map((n) => 1 - Math.exp(-n)), C.grey, 1, [4, 3]).text('C_r = 0 (condenser)', 3.4, 0.93, C.grey);
    p.line(ns, ns.map((n) => cnt(n, v.cr)), C.lime, 2.5).line(ns, ns.map((n) => par(n, v.cr)), C.cyan, 2, [6, 4]);
    p.dots([v.ntu, v.ntu], [cnt(v.ntu, v.cr), par(v.ntu, v.cr)], C.paper, 5);
    p.text('counterflow', 4.2, cnt(4.2, v.cr) - 0.07, C.lime).text('parallel flow', 4.2, par(4.2, v.cr) - 0.07, C.cyan);
    out(`NTU = ${nf(2).format(v.ntu)}, C_r = ${nf(2).format(v.cr)}: counterflow ε = ${nf(3).format(cnt(v.ntu, v.cr))}, parallel ε = ${nf(3).format(par(v.ntu, v.cr))}. Parallel flow can never exceed 1/(1 + C_r) = ${nf(3).format(1 / (1 + v.cr))}. Q = ε C_min (T_h,in − T_c,in).`);
  },
});

// 13.14 e-bike battery temperature over a ride
def('battthermal', {
  controls: [{ k: 'Ta', label: 'Air temperature (°C)', min: 10, max: 40, step: 1, v: 32, f: 0 }, { k: 'Ic', label: 'Current on the climb (A)', min: 5, max: 40, step: 1, v: 25, f: 0 }, { k: 'tc', label: 'Climb duration (min)', min: 0, max: 45, step: 1, v: 15, f: 0 }],
  draw(p, v, out) {
    const R = 0.09, Cc = 2070, Cs = 540, Ri = 0.25, A = 0.12;
    const ride = [[20, 10, 1], [v.tc, v.Ic, 1], [25, 8, 1], [30, 0, 0]];
    let Tc = v.Ta, Ts = v.Ta, t = 0; const ts = [0], cs = [Tc], ss = [Ts], Is = [10];
    const f = (a, b, I, h) => [(I * I * R - (a - b) / Ri) / Cc, ((a - b) / Ri - h * A * (b - v.Ta)) / Cs];
    for (const [m, I, rid] of ride) { const h = rid ? 15 : 5; for (let k = 0; k < m * 12; k++) { const dt = 5; const k1 = f(Tc, Ts, I, h), k2 = f(Tc + dt / 2 * k1[0], Ts + dt / 2 * k1[1], I, h), k3 = f(Tc + dt / 2 * k2[0], Ts + dt / 2 * k2[1], I, h), k4 = f(Tc + dt * k3[0], Ts + dt * k3[1], I, h); Tc += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); Ts += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]); t += dt; if (k % 6 === 5) { ts.push(t / 60); cs.push(Tc); ss.push(Ts); Is.push(I); } } }
    const tend = t / 60, peak = Math.max(...cs), tp = ts[cs.indexOf(peak)], ss15 = v.Ta + v.Ic * v.Ic * R * (Ri + 1 / (15 * A));
    p.frame({ x: [0, 135], y: [0, 80], xlabel: 'time, min', ylabel: '°C (bars: current, A)' });
    for (let i = 1; i < ts.length; i++) p.rect(ts[i - 1], ts[i], 0, Is[i], 'rgba(154,157,147,0.35)');
    p.line([0, 135], [60, 60], C.red, 1, [4, 3]).text('60 °C cell limit', 2, 63, C.red);
    p.line(ts, ss, C.cyan, 2, [6, 4]).line(ts, cs, C.lime, 2.5);
    out(`Peak cell temperature ${nf(1).format(peak)} °C at ${nf(0).format(tp)} min (case, cyan dashed, runs cooler). Holding ${v.Ic} A for ever would settle at ${nf(1).format(ss15)} °C; the pack's thermal mass (time constant about 31 min) keeps a short climb well below that. ${peak > 60 ? 'Warning: above the 60 °C limit, the controller should cut power.' : ''} Parked from ${nf(0).format(tend - 30)} min, h falls from 15 to 5 W/(m² K).`);
  },
});

// 14.01 orthographic views of a stepped block
def('orthoviews', {
  controls: [{ type: 'select', k: 'vw', label: 'View', options: ['Rotated (use the sliders)', 'Front', 'Top', 'Right side', 'Isometric'], v: 'Rotated (use the sliders)' }, { k: 'yaw', label: 'Turn about the vertical axis (°)', min: -180, max: 180, step: 1, v: 30, f: 0 }, { k: 'pit', label: 'Tilt towards you (°)', min: -90, max: 90, step: 1, v: 20, f: 0 }],
  draw(p, v, out) {
    const P0 = [[0, 0, 0], [60, 0, 0], [60, 0, 15], [35, 0, 15], [35, 0, 30], [0, 0, 30]], V = P0.concat(P0.map((q) => [q[0], 40, q[2]])).map((q) => [q[0] - 30, q[1] - 20, q[2] - 15]);
    const E = []; for (let i = 0; i < 6; i++) E.push([i, (i + 1) % 6], [i + 6, ((i + 1) % 6) + 6], [i, i + 6]);
    const d = Math.PI / 180;
    let yaw = v.yaw, pit = v.pit, name = v.vw;
    if (name === 'Front') { yaw = 0; pit = 0; } else if (name === 'Top') { yaw = 0; pit = 90; } else if (name === 'Right side') { yaw = -90; pit = 0; } else if (name === 'Isometric') { yaw = -45; pit = Math.atan(1 / Math.SQRT2) / d; }
    const cy = Math.cos(yaw * d), sy = Math.sin(yaw * d), cp = Math.cos(pit * d), sp = Math.sin(pit * d);
    const proj = (q) => { const x = cy * q[0] - sy * q[1], y = sy * q[0] + cy * q[1], z = q[2]; return [x, sp * y + cp * z]; };
    sqframe(p, 45, 'screen x, mm', 'screen y, mm');
    const Q = V.map(proj);
    for (const [a, b] of E) p.line([Q[a][0], Q[b][0]], [Q[a][1], Q[b][1]], C.lime, 2);
    const ax = [[[0, 0, 0], [20, 0, 0], 'x'], [[0, 0, 0], [0, 20, 0], 'y'], [[0, 0, 0], [0, 0, 20], 'z']];
    for (const [o, e, l] of ax) { const a = proj([o[0] - 40, o[1] - 30, o[2] - 25]), b = proj([e[0] - 40, e[1] - 30, e[2] - 25]); p.line([a[0], b[0]], [a[1], b[1]], C.cyan, 1.5); if (Math.hypot(b[0] - a[0], b[1] - a[1]) > 3) p.text(l, b[0] + 1, b[1] + 1, C.cyan); }
    out(`${name}: turn ${nf(0).format(yaw)}°, tilt ${nf(1).format(pit)}°. Screen coordinates are a linear map of (x, y, z): [cos θ, −sin θ, 0] and [sin φ sin θ, sin φ cos θ, cos φ]. Edges that coincide in a principal view collapse onto one line; that is why a drawing needs several views. Wireframe: hidden edges are drawn too.`);
  },
});

// 14.02 composition order of 2D transforms
def('xform2d', {
  controls: [{ k: 'a', label: 'Rotation (°)', min: -180, max: 180, step: 5, v: 90, f: 0 }, { k: 'tx', label: 'Translation x', min: -4, max: 4, step: 0.5, v: 3, f: 1 }, { k: 'ty', label: 'Translation y', min: -4, max: 4, step: 0.5, v: 0, f: 1 }],
  draw(p, v, out) {
    const sh = [[0, 0], [2, 0], [2, 1], [1, 1.8], [0, 1], [0, 0]], t = v.a * Math.PI / 180, c = Math.cos(t), s = Math.sin(t);
    const R = (q) => [c * q[0] - s * q[1], s * q[0] + c * q[1]], T = (q) => [q[0] + v.tx, q[1] + v.ty];
    const rt = sh.map((q) => T(R(q))), tr = sh.map((q) => R(T(q)));
    sqframe(p, 7, 'x', 'y');
    p.line([-7, 7], [0, 0], C.rule, 1).line([0, 0], [-7, 7], C.rule, 1);
    p.line(sh.map((q) => q[0]), sh.map((q) => q[1]), C.grey, 2);
    p.line(tr.map((q) => q[0]), tr.map((q) => q[1]), C.cyan, 2, [6, 4]);
    p.line(rt.map((q) => q[0]), rt.map((q) => q[1]), C.lime, 2.5);
    p.dots([0], [0], C.paper, 4);
    out(`Grey: the original shape. Lime: rotate ${v.a}° about the origin, then translate by (${v.tx}, ${v.ty}), matrix T·R. Cyan dashed: translate first, then rotate, matrix R·T; the translation itself gets rotated. ${Math.abs(v.a % 360) < 1e-9 || (v.tx === 0 && v.ty === 0) ? 'With no rotation or no translation the two orders agree.' : 'The two results differ: matrix products do not commute.'}`);
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
