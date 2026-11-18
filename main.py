"""News image for Tuesday 17 November 2026 (make.fun news-image-20261117).

Draws one 1024x1024 newspaper-style front page, stdlib only, and writes it
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

The day's stories, as reported on 17 Nov 2026:
  1. Ukraine strike collapses a road span of the Kerch Bridge to Crimea,
     the second day in a row; Russia hits two bridges in Kyiv in reply.
  2. Two tankers strike mines and catch fire off the Strait of Hormuz.
  3. Trump lands in Manila for ASEAN; Xi, Trump and Putin meet Thursday
     in Shenzhen.
  4. A ULA Vulcan rocket fails in flight; 40 Amazon Leo satellites lost.
Also: JPMorgan blames a software bug for its banking outage; Nvidia
reports after the close; Estonia moves to shut its Russia border.

The program is fully deterministic: same input, same bytes, every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 231)
INK = (17, 24, 39)
NAVY = (15, 42, 68)
NAVY_DARK = (10, 30, 50)
RED = (192, 57, 43)
GOLD = (255, 211, 77)
WHITE = (255, 255, 255)
SKY = (173, 216, 230)
SKY_PALE = (214, 235, 242)
SEA = (16, 78, 96)
SEA_DARK = (11, 60, 74)
GREY = (52, 58, 64)
GREY_LIGHT = (148, 163, 184)
ORANGE = (234, 88, 12)
YELLOW = (250, 204, 21)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells. '#' is on, '.' is off.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 cells per char)."""
    return len(text) * 6 * scale - scale


