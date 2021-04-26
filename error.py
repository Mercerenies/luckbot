
from discord.ext import commands

class UnmanagedRole(commands.BadArgument):
    pass

class PermissionsException(Exception):
    pass

class InputsTooLarge(Exception):
    pass
