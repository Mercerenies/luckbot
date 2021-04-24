
from util import Context
from storage import json_data

import random
import discord
from discord.ext import commands
import alakazam as zz

class DiscordFun(commands.Cog, name="Discord Fun"):

    @commands.command()
    async def genitem(self, ctx: Context, item_name: str):
        """Generates an item"""
        #0 = Dex, 1 = Intr, 2 = Str, 3 = Cont, 4 = Wis
        stat_int = random.randint(0, 4)
        stat_range = random.randint(-3, 10)

        if ('dumb' in item_name):
            stat_int = 1
            stat_range = random.randint(-5, -1)

        if ('intelligence' in item_name):
            stat_int = 1
            stat_range = random.randint(1, 10)

        if ('weakness' in item_name):
            stat_int = 2
            stat_range = random.randint(-5, -1)

        if ('strength' in item_name):
            stat_int = 2
            stat_range = random.randint(1, 10)

        if ('slow' in item_name):
            stat_int = 0
            stat_range = random.randint(-5, -1)

        if ('speed' in item_name):
            stat_int = 0
            stat_range = random.randint(1, 10)

        if ('swiftness' in item_name):
            stat_int = 0
            stat_range = random.randint(1, 10)

        if ('drain' in item_name):
            stat_int = 3
            stat_range = random.randint(-5, -1)

        if ('protection' in item_name):
            stat_int = 3
            stat_range = random.randint(1, 10)

        if ('ignorance' in item_name):
            stat_int = 4
            stat_range = random.randint(-5, -1)

        if ('wisdom' in item_name):
            stat_int = 4
            stat_range = random.randint(1, 10)

        if (stat_range == 0):
            stat_range = 1
        stat = ""
        if (stat_int == 0):
            stat = "Dexterity"

        if (stat_int == 1):
            stat = "Intelligence"

        if (stat_int == 2):
            stat = "Strength"

        if (stat_int == 3):
            stat = "Constitution"

        if (stat_int == 4):
            stat = "Wisdom"

        if (stat_range < 0):
            await ctx.send(str(item_name) + "\n" + stat + ": " + str(stat_range))

        if (stat_range > 0):
            await ctx.send(str(item_name) + "\n" + stat + ": +" + str(stat_range))

    @commands.command()
    async def genchar(self, ctx: Context, minlevel: int, maxlevel: int, pokemon: str):
        """Generates a character"""

        randlevel = random.randint(minlevel, maxlevel)
        dex = random.randint(-5, 5)
        itl = random.randint(-5, 5)
        sre = random.randint(-5, 5)
        con = random.randint(-5, 5)
        wis = random.randint(-5, 5)
        cha = random.randint(-5, 5)

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            dex += randlevel

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            itl += randlevel

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            sre += randlevel

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            con += randlevel

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            wis += randlevel

        rarr = random.randint(randlevel, 100)
        if (rarr >= 80):
            cha += randlevel

        hlt = (4*randlevel) + con
        xpr = hlt - (randlevel * 3)

        await ctx.send(pokemon + "'s Stats\nLevel: " + str(randlevel) + "\nHP: " + str(hlt) + "\nDexterity: " + str(dex) + "\nIntelligence: " + str(itl) + "\nStrength: " + str(sre) + "\nConstitution: " + str(con) + "\nWisdom: " + str(wis) + "\nCharisma: " + str(cha))

    @commands.command()
    async def votes(self, ctx: Context) -> None:
        """How good of a bot am I?"""
        if json_data.good > json_data.bad:
            await ctx.send("This bot is a good bot. Voted {} to {}.".format(json_data.good, json_data.bad))
        elif json_data.bad > json_data.good:
            await ctx.send("This bot is a bad bot. Voted {} to {}.".format(json_data.bad, json_data.good))
        else:
            await ctx.send("This bot is an okay bot. Voted {} to {}.".format(json_data.good, json_data.bad))

    @commands.command()
    async def ducksay(self, ctx: Context, message: str) -> None:
        """Duck says what?"""
        MAX_LEN = 50
        data = message.split(' ')
        res = []
        curr = ""
        for val in data:
            new = curr + ' ' + val if curr else curr + val
            if len(new) >= MAX_LEN:
                res.append(curr)
                curr = ""
                new = curr + val
            curr = new
        if curr:
            res.append(curr)
        max_len = len(zz.of(res).max(len))
        if len(res) > 1:
            delim = zz.empty().chain(
                zz.of(["/\\"]),
                zz.repeat("||", n = len(res) - 2),
                zz.of(["\\/"])
            )
        else:
            delim = zz.repeat("<>")
        final = ''
        final += "```\n"
        final += " " + "_" * (max_len + 2) + " \n"
        for d, elem in zip(delim, res):
            elem += " " * (max_len - len(elem))
            final += d[0] + " " + elem + " " + d[1] + "\n"
        final += " " + "-" * (max_len + 2) + " \n"
        final += "  \\\n"
        final += "   \\\n"
        final += "    \\ >()_\n"
        final += "       (__)__ _\n"
        final += "```"
        await ctx.send(final)
