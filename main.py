#!/usr/bin/env python3
"""The World in One Day -- 26 November 2026.
Builds one 1024x1024 PNG newspaper front page from 26 Nov 2026 world news.
Python 3 stdlib only. No network. Deterministic: two runs write identical bytes.
Writes exactly one file: entry.png in $MAKEFUN_OUTPUT_DIR (default /output).
Stories were verified live from news sources on 26 Nov 2026 and hardcoded here.
"""

import hashlib
import math
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # warm newsprint
INK = (18, 18, 18)
NAVY = (27, 42, 74)
RED = (176, 32, 32)
GREEN = (0, 110, 60)
GRAY = (96, 92, 84)
FAINT = (198, 192, 178)   # card border
TINT = (238, 232, 218)    # alternate card fill
GOLD = (184, 146, 46)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = ink. Written by hand for this entry.
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
'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
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
}

FONT.update({
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
't': ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
'w': ("00000", "00000", "10001", "10001", "10101", "10101", "01010"),
'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
'.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
'!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
'?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
"'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
'"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
'-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
'/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
'(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
'%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
'$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
'+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
'=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
'&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
'@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
'#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
'*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
'_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
'>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
'<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
'[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
'\u2022': ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
'\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
})

BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            for xx in range(x0, x1):
                self.px(xx, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for yy in range(y0, y1):
                self.px(xx, yy, c)

    def rect_outline(self, x, y, w, h, c):
        self.hline(x, x + w, y, c)
        self.hline(x, x + w, y + h - 1, c)
        self.vline(x, y, y + h, c)
        self.vline(x + w - 1, y, y + h, c)

    def circle(self, cx, cy, r, c):
        # midpoint circle outline
        x = 0
        y = r
        d = 1 - r
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.px(cx + sx, cy + sy, c)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def ellipse(self, cx, cy, rx, ry, c):
        # parametric outline, deterministic
        steps = 720
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            self.px(x, y, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(round(math.sqrt(max(0, r * r - dy * dy))))
            for xx in range(cx - dx, cx + dx + 1):
                self.px(xx, cy + dy, c)


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            cv.px(cx + col * scale + dx, y + row * scale + dy, color)
        cx += 6 * scale


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def draw_text_centered_clamped(cv, cx, y, s, scale, color, lo=24, hi=1000):
    w = text_width(s, scale)
    x = cx - w // 2
    x = max(lo, min(x, hi - w))
    draw_text(cv, x, y, s, scale, color)


def wrap(s, maxw, scale):
    """Greedy word wrap to lines of pixel width <= maxw."""
    words = s.split(' ')
    lines = []
    cur = ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_width(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- PNG writer
def write_png(path, cv):
    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return png


# ---------------------------------------------------------------- content
# All stories verified live from news sources on 26 Nov 2026.
HERO = {
    "kicker": "ECONOMY \u2014 WASHINGTON, D.C.",
    "head": ["US HITS 14 PARTNERS", "WITH NEW TARIFFS"],
    "deck": ("Washington proposes country-specific tariffs of up to 35% on 14 "
             "partners, including China, the EU, Japan and India. India faces "
             "25%, the second-highest rate. Markets fell, then clawed most "
             "of it back."),
    "stats": [("14", "PARTNERS HIT"), ("35%", "MAX RATE"), ("25%", "INDIA RATE")],
}

SIDE = [
    {"kicker": "CONFLICT \u2014 RIYADH",
     "head": "HOUTHIS HIT SAUDI REFINERY",
     "deck": ("Yemen's Houthis claim strikes on Saudi ports and the Ras "
              "Tanura refinery; Riyadh says missiles were intercepted. "
              "Oil jumps.")},
    {"kicker": "DISASTER \u2014 CAIRO",
     "head": "CAIRO TANKER FIRE KILLS 31",
     "deck": ("A fuel tanker overturns and ignites on the ring road; at "
              "least 31 dead, about 21 hurt, the health ministry says.")},
    {"kicker": "MARKETS \u2014 NEW YORK",
     "head": "DOW TOPS 50,000 FIRST TIME",
     "deck": ("The Dow closes at 50,182.95, up 0.33%, as stocks claw back "
              "most of a steep morning sell-off.")},
]

# (UTC time, short label) -- times from first-report timestamps, 26 Nov 2026
TIMELINE = [
    ("01:00", "Luma power deal cancelled"),
    ("01:39", "Ukraine hits Savasleyka: 5 jets"),
    ("02:03", "Kim: widen nuke deployment"),
    ("05:14", "13 miners trapped in Bogor"),
    ("05:44", "EU leaders meet on loan"),
    ("06:29", "Trump, Rutte warn Russia"),
    ("08:29", "Ebola worsens in DR Congo"),
    ("10:06", "Bangkok depot fire"),
]

# (kicker, headline, deck)
GRID = [
    ("EUROPE \u2022 CONFLICT", "KYIV HITS RUSSIAN AIRBASE",
     "Kyiv says its strike on Savasleyka damaged three MiG-31s and two Su-34s."),
    ("EUROPE \u2022 POLITICS", "EU SPLIT OVER UKRAINE LOAN",
     "Leaders meet in Brussels over a 45-billion-euro loan and the 2028-34 budget."),
    ("EAST ASIA \u2022 DEFENCE", "KIM: WIDEN NUKE DEPLOYMENT",
     "North Korea should deploy tactical nuclear arms more widely, Kim says."),
    ("SE ASIA \u2022 DISASTER", "MINERS TRAPPED IN BOGOR",
     "Rescuers race to reach miners in a flooded gold mine south of Jakarta."),
    ("EAST ASIA \u2022 SPACE", "FIRST PAKISTANI IN ORBIT",
     "Muhammad Zeeshan Ali boards China's Tiangong station on Shenzhou-24."),
    ("MIDDLE EAST \u2022 CONFLICT", "ISRAEL KILLS HAMAS CHIEF",
     "A strike in Gaza kills Naeem Abu Nahel and six others, officials say."),
    ("MIDDLE EAST \u2022 DIPLOMACY", "US: CITIZENS LEAVE IRAN",
     "Washington warns Americans as fears of war with Iran grow."),
    ("EAST ASIA \u2022 DIPLOMACY", "PYONGYANG EXPELS ENVOY",
     "North Korea gives its top Swiss diplomat 48 hours to leave."),
    ("N. AFRICA \u2022 CONFLICT", "KYIV SINKS SHIP IN LIBYA",
     "Maritime drones hit a Russian warship in Benghazi; two Libyan officers die."),
    ("W. EUROPE \u2022 POLITICS", "SPAIN TO VOTE ON SUNDAY",
     "Snap election could end Pedro Sanchez's eight-year government."),
    ("W. EUROPE \u2022 TRANSPORT", "TUBE STRIKE HITS LONDON",
     "The Underground faces severe disruption on Thursday and Friday."),
    ("W. EUROPE \u2022 MIGRATION", "MIGRANTS REACH CANARIES",
     "Nearly 2,000 people arrive in the Canary Islands in a single day."),
    ("W. EUROPE \u2022 SPORT", "LIVERPOOL 3-0 BRUGGE",
     "Isak scores twice and Wirtz once in the Champions League."),
    ("CARIBBEAN \u2022 CULTURE", "BARRETO IS MISS UNIVERSE",
     "Puerto Rico's Jennifer Barreto is the first mother to win the crown."),
    ("N. AMERICA \u2022 TECH", "SPACEX: 1M SATELLITES",
     "The US authorises launches for orbital data centres."),
]

# (label, value, change, up?) -- Wed 25 Nov close, verified 26 Nov 2026
MARKETS = [
    ("S&P 500", "7,182.78", "-0.25%", False),
    ("NASDAQ", "23,585.80", "-0.62%", False),
    ("DOW", "50,182.95", "+0.33%", True),
    ("RUSSELL 2000", "2,704.06", "+0.70%", True),
    ("GOLD", "$3,589.18", "+0.92%", True),
    ("BRENT", "$94.61", "+3.5%", True),
    ("WTI", "$83.68", "+2.0%", True),
    ("BITCOIN", "$60,900", "+2.7%", True),
]

BRIEF = [
    "Bank of Korea raises rates amid an AI chip boom.",
    "DR Congo Ebola outbreak worsens as fighting disrupts the response.",
    "Bangkok oil depot fire forces evacuations.",
    "UK declares Rohingya genocide; sanctions five Myanmar generals.",
    "Finland gives $59m to Ukraine energy after grid strikes.",
    "New York jury convicts Huawei of stealing trade secrets.",
]


# ---------------------------------------------------------------- layout
MARGIN = 24
RIGHT = 1000


def draw_masthead(cv):
    cv.fill(0, 0, W, 88, NAVY)
    draw_text_centered(cv, W // 2, 14, "THE WORLD IN ONE DAY", 5, PAPER)
    draw_text_centered(cv, W // 2, 64, "THE DAY'S WORLD NEWS IN ONE IMAGE",
                       1, (200, 205, 220))
    cv.hline(0, W, 88, INK, 2)
    draw_text_centered(
        cv, W // 2, 99,
        "THURSDAY 26 NOVEMBER 2026  |  27 STORIES  |  10 REGIONS  |  "
        "14 FIELDS  |  ALL TIMES UTC", 1, INK)
    cv.hline(0, W, 116, INK, 2)


def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, NAVY)
    cv.circle(cx, cy, r - 1, NAVY)
    cv.ellipse(cx, cy, 28, r, NAVY)
    cv.ellipse(cx, cy, r, 28, NAVY)
    cv.hline(cx - r, cx + r, cy, NAVY)
    for dx, dy in ((-28, -24), (18, 12), (-6, 30)):
        cv.disc(cx + dx, cy + dy, 3, RED)


def draw_hero(cv):
    draw_text(cv, MARGIN, 128, HERO["kicker"], 1, RED)
    y = 146
    for line in HERO["head"]:
        draw_text(cv, MARGIN, y, line, 4, INK)
        y += 32
    lines = wrap(HERO["deck"], 576, 1)
    y = 212
    for line in lines:
        draw_text(cv, MARGIN, y, line, 1, INK)
        y += 9
    # stat boxes
    bx = MARGIN
    for num, lab in HERO["stats"]:
        cv.rect_outline(bx, 256, 180, 32, GRAY)
        draw_text_centered(cv, bx + 90, 260, num, 2, INK)
        draw_text_centered(cv, bx + 90, 277, lab, 1, GRAY)
        bx += 200
    # globe on the right
    draw_globe(cv, 840, 202, 66)
    draw_text_centered(cv, 840, 282, "TARIFFS REACH 14 PARTNERS", 1, GRAY)
    cv.hline(MARGIN, RIGHT, 292, INK)


def draw_side(cv):
    xs = [MARGIN, 353, 682]
    for x, item in zip(xs, SIDE):
        draw_text(cv, x, 306, item["kicker"], 1, RED)
        draw_text(cv, x, 320, item["head"], 2, INK)
        lines = wrap(item["deck"], 301, 1)[:3]
        y = 338
        for line in lines:
            draw_text(cv, x, y, line, 1, INK)
            y += 9
    cv.hline(MARGIN, RIGHT, 390, INK)


def draw_timeline(cv):
    draw_text(cv, MARGIN, 398, "THE DAY IN UTC", 1, RED)
    cv.hline(40, 984, 424, INK)
    centers = [40, 175, 310, 445, 579, 714, 849, 984]
    for (t, label), cx in zip(TIMELINE, centers):
        draw_text_centered_clamped(cv, cx, 406, t, 1, INK)
        cv.disc(cx, 424, 4, RED)
        lines = wrap(label, 120, 1)[:2]
        y = 432
        for line in lines:
            draw_text_centered_clamped(cv, cx, y, line, 1, INK)
            y += 9
    cv.hline(MARGIN, RIGHT, 460, INK)


def draw_grid(cv):
    draw_text(cv, MARGIN, 468, "THE DAY'S STORIES", 1, RED)
    note = "15 STORIES"
    draw_text(cv, RIGHT - text_width(note, 1), 468, note, 1, GRAY)
    for row in range(5):
        for col in range(3):
            idx = row * 3 + col
            kicker, head, deck = GRID[idx]
            x = MARGIN + col * (317 + 12)
            y = 486 + row * 80
            if idx % 2 == 0:
                cv.fill(x, y, 317, 80, TINT)
            cv.rect_outline(x, y, 317, 80, FAINT)
            draw_text(cv, x + 8, y + 6, kicker, 1, RED)
            hlines = wrap(head, 301, 2)[:2]
            hy = y + 18
            for line in hlines:
                draw_text(cv, x + 8, hy, line, 2, INK)
                hy += 15
            dlines = wrap(deck, 301, 1)[:2]
            dy = hy + 2
            for line in dlines:
                draw_text(cv, x + 8, dy, line, 1, INK)
                dy += 9
    cv.hline(MARGIN, RIGHT, 892, INK)


def draw_markets(cv):
    draw_text(cv, MARGIN, 896, "MARKETS \u2014 WED 25 NOV CLOSE", 1, RED)
    note = "US CLOSED THU \u2014 THANKSGIVING"
    draw_text(cv, RIGHT - text_width(note, 1), 896, note, 1, GRAY)
    for i, (name, val, chg, up) in enumerate(MARKETS):
        col = i % 4
        row = i // 4
        x = MARGIN + col * 244
        y = 912 + row * 14
        base = name + " " + val + " "
        draw_text(cv, x, y, base, 1, INK)
        draw_text(cv, x + text_width(base, 1), y, chg, 1,
                  GREEN if up else RED)
    cv.hline(MARGIN, RIGHT, 940, INK)


def draw_brief(cv):
    draw_text(cv, MARGIN, 948, "IN BRIEF", 1, RED)
    for i, item in enumerate(BRIEF):
        col = i // 3
        row = i % 3
        x = MARGIN + col * 488
        y = 964 + row * 12
        draw_text(cv, x, y, "\u2022 " + item, 1, INK)
    cv.hline(MARGIN, RIGHT, 1004, INK)
    draw_text_centered(
        cv, W // 2, 1010,
        "THE WORLD IN ONE DAY \u2022 26 NOVEMBER 2026 \u2022 STORIES VERIFIED "
        "FROM LIVE REPORTS", 1, GRAY)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_hero(cv)
    draw_side(cv)
    draw_timeline(cv)
    draw_grid(cv)
    draw_markets(cv)
    draw_brief(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = build()
    write_png(path, cv)
    data = open(path, "rb").read()
    print("wrote %s (%d bytes)" % (path, len(data)))
    print("sha256 %s" % hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
