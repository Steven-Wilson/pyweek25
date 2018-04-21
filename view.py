import attr


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Box:
    x: int
    y: int
    w: int
    h: int


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Image:
    filename: str
    clip: Box


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Sprite:
    image: Image
    dest: Box


class Font:
    filename: str
    glyphs_wide: int
    size_x: int
    size_y: int
    characters: str
    offsets: dict

    def __init__(self, filename, glyphs_wide, size_x, size_y, characters, offsets):
        self.filename = filename
        self.glyphs_wide = glyphs_wide
        self.size_x = size_x
        self.size_y = size_y
        self.characters = characters
        self.offsets = offsets
        self.glyphs = {
            c: Image(
                self.filename,
                Box(
                    int((i % self.glyphs_wide) * self.size_x),
                    int((i // self.glyphs_wide) * self.size_y),
                    self.size_x, self.size_y
                )
            )
            for i, c in enumerate(self.characters)
        }


@attr.s(auto_attribs=True, frozen=True, slots=True)
class Text:
    font: Font
    text: str
    position_x: int
    position_y: int
    centered: bool


MAIN_FONT = Font(
    'images/font.png', 8, 8, 8, (
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        'abcdefghijklmnopqrstuvwxyz'
        '.!:,"-?\''
    ), {
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
        'y': (7, 2), 'z': (7, 0), '.': (8, 0), '!': (3, 0),
        ':': (3, 0), ',': (3, 1), '"': (4, 0), '-': (6, 0),
        '?': (6, 0), "'": (2, 0),
    }
)


FULLSCREEN = Box(0, 0, 512, 288)
HALFSCREEN = Box(0, 0, 256, 144)
MENU_BACKGROUND = Image('images/menu.png', FULLSCREEN)
CAVE = Image('images/cave.png', HALFSCREEN)
BAR = Image('images/bar.png', HALFSCREEN)
RIGHT_ARROW = Image('images/menu-icons.png', Box(0, 0, 16, 16))
DOWN_ARROW = Image('images/menu-icons.png', Box(32, 0, 16, 16))
SAVE_BACKGROUND = Image('images/menu-icons.png', Box(0, 16, 32, 32))
SAVE_1 = Image('images/menu-icons.png', Box(32, 16, 16, 16))
SAVE_2 = Image('images/menu-icons.png', Box(48, 16, 16, 16))
SAVE_3 = Image('images/menu-icons.png', Box(32, 32, 16, 16))
SAVE_4 = Image('images/menu-icons.png', Box(48, 32, 16, 16))
TITLE_BAR = Image('images/title-bar.png', Box(0, 32, 256, 32))


CHARACTERS = {
    'Nyx': Image('images/characters.png', Box(0, 0, 32, 32)),
    'Kerr': Image('images/characters.png', Box(32, 0, 32, 32)),
    'Kivash': Image('images/characters.png', Box(64, 0, 32, 32)),
    'Necromancer': Image('images/characters.png', Box(96, 0, 32, 32)),
    'Skeleton': Image('images/characters.png', Box(128, 0, 32, 32)),
    'DM': Image('images/characters.png', Box(160, 0, 32, 32)),
    'Ghost': Image('images/characters.png', Box(192, 0, 32, 32)),
    'Giant Rat': Image('images/characters.png', Box(0, 32, 32, 32)),
    'Ooze': Image('images/characters.png', Box(32, 32, 32, 32)),
    'Pirate': Image('images/characters.png', Box(64, 32, 32, 32)),
    'Feral Shih-Tzu': Image('images/characters.png', Box(128, 32, 32, 32)),
}

DEAD_OVERLAY = Image('images/characters.png', Box(96, 32, 32, 32))
