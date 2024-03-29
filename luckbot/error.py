
from discord.ext import commands

class UnmanagedRole(commands.BadArgument):
    pass

class PermissionsException(Exception):
    pass

class InputsTooLarge(Exception):
    pass

class TooManyMembers(Exception):
    pass

class BadFaceArgument(commands.BadArgument):
    argument: str

    def __init__(self, argument: str) -> None:
        self.argument = argument

class DeckNotFound(commands.BadArgument):
    argument: str

    def __init__(self, argument: str) -> None:
        self.argument = argument

class DeckTemplateNotFound(commands.BadArgument):
    argument: str

    def __init__(self, argument: str) -> None:
        self.argument = argument
