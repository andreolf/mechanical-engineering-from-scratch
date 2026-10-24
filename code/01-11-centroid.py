"""Area and centroid of any simple polygon by the shoelace formula."""
import math


def polygon_centroid(pts):
    A = cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        A += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    A *= 0.5
    if abs(A) < 1e-15:
        raise ValueError("degenerate polygon")
    return A, cx / (6 * A), cy / (6 * A)   # a clockwise outline gives negative A, same centroid


def semicircle(r, n):
    return [(r * math.cos(math.pi * k / n), r * math.sin(math.pi * k / n)) for k in range(n + 1)]


if __name__ == "__main__":
    r = 1.0
    for n in (16, 256, 4096):
        A, x, y = polygon_centroid(semicircle(r, n))
        print(f"n={n:5d}: area {A:.6f}, y_c {y:.6f}  (4r/3pi = {4 * r / (3 * math.pi):.6f})")
    assert abs(y - 4 * r / (3 * math.pi)) < 1e-6 and abs(x) < 1e-12   # the lesson's test

    T = [(40, 0), (60, 0), (60, 80), (100, 80), (100, 100), (0, 100), (0, 80), (40, 80)]
    A, x, y = polygon_centroid(T)
    assert abs(A - 3600) < 1e-9 and abs(x - 50) < 1e-9 and abs(y - 67.7778) < 1e-4
    print(f"T-section: area {A:.0f} mm^2, centroid y = {y:.2f} mm")
