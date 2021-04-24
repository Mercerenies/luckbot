
from util import OptionalChecked, Context

import traceback
from storage import json_data
import dice
import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1
import random

class LuckCommands(commands.Cog, name="Luck-Based Commands"):

    def __init__(self, _bot) -> None:
        pass

    @commands.command()
    async def roll(self, ctx: Context, die: str = None, name: OptionalChecked[discord.Member] = None) -> None:
        """Rolls one or more dice"""

        target_name: object = name or ctx.message.author

        if die is None:
            die = "d6"
        try:
            res = dice.dice(die)
            if res is None:
                await ctx.send("Sorry, I don't understand that.")
                print(("{} made invalid command {}").format(target_name, die))
            else:
                final, data = res
                await ctx.send("{} got {} (individual results: {})".format(target_name, final, data))
        except TypeError:
            await ctx.send("I'm afraid that doesn't make sense...")
            traceback.print_exc()

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
