"""Draws banner.png for the profile: NoVas's pixel eyes and a few words in blocky 5x7 pixel letters."""
from PIL import Image

GLYPHS = {
 "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
 "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
 "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
 "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
 "I": "01110 00100 00100 00100 00100 00100 01110", "L": "10000 10000 10000 10000 10000 10000 11111",
 "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
 "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
 "R": "11110 10001 10001 11110 10100 10010 10001", "S": "01111 10000 10000 01110 00001 00001 11110",
 "T": "11111 00100 00100 00100 00100 00100 00100", "U": "10001 10001 10001 10001 10001 10001 01110",
 "V": "10001 10001 10001 10001 10001 01010 00100", "W": "10001 10001 10001 10101 10101 11011 10001",
 "Y": "10001 10001 01010 00100 00100 00100 00100", ",": "00000 00000 00000 00000 00110 00100 01000",
 "'": "00100 00100 01000 00000 00000 00000 00000", ".": "00000 00000 00000 00000 00000 00110 00110",
 " ": "00000 00000 00000 00000 00000 00000 00000",
}
W, H = 1600, 500
BG = (0, 0, 0)
GREEN, WHITE, GREY = (24, 255, 110), (240, 242, 245), (120, 126, 134)
img = Image.new("RGB", (W, H), BG)
px = img.load()


def block(x, y, s, color):
    for yy in range(y, min(y + s, H)):
        for xx in range(x, min(x + s, W)):
            px[xx, yy] = color


def text(s, x, y, b, color):
    for ch in s:
        rows = GLYPHS[ch].split()
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                if v == "1":
                    block(x + c * b, y + r * b, b, color)
        x += 6 * b


# the face: NoVas's normal eyes, cut from the real screen picture, 3x bigger with no smoothing
face = Image.open("face.png").convert("RGB").crop((20, 10, 260, 140))
face = face.resize((face.width * 3, face.height * 3), Image.NEAREST)
img.paste(face, (50, (H - face.height) // 2))
# the words
text("HI, I'M", 840, 70, 9, GREEN)
text("YARIEL", 840, 150, 18, WHITE)
text("I BUILD TINY THINGS.", 840, 320, 5, GREY)
text("SOME OF THEM HAVE FACES.", 840, 372, 5, GREY)
img.save("banner.png", optimize=True)
print("banner.png", img.size)
