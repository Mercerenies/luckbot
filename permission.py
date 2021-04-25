
import error

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

def is_admin(member: discord.abc.User) -> bool:
    if not isinstance(member, discord.Member):
        return False
    return member.guild_permissions.administrator

def must_be_admin(member: discord.abc.User) -> None:
    if not is_admin(member):
        raise error.PermissionsException()

def is_admin_check() -> _CheckDecorator:
    return commands.has_guild_permissions(administrator=True)
