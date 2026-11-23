#!/usr/bin/env python3
"""One Day, One World — Monday 23 November 2026.

Pure-stdlib Python 3 program. Draws a newspaper front page summing up
23 November 2026's world news and writes it to /output/entry.png
(1024x1024 PNG, deterministic: two runs are byte-identical).

No network, no third-party libraries, no external files. Text is rendered
with an embedded 5x7 bitmap font scaled up; the image is encoded with a
hand-rolled PNG writer (zlib, stdlib only).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (20, 20, 20)
RED = (178, 34, 24)
RED_DK = (140, 22, 16)
NAVY = (18, 53, 91)
TEAL = (18, 88, 107)
TEAL_DK = (10, 60, 76)
SAND = (217, 196, 143)
SAND_DK = (190, 164, 105)
GOLD = (201, 162, 39)
GREY = (90, 86, 76)
WHITE = (255, 255, 255)
CREAM = (252, 248, 238)
SKY = (214, 228, 232)
ORANGE = (214, 106, 24)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '#' = on, '.' = off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    'q': ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2013': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '\u2022': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
    '\u00d7': ("00000", "10001", "01010", "00100", "01010", "10001", "00000"),
}
BLANK = ("00000",) * 7


def glyph(ch):
    return FONT.get(ch, BLANK)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def disc_outline(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        n = max(dx, dy, 1)
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i // n
            y = y0 + (y1 - y0) * i // n
            self.rect(x - t // 2, y - t // 2, t, t, c)

    def poly(self, pts, c):
        # scanline fill
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def draw_text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = glyph(ch)
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, y, s, scale, c, cx=512):
        w = text_width(s, scale)
        self.draw_text(cx - w // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines."""
        words = s.split(' ')
        lines, cur = [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, s, scale, c, max_w, leading=None):
        lh = leading if leading is not None else 9 * scale
        for i, ln in enumerate(self.wrap(s, scale, max_w)):
            self.draw_text(x, y + i * lh, ln, scale, c)
        return y + len(self.wrap(s, scale, max_w)) * lh


# ---------------------------------------------------------------- PNG writer
def write_png(path, cv):
    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)

    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


# ---------------------------------------------------------------- hero scene
def draw_strait(cv, x, y, w, h):
    """Stylised map of the Strait of Hormuz: Iran above, Oman below,
    a tanker in the channel, dashed shipping lane, alert burst."""
    cv.rect(x, y, w, h, TEAL)
    # lighter sea bands
    for i in range(0, h, 14):
        cv.rect(x, y + i, w, 3, (24, 102, 122))
    # Iran landmass (top)
    cv.poly([(x, y), (x + w, y), (x + w, y + 58), (x + int(w * 0.72), y + 96),
             (x + int(w * 0.55), y + 78), (x + int(w * 0.38), y + 104),
             (x + int(w * 0.20), y + 82), (x, y + 92)], SAND)
    # Oman / UAE landmass (bottom)
    cv.poly([(x, y + h), (x + w, y + h), (x + w, y + h - 62),
             (x + int(w * 0.78), y + h - 96), (x + int(w * 0.60), y + h - 70),
             (x + int(w * 0.42), y + h - 104), (x + int(w * 0.24), y + h - 74),
             (x, y + h - 88)], SAND_DK)
    # labels
    cv.draw_text(x + 24, y + 16, "IRAN", 3, NAVY)
    cv.draw_text(x + w - 150, y + h - 66, "OMAN", 3, (60, 42, 10))
    cv.draw_text(x + w - 300, y + h - 66, "U.A.E.", 3, (60, 42, 10))
    # dashed shipping lane through the strait
    lx, ly = x + 30, y + h - 60
    rx, ry = x + w - 30, y + 70
    steps = 26
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 0.55) / steps
        cv.line(int(lx + (rx - lx) * t0), int(ly + (ry - ly) * t0),
                int(lx + (rx - lx) * t1), int(ly + (ry - ly) * t1),
                WHITE, 3)
    # tanker silhouette mid-channel
    tx, ty = x + int(w * 0.44), y + int(h * 0.52)
    cv.rect(tx, ty, 190, 26, INK)                    # hull
    cv.poly([(tx + 190, ty), (tx + 214, ty + 12), (tx + 190, ty + 26)], INK)
    cv.rect(tx + 30, ty - 22, 46, 22, INK)           # bridge block
    cv.rect(tx + 96, ty - 14, 60, 14, INK)           # deck house
    cv.rect(tx + 160, ty - 30, 10, 30, RED)          # funnel
    cv.rect(tx + 8, ty + 26, 182, 6, RED_DK)         # waterline stripe
    # second smaller tanker, far side
    tx2, ty2 = x + int(w * 0.70), y + int(h * 0.30)
    cv.rect(tx2, ty2, 110, 16, (30, 30, 30))
    cv.poly([(tx2 + 110, ty2), (tx2 + 124, ty2 + 8), (tx2 + 110, ty2 + 16)],
            (30, 30, 30))
    cv.rect(tx2 + 18, ty2 - 12, 26, 12, (30, 30, 30))
    cv.rect(tx2 + 84, ty2 - 16, 7, 16, RED)
    # alert burst where tankers were hit (just behind the lead tanker)
    bx, by = x + int(w * 0.62), y + int(h * 0.58)
    for r, col in ((46, RED), (34, ORANGE), (22, GOLD)):
        pts = []
        import math
        for k in range(16):
            ang = math.pi * k / 8
            rr = r if k % 2 == 0 else r * 0.55
            pts.append((int(bx + rr * math.cos(ang)),
                        int(by + rr * math.sin(ang))))
        cv.poly(pts, col)
    cv.circle(bx, by, 10, WHITE)
    cv.draw_text(bx - 8, by - 4, "!", 2, RED)
    cv.draw_text(bx - 140, by - 72, "TANKERS HIT", 3, WHITE)
    # compass rose
    cx0, cy0 = x + w - 64, y + 52
    cv.disc_outline(cx0, cy0, 26, WHITE, 2)
    cv.line(cx0, cy0 - 24, cx0, cy0 + 24, WHITE, 2)
    cv.line(cx0 - 24, cy0, cx0 + 24, cy0, WHITE, 2)
    cv.poly([(cx0, cy0 - 24), (cx0 - 6, cy0), (cx0 + 6, cy0)], RED)
    cv.draw_text(cx0 - 6, cy0 - 44, "N", 2, WHITE)
    # caption strip
    cv.rect(x, y + h - 34, w, 34, NAVY)
    cv.draw_text(x + 16, y + h - 26,
                 "THE STRAIT OF HORMUZ: THE WORLD'S OIL CHOKEPOINT",
                 2, WHITE)


