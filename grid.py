
from PIL import Image, ImageDraw, ImageFont
import random

import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import List, Tuple, Optional, Union

# TODO Custom word list

class WordList:

    def sample(self) -> str:
        return ""

class DefaultWordList(WordList):
    words: List[str]

    def __init__(self) -> None:
        with open('words.txt') as file:
            self.words = zz.of(file).map(_1[:-1]).list()
        random.shuffle(self.words)

    def sample(self) -> str:
        return self.words.pop()

class CustomWordList(WordList):
    words: List[str]

    def __init__(self, lst: List[str]) -> None:
        self.words = lst
        random.shuffle(self.words)

    def sample(self) -> str:
        return self.words.pop()

class CellManager:

    def text(self, i: int, j: int) -> str:
        return ""

    def foreground(self, i: int, j: int) -> str:
        return "black"

    def background(self, i: int, j: int) -> str:
        return "white"

class HiddenColorsManager(CellManager):
    man: CellManager
    fg: str
    bg: str

    def __init__(self, man: CellManager, fg: str = 'black', bg: str = 'white'):
        self.man = man
        self.fg = fg
        self.bg = bg

    def background(self, i: int, j: int) -> str:
        return self.bg

    def foreground(self, i: int, j: int) -> str:
        return self.fg

    def text(self, i: int, j: int) -> str:
        return self.man.text(i, j)

class CodenameManager(CellManager):
    contents: List[List[str]]
    texts: List[List[str]]

    def __init__(self, rows: int, cols: int, defcolor: str = 'lightgray', colors: Tuple[Tuple[str, int], ...] = (('red', 9), ('blue', 9), ('black', 1)), words: Optional[WordList] = None):
        self.contents = []
        self.texts = []

        words = words or DefaultWordList()

        coordinates: List[Tuple[int, int]] = zz.range(rows).cross_product(zz.range(cols)).list()
        random.shuffle(coordinates)

        # Generate
        for i in range(rows):
            arr  = []
            arr1 = []
            for j in range(cols):
                arr .append(defcolor)
                arr1.append(words.sample())
            self.contents.append(arr)
            self.texts.append(arr1)

        # Fill in
        for c, n in colors:
            for _ in range(n):
                i, j = coordinates.pop()
                self.contents[i][j] = c

    def background(self, i: int, j: int) -> str:
        return self.contents[i][j]

    def foreground(self, i: int, j: int) -> str:
        return 'white' if self.contents[i][j] == 'black' else 'black'

    def text(self, i: int, j: int) -> str:
        return self.texts[i][j]

    def hidden(self) -> HiddenColorsManager:
        return HiddenColorsManager(self)

class FirstContactManager(CodenameManager):

    def __init__(self, rows: int, cols: int, words: Optional[WordList] = None):
        super().__init__(
            rows=rows,
            cols=cols,
            defcolor='white',
            colors=(('red', 4), ('blue', 5), ('green', 6)),
            words=words,
        )

class BasicCellManager(CellManager):
    _bg: str
    _fg: str
    _text: str

    def __init__(self, text: str, bg: str, fg: str):
        self._bg = bg
        self._fg = fg
        self._text = text

    def text(self, i: int, j: int) -> str:
        return self._text

    def foreground(self, i: int, j: int) -> str:
        return self._fg

    def background(self, i: int, j: int) -> str:
        return self._bg

class GridConfig:
    rows: int
    cols: int
    cells: CellManager

    WIDTH = 64
    HEIGHT = 64

    def __init__(self, rows: int, cols: int, cells: CellManager = BasicCellManager(text='', bg='white', fg='black')) -> None:
        self.rows = rows
        self.cols = cols
        self.cells = cells

    @staticmethod
    def print_text(draw: ImageDraw, text: str, fg: str, x: int, y: int) -> None:
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        if text == '':
            return

        font_size = 12
        while True:
            font = ImageFont.truetype('DejaVuSans.ttf', font_size)
            w, h = font.getsize(text)
            if w < WIDTH and h < HEIGHT:
                break
            font_size -= 1
        draw.text((x - w / 2, y - h / 2), text, font=font, fill=fg)

    def make_grid(self) -> Image:
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        n, m = self.rows, self.cols

        image = Image.new("RGBA", (m * WIDTH + 1, n * HEIGHT + 1))
        draw = ImageDraw.Draw(image)
        for i, j in zz.range(m).cross_product(zz.range(n)):
            pos0 = (i * WIDTH, j * HEIGHT)
            pos1 = ((i + 1) * WIDTH, (j + 1) * HEIGHT)
            fg = self.cells.foreground(i, j)
            draw.rectangle([pos0, pos1],
                           fill=self.cells.background(i, j),
                           outline=fg)
            text = self.cells.text(i, j)
            GridConfig.print_text(draw, text, fg, (i + 0.5) * WIDTH, (j + 0.5) * HEIGHT)
        return image
