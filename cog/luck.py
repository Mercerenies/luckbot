
from util import OptionalChecked, Context

import traceback
import dice
from dice.parser import MAXIMUM_IMAGES
import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1
import random
import os.path
from typing import Iterable
from contextlib import ExitStack


class LuckCommands(commands.Cog, name="Luck-Based Commands"):

    def __init__(self, _bot) -> None:
        pass

    @commands.command()
    async def roll(self, ctx: Context, die: str = "d6", name: OptionalChecked[discord.Member] = None) -> None:
        """Rolls one or more dice"""

        target_name: object = name or ctx.message.author

        try:
            res = dice.dice(die)
            if res is None:
                await ctx.send("Sorry, I don't understand that.")
                print(("{} made invalid command {}").format(target_name, die))
            else:
                final, data = res
                await ctx.send("{} got {} (individual results: {})".format(target_name, final.value, data))
                if len(final.images) <= MAXIMUM_IMAGES:
                    await self._send_images(ctx, final.images)
        except TypeError:
            await ctx.send("I'm afraid that doesn't make sense...")
            traceback.print_exc()

    async def _send_images(self, ctx: Context, images: Iterable[str]) -> None:
        with ExitStack() as stack:
            embeds = []
            files = []
            for i, image_path in enumerate(images):
                image = stack.enter_context(open(image_path, 'rb'))
                filename = f'image{i}.png'
                file = discord.File(image, filename)
                embed = discord.Embed(url='https://localhost:8080')
                embed.set_image(url='attachment://' + filename)
                embeds.append(embed)
                files.append(file)
            await ctx.send(files=files, embeds=embeds)

    @commands.command()
    async def listdice(self, ctx: Context) -> None:
        """Lists all available named dice"""
        dice_list = '\n'.join(f"* {d.die_name}" for d in dice.ALL_DICE)
        await ctx.send(f"All named dice:\n{dice_list}")

    @commands.command()
    async def volunteer(self, ctx: Context, role: OptionalChecked[discord.Role] = None):
        """Randomly selects a player"""
        choices = zz.of(ctx.bot.get_all_members())
        if role:
            choices = choices.filter(lambda x: zz.of(x.roles).find(_1.id == role.id))
        choices = choices.list()
        member = random.choice(choices)
        await ctx.send("I choose {}!".format(member.name))

    @commands.command()
    async def choose(self, ctx: Context, vals: str, n: int = 1) -> None:
        """Chooses from a collection of elements.
        The values should be separated by a semicolon."""
        vals1 = vals.split(';')
        results = random.sample(vals1, n)
        await ctx.send("Drawing {} items: {}.".format(n, ', '.join(results)))
