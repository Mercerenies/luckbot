
from permission import is_admin_check
from util import Context, OptionalChecked, log_message
import timezone as tz
from storage import json_data

import alakazam as zz
from alakazam import _1, _2, _3
import discord
from discord.ext import commands
import re

LINK_RE = re.compile("https?://|discord.gg/|discordapp.com/")

def contains_link(text: str) -> bool:
    return bool(re.search(LINK_RE, text))

class Administrative(commands.Cog, name="Administrative"):
    _bot: commands.Bot

    def __init__(self, bot) -> None:
        self._bot = bot

    async def spam_check(self, message: discord.Message) -> None:
        if message.author == self._bot.user:
            return
        if json_data.linky and contains_link(message.content):
            role = json_data.linky
            if isinstance(message.author, discord.Member):
                if role not in zz.of(message.author.roles).map(_1.id):
                    await message.delete()
                    await message.author.send("You don't have permission to post links. Feel free to ask an admin for this permission :)")
                    await log_message(self._bot, "{} (in channel #{}) just tried to post the link: {}".format(message.author, message.channel, message.content))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self._bot.user:
            return
        await self.spam_check(message) # Spam checking for links

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        await self.spam_check(after)

    @commands.command()
    @is_admin_check()
    async def assignlinkrole(self, ctx: Context, role: OptionalChecked[discord.Role] = None) -> None:
        """Determines the role used for spam-checking against links.

        !assignlinkrole [role]

        (admin only)

        """
        if not role:
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
        if not tz.is_timezone(frm):
            await ctx.send(f"I don't know the timezone '{frm}'... sorry...")
            return
        if not tz.is_timezone(to):
            await ctx.send(f"I don't know the timezone '{to}'... sorry...")
            return
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
    @is_admin_check()
    async def playing(self, ctx: Context, mygame: str = ''):
        """Sets my presence tagline.

        (admin only)"""
        game = discord.Game(name=mygame) if mygame != '' else None
        await ctx.bot.change_presence(activity=game)
