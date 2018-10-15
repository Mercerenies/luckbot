
from PIL import Image, ImageDraw
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

class GridConfig:

    WIDTH = 64
    HEIGHT = 64

    def __init__(self, rows, cols, bgcolor='white', fgcolor='black'):
        self.rows = rows
        self.cols = cols
        self.bgcolor = bgcolor if callable(bgcolor) else lambda i, j: bgcolor
        self.fgcolor = fgcolor if callable(fgcolor) else lambda i, j: fgcolor

    def make_grid(self):
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        n, m = self.rows, self.cols

        image = Image.new("RGBA", (m * WIDTH + 1, n * HEIGHT + 1))
        draw = ImageDraw.Draw(image)
        for i, j in zz.range(m).cross_product(zz.range(n)):
            pos0 = (i * WIDTH, j * HEIGHT)
            pos1 = ((i + 1) * WIDTH, (j + 1) * HEIGHT)
            draw.rectangle([pos0, pos1], fill=self.bgcolor(i, j), outline=self.fgcolor(i, j))
        return image
