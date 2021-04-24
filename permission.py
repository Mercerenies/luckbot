
import error

import discord

def is_admin(member: discord.abc.User) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return member.guild_permissions.administrator

def must_be_admin(member: discord.abc.User) -> None:
    if not is_admin(member):
        raise error.PermissionsException()
