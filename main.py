import random

import pyxelen
import pyxelen.api as api


TITLE = 'pyweek25'
WIDTH = 2 * 16 * 16
HEIGHT = 2 * 9 * 16


tilesize = api.Size(w=16, h=16)
offsets = [
    api.Position(x=int((i % 16) * 16), y=int((i // 16) * 16))
    for i in range(21 * 16)
]

images = [
    api.Image(
        filename='images/cave.png',
        clip=api.Box(size=tilesize, position=position)
    ) for position in offsets
]


MAIN_FONT = {
    c: api.Image(
        filename='images/font.png',
        clip=api.Box(
            size=api.Size(w=8, h=8),
            position=api.Position(
                x=int((i % 8) * 8),
                y=int((i // 8) * 8)
            )
        )
    )
    for i, c in enumerate(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz.!'
    )
}

MAIN_FONT_OFFSETS = {
    'A': (8, 0), 'B': (8, 0), 'C': (8, 0), 'D': (8, 0),
    'E': (8, 0), 'F': (8, 0), 'G': (8, 0), 'H': (8, 0),
    'I': (7, 0), 'J': (8, 0), 'K': (8, 0), 'L': (8, 0),
    'M': (8, 0), 'N': (8, 0), 'O': (8, 0), 'P': (8, 0),
    'Q': (8, 0), 'R': (8, 0), 'S': (8, 0), 'T': (8, 0),
    'U': (8, 0), 'V': (8, 0), 'W': (8, 0), 'X': (8, 0),
    'Y': (8, 0), 'Z': (8, 0), '0': (8, 0), '1': (7, 0),
    '2': (8, 0), '3': (8, 0), '4': (8, 0), '5': (8, 0),
    '6': (8, 0), '7': (8, 0), '8': (8, 0), '9': (8, 0),
    'a': (7, 0), 'b': (6, 0), 'c': (6, 0), 'd': (7, 0),
    'e': (6, 0), 'f': (6, 0), 'g': (6, 2), 'h': (6, 0),
    'i': (3, 0), 'j': (5, 0), 'k': (7, 0), 'l': (3, 0),
    'm': (8, 0), 'n': (6, 0), 'o': (6, 0), 'p': (6, 2),
    'q': (6, 2), 'r': (7, 0), 's': (7, 0), 't': (6, 0),
    'u': (7, 0), 'v': (7, 0), 'w': (8, 0), 'x': (7, 0),
    'y': (7, 0), 'z': (7, 0), '.': (8, 0), '!': (8, 0),
}


def draw_text(text, renderer, x, y):
    for c in text:
        if c in MAIN_FONT:
            renderer.draw_image(
                MAIN_FONT[c],
                api.Position(x=x, y=y + MAIN_FONT_OFFSETS[c][1])
            )
            x += MAIN_FONT_OFFSETS[c][0] + 1
        else:
            x += 4


dirt = [
    images[16 * 10 + 1],
    images[16 * 10],
    images[16 * 9 + 1],
    images[16 * 9],
]


dot = api.Image(
    filename='images/cave.png',
    clip=api.Box(size=api.Size(w=2, h=2), position=api.Position(x=71, y=81))
)


class DirtBackground(api.Texture):

    def draw(self, renderer):
        for x in range(2 * 16):
            for y in range(2 * 9):
                renderer.draw_image(
                    random.choice(dirt),
                    api.Position(x=x * 16, y=y * 16)
                )


DIRT_BACKGROUND = DirtBackground(uid=1, size=512)


class Model(api.Model):

    def on_update(self, controls):
        return self.set(music="music/25 - Finale.ogg")

    def draw(self, renderer):
        renderer.draw_image(
            api.Image(
                filename='images/world-map.png',
                clip=api.Box(
                    size=api.Size(w=WIDTH, h=HEIGHT),
                    position=api.Position(x=0, y=0)
                )
            ),
            api.Position(x=0, y=0)
        )
        renderer.draw_image(
            api.Image(
                filename='images/dialog.png',
                clip=api.Box(
                    size=api.Size(w=240, h=75),
                    position=api.Position(x=0, y=0)
                )
            ),
            api.Position(x=10, y=10)
        )
        draw_text('The quick brown fox jumps over', renderer, 20, 20)
        draw_text('the lazy dog!', renderer, 20, 30)


pyxelen.run('pyweek25', WIDTH, HEIGHT, Model(), 40)