# ---------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    M = 30
    CW = W - 2 * M  # 964

    # paper edge
    cv.rect(0, 0, W, 10, NAVY)
    cv.hline(M, 22, CW, INK, 2)

    # ---- masthead
    cv.text_center(30, "THE WORLD IN ONE PAGE", 7, INK)
    cv.hline(M, 96, CW, INK, 3)
    cv.draw_text(M, 106, "ONE DAY. ONE WORLD. ONE PAGE.", 2, GREY)
    right = "No. 327  |  PRICE: ONE DAY'S NEWS"
    cv.draw_text(W - M - text_width(right, 2), 106, right, 2, GREY)

    # ---- date bar
    cv.rect(M, 132, CW, 52, RED)
    cv.text_center(142, "MONDAY 23 NOVEMBER 2026", 6, WHITE)
    cv.hline(M, 192, CW, INK, 2)

    # ---- hero illustration
    draw_strait(cv, M, 202, CW, 230)

    # ---- hero kicker + headline
    cv.draw_text(M, 444, "MIDDLE EAST  -  WAR WARNING", 3, RED)
    cv.draw_text(M, 470, "HORMUZ ON EDGE", 9, INK)
    cv.draw_text(M, 545, "TRUMP: NEW STRIKES AFTER JAN 1", 5, INK)
    cv.hline(M, 592, CW, INK, 2)

    # ---- hero deck
    deck = ("Two oil tankers are hit in the Strait of Hormuz. "
            "Iran says it downed two US drones and struck Patriot radars "
            "in Bahrain. Trump warns of fresh strikes after Jan 1.")
    cv.paragraph(M, 602, deck, 3, INK, CW, leading=28)

    # ---- rule before grid
    cv.hline(M, 722, CW, INK, 3)

    # ---- secondary stories, 2 x 2 grid
    stories = [
        ("CLIMATE", RED, "COP31 COLLAPSES",
         "Antalya talks end with no deal. The pact never even names "
         "fossil fuels."),
        ("SPORT", NAVY, "INDIA 720/9 IN WELLINGTON",
         "Pant 128, Rahul 136 in a record total. New Zealand 119/2 "
         "at stumps."),
        ("SOUTH ASIA", RED, "MODI MEETS NEPAL'S SHAH",
         "Nepal PM Balendra Shah meets Modi in Delhi: energy, rail "
         "and hydropower."),
        ("ASIA", NAVY, "BANTEN FACTORY FIRE",
         "24 body bags found at the Banten factory; dozens of workers "
         "still missing."),
    ]
    col_w = (CW - 20) // 2
    cell_h = 100
    for idx, (kick, kcol, head, body) in enumerate(stories):
        col = idx % 2
        row = idx // 2
        x = M + col * (col_w + 20)
        y = 736 + row * (cell_h + 8)
        cv.draw_text(x, y, kick, 2, kcol)
        cv.draw_text(x, y + 18, head, 3, INK)
        cv.paragraph(x, y + 48, body, 2, INK, col_w, leading=18)
        if col == 0:
            cv.vline(x + col_w + 10, y, cell_h - 6, GREY, 1)

    # ---- also-today ticker (two lines)
    ty = 948
    cv.rect(M, ty, CW, 48, NAVY)
    cv.draw_text(M + 12, ty + 7,
                 "ALSO TODAY: 'El Chapo Isidro' captured  \u2022  UN talks "
                 "on lethal AI go on", 2, WHITE)
    cv.draw_text(M + 12, ty + 27,
                 "Russian cargo ship burns off Finland  \u2022  14 missing "
                 "after drone hit near Kyiv", 2, WHITE)

    # ---- footer
    cv.hline(M, 1004, CW, INK, 1)
    cv.draw_text(M, 1008, "Illustrated front page. All stories reported 23 November 2026.",
                 2, GREY)
    return cv


def main():
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    # clear only the contents of /output, never the directory itself
    for name in os.listdir(out_dir):
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            os.remove(p)
    cv = build()
    write_png(os.path.join(out_dir, "entry.png"), cv)
    print("wrote /output/entry.png", W, "x", H)


if __name__ == "__main__":
    main()