def wrap_lines(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.rect(x0, y + t, x1 - x0, 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.rect(x + t, y0, 1, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with a square brush."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = thick // 2
        while True:
            self.rect(x - half, y - half, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        if fill:
            for dy in range(-r, r + 1):
                dx = int((r * r - dy * dy) ** 0.5)
                self.hline(cx - dx, cx + dx + 1, cy + dy, color)
        else:
            import math
            steps = max(24, r * 4)
            prev = None
            for i in range(steps + 1):
                a = 2 * math.pi * i / steps
                p = (cx + int(r * math.cos(a)), cy + int(r * math.sin(a)))
                if prev is not None:
                    self.line(prev[0], prev[1], p[0], p[1], color, 2)
                prev = p

    def arc(self, cx, cy, r, a0_deg, a1_deg, color, thick=3):
        import math
        steps = 48
        prev = None
        for i in range(steps + 1):
            a = math.radians(a0_deg + (a1_deg - a0_deg) * i / steps)
            p = (cx + int(r * math.cos(a)), cy + int(r * math.sin(a)))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], color, thick)
            prev = p

    def polygon(self, points, color):
        """Scanline fill of a simple polygon."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(int(x0 + t * (x1 - x0)))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(xs[j], xs[j + 1] + 1, y, color)

    def triangle(self, p0, p1, p2, color):
        self.polygon([p0, p1, p2], color)

    def text(self, x, y, s, scale, color, bold=False):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for character: %r" % ch)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
                        if bold:
                            self.rect(cx + col * scale + 1, y + row * scale,
                                      scale, scale, color)
            cx += 6 * scale

    def text_center(self, cx, y, s, scale, color, bold=False):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color, bold)


# ---------------------------------------------------------------- scenes

def draw_bridge(cv, x0, y0, x1, y1):
    """Kerch Bridge: sky, sea, deck with a collapsed middle span, smoke."""
    # sky bands
    cv.rect(x0, y0, x1 - x0, 70, SKY_PALE)
    cv.rect(x0, y0 + 70, x1 - x0, 70, SKY)
    cv.rect(x0, y0 + 140, x1 - x0, y1 - y0 - 140 - 72, (120, 190, 210))
    # sun
    cv.circle(x1 - 90, y0 + 42, 26, GOLD)
    cv.circle(x1 - 90, y0 + 42, 18, (255, 224, 130))
    # sea
    sea_y = y1 - 72
    cv.rect(x0, sea_y, x1 - x0, 72, SEA)
    cv.rect(x0, sea_y, x1 - x0, 10, SEA_DARK)
    for wx in range(x0 + 30, x1 - 20, 90):
        cv.arc(wx, sea_y + 34, 22, 200, 340, WHITE, 3)
        cv.arc(wx + 45, sea_y + 56, 18, 200, 340, (190, 220, 230), 3)
    # pillars in the sea
    for px in (x0 + 110, x0 + 300, x1 - 320, x1 - 130):
        cv.rect(px, sea_y - 6, 18, 78, GREY)
    # deck: left span, gap, right span
    deck_y = sea_y - 16
    cv.rect(x0, deck_y, 460, 14, GREY)
    cv.rect(x0 + 524, deck_y, x1 - x0 - 524, 14, GREY)
    cv.rect(x0, deck_y + 14, 460, 4, (30, 34, 40))
    cv.rect(x0 + 524, deck_y + 14, x1 - x0 - 524, 4, (30, 34, 40))
    # arches over the intact spans
    cv.arc(x0 + 230, deck_y, 120, 180, 360, RED, 7)
    cv.arc(x1 - 262, deck_y, 120, 180, 360, RED, 7)
    # broken stubs leaning into the gap
    cv.line(x0 + 452, deck_y, x0 + 478, deck_y + 52, GREY, 8)
    cv.line(x0 + 532, deck_y, x0 + 506, deck_y + 52, GREY, 8)
    # collapsed span sinking in the gap
    cv.polygon([(x0 + 462, deck_y + 58), (x0 + 522, deck_y + 58),
                (x0 + 512, deck_y + 74), (x0 + 472, deck_y + 74)], GREY)
    # explosion + smoke over the gap
    cv.polygon([(512, 218), (524, 244), (550, 238), (534, 258),
                (546, 282), (520, 270), (506, 292), (500, 266),
                (476, 272), (492, 252), (474, 240), (498, 240)],
               ORANGE)
    cv.circle(512, 252, 16, YELLOW)
    cv.circle(478, 208, 20, GREY_LIGHT)
    cv.circle(512, 186, 26, (170, 180, 190))
    cv.circle(548, 206, 18, GREY_LIGHT)
    cv.circle(500, 168, 14, (190, 198, 206))


def draw_tanker(cv, x0, y0, x1, y1):
    """Tanker on fire at sea, a mine in the water."""
    cv.rect(x0, y0, x1 - x0, 44, SKY_PALE)
    cv.rect(x0, y0 + 44, x1 - x0, y1 - y0 - 44, SEA)
    cv.rect(x0, y0 + 44, x1 - x0, 8, SEA_DARK)
    # hull
    mid_y = y0 + 78
    cv.polygon([(x0 + 18, mid_y), (x0 + 292, mid_y),
                (x0 + 272, mid_y + 34), (x0 + 38, mid_y + 34)], (30, 34, 40))
    cv.rect(x0 + 18, mid_y, 274, 6, RED)
    # containers
    cv.rect(x0 + 40, mid_y - 26, 44, 26, RED)
    cv.rect(x0 + 88, mid_y - 26, 44, 26, GOLD)
    cv.rect(x0 + 136, mid_y - 26, 44, 26, (37, 99, 235))
    cv.rect(x0 + 184, mid_y - 26, 44, 26, (34, 139, 90))
    # fire on deck
    cv.triangle((x0 + 218, mid_y - 4), (x0 + 246, mid_y - 4),
                (x0 + 232, mid_y - 52), ORANGE)
    cv.triangle((x0 + 236, mid_y - 4), (x0 + 258, mid_y - 4),
                (x0 + 247, mid_y - 38), YELLOW)
    cv.triangle((x0 + 206, mid_y - 4), (x0 + 224, mid_y - 4),
                (x0 + 215, mid_y - 30), YELLOW)
    # smoke
    cv.circle(x0 + 232, mid_y - 62, 14, GREY_LIGHT)
    cv.circle(x0 + 250, mid_y - 78, 18, (170, 180, 190))
    cv.circle(x0 + 226, mid_y - 92, 12, GREY_LIGHT)
    # mine in the water, right
    mx, my = x1 - 42, y1 - 22
    cv.circle(mx, my, 11, INK)
    for dx, dy in ((-14, 0), (14, 0), (0, -14), (-10, -10), (10, -10)):
        cv.line(mx, my, mx + dx, my + dy, INK, 3)
    # waves
    for wx in range(x0 + 16, x1 - 10, 64):
        cv.arc(wx, y1 - 12, 16, 200, 340, WHITE, 3)


def draw_flags(cv, x0, y0, x1, y1):
    """Three flags on poles: USA, China, Russia."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, SKY_PALE)
    cv.rect(x0, y1 - 26, x1 - x0, 26, (34, 139, 90))
    cv.rect(x0, y1 - 26, x1 - x0, 4, (22, 101, 64))
    flags = [
        ("us", x0 + 22),
        ("cn", x0 + 118),
        ("ru", x0 + 214),
    ]
    for kind, fx in flags:
        cv.rect(fx + 38, y0 + 18, 4, 92, GREY)
        cv.circle(fx + 40, y0 + 16, 5, GOLD)
        fy = y0 + 22
        if kind == "us":
            for s in range(7):
                cv.rect(fx, fy + s * 8, 76, 8,
                        RED if s % 2 == 0 else WHITE)
            cv.rect(fx, fy, 32, 24, NAVY)
            for sx in (6, 16, 26):
                for sy in (6, 16):
                    cv.circle(fx + sx, fy + sy, 2, WHITE)
        elif kind == "cn":
            cv.rect(fx, fy, 76, 56, (222, 41, 16))
            cv.circle(fx + 16, fy + 16, 7, GOLD)
            for sx, sy in ((36, 10), (44, 18), (44, 28), (36, 34)):
                cv.circle(fx + sx, fy + sy, 3, GOLD)
        else:
            cv.rect(fx, fy, 76, 19, WHITE)
            cv.rect(fx, fy + 19, 76, 18, (37, 99, 235))
            cv.rect(fx, fy + 37, 76, 19, RED)


def draw_rocket(cv, x0, y0, x1, y1):
    """Vulcan rocket breaking up; satellites tumbling away."""
    cv.rect(x0, y0, x1 - x0, y1 - y0, NAVY_DARK)
    for sx, sy in ((24, 18), (70, 44), (130, 14), (200, 52), (260, 22),
                    (40, 90), (150, 80), (240, 100), (290, 60), (100, 110)):
        cv.circle(x0 + sx, y0 + sy, 2, WHITE)
    cx = (x0 + x1) // 2
    # falling satellite pieces
    cv.rect(x0 + 26, y0 + 46, 34, 12, GREY_LIGHT)
    cv.rect(x0 + 14, y0 + 49, 12, 6, (37, 99, 235))
    cv.rect(x1 - 62, y0 + 74, 34, 12, GREY_LIGHT)
    cv.rect(x1 - 28, y0 + 77, 12, 6, (37, 99, 235))
    # dashed orbit arc
    for i in range(0, 9):
        ax = x0 + 30 + i * 30
        ay = y0 + 118 - i * 4
        cv.circle(ax, ay, 2, GOLD)
    # rocket body, tilted, breaking
    cv.polygon([(cx - 12, y0 + 34), (cx + 12, y0 + 34),
                (cx + 12, y0 + 78), (cx - 12, y0 + 78)], WHITE)
    cv.triangle((cx - 12, y0 + 34), (cx + 12, y0 + 34),
                (cx, y0 + 14), RED)
    cv.rect(cx - 12, y0 + 56, 24, 6, RED)
    cv.polygon([(cx - 12, y0 + 78), (cx - 26, y0 + 96),
                (cx - 12, y0 + 92)], RED)
    cv.polygon([(cx + 12, y0 + 78), (cx + 26, y0 + 96),
                (cx + 12, y0 + 92)], RED)
    # second, broken piece falling away
    cv.polygon([(cx + 44, y0 + 66), (cx + 62, y0 + 74),
                (cx + 52, y0 + 92), (cx + 38, y0 + 84)], GREY_LIGHT)
    # flame and smoke
    cv.triangle((cx - 10, y0 + 96), (cx + 10, y0 + 96),
                (cx, y0 + 122), ORANGE)
    cv.triangle((cx - 5, y0 + 96), (cx + 5, y0 + 96),
                (cx, y0 + 112), YELLOW)
    cv.circle(cx - 22, y0 + 116, 10, GREY_LIGHT)
    cv.circle(cx + 24, y0 + 120, 12, (170, 180, 190))


# ---------------------------------------------------------------- build

def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead
    cv.rect(0, 0, W, 132, NAVY)
    cv.rect(0, 132, W, 5, GOLD)
    cv.text_center(W // 2, 14, "WORLD NEWS", 8, WHITE, bold=True)
    cv.text_center(W // 2, 82, "TUESDAY 17 NOVEMBER 2026", 4, GOLD, bold=True)
    cv.circle(178, 96, 5, GOLD)
    cv.circle(846, 96, 5, GOLD)

    # ---- hero: the Kerch Bridge
    cv.rect(16, 148, 992, 400, WHITE)
    cv.rect(16, 148, 992, 400, INK)  # border via outline below
    cv.rect(20, 152, 984, 392, WHITE)
    draw_bridge(cv, 20, 152, 1004, 392)
    cv.rect(20, 152, 216, 34, RED)
    cv.text(30, 161, "UKRAINE WAR", 3, WHITE, bold=True)
    cv.text_center(W // 2, 404, "KERCH BRIDGE FALLS", 7, INK, bold=True)
    cv.text_center(W // 2, 462, "UKRAINE STRIKE COLLAPSES ROAD SPAN", 4, INK)
    cv.text_center(W // 2, 498, "RUSSIA HITS TWO BRIDGES IN KYIV", 3, RED)

    # ---- three stories
    panels = [
        (16, "MIDDLE EAST", draw_tanker,
         ["TANKERS HIT", "BY MINES"],
         ["2 TANKERS CATCH", "FIRE OFF HORMUZ"]),
        (352, "ASIA DIPLOMACY", draw_flags,
         ["TRUMP LANDS", "IN MANILA"],
         ["XI, TRUMP, PUTIN", "THU IN SHENZHEN"]),
        (688, "SPACE", draw_rocket,
         ["VULCAN", "ROCKET FAILS"],
         ["40 AMAZON", "SATELLITES LOST"]),
    ]
    for px, kicker, scene, head_lines, sub_lines in panels:
        cv.rect(px, 564, 320, 320, WHITE)
        cv.rect(px, 564, 320, 3, INK)
        cv.rect(px, 564, 3, 320, INK)
        cv.rect(px + 317, 564, 3, 320, INK)
        cv.rect(px, 881, 320, 3, INK)
        scene(cv, px + 4, 568, px + 316, 700)
        cv.text_center(px + 160, 710, kicker, 3, RED, bold=True)
        y = 736
        for line in head_lines:
            cv.text_center(px + 160, y, line, 4, INK, bold=True)
            y += 30
        y = 800
        for line in sub_lines:
            cv.text_center(px + 160, y, line, 3, INK)
            y += 22

    # ---- footer ticker
    cv.rect(0, 900, W, 124, NAVY)
    cv.rect(0, 900, W, 4, GOLD)
    cv.text(24, 916, "ALSO TODAY", 3, GOLD, bold=True)
    cv.text(24, 944, "JPMORGAN BLAMES SOFTWARE BUG FOR OUTAGE", 3, WHITE)
    cv.text(24, 972, "NVIDIA REPORTS TODAY - ESTONIA SHUTS RUSSIA BORDER", 3, WHITE)

    return cv


# ---------------------------------------------------------------- png

def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * cv.w * 3
        raw += cv.px[start:start + cv.w * 3]
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        out += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", data)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build(), path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
