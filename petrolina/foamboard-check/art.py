"""Low-poly hero art for the Petrolina prize card.

Last year's card carried a low-poly Spartan helmet with a draped cape. This
year's equivalent is a low-poly racing helmet in Petrolina livery, resting on a
draped chequered flag.

Everything is generated: shapes are described as polygons/curves, sampled into
points, Delaunay-triangulated, and every facet is flat-shaded from a fake 3D
normal plus a little jitter. The seed is fixed, so the output is stable.

    art_svg() -> str   (an <svg> fragment in card coordinates, 1712 x 1080)
"""
import math
import random

RNG = random.Random(20260913)

BLUE = (0x00, 0x52, 0x9B)
BLUE_BRIGHT = (0x00, 0x9C, 0xDE)
BLUE_DEEP = (0x00, 0x30, 0x87)
WHITE = (0xF4, 0xF7, 0xFA)
SILVER = (0xC9, 0xD2, 0xDC)
NAVY = (0x0A, 0x16, 0x2B)
CARBON = (0x1A, 0x22, 0x30)
VISOR = (0x10, 0x24, 0x44)


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------

def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def shade(c, k):
    """k < 1 darkens, k > 1 lightens toward white."""
    if k <= 1:
        return tuple(max(0, v * k) for v in c)
    t = min(1.0, k - 1)
    return tuple(v + (255 - v) * t for v in c)


def hexc(c):
    return "#%02X%02X%02X" % tuple(int(max(0, min(255, round(v)))) for v in c)


