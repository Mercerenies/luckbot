
from error import PermissionsException

import discord.ext.commands as commands
import discord
import traceback

UNHANDLED_RESPONSE = "Something went wrong when I tried to evaluate that command. You'll have to check the logs for more information."

class Response:

    async def perform(self, ctx: commands.Context) -> None:
        pass

    def is_handled(self) -> bool:
        return True

    def or_else(self, other: 'Response') -> 'Response':
        if self.is_handled():
            return self
        else:
            return other

class Handled(Response):
    response_text: str

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text

    async def perform(self, ctx: commands.Context) -> None:
        await ctx.send(self.response_text)

class Unhandled(Response):
    response_text: str
    exc: Exception

    def __init__(self, exc: Exception, response_text: str = UNHANDLED_RESPONSE) -> None:
        self.response_text = response_text
        self.exc = exc

    async def perform(self, ctx: commands.Context) -> None:
        await ctx.send(self.response_text)
        traceback.print_exception(None, self.exc, self.exc.__traceback__)

    def is_handled(self) -> bool:
        return False

# This provides a bunch of attempts to get friendly user-facing error
# messages and falls back to a generic message in case of absolute
# failure.
def appropriate_response(ctx: commands.Context, error: Exception) -> Response:
    if isinstance(error, commands.MissingRequiredArgument):
        return Handled(f"You didn't supply enough arguments. Specifically, I need '{error.param}'")
    elif isinstance(error, commands.ConversionError):
        return appropriate_response(ctx, error.original)
    elif isinstance(error, commands.CommandInvokeError):
        return appropriate_response(ctx, error.original)
    elif isinstance(error, PermissionsException):
        return Handled("You don't have permission to do that.")
    elif isinstance(error, commands.CommandNotFound):
        return Handled(f"Sorry, I don't know what '{ctx.invoked_with}' is.")
    elif isinstance(error, commands.RoleNotFound):
        return Handled(f"I don't know of any role called '{error.argument}'.")
    elif isinstance(error, commands.MemberNotFound):
        return Handled(f"I don't know of any member called '{error.argument}'.")
    return Unhandled(error)
