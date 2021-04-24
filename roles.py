
from storage import json_data, RoleData
from permission import is_admin, must_be_admin
from util import find_member

import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Union, List

Context = discord.ext.commands.Context

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

class RoleManagement(commands.Cog):

    @commands.command()
    async def role(self, ctx: Context, cmd: str, *args: str) -> None:
        """Manages roles

        Anyone can use
        !role owner list <rolename>
        !role volunteer <rolename>
        !role unvolunteer <rolename>

        Admin / role owner only
        !role owner add <rolename> <members>...
        !role owner remove <rolename> <members>...
        !role voluntary <rolename>
        !role add <rolename> <members>...
        !role remove <rolename> <members>...

        Admin only
        !role manage <rolename>
        !role unmanage <rolename>"""
        if cmd == "manage":
            await self.role_manage(ctx, *args)
        elif cmd == "unmanage":
            await self.role_unmanage(ctx, *args)
        elif cmd == "owner":
            await self.role_owner(ctx, *args)
        elif cmd == "voluntary":
            await self.role_voluntary(ctx, *args)
        elif cmd == "volunteer":
            await self.role_volunteer(ctx, *args)
        elif cmd == "unvolunteer":
            await self.role_unvolunteer(ctx, *args)
        elif cmd == "add":
            await self.role_add(ctx, *args)
        elif cmd == "remove":
            await self.role_remove(ctx, *args)

    async def role_manage(self, ctx: Context, role_name: str) -> None:
        # !role manage <rolename>
        author = ctx.message.author
        if not isinstance(author, discord.Member):
            return
        must_be_admin(author)
        role = name_to_role(ctx.bot, role_name)
        if role:
            if role.id in json_data.roles:
                await ctx.send("I'm already managing that role.")
            else:
                json_data.roles[role.id] = RoleData()
                json_data.roles[role.id].name = role.name
                await ctx.send("Okay, I'll manage {} now".format(role.name))
        else:
            await ctx.send("I don't know of any role by that name.")

    async def role_unmanage(self, ctx: Context, role_name: str) -> None:
        # !role unmanage <rolename>
        author = ctx.message.author
        if not isinstance(author, discord.Member):
            return
        must_be_admin(author)
        role = name_to_role(ctx.bot, role_name)
        if role and role.id in json_data.roles:
            del json_data.roles[role.id]
            await ctx.send("Okay, I'll forget about {}".format(role.name))
        else:
            await ctx.send("I'm not managing any role by that name.")

    async def role_owner(self, ctx: Context, cmd: str, role_name: str, *args: str):
        # !role owner list <rolename>
        # !role owner add <rolename> <members>...
        # !role owner remove <rolename> <members>...
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        # Anyone can use list
        if cmd == 'list':
            if ctx.message.guild:
                result = zz.of(owner_list(ctx.message.guild, role)).map(_1.display_name).list()
            else:
                result = []
            await ctx.send("Members who own the role {}: {}".format(role.name, ', '.join(result)))
            return
        # Perms
        if (not is_owner_of_role(author, role)) and (not is_admin(author)):
            await ctx.send("You don't have control over that role.")
            return
        # Make sure the owner list exists
        data = json_data.roles[role.id]
        # Add
        if cmd == "add":
            for arg in args:
                member = ctx.message.guild and find_member(ctx.message.guild, arg)
                if not member:
                    await ctx.send("I don't know a {}".format(arg))
                elif member.id in data.owners:
                    await ctx.send("{} already owns {}".format(member.display_name, role.name))
                else:
                    data.owners.append(member.id)
                    await ctx.send("{} is now an owner of {}".format(member.display_name, role.name))
        elif cmd == "remove":
            for arg in args:
                member = ctx.message.guild and find_member(ctx.message.guild, arg)
                if not member:
                    await ctx.send("I don't know a {}".format(arg))
                elif member.id in data.owners:
                    data.owners.remove(member.id)
                    await ctx.send("{} no longer owns {}".format(member.display_name, role.name))
                else:
                    await ctx.send("{} doesn't own {}".format(member.display_name, role.name))

    async def role_voluntary(self, ctx: Context, role_name: str) -> None:
        # !role voluntary <rolename>
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        # Perms
        if (not is_owner_of_role(author, role)) and (not is_admin(author)):
            await ctx.send("You don't have control over that role.")
            return
        if is_voluntary_role(role):
            await ctx.send("{} is no longer a voluntary role".format(role.name))
            json_data.roles[role.id].voluntary = False
        else:
            await ctx.send("Members can now join and leave {} freely".format(role.name))
            json_data.roles[role.id].voluntary = True

    async def role_volunteer(self, ctx: Context, role_name: str) -> None:
        # !role volunteer <rolename>
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        if not is_voluntary_role(role):
            await ctx.send("You can't volunteer for that role")
        elif not isinstance(author, discord.Member):
            await ctx.send("Cannot manage roles in this channel")
        elif role in author.roles:
            await ctx.send("You already belong to that role")
        else:
            await author.add_roles(role)
            await ctx.send("You are now in {}, {}".format(role.name, author.display_name))

    async def role_unvolunteer(self, ctx: Context, role_name: str) -> None:
        # !role unvolunteer <rolename>
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        if not is_voluntary_role(role):
            await ctx.send("You can't unvolunteer for that role")
        elif not isinstance(author, discord.Member):
            await ctx.send("Cannot manage roles in this channel")
        elif role in author.roles:
            await author.remove_roles(role)
            await ctx.send("You are no longer {}, {}".format(role.name, author.display_name))
        else:
            await ctx.send("You don't have that role")

    async def role_add(self, ctx: Context, role_name: str, *args: str) -> None:
        # !role add <rolename> <members>...
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        # Perms
        if (not is_owner_of_role(author, role)) and (not is_admin(author)):
            await ctx.send("You don't have control over that role.")
            return
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif role in member.roles:
                await ctx.send("{} already has {}".format(member.display_name, role.name))
            else:
                await member.add_roles(role)
                await ctx.send("{} now has {}".format(member.display_name, role.name))

    async def role_remove(self, ctx: Context, role_name: str, *args: str) -> None:
        # !role remove <rolename> <members>...
        author = ctx.message.author
        role = name_to_role(ctx.bot, role_name)
        if (not role) or (role.id not in json_data.roles):
            await ctx.send("I'm not managing any role by that name.")
            return
        # Perms
        if (not is_owner_of_role(author, role)) and (not is_admin(author)):
            await ctx.send("You don't have control over that role.")
            return
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif role in member.roles:
                await member.remove_roles(role)
                await ctx.send("{} no longer has {}".format(member.display_name, role.name))
            else:
                await ctx.send("{} doesn't have {}".format(member.display_name, role.name))

