
from PIL import Image, ImageDraw

import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

class GridConfig:

    WIDTH = 64
    HEIGHT = 64

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def make_grid(self):
        WIDTH, HEIGHT = GridConfig.WIDTH, GridConfig.HEIGHT
        n, m = self.rows, self.cols
        image = Image.new("RGBA", (m * WIDTH + 1, n * HEIGHT + 1))
        draw = ImageDraw.Draw(image)
        for i, j in zz.range(0, m).cross_product(zz.range(0, n)):
            pos0 = (i * WIDTH, j * HEIGHT)
            pos1 = ((i + 1) * WIDTH, (j + 1) * HEIGHT)
            draw.rectangle([pos0, pos1], fill='white', outline='black')
        return image
