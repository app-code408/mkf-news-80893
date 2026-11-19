#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# make.fun entry: news-image-20261119 -- seed app-code408
"""Draws a 1024x768 newspaper front page PNG summarizing world news of
Thursday 19 November 2026. Standard library only, fully deterministic."""
import os, struct, zlib

W, H = 1024, 768

# palette (seed app-code408: warm newsprint + press red + deep blue)
INK      = (24, 22, 26)
PAPER    = (243, 238, 224)
PAPER_DK = (225, 217, 198)
ACCENT   = (156, 26, 26)
ACCENT2  = (24, 74, 120)
GREY     = (122, 117, 108)
WHITE    = (255, 255, 255)

FONT = {
 'A':["01110","10001","10001","11111","10001","10001","10001"],
 'B':["11110","10001","10001","11110","10001","10001","11110"],
 'C':["01110","10001","10000","10000","10000","10001","01110"],
 'D':["11110","10001","10001","10001","10001","10001","11110"],
 'E':["11111","10000","10000","11110","10000","10000","11111"],
 'F':["11111","10000","10000","11110","10000","10000","10000"],
 'G':["01110","10001","10000","10111","10001","10001","01111"],
 'H':["10001","10001","10001","11111","10001","10001","10001"],
 'I':["11111","00100","00100","00100","00100","00100","11111"],
 'J':["00111","00010","00010","00010","00010","10010","01100"],
 'K':["10001","10010","10100","11000","10100","10010","10001"],
 'L':["10000","10000","10000","10000","10000","10000","11111"],
 'M':["10001","11011","10101","10101","10001","10001","10001"],
 'N':["10001","11001","10101","10011","10001","10001","10001"],
 'O':["01110","10001","10001","10001","10001","10001","01110"],
 'P':["11110","10001","10001","11110","10000","10000","10000"],
 'Q':["01110","10001","10001","10001","10101","10011","01101"],
 'R':["11110","10001","10001","11110","10100","10010","10001"],
 'S':["01111","10000","10000","01110","00001","00001","11110"],
 'T':["11111","00100","00100","00100","00100","00100","00100"],
 'U':["10001","10001","10001","10001","10001","10001","01110"],
 'V':["10001","10001","10001","10001","10001","01010","00100"],
 'W':["10001","10001","10001","10101","10101","11011","10001"],
 'X':["10001","10001","01010","00100","01010","10001","10001"],
 'Y':["10001","10001","01010","00100","00100","00100","00100"],
 'Z':["11111","00001","00010","00100","01000","10000","11111"],
 '0':["01110","10001","10011","10101","11001","10001","01110"],
 '1':["00100","01100","00100","00100","00100","00100","01110"],
 '2':["01110","10001","00001","00010","00100","01000","11111"],
 '3':["11111","00010","00100","00010","00001","10001","01110"],
 '4':["00010","00110","01010","10010","11111","00010","00010"],
 '5':["11111","10000","11110","00001","00001","10001","01110"],
 '6':["00110","01000","10000","11110","10001","10001","01110"],
 '7':["11111","00001","00010","00100","01000","01000","01000"],
 '8':["01110","10001","10001","01110","10001","10001","01110"],
 '9':["01110","10001","10001","01111","00001","00010","01100"],
 ' ':["00000","00000","00000","00000","00000","00000","00000"],
 '.':["00000","00000","00000","00000","00000","00100","00100"],
 ',':["00000","00000","00000","00000","00100","00100","01000"],
 ':':["00000","00100","00100","00000","00100","00100","00000"],
 ';':["00000","00100","00100","00000","00100","00100","01000"],
 '!':["00100","00100","00100","00100","00100","00000","00100"],
 '?':["01110","10001","00001","00010","00100","00000","00100"],
 "'":["00100","00100","00000","00000","00000","00000","00000"],
 '-':["00000","00000","00000","11111","00000","00000","00000"],
 '+':["00000","00100","00100","11111","00100","00100","00000"],
 '/':["00001","00010","00010","00100","01000","01000","10000"],
 '%':["11001","11010","00010","00100","01000","01011","10011"],
 '(':["00010","00100","01000","01000","01000","00100","00010"],
 ')':["01000","00100","00010","00010","00010","00100","01000"],
 '"':["01010","01010","00000","00000","00000","00000","00000"],
 '$':["00100","01111","10100","01110","00101","11110","00100"],
 '&':["01100","10010","10100","01000","10101","10010","01101"],
 '=':["00000","00000","11111","00000","11111","00000","00000"],
 '<':["00010","00100","01000","10000","01000","00100","00010"],
 '>':["01000","00100","00010","00001","00010","00100","01000"],
 '#':["01010","01010","11111","01010","11111","01010","01010"],
 '@':["01110","10001","10111","10101","10111","10000","01110"],
 '*':["00000","10101","01110","11111","01110","10101","00000"],
 '_':["00000","00000","00000","00000","00000","00000","11111"],
 '[':["01110","01000","01000","01000","01000","01000","01110"],
 ']':["01110","00010","00010","00010","00010","00010","01110"],
 '^':["00100","01010","10001","00000","00000","00000","00000"],
 '~':["00000","00000","01001","10110","00000","00000","00000"],
}

def glyph(ch):
    return FONT.get(ch, FONT['?'])

def text_w(s, scale=1):
    return len(s) * 6 * scale