def pip(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def curve_y(pts, x):
    """Piecewise-linear y(x) through pts sorted by x (clamped at the ends)."""
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return lerp(y0, y1, (x - x0) / (x1 - x0))
    return pts[-1][1]


def catmull(pts, closed=True, steps=8):
    """Smooth a control polygon into a dense polyline."""
    out = []
    n = len(pts)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def resample(line, spacing, closed=True):
    pts = list(line) + ([line[0]] if closed else [])
    out = [pts[0]]
    carry = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        d = spacing - carry
        while d <= seg:
            t = d / seg
            out.append((lerp(x0, x1, t), lerp(y0, y1, t)))
            d += spacing
        carry = seg - (d - spacing)
    if closed and math.hypot(out[-1][0] - out[0][0], out[-1][1] - out[0][1]) < spacing * 0.5:
        out.pop()
    return out


def delaunay(points):
    """Bowyer-Watson. Returns triangles as index triples."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    d = max(maxx - minx, maxy - miny) * 10
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    pts = list(points) + [(cx - d, cy - d), (cx + d, cy - d), (cx, cy + d)]
    n = len(points)
    tris = {(n, n + 1, n + 2): circum(pts, (n, n + 1, n + 2))}
    for i in range(n):
        px, py = pts[i]
        bad = [t for t, (ux, uy, r2) in tris.items() if (px - ux) ** 2 + (py - uy) ** 2 < r2]
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e))
                edges[k] = edges.get(k, 0) + 1
            del tris[t]
        for (a, b), cnt in edges.items():
            if cnt == 1:
                t = (a, b, i)
                c = circum(pts, t)
                if c:
                    tris[t] = c
    return [t for t in tris if max(t) < n]


def circum(pts, t):
    (ax, ay), (bx, by), (cx, cy) = pts[t[0]], pts[t[1]], pts[t[2]]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-9:
        return (0, 0, -1)
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy, (ax - ux) ** 2 + (ay - uy) ** 2)


def poisson(poly, min_d, tries=4000):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    out = []
    for _ in range(tries):
        x = RNG.uniform(min(xs), max(xs))
        y = RNG.uniform(min(ys), max(ys))
        if not pip(x, y, poly):
            continue
        if all((x - a) ** 2 + (y - b) ** 2 > min_d * min_d for a, b in out):
            out.append((x, y))
    return out


def poly_svg(pts, fill, extra=""):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return '<polygon points="%s" fill="%s"%s/>' % (d, fill, extra)


# --------------------------------------------------------------------------
# racing helmet (helmet-local units, facing left)
# --------------------------------------------------------------------------

SHELL = catmull([
    (170, 800), (112, 742), (80, 652), (88, 566), (134, 500), (150, 420),
    (200, 300), (300, 210), (430, 160), (570, 148), (700, 170), (810, 230),
    (890, 320), (935, 430), (940, 540), (915, 630), (870, 700), (800, 715),
    (620, 710), (470, 718), (380, 742), (280, 782),
], steps=7)

# visor lens: its own piece, standing slightly proud of the shell at the front
VISOR_POLY = catmull([
    (104, 522), (98, 430), (132, 344), (204, 292), (320, 270), (460, 268),
    (570, 284), (632, 328), (640, 398), (600, 444), (480, 470), (320, 500), (180, 526),
], steps=7)

PIVOT = [(726 + 30 * math.cos(a * math.pi / 5), 372 + 30 * math.sin(a * math.pi / 5)) for a in range(10)]

SPOILER = [(650, 158), (760, 150), (856, 186), (916, 244), (940, 290), (896, 284), (806, 228), (700, 184)]

NECK = catmull([
    (300, 772), (400, 726), (520, 700), (660, 694), (790, 696), (880, 670),
    (896, 694), (800, 728), (660, 726), (520, 734), (420, 756), (330, 796),
], steps=4)

# livery curves: y(x), left to right (the band kicks up toward the back)
TOP_1 = [(60, 566), (200, 552), (420, 534), (640, 510), (800, 486), (980, 450)]   # cyan pinstripe top
TOP_2 = [(60, 582), (200, 568), (420, 550), (640, 526), (800, 502), (980, 466)]   # blue band top
TOP_3 = [(60, 676), (200, 658), (420, 634), (640, 606), (800, 582), (980, 546)]   # blue band bottom
LOW_1 = [(60, 694), (200, 676), (420, 652), (640, 624), (800, 600), (980, 564)]   # cyan pinstripe bottom
CROWN = [(60, 300), (300, 222), (520, 196), (700, 208), (860, 270), (980, 340)]   # blue crown stripe
CROWN_2 = [(60, 332), (300, 254), (520, 228), (700, 240), (860, 302), (980, 372)]


def inset(poly, d):
    """Offset a closed polyline inward by d (poly is clockwise on screen)."""
    n = len(poly)
    out = []
    for i in range(n):
        ax, ay = poly[i - 1]
        bx, by = poly[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        m = math.hypot(tx, ty) or 1
        nx, ny = -ty / m, tx / m
        px, py = poly[i]
        if not pip(px + nx * d, py + ny * d, poly):
            nx, ny = -nx, -ny
        out.append((px + nx * d, py + ny * d))
    return out


SHELL_IN = inset(SHELL, 15)


def seg_dist(px, py, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - ax - dx * t, py - ay - dy * t))
    return best


def helmet_region(x, y):
    if pip(x, y, SPOILER):
        return "spoiler"
    if pip(x, y, VISOR_POLY):
        return "visor"
    if pip(x, y, NECK):
        return "neck"
    if not pip(x, y, SHELL):
        return None
    if not pip(x, y, SHELL_IN):
        return "rim"
    if curve_y(TOP_1, x) < y < curve_y(TOP_2, x) or curve_y(TOP_3, x) < y < curve_y(LOW_1, x):
        return "cyan"
    if curve_y(TOP_2, x) <= y <= curve_y(TOP_3, x):
        return "blue"
    if curve_y(CROWN, x) < y < curve_y(CROWN_2, x):
        return "blue"
    return "shell"


def livery_line(pts):
    return resample([(x, curve_y(pts, x)) for x in range(60, 981, 8)], 22, closed=False)


def helmet_polys():
    pts = []
    pts += [p for p in resample(SHELL, 24) if not pip(p[0], p[1], VISOR_POLY) and not pip(p[0], p[1], NECK)]
    pts += [p for p in resample(SHELL_IN, 30) if not pip(p[0], p[1], VISOR_POLY) and not pip(p[0], p[1], NECK)
            and seg_dist(p[0], p[1], NECK) > 12]
    pts += resample(VISOR_POLY, 22)
    pts += resample(NECK, 24)
    pts += resample(SPOILER + [SPOILER[0]], 20, closed=False)
    for c in (TOP_1, TOP_2, TOP_3, LOW_1, CROWN, CROWN_2):
        pts += [p for p in livery_line(c) if pip(p[0], p[1], SHELL_IN) and seg_dist(p[0], p[1], VISOR_POLY) > 10 and not pip(p[0], p[1], VISOR_POLY)]
    pts += [p for p in poisson(SHELL_IN, 50)
            if seg_dist(p[0], p[1], NECK) > 16 and seg_dist(p[0], p[1], VISOR_POLY) > 12]
    clean = []
    for p in pts:
        if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 81 for q in clean):
            clean.append(p)
    pts = clean

    center = (500, 460)
    radius = 500.0
    L = norm3((-0.55, -0.66, 0.52))

    out = []
    for t in delaunay(pts):
        a, b, c = (pts[i] for i in t)
        cx, cy = (a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3
        region = helmet_region(cx, cy)
        if region is None:
            continue
        nx = (cx - center[0]) / radius
        ny = (cy - center[1]) / radius
        nz = math.sqrt(max(0.05, 1 - nx * nx - ny * ny))
        n = norm3((nx + RNG.uniform(-0.26, 0.26), ny + RNG.uniform(-0.26, 0.26), nz))
        lit = max(0.0, dot3(n, L))
        if region == "shell":
            col = mix(mix((96, 108, 126), SILVER, min(1, lit * 1.3)), WHITE, max(0, lit - 0.5) * 2.0)
        elif region == "rim":
            # bright trim, like the gold edging on last year's helmet
            col = mix(shade(BLUE_BRIGHT, 0.75 + 0.4 * lit), (190, 236, 255), max(0, lit - 0.45) * 1.4)
        elif region == "visor":
            refl = max(0.0, 1 - math.hypot(cx - 280, cy - 350) / 250) * (0.45 + 0.55 * lit)
            col = mix(shade(VISOR, 0.5 + 0.7 * lit), (80, 196, 244), refl * 0.8)
        elif region in ("neck", "spoiler"):
            col = shade(CARBON, 0.55 + 1.0 * lit)
        elif region == "cyan":
            col = shade(BLUE_BRIGHT, 0.7 + 0.5 * lit)
        else:
            col = shade(BLUE, 0.62 + 0.62 * lit) if lit < 0.8 else shade(BLUE, 1 + (lit - 0.8) * 0.8)
        out.append(((a, b, c), col))

    # visor pivot: a faceted stud laid over the shell
    cx, cy = 726, 372
    for k in range(len(PIVOT)):
        p, q = PIVOT[k], PIVOT[(k + 1) % len(PIVOT)]
        ang = math.atan2((p[1] + q[1]) / 2 - cy, (p[0] + q[0]) / 2 - cx)
        lit = 0.5 + 0.5 * math.cos(ang - math.radians(225))
        out.append((((cx, cy), p, q), shade(SILVER, 0.55 + 0.6 * lit)))
    return out


def norm3(v):
    m = math.sqrt(sum(x * x for x in v))
    return tuple(x / m for x in v)


def dot3(a, b):
    return sum(x * y for x, y in zip(a, b))


# --------------------------------------------------------------------------
# chequered flag drape (card units)
# --------------------------------------------------------------------------

FLAG_UNDER_HELMET = [(760, 1200), (900, 1010), (1120, 890), (1400, 900), (1640, 960), (1900, 900)]
# no helmet: the flag takes the whole right side, sweeping up out of the corner
FLAG_SOLO = [(700, 1260), (860, 1010), (1080, 780), (1340, 620), (1600, 520), (1900, 470)]


def flag_polys(control=FLAG_UNDER_HELMET, w0=230, w1=330, nu=20):
    nv = 5
    sub = 2  # vertices per checker edge
    U, V = nu * sub, nv * sub

    path = catmull(control, closed=False, steps=40)
    lengths = [0.0]
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        lengths.append(lengths[-1] + math.hypot(x1 - x0, y1 - y0))

    def centre(u):
        target = u * lengths[-1]
        for k in range(1, len(lengths)):
            if lengths[k] >= target:
                t = (target - lengths[k - 1]) / ((lengths[k] - lengths[k - 1]) or 1)
                return (lerp(path[k - 1][0], path[k][0], t), lerp(path[k - 1][1], path[k][1], t))
        return path[-1]

    def width(u):
        return lerp(w0, w1, u)

    grid = {}
    for i in range(U + 1):
        u = i / U
        x0, y0 = centre(max(0, u - 0.002))
        x1, y1 = centre(min(1, u + 0.002))
        tx, ty = x1 - x0, y1 - y0
        m = math.hypot(tx, ty)
        nx, ny = -ty / m, tx / m
        w = width(u)
        cx, cy = centre(u)
        for j in range(V + 1):
            v = j / V - 0.5
            # ripple across the width so the folds read
            fold = 7 * math.sin(u * 11 + v * 2.4)
            jx = RNG.uniform(-2.5, 2.5) if 0 < j < V and 0 < i < U else 0
            jy = RNG.uniform(-2.5, 2.5) if 0 < j < V and 0 < i < U else 0
            grid[i, j] = (cx + nx * (v * w + fold) + jx, cy + ny * (v * w + fold) + jy)

    out = []
    for i in range(U):
        for j in range(V):
            u = (i + 0.5) / U
            dark = ((i // sub) + (j // sub)) % 2 == 0
            p00, p10, p01, p11 = grid[i, j], grid[i + 1, j], grid[i, j + 1], grid[i + 1, j + 1]
            tris = [(p00, p10, p11), (p00, p11, p01)] if (i + j) % 2 else [(p00, p10, p01), (p10, p11, p01)]
            wave = math.cos(u * math.pi * 3.0 + 0.9 + (j / V) * 1.1)
            for k, tri in enumerate(tris):
                lit = 0.78 + 0.26 * wave + RNG.uniform(-0.09, 0.09) + (0.05 if k else -0.03)
                if dark:
                    col = shade(NAVY, 0.7 + 0.9 * lit)
                else:
                    col = shade(mix((150, 165, 185), WHITE, min(1, lit)), 1 + max(0, lit - 1) * 0.4)
                out.append((tri, col))
    # blue hem along both long edges
    for edge_j, sign in ((0, -1), (V, 1)):
        for i in range(U):
            a, b = grid[i, edge_j], grid[i + 1, edge_j]
            u = (i + 0.5) / U
            h = lerp(10, 26, u)
            ox, oy = normal_of(grid, i, edge_j, sign, h)
            c = (a[0] + ox, a[1] + oy)
            d = (b[0] + ox, b[1] + oy)
            wave = math.cos(u * math.pi * 3.0 + 0.9)
            lit = 0.8 + 0.25 * wave + RNG.uniform(-0.08, 0.08)
            out.append(((a, b, d), shade(BLUE_BRIGHT, lit)))
            out.append(((a, d, c), shade(BLUE_BRIGHT, lit * 0.9)))
    return out


def normal_of(grid, i, j, sign, h):
    a, b = grid[i, j], grid[i + 1, j]
    tx, ty = b[0] - a[0], b[1] - a[1]
    m = math.hypot(tx, ty) or 1
    inner = grid[i, j + (1 if j == 0 else -1)]
    nx, ny = -ty / m, tx / m
    # point away from the flag body
    if (inner[0] - a[0]) * nx + (inner[1] - a[1]) * ny > 0:
        nx, ny = -nx, -ny
    return nx * h, ny * h


# --------------------------------------------------------------------------
# compose
# --------------------------------------------------------------------------

HELMET_SCALE = 0.9
HELMET_OFFSET = (812, 84)


HELMET_LEAN = math.radians(-4)  # nose down, like it's tucked in on a straight


def to_card(p):
    x, y = p[0] - 500, p[1] - 480
    c, s = math.cos(HELMET_LEAN), math.sin(HELMET_LEAN)
    x, y = x * c - y * s, x * s + y * c
    return (HELMET_OFFSET[0] + (x + 500) * HELMET_SCALE, HELMET_OFFSET[1] + (y + 480) * HELMET_SCALE)


def art_svg(helmet=True):
    RNG.seed(20260913)  # every variant is stable build to build
    parts = []

    stroke = ' stroke="%s" stroke-width="0.6" stroke-linejoin="round"'
    flag = flag_polys() if helmet else flag_polys(FLAG_SOLO, 300, 430, nu=18)
    for tri, col in flag:
        parts.append(poly_svg(tri, hexc(col), stroke % hexc(col)))

    if helmet:
        # contact shadow where the helmet sits on the flag
        parts.append('<ellipse cx="1300" cy="790" rx="330" ry="46" fill="#000A1E" opacity="0.55" filter="url(#soft)"/>')
        for tri, col in helmet_polys():
            parts.append(poly_svg([to_card(p) for p in tri], hexc(col), stroke % hexc(col)))

    return (
        '<svg class="art" viewBox="0 0 1712 1080" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<defs><filter id="soft" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="28"/></filter></defs>'
        + "".join(parts) + "</svg>"
    )


# --------------------------------------------------------------------------
# guilloche security pattern for the cheque
# --------------------------------------------------------------------------

def _path(pts, closed=False):
    d = "M" + " L".join("%.1f %.1f" % p for p in pts)
    return d + (" Z" if closed else "")


def guilloche_rosette(cx, cy, r_in, r_out, lobes=18, rings=14, rot_step=4.0):
    """Nested wavy rings: the rosette you find on banknotes and cheques."""
    paths = []
    for k in range(rings):
        t = k / max(1, rings - 1)
        base = lerp(r_in, r_out, t)
        amp = lerp(r_out * 0.05, r_out * 0.11, math.sin(t * math.pi))
        phase = math.radians(k * rot_step)
        pts = []
        for i in range(720):
            a = i / 720 * 2 * math.pi
            r = base + amp * math.sin(lobes * a + phase) + amp * 0.35 * math.sin((lobes * 2 + 1) * a - phase)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        paths.append(_path(pts, closed=True))
    return paths


def guilloche_band(x0, x1, y, height, lines=16, waves=9.0):
    """Interlaced sine ribbons running across the document."""
    paths = []
    for k in range(lines):
        phase = k / lines * 2 * math.pi
        pts = []
        steps = int((x1 - x0) / 4)
        for i in range(steps + 1):
            u = i / steps
            x = lerp(x0, x1, u)
            yy = (y + height / 2 * math.sin(u * waves * 2 * math.pi + phase)
                  * (0.55 + 0.45 * math.sin(u * math.pi * 3 + phase / 2)))
            pts.append((x, yy))
        paths.append(_path(pts))
    return paths


def guilloche_svg(width, height):
    band = guilloche_band(-20, width + 20, height * 0.80, 150, lines=18, waves=11)
    rose = guilloche_rosette(width * 0.52, height * 0.60, 140, 290, lobes=22, rings=16)
    rose_small = guilloche_rosette(width * 0.52, height * 0.60, 36, 118, lobes=12, rings=8, rot_step=9)
    return (
        '<svg class="guilloche" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' % (width, height)
        + '<g fill="none" stroke="#009CDE" stroke-width="1.3" opacity="0.30">'
        + "".join('<path d="%s"/>' % d for d in band) + "</g>"
        + '<g fill="none" stroke="#00529B" stroke-width="1.2" opacity="0.12">'
        + "".join('<path d="%s"/>' % d for d in rose + rose_small) + "</g>"
        + "</svg>"
    )


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "_art_preview.html"), "w", encoding="utf-8") as f:
        f.write('<body style="margin:0;background:#00529B">' + art_svg() + "</body>")
    print("wrote _art_preview.html")
