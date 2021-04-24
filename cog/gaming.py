
from util import Context
from grid import GridConfig, WordList, DefaultWordList, CustomWordList, CodenameManager

import discord
from discord.ext import commands

from io import BytesIO
import re

from typing import Optional

async def send_image_of_grid(ctx: Context, cfg: GridConfig, filename: str = "image.png") -> None:
    image = cfg.make_grid()
    with BytesIO() as buffer:
        image.save(buffer, 'PNG')
        buffer.seek(0)
        f = discord.File(buffer, filename)
        await ctx.send(file=f)

class GamingUtilities(commands.Cog, name="Gaming Utilities"):

    @commands.command()
    async def grid(self, ctx: Context, dims: str = "3x3") -> None:
        """Generates a grid.

        !grid NxM

        """
        n, m = map(int, re.findall(r"[0-9]+", dims))
        cfg = GridConfig(rows=n, cols=m)
        await send_image_of_grid(ctx, cfg)

    @commands.command()
    async def codenames(self, ctx: Context, words: Optional[str] = None) -> None:
        """Generates a Codenames board.

        !codenames <words>

        If provided, the word list should be a semicolon-separated list of
        words to include. The list must contain at least 25 elements but
        can contain more.

        """

        wordlist: WordList
        if words is None:
            wordlist = DefaultWordList()
        else:
            words1 = words.split(';')
            if len(words1) < 25:
                await ctx.send("Not enough words.")
                return
            wordlist = CustomWordList(words1)

        manager = CodenameManager(rows=5, cols=5, words=wordlist)
        cfg  = GridConfig(rows=5, cols=5, cells=manager)
        cfg1 = GridConfig(rows=5, cols=5, cells=manager.hidden())
        await send_image_of_grid(ctx, cfg )
        await send_image_of_grid(ctx, cfg1)
