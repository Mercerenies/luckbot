
from storage import json_data

import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Union, List

def name_to_role(bot: commands.Bot, name: str) -> discord.Role:
    return zz.of(bot.guilds).map(_1.roles).flatten().find(_1.name == name)

def is_owner_of_role(member: Union[discord.Member, discord.User], role: discord.Role) -> bool:
    if role.id not in json_data.roles:
        return False
    data = json_data.roles[role.id]
    return member.id in data.owners

def is_voluntary_role(role: discord.Role) -> bool:
    if role.id not in json_data.roles:
        return False
    data = json_data.roles[role.id]
    return data.voluntary

def owner_list(server: discord.Guild, role: discord.Role) -> List[discord.Member]:
    if role.id not in json_data.roles:
        return []
    data = json_data.roles[role.id]
    return zz.of(data.owners).map(server.get_member).filter(_1).list()

"""
class RoleManagement(commands.Cog):

    @commands.command()
"""
