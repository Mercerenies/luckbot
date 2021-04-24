
from permission import must_be_admin, is_admin
from util import Context, OptionalChecked
import timezone as tz
from storage import json_data

import discord
from discord.ext import commands

class Administrative(commands.Cog, name="Administrative"):

    @commands.command()
    async def assignlinkrole(self, ctx: Context, role: OptionalChecked[discord.Role] = None) -> None:
        """Determines the role used for spam-checking against links.

        !assignlinkrole <role_name>

        (admin only)

        """
        if not is_admin(ctx.message.author):
            await ctx.send("You don't have permission to do that")
        elif not role:
            await ctx.send("I'll no longer mess with links")
            del json_data.linky
        else:
            await ctx.send("I'll make sure this server stays spam-free!")
            json_data.linky = role.id

    @commands.command()
    async def whois(self, ctx: Context, member: discord.Member) -> None:
        """Identifies a member of this server.

        !whois <name>

        If I recognize the name of that person, I'll tell you who it
        is.

        """
        embed = discord.Embed(title="", description="", color=0x000000)
        embed.add_field(name="Name", value=str(member), inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)
        embed.add_field(name="Bot?", value=str(member.bot), inline=True)
        embed.set_thumbnail(url=str(member.avatar_url or member.default_avatar_url))
        await ctx.send(embed=embed)

    @commands.command()
    async def timezone(self, ctx: Context, time: str, frm: str, keyword: str, to: str) -> None:
        """Converts between timezones
        !timezone <time> <from-zone> to <to-zone>"""
        if not tz.is_timezone(frm) or not tz.is_timezone(to):
            await ctx.send("I don't know that timezone... sorry...")
            return None
        res = tz.convert_formatted(time, frm, to)
        if res:
            hr, min = res
            cap = ''
            if hr < 0:
                cap = " on the previous day"
                hr += 24
            if hr > 24:
                cap = " on the following day"
                hr -= 24
            tzname = tz.timezone_name(to)
            await ctx.send("In {}, that's {}:{:-02}{}!".format(tzname, int(hr), int(min), cap))
        else:
            await ctx.send("Sorry... I didn't understand the time format...")

    @commands.command()
    async def playing(self, ctx: Context, *, mygame: str = ''):
        """Sets my presence tagline.

        (admin only)"""
        must_be_admin(ctx.author)
        game = discord.Game(name=mygame) if mygame != '' else None
        await ctx.bot.change_presence(activity=game)
