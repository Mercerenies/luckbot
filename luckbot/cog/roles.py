
from luckbot.storage import json_data, RoleData
from luckbot.permission import is_admin_check, is_admin_or_role_owner_check
from luckbot.util import find_member, Context
import luckbot.error as error

import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    ManagedRole = discord.Role
else:
    class ManagedRole(commands.Converter):
        _inner: commands.RoleConverter

        def __init__(self):
            self._inner = commands.RoleConverter()

        async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
            role = await self._inner.convert(ctx, argument)
            if role.id not in json_data.roles:
                raise error.UnmanagedRole()
            return role

def name_to_role(bot: commands.Bot, name: str) -> discord.Role:
    return zz.of(bot.guilds).map(_1.roles).flatten().find(_1.name == name)

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

class RoleManagement(commands.Cog, name="Role Management"):

    def __init__(self, _bot) -> None:
        pass

    @commands.group(invoke_without_command=True)
    async def role(self, ctx: Context) -> None:
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
        await ctx.send_help(ctx.command)

    @role.command()
    @is_admin_check()
    async def manage(self, ctx: Context, role: discord.Role) -> None:
        """Set up Luckbot to manage a role. Admin only."""
        author = ctx.message.author
        if not isinstance(author, discord.Member):
            return
        if role.id in json_data.roles:
            await ctx.send("I'm already managing that role.")
        else:
            json_data.roles[role.id] = RoleData()
            json_data.roles[role.id].name = role.name
            await ctx.send("Okay, I'll manage {} now".format(role.name))

    @role.command()
    @is_admin_check()
    async def unmanage(self, ctx: Context, role: discord.Role) -> None:
        """Tell Luckbot to stop managing a role. This deletes any information
        the bot had on the role. Admin only."""
        author = ctx.message.author
        if role.id in json_data.roles:
            del json_data.roles[role.id]
            await ctx.send("Okay, I'll forget about {}".format(role.name))
        else:
            await ctx.send("I'm not managing any role by that name.")

    @role.group(invoke_without_command=True)
    async def owner(self, ctx: Context):
        """Manage the owner(s) of a role.

        Anyone can use
        !role owner list <rolename>

        Admin / role owner only
        !role owner add <rolename> <members>...
        !role owner remove <rolename> <members>..."""
        await ctx.send_help(ctx.command)

    @role.command()
    @is_admin_or_role_owner_check()
    async def voluntary(self, ctx: Context, role: ManagedRole) -> None:
        """Toggle whether or not the given role can be opted into and out of.
        Admins and role owners only."""
        author = ctx.message.author
        if is_voluntary_role(role):
            await ctx.send("{} is no longer a voluntary role".format(role.name))
            json_data.roles[role.id].voluntary = False
        else:
            await ctx.send("Members can now join and leave {} freely".format(role.name))
            json_data.roles[role.id].voluntary = True

    @role.command()
    async def volunteer(self, ctx: Context, role: ManagedRole) -> None:
        """Volunteer for a role. Can only be used on roles which are set as voluntary."""
        author = ctx.message.author
        if not is_voluntary_role(role):
            await ctx.send("You can't volunteer for that role")
        elif not isinstance(author, discord.Member):
            await ctx.send("Cannot manage roles in this channel")
        elif role in author.roles:
            await ctx.send("You already belong to that role")
        else:
            await author.add_roles(role)
            await ctx.send("You are now in {}, {}".format(role.name, author.display_name))

    @role.command()
    async def unvolunteer(self, ctx: Context, role: ManagedRole) -> None:
        """Opt out of a role. Can only be used on roles which are set as voluntary."""
        author = ctx.message.author
        if not is_voluntary_role(role):
            await ctx.send("You can't unvolunteer for that role")
        elif not isinstance(author, discord.Member):
            await ctx.send("Cannot manage roles in this channel")
        elif role in author.roles:
            await author.remove_roles(role)
            await ctx.send("You are no longer {}, {}".format(role.name, author.display_name))
        else:
            await ctx.send("You don't have that role")

    @role.command()
    @is_admin_or_role_owner_check()
    async def add(self, ctx: Context, role: ManagedRole, *args: str) -> None:
        """Add member(s) to a role. Admins and role owners only."""
        author = ctx.message.author
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif role in member.roles:
                await ctx.send("{} already has {}".format(member.display_name, role.name))
            else:
                await member.add_roles(role)
                await ctx.send("{} now has {}".format(member.display_name, role.name))

    @role.command()
    @is_admin_or_role_owner_check()
    async def remove(self, ctx: Context, role: ManagedRole, *args: str) -> None:
        """Remove member(s) to a role. Admins and role owners only."""
        author = ctx.message.author
        for arg in args:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif role in member.roles:
                await member.remove_roles(role)
                await ctx.send("{} no longer has {}".format(member.display_name, role.name))
            else:
                await ctx.send("{} doesn't have {}".format(member.display_name, role.name))

    @owner.command(name='list')
    async def owner_list(self, ctx: Context, role: ManagedRole) -> None:
        """List all owners of a role."""
        if ctx.message.guild:
            result = zz.of(owner_list(ctx.message.guild, role)).map(_1.display_name).list()
        else:
            result = []
        await ctx.send("Members who own the role {}: {}".format(role.name, ', '.join(result)))

    @owner.command(name='add')
    @is_admin_or_role_owner_check()
    async def owner_add(self, ctx: Context, role: ManagedRole, *members: str) -> None:
        """Add owner(s) to a role. Admins and role owners only."""
        author = ctx.message.author
        # Make sure the owner list exists
        data = json_data.roles[role.id]
        # Add
        for arg in members:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in data.owners:
                await ctx.send("{} already owns {}".format(member.display_name, role.name))
            else:
                data.owners.append(member.id)
                await ctx.send("{} is now an owner of {}".format(member.display_name, role.name))

    @owner.command(name='remove')
    @is_admin_or_role_owner_check()
    async def owner_remove(self, ctx: Context, role: ManagedRole, *members: str) -> None:
        """Removes owner(s) to a role. Admins and role owners only."""
        author = ctx.message.author
        # Make sure the owner list exists
        data = json_data.roles[role.id]
        # Remove
        for arg in members:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in data.owners:
                data.owners.remove(member.id)
                await ctx.send("{} no longer owns {}".format(member.display_name, role.name))
            else:
                await ctx.send("{} doesn't own {}".format(member.display_name, role.name))