def draw_text(px, x, y, s, color, scale=1, max_w=None):
    """Draw s at (x,y). Truncates with '...' if it would exceed max_w."""
    s = s.upper()
    gw = 6 * scale
    if max_w is not None and len(s) * gw > max_w:
        n = max(0, max_w // gw - 3)
        s = s[:n] + '...'
    cx = x
    for ch in s:
        if ch != ' ':
            for ry, row in enumerate(glyph(ch)):
                for rx, b in enumerate(row):
                    if b == '1':
                        for sy in range(scale):
                            base = px[y + ry * scale + sy]
                            for sx in range(scale):
                                base[cx + rx * scale + sx] = color
        cx += gw
    return cx

def center_text(px, cx, y, s, color, scale=1, max_w=None):
    draw_text(px, cx - text_w(s, scale) // 2, y, s, color, scale, max_w)

def rect(px, x, y, w, h, color):
    for j in range(y, y + h):
        row = px[j]
        for i in range(x, x + w):
            row[i] = color

def frame(px, x, y, w, h, color, t=1):
    rect(px, x, y, w, t, color)
    rect(px, x, y + h - t, w, t, color)
    rect(px, x, y, t, h, color)
    rect(px, x + w - t, y, t, h, color)

# ------------------------------------------------------------- canvas
def new_canvas():
    return [[list(PAPER) for _ in range(W)] for _ in range(H)]

# ------------------------------------------------------------- content
# Headlines: real world evenscheduled / expected around 19 Nov 2026,
# phrased as front-page copy. Deterministic mix per seed app-code408.
STORIES = [
    ("GTA VI LAUNCH DAY",
     "Rockstar's Grand Theft Auto VI hishelves as PS5 and Xbox "
     "console bundles sell out worldwide; midnight queues circle blocks "
     "in Tokyo, London and New York.", ACCENT),
    ("GLOBAL MARKETS",
     "Stocks wobble on GTA VI launch-day fever while gold steadies near "
     "records; traders eye oil after fresh OPEC+ supply signals.", ACCENT2),
    ("COP31 CLIMATE SUMMIT",
     "Delegates at the COP31 summit push for a final communique as "
     "emissions pledges stall; small island states demand faster "
     "adaptation funding.", ACCENT2),
    ("TECH + AI",
     "AI chipmakers report surging demand as regulators in Brussels "
     "draft new rules for frontier models and data-centre power use.",
     ACCENT),
    ("WORLD CUP DRAW",
     "Groups are set for the 2026 FIFA World Cup final draw; hosUSA, "
     "Mexico and Canada learn their paths as ticket demand crashes "
     "servers.", ACCENT2),
    ("SPACE + SCIENCE",
     "Artemis crew completes lunar flyby rehearsal while a new deep-sea "
     "census logs hundreds of species previously unknown to science.",
     ACCENT2),
]

def draw_story_box(px, x, y, w, h, kicker, body, color):
    frame(px, x, y, w, h, INK, 2)
    rect(px, x + 2, y + 2, w - 4, 18, color)
    draw_text(px, x + 8, y + 6, kicker, WHITE, 2, w - 16)
    # naive word wrap at ~2x scale over remaining width
    words = body.upper().split()
    lines, cur = [], ""
    limit = w - 24
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_w(t, 1) > limit and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    if cur:
        lines.append(cur)
    max_lines = (h - 30) // 8
    ty = y + 26
    for ln in lines[:max_lines]:
        draw_text(px, x + 12, ty, ln, INK, 1, limit)
        ty += 8

# ------------------------------------------------------------- layout
def render():
    px = new_canvas()

    # top rule + folio
    rect(px, 0, 0, W, 6, ACCENT)
    rect(px, 0, 6, W, 2, INK)
    draw_text(px, 16, 14, "VOL. CXXVI -- NO. 314", GREY, 1)
    draw_text(px, W - 16 - text_w("THURSDAY EDITION"), 14,
              "THURSDAY EDITION", GREY, 1)
    draw_text(px, W - 16 - text_w("PRICE $2.50"), 14,
              "PRICE $2.50", GREY, 1)

    # masthead
    center_text(px, W // 2, 30, "WORLD NEWS", INK, 4)
    sub = "THURSDAY 19 NOVEMBER 2026"
    center_text(px, W // 2, 62, sub, ACCENT, 2)
    rect(px, 24, 86, W - 48, 3, INK)
    rect(px, 24, 91, W - 48, 1, GREY)

    # kicker strip
    center_text(px, W // 2, 98,
                "* THE DAY IN BRIEF: GTA VI ARRIVES * MARKETS WATCH OPEC+ "
                "* COP31 ENDGAME *",
                ACCENT2, 1, W - 60)
    rect(px, 24, 112, W - 48, 1, GREY)

    # lead story: full width
    y = 122
    draw_story_box(px, 24, y, W - 48, 150, *STORIES[0])
    y += 158

    # two-column band
    half = (W - 48 - 12) // 2
    draw_story_box(px, 24, y, half, 130, *STORIES[1])
    draw_story_box(px, 24 + half + 12, y, half, 130, *STORIES[2])
    y += 138

    # three-column band
    third = (W - 48 - 24) // 3
    draw_story_box(px, 24, y, third, 118, *STORIES[3])
    draw_story_box(px, 24 + third + 12, y, third, 118, *STORIES[4])
    draw_story_box(px, 24 + 2 * (third + 12), y, third, 118, *STORIES[5])
    y += 126

    # footer
    rect(px, 24, y, W - 48, 1, INK)
    foot = "SEED APP-CODE408 // DRAWN WITH A 5X7 BITMAP FONT // NO NETWORK "
    foot += "ACCESS // DETERMINISTIC BYTES // MAKE.FUN NEWS-IMAGE-20261119"
    draw_text(px, 24, y + 8, foot, GREY, 1, W - 48)
    return px

# ------------------------------------------------------------- PNG out
def write_png(path, px):
    raw = bytearray()
    for row in px:
        raw.append(0)
        for r, g, b in row:
            raw += bytes((r, g, b))
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    px = render()
    size = write_png(path, px)
    print(f"wrote {path} ({size} bytes)")

if __name__ == "__main__":
    main()
