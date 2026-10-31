// Involute spur-gear outline for three.js, from the same relations as lesson 15.08:
// pitch radius r = m z / 2, tip r + m, root r - 1.25 m, base r cos(phi), tooth half-angle at radius r'
// psi(r') = pi / (2 z) + inv(phi) - inv(phi'), with cos(phi') = r_b / r' and inv(x) = tan x - x.
import * as THREE from 'three';
const inv = (a) => Math.tan(a) - a;
export function gearShape(THREE_, { m, z, phi = (20 * Math.PI) / 180, bore = 0 }) {
  const r = (m * z) / 2, ra = r + m, rf = Math.max(r - 1.25 * m, m * 0.5), rb = r * Math.cos(phi);
  const half = (rr) => { const c = Math.min(1, rb / rr); return Math.PI / (2 * z) + inv(phi) - inv(Math.acos(c)); };
  const shape = new THREE.Shape(); const N = 5; let first = true;
  const P = (rr, a) => { const x = rr * Math.cos(a), y = rr * Math.sin(a); if (first) { shape.moveTo(x, y); first = false; } else shape.lineTo(x, y); };
  const r0 = Math.max(rf, rb);
  for (let k = 0; k < z; k++) {
    const c = (2 * Math.PI * k) / z;
    const hb = half(r0);
    P(rf, c - hb - 0.15 / z); // root, just before the flank
    for (let i = 0; i <= N; i++) { const rr = r0 + ((ra - r0) * i) / N; P(rr, c - half(rr)); }
    for (let i = N; i >= 0; i--) { const rr = r0 + ((ra - r0) * i) / N; P(rr, c + half(rr)); }
    P(rf, c + hb + 0.15 / z);
  }
  shape.closePath();
  if (bore > 0) { const hole = new THREE.Path(); hole.absarc(0, 0, bore, 0, Math.PI * 2, true); shape.holes.push(hole); }
  return { shape, r, ra, rf, rb };
}
// Extruded along +z, centred on z = 0.
export function gearGeometry({ m, z, width, bore = 0 }) {
  const { shape, r, ra } = gearShape(THREE, { m, z, bore });
  const g = new THREE.ExtrudeGeometry(shape, { depth: width, bevelEnabled: true, bevelSize: m * 0.06, bevelThickness: m * 0.06, bevelSegments: 1, curveSegments: 6 });
  g.translate(0, 0, -width / 2); g.computeVertexNormals();
  return { geo: g, r, ra };
}
