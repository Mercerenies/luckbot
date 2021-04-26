
import alakazam as zz
from alakazam import _1, _2, _3
import discord
from discord.ext import commands

from typing import Optional, TYPE_CHECKING, Union, TypeVar

T = TypeVar('T')

def find_member(server: discord.Guild, name: str) -> Optional[discord.Member]:
    name = name.lower()
    def match(person: discord.Member) -> bool:
        return (person.name.lower() == name or person.display_name.lower() == name)
    return zz.of(server.members).find(match)

async def log_message(bot: commands.Bot, text: str) -> None:
    channel = zz.of(bot.get_all_channels()).find(_1.name == "bot-logs")
    if channel:
        await channel.send(text)

Context = discord.ext.commands.Context

# This bit of hackery is to reconcile a difference in the way
# discord.py is treating type annotations and the way I want them
# treated in some cases. discord.py treats Optional[T] (equivalently,
# Union[T, NoneType]) as an invitation to attempt to convert to T and,
# if that fails, return None. I want to attempt to convert to T and,
# if that fails, throw a ConversionError, while the argument is still
# optional. That is, I want an argument that can be omitted completely
# but, if provided, must be correct. At type-checking time (mypy),
# OptionChecked = Optional, but at runtime it has a more complicated
# value that interacts with discord.py.
if TYPE_CHECKING:
    FailedParsingNone = type(None)
else:
    class FailedParsingNone(commands.Converter):
        async def convert(ctx: commands.Context, argument: str) -> Optional[type(None)]:
            raise Exception("Failed conversion")
OptionalChecked = Union[T, FailedParsingNone]
