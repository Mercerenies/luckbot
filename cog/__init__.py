
from .roles import RoleManagement
from .luck import LuckCommands
from .admin import Administrative
from .fun import DiscordFun
from .gaming import GamingUtilities

from discord.ext import commands

COGS = [RoleManagement, LuckCommands, Administrative, DiscordFun, GamingUtilities]

def add_cogs(bot: commands.Bot) -> None:
    for cog in COGS:
        bot.add_cog(cog())
