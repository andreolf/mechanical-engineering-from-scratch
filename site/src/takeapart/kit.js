// Small helpers shared by the take-apart models: meshes, groups, annular rings and a ball bearing.
import * as THREE from 'three';
export const V = (x, y, z) => new THREE.Vector3(x, y, z);
export const mesh = (geo, mat, x = 0, y = 0, z = 0) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); return m; };
export const grp = (x = 0, y = 0, z = 0, ...kids) => { const g = new THREE.Group(); g.position.set(x, y, z); kids.forEach((k) => g.add(k)); return g; };
// annulus extruded along z (inner radius a, outer b, width w), centred on z = 0
export function ringGeo(a, b, w, seg = 48) {
  const g = new THREE.LatheGeometry([new THREE.Vector2(a, -w / 2), new THREE.Vector2(b, -w / 2), new THREE.Vector2(b, w / 2), new THREE.Vector2(a, w / 2), new THREE.Vector2(a, -w / 2)], seg);
  g.rotateX(Math.PI / 2); return g;
}
// cylinder along z
export const cylZ = (r, len, seg = 32, r2 = r) => { const g = new THREE.CylinderGeometry(r2, r, len, seg); g.rotateX(Math.PI / 2); return g; };
// deep-groove ball bearing on a bore of radius a: outer ring, inner ring, balls and a cage
export function bearing(M, a, w) {
  const t = Math.max(0.03, a * 0.32), b = a + t * 2.6, pitch = (a + b) / 2, rb = t * 0.62;
  const g = new THREE.Group();
  g.add(mesh(ringGeo(b - t, b, w), M.metal), mesh(ringGeo(a, a + t, w), M.metal), mesh(ringGeo(pitch - rb * 0.25, pitch + rb * 0.25, w * 0.4), M.brass));
  const n = Math.max(7, Math.round((2 * Math.PI * pitch) / (rb * 2.6))); const ball = new THREE.SphereGeometry(rb, 14, 10);
  for (let k = 0; k < n; k++) { const ang = (k / n) * Math.PI * 2; g.add(mesh(ball, M.steel, Math.cos(ang) * pitch, Math.sin(ang) * pitch, 0)); }
  g.userData.outer = b; return g;
}
// hex bolt along +y with a washer
export function bolt(M, d, len) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.CylinderGeometry(d * 0.85, d * 0.85, d * 0.7, 6), M.steel, 0, d * 0.35, 0), mesh(new THREE.CylinderGeometry(d * 1.05, d * 1.05, d * 0.12, 24), M.metal, 0, -0.0, 0), mesh(new THREE.CylinderGeometry(d * 0.5, d * 0.5, len, 12), M.metal, 0, -len / 2, 0));
  return g;
}
