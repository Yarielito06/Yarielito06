"""
Draws streak.svg: a pixel flame and how many days in a row you've contributed.

    gh api graphql -f query="$(cat scripts/query.graphql)" -f login=YOUR_NAME > calendar.json
    python scripts/streak.py calendar.json streak.svg

(.github/workflows/heatmap.yml does this by itself every day.)
"""
import json, sys

GLYPHS = {
 "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
 "D": "11110 10001 10001 10001 10001 10001 11110", "E": "11111 10000 10000 11110 10000 10000 11111",
 "K": "10001 10010 10100 11000 10100 10010 10001", "R": "11110 10001 10001 11110 10100 10010 10001",
 "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
 "Y": "10001 10001 01010 00100 00100 00100 00100",
 "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
 "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
 "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
 "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
 "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
 " ": "00000 00000 00000 00000 00000 00000 00000",
}
# the flame, one letter per pixel: r red, o orange, y yellow, w white-hot
FIRE = [
 ".....rr.....",
 ".....rr.....",
 "....rrrr....",
 "....rrorr...",
 "...rrooorr..",
 "..rrooooorr.",
 "..rooooyoorr",
 ".rrooyyyyoor",
 ".rooyyyyyyor",
 ".rooyyywyyor",
 ".rooyywwwyor",
 ".rrooyywwyor",
 "..rroyyyyorr",
 "...rrooooorr",
 "....rrrrrr..",
]
LIT = {"r": "#d7261e", "o": "#ff7a18", "y": "#ffc61a", "w": "#fff3b0"}
OUT = {"r": "#23282c", "o": "#2f353a", "y": "#3b4147", "w": "#4a5058"}   # flame is out: no streak yet
NUM, GREY = "#ffb020", "#78808a"


def text_rects(s, x, y, b, color, out):
    for ch in s:
        rows = GLYPHS.get(ch, GLYPHS[" "]).split()
        for r, row in enumerate(rows):
            c = 0
            while c < 5:
                if row[c] == "1":
                    start = c
                    while c < 5 and row[c] == "1":
                        c += 1
                    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x + start * b, y + r * b, (c - start) * b, b, color))
                else:
                    c += 1
        x += 6 * b


def main(src, dst):
    cal = json.load(open(src))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    counts = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
    best = run = 0
    for n in counts:
        run = run + 1 if n > 0 else 0
        best = max(best, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:      # today is still young: a quiet today doesn't break the streak yet
        i -= 1
    streak = 0
    while i >= 0 and counts[i] > 0:
        streak += 1
        i -= 1

    cell, pad = 10, 20
    W, H = 440, 15 * cell + pad * 2
    pal = LIT if streak > 0 else OUT
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" shape-rendering="crispEdges">' % (W, H, W, H),
           '<rect width="%d" height="%d" fill="#000"/>' % (W, H)]
    for r, row in enumerate(FIRE):
        if r < 2 and streak > 0:       # the tip of the flame flickers
            out.append('<g><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" dur="1.2s" repeatCount="indefinite"/>')
        for c, ch in enumerate(row):
            if ch != ".":
                out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (pad + c * cell, pad + r * cell, cell, cell, pal[ch]))
        if r < 2 and streak > 0:
            out.append('</g>')
    x = pad + 12 * cell + 30
    text_rects(str(streak), x, pad + 6, 10, NUM if streak > 0 else GREY, out)
    text_rects("DAY STREAK", x, pad + 90, 4, "#f0f2f5", out)
    text_rects("BEST %d" % best, x, pad + 122, 3, GREY, out)
    out.append("</svg>")
    open(dst, "w").write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
