"""
Draws heatmap.svg: your last year of GitHub contributions as a grid of chunky pixel blocks.

    gh api graphql -f query="$(cat scripts/query.graphql)" -f login=YOUR_NAME > calendar.json
    python scripts/heatmap.py calendar.json heatmap.svg

(.github/workflows/heatmap.yml does this by itself every day.)
"""
import json, sys, datetime

GLYPHS = {
 "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
 "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
 "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
 "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
 "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
 "L": "10000 10000 10000 10000 10000 10000 11111", "M": "10001 11011 10101 10101 10001 10001 10001",
 "N": "10001 11001 10101 10011 10001 10001 10001", "O": "01110 10001 10001 10001 10001 10001 01110",
 "P": "11110 10001 10001 11110 10000 10000 10000", "R": "11110 10001 10001 11110 10100 10010 10001",
 "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
 "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
 "Y": "10001 10001 01010 00100 00100 00100 00100",
 "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
 "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
 "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
 "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
 "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
 ",": "00000 00000 00000 00000 00110 00100 01000", " ": "00000 00000 00000 00000 00000 00000 00000",
}
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
# five levels, from nothing to NoVas green
LEVELS = ("#15181a", "#0d4a2a", "#0a7a3c", "#14c25c", "#18ff6e")
GREY, WHITE = "#78808a", "#f0f2f5"
CELL, GAP = 11, 3


def level(n, top):
    if n <= 0:
        return 0
    return min(4, 1 + (n * 4 - 1) // max(top, 1))


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
    weeks = cal["weeks"]
    top = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1)
    pad, head = 22, 66
    W = pad * 2 + len(weeks) * (CELL + GAP) - GAP
    H = head + 7 * (CELL + GAP) - GAP + pad + 4
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" shape-rendering="crispEdges">' % (W, H, W, H),
           '<rect width="%d" height="%d" fill="#000"/>' % (W, H)]
    text_rects("%s CONTRIBUTIONS" % format(cal["totalContributions"], ","), pad, 14, 3, WHITE, out)
    seen = -1
    last_label = -9
    for wi, w in enumerate(weeks):
        x = pad + wi * (CELL + GAP)
        days = w["contributionDays"]
        if days:
            m = datetime.date.fromisoformat(days[0]["date"]).month - 1
            if m != seen and wi - last_label >= 4 and wi < len(weeks) - 2:
                text_rects(MONTHS[m], x, head - 22, 2, GREY, out)
                last_label = wi
            seen = m
        for d in days:
            wd = datetime.date.fromisoformat(d["date"]).weekday()          # Monday = 0
            wd = (wd + 1) % 7                                              # GitHub starts the week on Sunday
            y = head + wd * (CELL + GAP)
            out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x, y, CELL, CELL, LEVELS[level(d["contributionCount"], top)]))
    # a small legend, bottom right: less -> more
    lx = W - pad - 5 * (CELL + GAP) + GAP
    for i, c in enumerate(LEVELS):
        out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (lx + i * (CELL + GAP), 18, CELL, CELL, c))
    out.append("</svg>")
    open(dst, "w").write("\n".join(out))
    print(dst, W, H, "total", cal["totalContributions"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
