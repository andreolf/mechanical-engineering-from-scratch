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
