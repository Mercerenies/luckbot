
from PIL import Image, ImageDraw, ImageFont
import random

import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

class CodenameColors:

    def __init__(self, rows, cols, defcolor='white', colors=(('red', 9), ('blue', 9), ('black', 1))):
        self.contents = []

        coordinates = zz.range(rows).cross_product(zz.range(cols)).list()
        random.shuffle(coordinates)

        # Generate
        for i in range(rows):
            arr = []
            for j in range(cols):
                arr.append(defcolor)
            self.contents.append(arr)

        # Fill in
        for c, n in colors:
            for _ in range(n):
                i, j = coordinates.pop()
                self.contents[i][j] = c

    def __call__(self, i, j):
        return self.contents[i][j]

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

    def __init__(self, rows, cols, text='', bgcolor='white', fgcolor='black'):
        self.rows = rows
        self.cols = cols
        self.text = CallGuard(text)
        self.bgcolor = CallGuard(bgcolor)
        self.fgcolor = CallGuard(fgcolor)

    @staticmethod
    def print_text(draw, text, x, y):
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
        draw.text((x - w / 2, y - h / 2), text, font=font, fill='black')

    def make_grid(self):
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        n, m = self.rows, self.cols

        image = Image.new("RGBA", (m * WIDTH + 1, n * HEIGHT + 1))
        draw = ImageDraw.Draw(image)
        for i, j in zz.range(m).cross_product(zz.range(n)):
            pos0 = (i * WIDTH, j * HEIGHT)
            pos1 = ((i + 1) * WIDTH, (j + 1) * HEIGHT)
            draw.rectangle([pos0, pos1], fill=self.bgcolor(i, j), outline=self.fgcolor(i, j))
            text = self.text(i, j)
            GridConfig.print_text(draw, text, (i + 0.5) * WIDTH, (j + 0.5) * HEIGHT)
        return image
