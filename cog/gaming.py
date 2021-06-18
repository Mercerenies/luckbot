
from util import Context, expand_roles
from grid import GridConfig, WordList, DefaultWordList, CustomWordList, CodenameManager
from error import InputsTooLarge
from spyfall import Location as SpyfallLocation

import discord
from discord.ext import commands

from io import BytesIO
import re

from typing import Optional, Union

MAX_GRID_SIZE = 50

async def send_image_of_grid(ctx: Context, cfg: GridConfig, filename: str = "image.png") -> None:
    image = cfg.make_grid()
    with BytesIO() as buffer:
        image.save(buffer, 'PNG')
        buffer.seek(0)
        f = discord.File(buffer, filename)
        await ctx.send(file=f)

class GamingUtilities(commands.Cog, name="Gaming Utilities"):

    def __init__(self, _bot) -> None:
        pass

    @commands.command()
    async def grid(self, ctx: Context, dims: str = "3x3") -> None:
        """Generates a grid.

        !grid NxM

        """
        n, m = map(int, re.findall(r"[0-9]+", dims))
        if n > MAX_GRID_SIZE or m > MAX_GRID_SIZE:
            raise InputsTooLarge()
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

    @commands.command()
    async def spyfall(self, ctx: Context, *targets: Union[discord.Member, discord.Role]) -> None:
        """Deals out roles for a game of Spyfall.

        !spyfall <targets...>

        The targets can be either members or a role. If a role is
        provided, all members who have that role will be considered
        players.

        """
        members = list(expand_roles(targets))
        location = SpyfallLocation.random()
        game_roles = location.choose_roles(members)
        for member, role in game_roles:
            await member.send(embed=location.role_card(role=role, member_name=member.name))
        await ctx.send("I've dealt out everybody's Spyfall roles. Good luck!")
