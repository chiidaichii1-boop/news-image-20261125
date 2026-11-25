#!/usr/bin/env python3
"""The World, 25 November 2026 -- one-image news summary.

Draws a newspaper front page (1024x1024 PNG) with the day's top world
news, using only the Python standard library. The PNG is encoded by hand
(zlib + struct) so the program is fully deterministic: two runs write
byte-identical files. No network, no randomness, no timestamps.
"""

import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. "." = off, "#" = on. Only uppercase + digits + punctuation.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "'": ("..#..", "..#..", "..#..", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
}

# ------------------------------------------------------------- canvas -----
W, H = 1024, 1024
PAPER = (247, 243, 234)
NAVY = (15, 42, 74)
GOLD = (201, 162, 39)
INK = (24, 24, 24)
GREY = (110, 110, 105)
LIGHT = (232, 226, 214)
SKY = (168, 205, 232)
SEA = (38, 98, 150)
DARKSEA = (24, 74, 118)
WHITE = (255, 255, 255)
RED = (176, 48, 38)
GREEN = (46, 125, 70)
ORANGE = (224, 122, 42)
YELLOW = (240, 196, 60)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                if xx * xx + yy * yy <= r * r:
                    self.set(cx + xx, cy + yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(-r - thick, r + thick + 1):
            for xx in range(-r - thick, r + thick + 1):
                d = (xx * xx + yy * yy) ** 0.5
                if r - thick <= d <= r:
                    self.set(cx + xx, cy + yy, color)

    def polygon(self, pts, color):
        """Scanline fill for a simple polygon."""
        if not pts:
            return
        ymin = min(p[1] for p in pts)
        ymax = max(p[1] for p in pts)
        n = len(pts)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                xa, xb = int(xs[j]), int(xs[j + 1])
                for x in range(xa, xb + 1):
                    self.set(x, y, color)


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, y, text, scale, color):
    w = text_width(text, scale)
    draw_text(cv, (W - w) // 2, y, text, scale, color)


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    words = text.upper().split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------- png writer -----
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ------------------------------------------------------ scene + icons ----
def draw_lead_scene(cv, x, y, w, h):
    """Sea battle: a warship on the water under a drone, sky above."""
    cv.rect(x, y, w, h, SKY)
    # sun + clouds
    cv.circle(x + w - 52, y + 46, 26, YELLOW)
    cv.circle(x + 70, y + 42, 20, WHITE)
    cv.circle(x + 96, y + 42, 26, WHITE)
    cv.circle(x + 122, y + 42, 18, WHITE)
    cv.circle(x + w - 150, y + 88, 16, WHITE)
    cv.circle(x + w - 128, y + 88, 20, WHITE)
    # drone (small quad-copter silhouette)
    dx, dy = x + w // 2 + 60, y + 52
    cv.rect(dx - 16, dy - 3, 32, 6, INK)
    cv.rect(dx - 3, dy - 12, 6, 24, INK)
    cv.circle(dx - 18, dy, 7, INK)
    cv.circle(dx + 18, dy, 7, INK)
    cv.circle(dx, dy, 5, RED)
    # sea
    sea_y = y + h - 130
    cv.rect(x, sea_y, w, 130, SEA)
    cv.rect(x, sea_y, w, 6, DARKSEA)
    for wx in range(x + 12, x + w - 12, 46):
        cv.line(wx, sea_y + 34, wx + 22, sea_y + 34, WHITE)
        cv.line(wx + 8, sea_y + 78, wx + 30, sea_y + 78, WHITE)
    # ship hull + superstructure
    hx, hy = x + 56, sea_y + 26
    cv.polygon([(hx, hy), (hx + 300, hy), (hx + 268, hy + 62),
                (hx + 30, hy + 62)], (52, 52, 52))
    cv.rect(hx + 96, hy - 34, 108, 34, (74, 74, 74))
    cv.rect(hx + 138, hy - 62, 8, 28, (74, 74, 74))
    cv.polygon([(hx + 146, hy - 62), (hx + 146, hy - 84), (hx + 178, hy - 70)],
               RED)
    for px in (hx + 110, hx + 130, hx + 150, hx + 170):
        cv.rect(px, hy - 24, 10, 12, SKY)
    # explosion starburst above the stern
    ex, ey = hx + 268, hy - 52
    for k in range(8):
        ang = k * 3.14159 / 4
        tx = int(ex + 44 * (1 if k % 2 == 0 else 0.55) * math.cos(ang))
        ty = int(ey + 44 * (1 if k % 2 == 0 else 0.55) * math.sin(ang))
        cv.polygon([(ex, ey), (tx, ty),
                    (int(ex + 14 * math.cos(ang + 0.5)),
                     int(ey + 14 * math.sin(ang + 0.5)))],
                   ORANGE if k % 2 == 0 else YELLOW)
    cv.circle(ex, ey, 12, YELLOW)
    # smoke
    cv.circle(hx + 40, hy - 44, 16, (200, 200, 196))
    cv.circle(hx + 58, hy - 62, 20, (210, 210, 206))
    cv.circle(hx + 82, hy - 76, 14, (220, 220, 216))


def draw_icon(cv, x, y, kind):
    """100x100 pictogram in a light box with a navy frame."""
    cv.rect(x, y, 100, 100, LIGHT)
    cv.rect(x, y, 100, 4, NAVY)
    cv.rect(x, y + 96, 100, 4, NAVY)
    cv.rect(x, y, 4, 100, NAVY)
    cv.rect(x + 96, y, 4, 100, NAVY)
    cx, cy = x + 50, y + 50
    if kind == "climate":
        cv.circle(cx, cy, 30, SEA)
        cv.polygon([(cx - 22, cy - 8), (cx - 4, cy - 22), (cx + 8, cy - 6),
                    (cx - 2, cy + 6), (cx - 18, cy + 10)], GREEN)
        cv.polygon([(cx + 6, cy + 12), (cx + 24, cy + 2), (cx + 26, cy + 18),
                    (cx + 12, cy + 26)], GREEN)
        cv.circle(cx + 34, cy - 34, 10, YELLOW)
    elif kind == "cyber":
        cv.polygon([(cx, cy - 30), (cx + 26, cy - 18), (cx + 26, cy + 6),
                    (cx, cy + 30), (cx - 26, cy + 6), (cx - 26, cy - 18)],
                   NAVY)
        cv.polygon([(cx, cy - 20), (cx + 17, cy - 12), (cx + 17, cy + 4),
                    (cx, cy + 20), (cx - 17, cy + 4), (cx - 17, cy - 12)],
                   GOLD)
        cv.circle(cx, cy - 4, 6, NAVY)
        cv.rect(cx - 3, cy, 6, 12, NAVY)
    elif kind == "chip":
        cv.rect(cx - 26, cy - 26, 52, 52, INK)
        cv.rect(cx - 16, cy - 16, 32, 32, GOLD)
        cv.rect(cx - 7, cy - 7, 14, 14, NAVY)
        for i in range(4):
            off = -18 + i * 12
            cv.rect(cx + off - 2, cy - 36, 4, 10, INK)
            cv.rect(cx + off - 2, cy + 26, 4, 10, INK)
            cv.rect(cx - 36, cy + off - 2, 10, 4, INK)
            cv.rect(cx + 26, cy + off - 2, 10, 4, INK)
    elif kind == "market":
        bars = [14, 22, 18, 30, 26, 40]
        for i, bh in enumerate(bars):
            bx = cx - 34 + i * 12
            cv.rect(bx, cy + 22 - bh, 8, bh, GREEN if i < 5 else GOLD)
        cv.line(cx - 36, cy - 30, cx + 34, cy - 26, RED)
        cv.polygon([(cx + 34, cy - 26), (cx + 22, cy - 30), (cx + 26, cy - 18)],
                   RED)
    elif kind == "quake":
        cv.polygon([(cx - 38, cy + 26), (cx - 8, cy - 28), (cx + 4, cy - 2),
                    (cx + 16, cy - 18), (cx + 40, cy + 26)], (96, 96, 96))
        cv.polygon([(cx - 8, cy - 28), (cx - 2, cy - 12), (cx - 14, cy - 10)],
                   WHITE)
        for yy, xx in ((cy + 30, cx - 30), (cy + 38, cx + 10)):
            cv.line(xx, yy, xx + 12, yy - 8, RED)
            cv.line(xx + 12, yy - 8, xx + 24, yy, RED)


# ------------------------------------------------------------ layout ------
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 112, NAVY)
    cv.rect(0, 112, W, 5, GOLD)
    draw_text_centered(cv, 16, "THE WORLD", 6, WHITE)
    draw_text_centered(cv, 78, "WEDNESDAY, 25 NOVEMBER 2026", 2, GOLD)
    # lead story
    draw_lead_scene(cv, 24, 132, 446, 300)
    tx = 494
    draw_text(cv, tx, 140, "UKRAINE WAR", 2, RED)
    lead_head = wrap_text("UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA", 486, 3)
    ly = 168
    for line in lead_head:
        draw_text(cv, tx, ly, line, 3, INK)
        ly += 26
    ly += 6
    lead_body = wrap_text(
        "KYIV CONFIRMS DRONE STRIKES ON RUSSIAN VESSELS IN THE GULF OF "
        "FINLAND AND OFF BENGHAZI. MOSCOW CALLS THE ATTACKS TERRORISM.",
        486, 2)
    for line in lead_body:
        draw_text(cv, tx, ly, line, 2, INK)
        ly += 19
    cv.hline(24, 448, 976, GOLD)
    cv.hline(24, 452, 976, GOLD)
    # story rows
    rows = [
        ("climate", "COP31 COLLAPSES WITHOUT A DEAL",
         "ANTALYA CLIMATE SUMMIT ENDS IN DEADLOCK AS OIL AND GAS PRODUCERS "
         "BLOCK FOSSIL-FUEL PHASEOUT."),
        ("cyber", "CIA HIT BY CYBERATTACK",
         "US SPY AGENCY'S CLASSIFIED SYSTEMS BREACHED, CNN REPORTS - THE "
         "LATEST IN A WAVE OF US HACKS."),
        ("chip", "HUAWEI GUILTY OF STEALING TRADE SECRETS",
         "US JURY CONVICTS CHINESE TELECOM GIANT ON 10 OF 12 COUNTS AFTER "
         "A THREE-MONTH TRIAL."),
        ("market", "NVIDIA SURGES 31% AS HUANG RETURNS",
         "CHIPMAKER REGAINS NEARLY $1 TRILLION IN VALUE IN A DAY AS ITS "
         "CO-FOUNDER RETAKES THE HELM."),
        ("quake", "5.6 QUAKE SHAKES NEPAL",
         "TREMOR STRIKES KOSHI PROVINCE NEAR THE CHINA BORDER; NO MAJOR "
         "DAMAGE REPORTED."),
    ]
    y = 468
    for kind, head, body in rows:
        draw_icon(cv, 24, y, kind)
        draw_text(cv, 144, y + 10, head, 2, INK)
        lines = wrap_text(body, 836, 2)
        by = y + 38
        for line in lines:
            draw_text(cv, 144, by, line, 2, GREY)
            by += 19
        y += 104
    draw_text_centered(cv, 996, "THE WORLD - 25 NOVEMBER 2026", 2, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = build()
    size = write_png(cv, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
