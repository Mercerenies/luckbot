
from PIL import Image, ImageDraw, ImageFont
import random

import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

class WordList:

    def __init__(self):
        with open('words.txt') as file:
            self.words = zz.of(file).map(_1[:-1]).list()
        random.shuffle(self.words)

    def sample(self):
        return self.words.pop()

class HiddenColorsManager:

    def __init__(self, man, fg='black', bg='white'):
        self.man = man
        self.fg = fg
        self.bg = bg

    def background(self, i, j):
        return self.bg

    def foreground(self, i, j):
        return self.fg

    def text(self, i, j):
        return self.man.text(i, j)

class CodenameManager:

    def __init__(self, rows, cols, defcolor='white', colors=(('red', 9), ('blue', 9), ('black', 1))):
        self.contents = []
        self.texts = []

        words = WordList()

        coordinates = zz.range(rows).cross_product(zz.range(cols)).list()
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

    def background(self, i, j):
        return self.contents[i][j]

    def foreground(self, i, j):
        return 'white' if self.contents[i][j] == 'black' else 'black'

    def text(self, i, j):
        return self.texts[i][j]

    def hidden(self):
        return HiddenColorsManager(self)

class BasicCellManager:

    def __init__(self, text, bg, fg):
        self._bg = bg
        self._fg = fg
        self._text = text

    def text(self, i, j):
        return self._text

    def foreground(self, i, j):
        return self._fg

    def background(self, i, j):
        return self._bg

class GenericCellManager:

    def __init__(self, text='', bg='white', fg='black'):
        self.text = CallGuard(text)
        self.background = CallGuard(bg)
        self.foreground = CallGuard(fg)

class CallGuard:

    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        if callable(self.value):
            return self.value(*args, **kwargs)
        else:
            return self.value

class GridConfig:

    WIDTH = 64
    HEIGHT = 64

    def __init__(self, rows, cols, cells=BasicCellManager(text='', bg='white', fg='black')):
        self.rows = rows
        self.cols = cols
        self.cells = cells

    @staticmethod
    def print_text(draw, text, fg, x, y):
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        if text == '':
            return

        font_size = 12
        while True:
            font = ImageFont.truetype('LiberationSans-Regular.ttf', font_size)
            w, h = font.getsize(text)
            if w < WIDTH and h < HEIGHT:
                break
            font_size -= 1
        draw.text((x - w / 2, y - h / 2), text, font=font, fill=fg)

    def make_grid(self):
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
