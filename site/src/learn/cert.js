// Certificate of completion: drawn on a canvas in the browser, exported as PNG or PDF.
// The verification code is a SHA-256 hash of the certificate details, so anyone can recompute it.
export const CERT_VERSION = 'MEFS-1';

export function canonical({ scope, name, date, phases }) {
  return [CERT_VERSION, scope, name.normalize('NFC').trim().replace(/\s+/g, ' '), date, phases.join(',')].join('|');
}
export async function certCode(details) {
  const bytes = new TextEncoder().encode(canonical(details));
  let hex;
  if (globalThis.crypto?.subtle) {
    const buf = await crypto.subtle.digest('SHA-256', bytes);
    hex = [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
  } else {
    hex = sha256Fallback(bytes); // non-secure contexts (plain http) have no crypto.subtle
  }
  return hex.slice(0, 12).toUpperCase().match(/.{4}/g).join('-');
}

const W = 2000, H = 1414; // A4 landscape ratio
export function drawCertificate(canvas, c) {
  canvas.width = W; canvas.height = H;
  const g = canvas.getContext('2d');
  const lime = '#eeff41', paper = '#f2f3ec', grey = '#9a9d93';
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  // drawing-sheet border with a title block, like an engineering drawing
  g.strokeStyle = 'rgba(242,243,236,0.35)'; g.lineWidth = 2; g.strokeRect(60, 60, W - 120, H - 120);
  g.strokeStyle = 'rgba(242,243,236,0.15)'; g.lineWidth = 1; g.strokeRect(80, 80, W - 160, H - 160);
  // zone ticks
  g.fillStyle = 'rgba(242,243,236,0.35)';
  for (let x = 80; x <= W - 80; x += (W - 160) / 8) g.fillRect(x, 60, 1, 20), g.fillRect(x, H - 80, 1, 20);
  // cantilever mark
  g.save(); g.translate(150, 150); g.scale(2.6, 2.6);
  g.strokeStyle = paper; g.lineWidth = 1.6; g.strokeRect(3, 5, 5, 22); g.strokeRect(8, 13, 21, 4);
  g.strokeStyle = lime; g.lineWidth = 2; g.beginPath(); g.moveTo(8, 15); g.bezierCurveTo(15, 15, 22, 16.2, 29, 19.6); g.stroke();
  g.restore();
  const font = (w, s, f = "'Archivo Variable', Archivo, sans-serif") => `${w} ${s}px ${f}`;
  g.fillStyle = paper; g.font = font(700, 34); g.textBaseline = 'alphabetic';
  g.fillText('Mechanical Engineering from Scratch', 250, 205);
  g.fillStyle = grey; g.font = font(500, 26); g.fillText('A free, open-source course', 250, 245);
  g.fillStyle = lime; g.font = font(600, 30); g.fillText('Certificate of completion', 150, 400);
  g.fillStyle = paper; g.font = font(800, fitSize(g, c.name, 1500, 120, "'Archivo Variable', Archivo, sans-serif", 800));
  g.fillText(c.name, 150, 540);
  g.strokeStyle = lime; g.lineWidth = 3; g.beginPath(); g.moveTo(150, 580); g.lineTo(150 + Math.min(1500, g.measureText(c.name).width), 580); g.stroke();
  g.fillStyle = paper; g.font = font(400, 38, "'Source Serif 4 Variable', Georgia, serif");
  wrap(g, c.statement, 150, 660, 1500, 54);
  // title block (bottom right)
  const bx = W - 80 - 900, by = H - 80 - 300;
  g.strokeStyle = 'rgba(242,243,236,0.35)'; g.lineWidth = 2; g.strokeRect(bx, by, 900, 300);
  g.lineWidth = 1; g.beginPath(); g.moveTo(bx, by + 100); g.lineTo(bx + 900, by + 100); g.moveTo(bx, by + 200); g.lineTo(bx + 900, by + 200); g.moveTo(bx + 450, by); g.lineTo(bx + 450, by + 200); g.stroke();
  const cell = (label, value, x, y, color = paper) => { g.fillStyle = grey; g.font = font(500, 22); g.fillText(label, x + 20, y + 36); g.fillStyle = color; g.font = font(650, 34); g.fillText(value, x + 20, y + 80); };
  cell('Date', c.dateLabel, bx, by); cell('Scope', c.scopeLabel, bx + 450, by);
  cell('Phase tests passed', String(c.phases.length), bx, by + 100); cell('Verification code', c.code, bx + 450, by + 100, lime);
  g.fillStyle = grey; g.font = font(500, 21);
  g.fillText('Verify: andreolf.github.io/mechanical-engineering-from-scratch/learn.html#/verify', bx + 20, by + 245);
  g.fillText('Recompute the code from the name, date, scope and phases.', bx + 20, by + 275);
  // honesty statement (bottom left)
  g.fillStyle = grey; g.font = font(400, 22);
  wrap(g, 'This is a free certificate of completion generated in the learner’s browser. It is not an accredited qualification and is not affiliated with or endorsed by ETH Zurich. Completion is self-reported: the code proves the details were not altered, not who took the tests.', 150, H - 300, bx - 230, 32);
  return canvas;
}
function fitSize(g, text, maxW, start, fam, weight) {
  let s = start;
  while (s > 40) { g.font = `${weight} ${s}px ${fam}`; if (g.measureText(text).width <= maxW) break; s -= 4; }
  return s;
}
function wrap(g, text, x, y, maxW, lh) {
  const words = text.split(' ');
  let line = '';
  for (const w of words) {
    const t = line ? line + ' ' + w : w;
    if (g.measureText(t).width > maxW && line) { g.fillText(line, x, y); y += lh; line = w; } else line = t;
  }
  if (line) g.fillText(line, x, y);
  return y;
}

/** Minimal single-page PDF (A4 landscape) that embeds the canvas as a JPEG. */
export function canvasToPdf(canvas) {
  const jpeg = atob(canvas.toDataURL('image/jpeg', 0.92).split(',')[1]);
  const img = new Uint8Array(jpeg.length);
  for (let i = 0; i < jpeg.length; i++) img[i] = jpeg.charCodeAt(i);
  const pw = 841.89, ph = 595.28;
  const enc = new TextEncoder();
  const chunks = [], offsets = [];
  let len = 0;
  const push = (data) => { const b = typeof data === 'string' ? enc.encode(data) : data; chunks.push(b); len += b.length; };
  const obj = (n, body) => { offsets[n] = len; push(`${n} 0 obj\n`); body(); push('\nendobj\n'); };
  push('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
  obj(1, () => push('<< /Type /Catalog /Pages 2 0 R >>'));
  obj(2, () => push('<< /Type /Pages /Kids [3 0 R] /Count 1 >>'));
  obj(3, () => push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pw} ${ph}] /Resources << /XObject << /Im0 4 0 R >> >> /Contents 5 0 R >>`));
  obj(4, () => { push(`<< /Type /XObject /Subtype /Image /Width ${canvas.width} /Height ${canvas.height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${img.length} >>\nstream\n`); push(img); push('\nendstream'); });
  const content = `q ${pw} 0 0 ${ph} 0 0 cm /Im0 Do Q`;
  obj(5, () => push(`<< /Length ${content.length} >>\nstream\n${content}\nendstream`));
  const xref = len;
  push(`xref\n0 6\n0000000000 65535 f \n${[1, 2, 3, 4, 5].map((n) => String(offsets[n]).padStart(10, '0') + ' 00000 n \n').join('')}`);
  push(`trailer\n<< /Size 6 /Root 1 0 R /Info << /Title (Certificate of completion) /Producer (Mechanical Engineering from Scratch) >> >>\nstartxref\n${xref}\n%%EOF\n`);
  return new Blob(chunks, { type: 'application/pdf' });
}

// Compact SHA-256 for contexts without crypto.subtle.
function sha256Fallback(bytes) {
  const K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
  let h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  const l = bytes.length, n = (((l + 9) >> 6) + 1) << 6;
  const m = new Uint8Array(n); m.set(bytes); m[l] = 0x80;
  const dv = new DataView(m.buffer); dv.setUint32(n - 4, l * 8); dv.setUint32(n - 8, Math.floor((l * 8) / 2 ** 32));
  const w = new Uint32Array(64), r = (x, s) => (x >>> s) | (x << (32 - s));
  for (let o = 0; o < n; o += 64) {
    for (let i = 0; i < 16; i++) w[i] = dv.getUint32(o + 4 * i);
    for (let i = 16; i < 64; i++) w[i] = (w[i - 16] + (r(w[i - 15], 7) ^ r(w[i - 15], 18) ^ (w[i - 15] >>> 3)) + w[i - 7] + (r(w[i - 2], 17) ^ r(w[i - 2], 19) ^ (w[i - 2] >>> 10))) >>> 0;
    let [a, b, c, d, e, f, g, hh] = h;
    for (let i = 0; i < 64; i++) {
      const t1 = (hh + (r(e, 6) ^ r(e, 11) ^ r(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) >>> 0;
      const t2 = ((r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
      hh = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
    }
    h = h.map((v, i) => (v + [a, b, c, d, e, f, g, hh][i]) >>> 0);
  }
  return h.map((v) => v.toString(16).padStart(8, '0')).join('');
}
export { sha256Fallback };
