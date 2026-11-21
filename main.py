#!/usr/bin/env python3
"""Saturday 21 November 2026 - THE WORLD IN ONE DAY (make.fun news-image-20261121).

One-image summary of 21 November 2026 world news: 35 verified stories across
7 regions (3 features + 10 medium cards + 22 more), drawn entirely in code
below - a pure-stdlib PNG writer and a hand-built 5x7 bitmap font, no network,
no files read, deterministic: both runs write the same bytes.

News verified on the day (sources on the image): COP31 talks in overtime in
Antalya with no deal and no fossil-fuel language in the draft; three Houthi
missiles at Riyadh intercepted; a magnitude 6.7 quake in Peru; Bitcoin below
$56,000, its lowest since September 2024; Las Vegas qualifying - Antonelli
fastest, Verstappen inherits pole; Rahul 136 in Wellington. The red DATE
CHECK box lists what was left out as another day's news.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# --- palette: cream newspaper, black ink, red and blue accents ----------------
CREAM = (250, 246, 236)
PAPER = (244, 238, 224)
INK = (18, 18, 18)
GREY = (110, 108, 100)
RED = (176, 32, 32)
DARKRED = (140, 22, 22)
BLUE = (24, 58, 112)
STEEL = (58, 88, 128)
LIGHTBLUE = (208, 224, 238)
NAVY = (16, 26, 48)
SLATE = (42, 44, 50)
GREEN = (46, 120, 62)
GOLD = (212, 160, 32)
WHITE = (255, 255, 255)
EARTH = (48, 110, 178)
LAND = (74, 148, 74)

# --- pixel buffer -------------------------------------------------------------
BUF = bytearray(W * H * 3)


def _set(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            BUF[i] = c[0]
            BUF[i + 1] = c[1]
            BUF[i + 2] = c[2]


def rect_outline(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _set(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def polyline(points, c):
    for a, b in zip(points, points[1:]):
        line(a[0], a[1], b[0], b[1], c)


def circle(cx, cy, r, c, filled=True):
    if filled:
        for yy in range(cy - r, cy + r + 1):
            span = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - span, cx + span + 1):
                _set(xx, yy, c)
    else:
        steps = max(24, int(6.28 * r))
        for k in range(steps):
            a = 6.283185307 * k / steps
            _set(int(cx + r * _cos(a)), int(cy + r * _sin(a)), c)


def _cos(a):
    return _trig(a, True)


def _sin(a):
    return _trig(a, False)


def _trig(a, is_cos):
    # small Taylor-based trig, enough for circles and arcs (no math import
    # needed beyond what we already use, keeps the module list minimal)
    a = a % 6.283185307179586
    if is_cos:
        a = a + 1.5707963267948966
    x = a
    term = a
    total = a
    sign = -1.0
    for n in (3, 5, 7, 9, 11):
        term = term * a * a / (n * (n - 1))
        total += sign * term
        sign = -sign
    return total


def disc(cx, cy, r, c):
    circle(cx, cy, r, c, filled=True)


# --- PNG writer (stdlib only, deterministic) ----------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += BUF[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", comp)
        + _chunk(b"IEND", b"")
    )

# --- 5x7 bitmap font (hand-drawn glyphs, 7 rows of 5 pixels) -----------------
# Rows read top to bottom; '#' is ink, '.' is blank. Lowercase sits on the
# same 7-row cell (x-height rows 2-6, ascenders to row 0).
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
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
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".###.", "....#"),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".#.#.", "..#..", "..#.."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
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
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".....", ".##..", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".....", ".##..", ".....", ".##..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".###.", "#...#", "#...#", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", ".....", "..#..", ".###.", "..#..", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

# Characters that never appear in the copy are normalised to these.
NORMALISE = {
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00b7": ".", "\u2022": "*",
    "\u00d7": "x", "\u00b0": "o", "\u00e9": "e", "\u00fc": "u",
}


def clean_text(s):
    out = []
    for ch in s:
        ch = NORMALISE.get(ch, ch)
        out.append(ch if ch in FONT else "?")
    return "".join(out)


def text_w(s, scale):
    return len(clean_text(s)) * 6 * scale


def draw_text(x, y, s, scale, color):
    s = clean_text(s)
    cx = x
    for ch in s:
        rows = FONT[ch]
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == "#":
                    fill_rect(cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return cx - x


def draw_text_centered(cx, y, s, scale, color):
    w = text_w(s, scale)
    draw_text(cx - w // 2, y, s, scale, color)
    return w


def draw_text_right(rx, y, s, scale, color):
    w = text_w(s, scale)
    draw_text(rx - w, y, s, scale, color)
    return w


def wrap_lines(s, max_chars):
    words = clean_text(s).split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, max_chars, scale, color, leading=2):
    lines = wrap_lines(s, max_chars)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * (7 * scale + leading), ln, scale, color)
    return len(lines) * (7 * scale + leading)

# --- content: 35 verified stories, 7 regions ----------------------------------
# Region counts: Europe 8, Asia 4, Middle East 6, Africa 2, Americas 9,
# Oceania 3, Global 3 = 35.

FEATURES = [
    {
        "num": 1, "kicker": "CLIMATE - ANTALYA", "color": BLUE,
        "headline": ["COP31 IN OVERTIME:", "NO DEAL, NO FOSSIL FUELS"],
        "deck": ("Talks run past Friday's deadline; third draft due "
                 "Saturday. Text cut 144 to 80 paragraphs, no coal, "
                 "oil or gas. (AP)"),
        "art": "globe",
    },
    {
        "num": 2, "kicker": "MIDDLE EAST - RIYADH", "color": RED,
        "headline": ["FIVE MISSILES AT RIYADH", "SHOT DOWN"],
        "deck": ("Three Houthi missiles intercepted over Riyadh early "
                 "Saturday; two more at Jazan. No casualties. "
                 "(AP / AFP)"),
        "art": "missiles",
    },
    {
        "num": 3, "kicker": "PERU - JUNIN", "color": GREEN,
        "headline": ["MAG 6.7 QUAKE", "SHAKES PERU"],
        "deck": ("30 km NW of Junin, depth 108 km; felt in Lima. No "
                 "deaths; 34 houses damaged, rockfalls, outages. "
                 "(USGS)"),
        "art": "quake",
    },
]

MEDIUM = [
    ("UKRAINE", RED, ["ZELENSKY CRIMEA", "BRIDGE WILL NOT", "STAY"],
     "NBC interview; warns", "NBC"),
    ("IRAN / HORMUZ", RED, ["IRAN CLAIMS US", "DRONE DOWN OVER", "HORMUZ"],
     "IRGC claims MQ-9 down", "IRIB / ToI"),
    ("IRAN / NUCLEAR", BLUE, ["IRAN: URANIUM", "STOCK STAYS IN", "THE COUNTRY"],
     "Open to deal on 440.9kg", "IAEA"),
    ("USA / TECH", BLUE, ["TRUMP THREATENS", "'TREMENDOUS TAX'", "ON DATA CENTRES"],
     "Tax on US firms building abroad", "Reuters"),
    ("CHINA / JAPAN", RED, ["CHINA TO JAPAN:", "FIX 'ERRONEOUS", "WORDS AND DEEDS"],
     "Over Taiwan; Xi snubs Takaichi", "AP"),
    ("AIR NIUGINI", GREEN, ["146 SAFE AFTER", "ENGINE FIRE", "FORCES LANDING"],
     "Flight PX19 to Port Moresby", "dpa / ABC"),
    ("AUS / CHINA", BLUE, ["AUS AND CHINA", "AGREE AI TALKS"],
     "Xi-Albanese meet at APEC", "ABC"),
    ("CRYPTO", RED, ["BITCOIN BELOW", "$56,000, LOWEST", "SINCE SEPT 2024"],
     "Low $55,100; $2.4bn sold", "Reuters"),
    ("F1 / LAS VEGAS", BLUE, ["ANTONELLI FAST", "BUT VERSTAPPEN", "INHERITS POLE"],
     "1:33.893, then 5-place penalty", "F1 / FIA"),
    ("CRICKET", GREEN, ["RAHUL 136 INDIA", "BUILD LEAD IN", "WELLINGTON"],
     "Gill 98; India 486/4, lead 118", "ESPNcricinfo"),
]

# 22 more stories, two columns of 11, each one line.
ALSO = [
    "Kryvyi Rih: 2 killed, 42 hurt (Reuters)",
    "BepiColombo Mercury burn tonight (ESA)",
    "ATP semis today in Turin (ATP)",
    "Medvedev beat Tiafoe 6-3, 6-4 (ATP)",
    "Ferrari out in Q2: Leclerc 11th (F1)",
    "Pancreatic pill: 1 in 12 clear (Trial)",
    "Nigeria boat sinks, 4 dead (Police)",
    "Iraq enters Jurf al-Sakhar (Reuters)",
    "ANC worst vote since 1994 (IEC)",
    "Vance sidesteps on Iran strikes (Reuters)",
    "Coalition strikes Hodeidah port (UN)",
    "'35 by 35' stays in COP text (Reuters)",
    "Jakarta passes asset-seizure law (DPR)",
    "Texas execution takes 63 minutes (AP)",
    "Bayer $7.25bn Roundup deal approved (AP)",
    "Palisades fire starter convicted (AP)",
    "Takaichi snubbed at APEC (Asahi)",
    "128 nations back killer-robot rules (UN)",
    "Draft with no fossils angers islands (AP)",
    "India 486/4 at stumps, lead 118 (ESPN)",
    "FBI probes breach of crime database (FBI)",
    "Tankers hit by projectiles off Oman",
]

NUMBERS = [
    ("DAY 13", "COP31 TALKS"),
    ("5", "MISSILES DOWN"),
    ("6.7", "PERU QUAKE"),
    ("146", "DAVAO SAFE"),
    ("$55,100", "BITCOIN LOW"),
    ("136", "RAHUL RUNS"),
]

REGIONS_LINE = ("EUROPE 8 - ASIA 4 - MIDDLE EAST 6 - AFRICA 2 - "
                "AMERICAS 9 - OCEANIA 3 - GLOBAL 3 = 35 STORIES")

DATE_CHECK = ("LEFT OUT - ANOTHER DAY'S NEWS: Kyiv bridges, Poland missile, "
              "Cyclone Akvan, UK-EU deal, Wall St fall, ICJ Myanmar ruling, "
              "Virginia measles death (all Fri 20 Nov); Shenzhen summit, "
              "Anthropic +17%, GTA VI (Thu 19 Nov); Voyager 1 (18 Nov); "
              "Starc 7/58 (2025 Ashes).")

# Map: numbered dots for the 3 features + 10 medium stories (lon, lat).
MAP_DOTS = [
    (36.9, 30.7), (46.7, 24.7), (-75.2, -11.2), (34.0, 45.3),
    (56.5, 26.6), (51.4, 35.7), (-77.0, 38.9), (116.4, 39.9),
    (125.6, 7.1), (149.1, -35.3), (-74.0, 40.7), (-115.1, 36.2),
    (174.8, -41.3),
]

# Blocky continents as (lon0, lon1, lat0, lat1) rectangles.
CONTINENTS = [
    (-168, -95, 50, 71), (-125, -66, 25, 50), (-105, -80, 14, 26),
    (-90, -60, 45, 58), (-58, -20, 60, 84),
    (-80, -35, -55, 12), (-78, -45, -35, -8),
    (-10, 32, 36, 60), (5, 32, 55, 70), (-25, -12, 62, 67),
    (-18, 35, -2, 35), (8, 51, -35, 0), (32, 51, 0, 12),
    (32, 180, 45, 75), (42, 140, 28, 48), (68, 100, 8, 35),
    (95, 141, 5, 30), (128, 180, 38, 62), (95, 140, -10, 5),
    (113, 154, -40, -10),
]


# --- pictograms ----------------------------------------------------------------
def draw_globe(x, y, w, h):
    fill_rect(x, y, w, h, BLUE)
    cx, cy, r = x + 52, y + h // 2, 26
    disc(cx, cy, r, EARTH)
    disc(cx - 9, cy - 8, 7, LAND)
    disc(cx + 10, cy + 9, 6, LAND)
    disc(cx + 12, cy - 12, 4, LAND)
    # latitude arcs
    for dy, rr in ((-13, 22), (0, 26), (13, 22)):
        for k in range(-rr, rr + 1, 2):
            _set(cx + k, cy + dy, WHITE)
    for dx in (-13, 0, 13):
        for k in range(-20, 21, 2):
            _set(cx + dx, cy + k, WHITE)
    draw_text(x + 96, y + 12, "DAY 13", 3, WHITE)
    draw_text(x + 96, y + 38, "NO DEAL YET", 2, GOLD)


def draw_missiles(x, y, w, h):
    fill_rect(x, y, w, h, NAVY)
    # three incoming arcs, intercepted mid-sky
    for x0, x1, peak in ((x + 8, x + 150, y + 14), (x + 60, x + 190, y + 8),
                         (x + 110, x + 235, y + 18)):
        pts = []
        for t in range(0, 11):
            px = x0 + (x1 - x0) * t // 10
            py = y + h - 6 - (y + h - 6 - peak) * (2 * t * (10 - t)) // 100
            pts.append((px, py))
        polyline(pts, WHITE)
        disc(x1, pts[-1][1], 3, GOLD)
    # intercept starbursts
    for sx, sy in ((x + 150, y + 20), (x + 235, y + 24)):
        for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0), (-4, -4), (4, 4),
                       (-4, 4), (4, -4)):
            line(sx, sy, sx + dx, sy + dy, GOLD)
        disc(sx, sy, 2, GOLD)
    draw_text(x + 232, y + h - 18, "5 DOWN", 2, WHITE)


def draw_quake(x, y, w, h):
    fill_rect(x, y, w, h, SLATE)
    pts = []
    px = x + 8
    py = y + h // 2
    wave = [0, 2, -3, 8, -14, 20, -26, 18, -10, 5, -2, 1, 0, 0, 3, -6, 12,
            -18, 24, -16, 8, -4, 2, 0]
    for i, amp in enumerate(wave):
        pts.append((px + i * 9, py + amp))
    polyline(pts, WHITE)
    line(x + 8, py, x + 8 + 23 * 9, py, GREY)
    draw_text(x + 232, y + 16, "6.7", 4, GOLD)


def draw_art(kind, x, y, w, h):
    if kind == "globe":
        draw_globe(x, y, w, h)
    elif kind == "missiles":
        draw_missiles(x, y, w, h)
    else:
        draw_quake(x, y, w, h)


# --- world map ------------------------------------------------------------------
# Display nudges so clustered map dots do not sit on each other.
DOT_OFFSETS = {1: (-14, -10), 2: (2, 10), 3: (-2, 8), 4: (-16, 2),
               5: (14, -2), 6: (4, -12)}


def draw_map(x, y, w, h):
    fill_rect(x, y, w, h, LIGHTBLUE)
    rect_outline(x, y, w, h, STEEL, 1)
    lat0, lat1 = 85.0, -60.0

    def px(lon):
        return x + int((lon + 180.0) / 360.0 * w)

    def py(lat):
        return y + int((lat0 - lat) / (lat0 - lat1) * h)

    for lon0, lon1, la0, la1 in CONTINENTS:
        fill_rect(px(lon0), py(la1), px(lon1) - px(lon0), py(la0) - py(la1),
                  (96, 110, 122))
    for i, (lon, lat) in enumerate(MAP_DOTS, start=1):
        cx, cy = px(lon), py(lat)
        dx, dy = DOT_OFFSETS.get(i, (0, 0))
        cx += dx
        cy += dy
        disc(cx, cy, 9, RED)
        rect_outline(cx - 9, cy - 9, 18, 18, WHITE, 1)
        label = str(i)
        lw = text_w(label, 1)
        draw_text(cx - lw // 2, cy - 3, label, 1, WHITE)

# --- layout ----------------------------------------------------------------------
MX = 16          # left margin
RX = 1008        # right edge (1024 - 16)
CW = RX - MX     # 992 content width


def section_rule(y):
    hline(MX, y, CW, INK, 2)
    return y + 2


def draw_masthead(y):
    draw_text(MX, y, "THE WORLD IN ONE DAY", 4, INK)
    draw_text_right(RX, y + 6, "SATURDAY 21 NOVEMBER 2026", 2, INK)
    draw_text(MX, y + 30, "35 STORIES - 7 REGIONS - EVERY ONE DATED "
                           "SATURDAY 21 NOVEMBER 2026", 2, RED)
    return y + 46


def draw_date_headline(y):
    draw_text_centered(512, y, "SATURDAY 21 NOVEMBER 2026", 5, INK)
    return y + 35


def draw_subhead(y):
    draw_text_centered(512, y, "COP31 overtime - Riyadh missiles down - "
                               "Peru quake 6.7 - Bitcoin below $56,000",
                        2, INK)
    return y + 14


def draw_numbers_strip(y):
    col_w = CW // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = MX + i * col_w + col_w // 2
        draw_text_centered(cx, y, num, 3, RED if i % 2 == 0 else BLUE)
        draw_text_centered(cx, y + 24, label, 2, INK)
    draw_text_centered(512, y + 40,
                       "EUROPE 8 - ASIA 4 - MIDDLE EAST 6 - AFRICA 2 - "
                       "AMERICAS 9 - OCEANIA 3 - GLOBAL 3 = 35",
                       2, INK)
    return y + 54


def draw_features(y):
    col_w = 320
    gap = 16
    for i, feat in enumerate(FEATURES):
        x = MX + i * (col_w + gap)
        draw_art(feat["art"], x, y, col_w, 56)
        draw_text(x, y + 60, feat["kicker"], 2, feat["color"])
        hy = y + 78
        for j, hline_text in enumerate(feat["headline"]):
            draw_text(x, hy + j * 15, hline_text, 2, INK)
        dy = y + 112
        lines = wrap_lines(feat["deck"], 26)
        for j, ln in enumerate(lines):
            draw_text(x, dy + j * 15, ln, 2, INK)
    return y + 187


def draw_medium(y):
    card_w = 192
    gap = 8
    card_h = 120
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            kicker, color, headline, deck, source = MEDIUM[idx]
            x = MX + col * (card_w + gap)
            cy = y + row * (card_h + 4)
            fill_rect(x, cy, card_w, card_h, PAPER)
            rect_outline(x, cy, card_w, card_h, GREY, 1)
            fill_rect(x, cy, card_w, 5, color)
            draw_text(x + 6, cy + 9, kicker, 2, color)
            hy = cy + 27
            for j, hline_text in enumerate(headline):
                draw_text(x + 6, hy + j * 15, hline_text, 2, INK)
            dy = cy + 74
            lines = wrap_lines(deck, 15)
            for j, ln in enumerate(lines):
                draw_text(x + 6, dy + j * 15, ln, 2, INK)
            draw_text(x + 6, cy + 106, source, 2, GREY)
    return y + 2 * card_h + 4


def draw_map_section(y):
    draw_text(MX, y, "WHERE IT HAPPENED", 2, INK)
    draw_text_right(RX, y, "NUMBERS MATCH THE STORIES ABOVE", 2, GREY)
    draw_map(MX, y + 18, CW, 52)
    return y + 70


def draw_also(y):
    draw_text(MX, y, "ALSO ON SATURDAY 21 NOVEMBER 2026 - 22 MORE STORIES",
              2, RED)
    col_x = [MX, MX + CW // 2 + 12]
    for i, item in enumerate(ALSO):
        col = i // 11
        row = i % 11
        draw_text(col_x[col], y + 18 + row * 16, item, 2, INK)
    return y + 18 + 11 * 16


def draw_date_check(y):
    box_h = 66
    fill_rect(MX, y, CW, box_h, (255, 238, 238))
    rect_outline(MX, y, CW, box_h, RED, 2)
    draw_text(MX + 8, y + 5, "LEFT OUT - ANOTHER DAY'S NEWS", 2, RED)
    body = ("Kyiv bridges, Poland missile, Cyclone Akvan, UK-EU deal, "
            "Wall St fall, ICJ Myanmar ruling, Virginia measles death "
            "(Fri); Shenzhen summit, Anthropic +17%, GTA VI (Thu); "
            "Voyager 1 (18 Nov); Starc 7/58 (2025).")
    lines = wrap_lines(body, 80)
    for j, ln in enumerate(lines):
        draw_text(MX + 8, y + 22 + j * 14, ln, 2, INK)
    return y + box_h


def draw_footer(y):
    draw_text_centered(512, y, "Every story happened, or was first reported, "
                               "on Saturday 21 November 2026.",
                        2, INK)
    return y + 14


def build():
    fill_rect(0, 0, W, H, CREAM)
    y = 8
    y = draw_masthead(y)
    y = section_rule(y + 6)
    y = draw_date_headline(y + 6)
    y = draw_subhead(y + 4)
    y = section_rule(y + 2)
    y = draw_numbers_strip(y + 4)
    y = section_rule(y + 4)
    y = draw_features(y + 4)
    y = section_rule(y + 4)
    y = draw_medium(y + 4)
    y = section_rule(y + 4)
    y = draw_map_section(y + 4)
    y = section_rule(y + 2)
    y = draw_also(y + 2)
    y = draw_date_check(y + 4)
    y = draw_footer(y + 4)
    return y


def main():
    final_y = build()
    data = png_bytes()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes), final y=%d" % (path, len(data), final_y))
    if final_y > 1016:
        raise SystemExit("layout overflow: final y=%d" % final_y)
    if len(data) > 1048576:
        raise SystemExit("image over 1 MiB: %d bytes" % len(data))


if __name__ == "__main__":
    main()
