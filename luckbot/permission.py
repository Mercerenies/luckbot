
import luckbot.error as error
from luckbot.storage import json_data
from luckbot.deck import Deck

import discord
from discord.ext import commands
import sys

from typing import Callable, TypeVar, Coroutine, Union, Any, TYPE_CHECKING

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

if TYPE_CHECKING:
    _F = TypeVar('_F', bound=Union[Callable[..., Coroutine[Any, Any, Any]], commands.Command[Any]])
else:
    _F = None

class _CheckDecorator(Protocol):
    def __call__(self, __func: _F) -> _F: ...

def is_owner_of_role(member: Union[discord.Member, discord.User], role: discord.Role) -> bool:
    if role.id not in json_data.roles:
        return False
    data = json_data.roles[role.id]
    return member.id in data.owners

def is_owner_of_deck(member: Union[discord.Member, discord.User], deck: Deck) -> bool:
    return member.id in deck.data.owners

def is_admin(member: discord.abc.User) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return member.guild_permissions.administrator

def is_admin_check() -> _CheckDecorator:
    return commands.has_guild_permissions(administrator=True)

def is_admin_or_role_owner(ctx: commands.Context) -> bool:
    if is_admin(ctx.author):
        return True
    if len(ctx.args) < 3:
        return True # Invalid command and not enough info to check against role
    if is_owner_of_role(ctx.author, ctx.args[2]):
        return True
    return False

def is_admin_or_role_owner_check() -> _CheckDecorator:
    return commands.check(is_admin_or_role_owner)

def is_admin_or_deck_owner(ctx: commands.Context) -> bool:
    if is_admin(ctx.author):
        return True
    if len(ctx.args) < 3:
        return True # Invalid command and not enough info to check against role
    if is_owner_of_deck(ctx.author, ctx.args[2]):
        return True
    return False

def is_admin_or_deck_owner_check() -> _CheckDecorator:
    return commands.check(is_admin_or_deck_owner)
