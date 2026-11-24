#!/usr/bin/env python3
"""Render entry.png: one image summing up the world news of Tuesday 24 Nov 2026.

Deterministic: PIL + DejaVu only. No network, no randomness, no timestamps.
Run:  python3 render.py   (writes entry.png next to this file)
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# ---- palette ----
BG = (247, 243, 234)        # warm newsprint
NAVY = (14, 42, 71)         # deep navy
GOLD = (232, 184, 75)       # gold
WHITE = (255, 255, 255)
INK = (51, 51, 51)          # body dark grey
MUTED = (68, 68, 68)
LIGHT_GREY = (200, 200, 200)
CHARCOAL = (34, 34, 34)
LIGHT_FOOT = (210, 210, 210)
MAP_BG = (220, 230, 238)    # light blue-grey
RED = (176, 58, 46)
GREEN = (30, 123, 52)
GREY_CHIP = (120, 120, 120)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def trunc(text, fnt, max_w):
    """Truncate to one line with an ellipsis if needed."""
    if fnt.getlength(text) <= max_w:
        return text
    while text and fnt.getlength(text + "…") > max_w:
        text = text[:-1]
    return text + "…"


def fit_font(text, max_w, start, bold=True, minimum=10):
    """Largest font size (<= start) at which text fits max_w."""
    size = start
    while size > minimum and font(size, bold).getlength(text) > max_w:
        size -= 1
    return font(size, bold)


# ---- dotted world map (64 cols x 32 rows, equirectangular lon -180..180, lat 75..-55) ----
MAP_RANGES = {
    0: [(8, 14), (30, 33), (40, 48)],
    1: [(6, 16), (29, 34), (38, 52)],
    2: [(5, 17), (28, 35), (37, 55)],
    3: [(6, 18), (29, 34), (38, 56)],
    4: [(7, 18), (30, 33), (38, 55)],
    5: [(8, 17), (31, 33), (39, 54)],
    6: [(9, 16), (31, 39), (40, 53)],
    7: [(10, 16), (31, 35), (40, 52)],
    8: [(11, 15), (32, 35), (41, 50)],
    9: [(10, 15), (33, 35), (42, 49)],
    10: [(13, 15), (33, 35), (43, 48)],
    11: [(14, 16), (31, 35), (44, 48)],
    12: [(15, 17), (30, 35), (41, 49)],
    13: [(16, 18), (30, 34), (46, 49)],
    14: [(17, 19), (31, 33), (46, 48)],
    15: [(18, 20), (31, 33), (47, 49)],
    16: [(18, 21), (31, 33), (48, 50)],
    17: [(19, 21), (32, 33), (48, 51)],
    18: [(19, 22), (48, 51)],
    19: [(20, 22), (49, 51)],
    20: [(20, 22), (49, 52)],
    21: [(20, 22), (50, 53)],
    22: [(20, 21), (51, 54)],
    23: [(20, 21), (51, 55)],
    24: [(20, 21), (52, 55)],
    25: [(20, 21), (52, 55)],
    26: [(20, 21), (53, 56)],
    27: [(20, 20), (53, 56)],
    28: [(53, 55)],
    29: [(53, 55)],
    30: [(54, 55)],
    31: [],
}

# pins: (col, row, label) — labels match the 8 story cards; ★ = lead story (NVIDIA, Santa Clara)
PINS = [
    (10, 9, "★"),    # Santa Clara — NVIDIA HQ (lead)
    (32, 5, "8"),    # Manchester
    (34, 7, "1"),    # Zurich — FIFA
    (37, 6, "3"),    # Kyiv
    (42, 12, "2"),   # Hormuz Strait
    (40, 13, "4"),   # Manama, Bahrain (nudged one row down so it clears the Hormuz pin)
    (47, 12, "6"),   # Kathmandu
    (51, 20, "7"),   # Banten
]

CARDS = [
    dict(num=1, kicker="FIFA / SPORT", color=(30, 123, 52), date="23 NOV", date_red=False,
         head="UK to host 2035 Women's World Cup",
         body="England, Scotland, Wales & N. Ireland host 2035.",
         glyph="circle"),
    dict(num=2, kicker="HORMUZ / ENERGY", color=(183, 121, 31), date="24 NOV", date_red=True,
         head="25 seafarers killed around Hormuz",
         body="UN count as tanker strikes mount; 7 since 16 Nov.",
         glyph="waves"),
    dict(num=3, kicker="UKRAINE / WAR", color=(43, 95, 158), date="23 NOV", date_red=False,
         head="Russian strikes kill 14 in Kyiv region",
         body="War enters its fifth winter; 21 facilities damaged.",
         glyph="plus"),
    dict(num=4, kicker="IRAN–US / GULF", color=(176, 58, 46), date="23 NOV", date_red=False,
         head="Iran hits US bases in Bahrain",
         body="Tehran claims two Patriot radars hit by missiles.",
         glyph="diamond"),
    dict(num=5, kicker="NATO / SPACE", color=(14, 42, 71), date="23 NOV", date_red=False,
         head="NATO vows space defence",
         body="Alliance answers reports of a Russian space weapon.",
         glyph="star"),
    dict(num=6, kicker="NEPAL / AID", color=(15, 118, 110), date="23 NOV", date_red=False,
         head="India pledges $1.6bn to rebuild Nepal",
         body="Flood aid plus 8 MoUs as Modi hosts Balen Shah.",
         glyph="heart"),
    dict(num=7, kicker="INDONESIA / DISASTER", color=(194, 65, 12), date="24 NOV", date_red=True,
         head="34 missing after Banten factory fire",
         body="Search goes on at the candy factory; 3 dead.",
         glyph="triangle"),
    dict(num=8, kicker="BRITAIN / SAFETY", color=(107, 33, 168), date="23 NOV", date_red=False,
         head="Manchester concert evacuated",
         body="Thousands flee after unknown substance released.",
         glyph="square"),
]

BRIEFS = [
    "Dems plan 12 debates for 2028",
    "Russia warns Estonia: 'open war'",
    "Tajikistan to quit ICC",
    "Denmark upholds 'ghetto law'",
    "Iranian singer flogged",
    "Ukraine hits Russian ships off Libya",
    "Houthis seize Bab el-Mandeb",
]


def draw_glyph(d, cx, cy, kind, color, s=15):
    """Small geometric picture-glyph, drawn with primitives (always renders)."""
    if kind == "circle":
        d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=color)
    elif kind == "square":
        d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=color)
    elif kind == "triangle":
        d.polygon([(cx, cy - s), (cx + s, cy + s), (cx - s, cy + s)], fill=color)
    elif kind == "diamond":
        d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=color)
    elif kind == "plus":
        t = max(4, s // 3)
        d.rectangle([cx - t, cy - s, cx + t, cy + s], fill=color)
        d.rectangle([cx - s, cy - t, cx + s, cy + t], fill=color)
    elif kind == "star":
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            r = s if i % 2 == 0 else s * 0.45
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=color)
    elif kind == "heart":
        r = s * 0.55
        d.ellipse([cx - 2 * r, cy - r, cx, cy + r], fill=color)
        d.ellipse([cx, cy - r, cx + 2 * r, cy + r], fill=color)
        d.polygon([(cx - 2 * r, cy), (cx + 2 * r, cy), (cx, cy + s)], fill=color)
    elif kind == "waves":
        for k in range(3):
            yy = cy - s + k * s
            pts = []
            for i in range(9):
                xx = cx - s + i * (2 * s / 8)
                pts.append((xx, yy + (4 if i % 2 else -4)))
            d.line(pts, fill=color, width=3, joint="curve")


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---------- masthead (y 0-92) ----------
    d.rectangle([0, 0, W, 92], fill=NAVY)
    title = "THE WORLD TODAY"
    date_str = "TUESDAY 24 NOVEMBER 2026"
    f_date = font(26, bold=True)
    date_w = f_date.getlength(date_str)
    f_title = fit_font(title, W - 48 - date_w - 40, 58, bold=True)
    d.text((24, 18), title, font=f_title, fill=WHITE)
    d.text((W - 24 - date_w, 30), date_str, font=f_date, fill=GOLD)
    d.rectangle([0, 92, W, 95], fill=GOLD)

    # ---------- lead hero (y 100-330) ----------
    d.rectangle([16, 100, 1008, 330], fill=WHITE, outline=LIGHT_GREY, width=1)
    d.rectangle([16, 100, 24, 330], fill=NAVY)
    # kicker chip
    f_kick = font(16, bold=True)
    kick = "TECH · MONDAY"
    kw = f_kick.getlength(kick)
    d.rounded_rectangle([40, 114, 40 + kw + 20, 140], radius=4, fill=RED)
    d.text((50, 118), kick, font=f_kick, fill=WHITE)
    # date chip top-right
    f_dchip = font(17, bold=True)
    dchip = "24 NOV"
    dw = f_dchip.getlength(dchip)
    d.rounded_rectangle([992 - dw - 20, 114, 992, 140], radius=4, fill=NAVY)
    d.text((992 - dw - 10, 118), dchip, font=f_dchip, fill=WHITE)
    # headline, 2 lines, auto-fit into the space left of the stats column
    head_lines = ["NVIDIA BRINGS BACK HUANG AS CEO", "AFTER TRUMP'S PUSH"]
    f_head = fit_font(head_lines[0], 730, 40, bold=True)
    lh = int(f_head.size * 1.2)
    y = 152
    for line in head_lines:
        d.text((40, y), line, font=f_head, fill=NAVY)
        y += lh
    # body, max 3 lines
    body = ("Board reinstates Jensen Huang 11 days after he quit over affair "
            "claims; shares leap 33% and the Nasdaq rallies 6%.")
    f_body = font(22)
    blines = wrap(body, f_body, 730)[:3]
    y = 152 + 2 * lh + 6
    for line in blines:
        d.text((40, y), line, font=f_body, fill=INK)
        y += 28
    # stat blocks, right side
    f_stat = font(58, bold=True)
    f_statlab = font(16, bold=True)
    d.text((800, 150), "+33%", font=f_stat, fill=GREEN)
    d.text((802, 216), "NVDA SHARES", font=f_statlab, fill=MUTED)
    d.text((800, 238), "+6%", font=f_stat, fill=GREEN)
    d.text((802, 304), "NASDAQ", font=f_statlab, fill=MUTED)

    # ---------- map strip (y 338-470) ----------
    d.rectangle([16, 338, 1008, 470], fill=MAP_BG)
    f_map = font(20, bold=True)
    d.text((30, 346), "WHERE THE NEWS HAPPENED — 24 NOV", font=f_map, fill=NAVY)
    ox, oy = 46, 372  # map origin (panel x+30, panel y+34)
    xs, ys = 9, 3.1
    for r, ranges in MAP_RANGES.items():
        for (c0, c1) in ranges:
            for c in range(c0, c1 + 1):
                x = ox + c * xs
                yy = oy + r * ys
                d.ellipse([x - 1.5, yy - 1.5, x + 1.5, yy + 1.5], fill=NAVY)
    # pins
    f_pin = font(10, bold=True)
    for (c, r, label) in PINS:
        x = ox + c * xs
        yy = oy + r * ys
        d.ellipse([x - 7, yy - 7, x + 7, yy + 7], fill=WHITE)
        d.ellipse([x - 5, yy - 5, x + 5, yy + 5], fill=RED)
        lw = f_pin.getlength(label)
        d.text((x - lw / 2, yy - 6.5), label, font=f_pin, fill=WHITE)
    # legend, right side of the panel
    f_leg = font(14)
    f_legb = font(14, bold=True)
    lx, ly = 660, 352
    d.text((lx, ly), "★  SANTA CLARA — NVIDIA LEAD STORY", font=f_legb, fill=NAVY)
    d.text((lx, ly + 22), "1 ZURICH  ·  2 HORMUZ  ·  3 KYIV  ·  4 MANAMA", font=f_leg, fill=NAVY)
    d.text((lx, ly + 44), "6 KATHMANDU  ·  7 BANTEN  ·  8 MANCHESTER", font=f_leg, fill=NAVY)
    d.text((lx, ly + 66), "(5 NATO — SPACE, NO PIN)", font=f_leg, fill=MUTED)

    # ---------- story grid (y 478-880): 2 cols x 4 rows ----------
    for i, card in enumerate(CARDS):
        col = i % 2
        row = i // 2
        x0 = 12 + col * 500
        y0 = 478 + row * 102
        x1, y1 = x0 + 500, y0 + 96
        color = card["color"]
        d.rectangle([x0, y0, x1, y1], fill=WHITE, outline=LIGHT_GREY, width=1)
        d.rectangle([x0, y0, x0 + 6, y1], fill=color)
        # glyph, left, vertically centred on the headline block
        draw_glyph(d, x0 + 26, y0 + 48, card["glyph"], color, s=13)
        # kicker
        f_k = font(14, bold=True)
        d.text((x0 + 52, y0 + 9), card["kicker"], font=f_k, fill=color)
        # date chip, top-right
        f_dc = font(13, bold=True)
        dtxt = card["date"]
        dw2 = f_dc.getlength(dtxt)
        chip_fill = RED if card["date_red"] else GREY_CHIP
        d.rounded_rectangle([x1 - dw2 - 18, y0 + 8, x1 - 8, y0 + 28], radius=3, fill=chip_fill)
        d.text((x1 - dw2 - 13, y0 + 11), dtxt, font=f_dc, fill=WHITE)
        # headline, max 2 lines
        f_h = font(20, bold=True)
        hlines = wrap(card["head"], f_h, 500 - 52 - 14)[:2]
        hy = y0 + 30
        for line in hlines:
            d.text((x0 + 52, hy), line, font=f_h, fill=NAVY)
            hy += 24
        # body, 1 line truncated
        f_b = font(16)
        bline = trunc(card["body"], f_b, 500 - 52 - 14)
        d.text((x0 + 52, y0 + 76), bline, font=f_b, fill=MUTED)

    # ---------- briefs ticker (y 888-960) ----------
    d.rectangle([0, 888, W, 960], fill=CHARCOAL)
    label = "ALSO TODAY:"
    joined = "  •  ".join(BRIEFS)
    # largest size (17..13) that wraps the briefs into at most 2 lines
    chosen = None
    for size in (17, 16, 15, 14, 13):
        f_br = font(size)
        f_lab = font(size, bold=True)
        avail = W - 24 - f_lab.getlength(label) - 16 - 24
        lines = wrap(joined, f_br, avail)
        if len(lines) <= 2:
            chosen = (size, lines)
            break
    size, blines = chosen
    f_lab = font(size, bold=True)
    f_br = font(size)
    lab_w = f_lab.getlength(label)
    tx = 24 + lab_w + 16
    d.text((24, 888 + (72 - 2 * int(size * 1.35)) // 2), label, font=f_lab, fill=GOLD)
    yy = 888 + (72 - len(blines) * int(size * 1.35)) // 2
    for line in blines:
        d.text((tx, yy), line, font=f_br, fill=WHITE)
        yy += int(size * 1.35)

    # ---------- footer (y 968-1024) ----------
    d.rectangle([0, 968, W, H], fill=CHARCOAL)
    left = ("ALL STORIES VERIFIED FROM REPORTS PUBLISHED 23–24 NOVEMBER 2026  ·  "
            "SOURCES: REUTERS, WSJ, CNN, BBC, FIFA, UN")
    right = "THE WORLD TODAY — 24 NOV 2026"
    # largest size (14..11) at which left and right fit on one line with a gap
    for fsize in (14, 13, 12, 11):
        f_f = font(fsize)
        f_fr = font(fsize, bold=True)
        if 16 + f_f.getlength(left) + 24 + f_fr.getlength(right) <= W - 16:
            break
    rw = f_fr.getlength(right)
    d.text((16, 992), left, font=f_f, fill=LIGHT_FOOT)
    d.text((W - 16 - rw, 992), right, font=f_fr, fill=LIGHT_FOOT)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()
