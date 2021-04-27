
from error import PermissionsException, InputsTooLarge, UnmanagedRole, DeckNotFound, DeckTemplateNotFound, BadFaceArgument

import discord.ext.commands as commands
import discord
import traceback

from typing import TypeVar, Generic

UNHANDLED_RESPONSE = "Something went wrong when I tried to evaluate that command. You'll have to check the logs for more information."

T_co = TypeVar('T_co', covariant=True, bound='Response')

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

    def with_debug_output(self: T_co, debug_output: str) -> 'WithDebugOutput[T_co]':
        return WithDebugOutput(self, debug_output)

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

class WithDebugOutput(Generic[T_co], Response):
    response: T_co
    debug_output: str

    def __init__(self, response: T_co, debug_output: str) -> None:
        self.response = response
        self.debug_output = debug_output

    async def perform(self, ctx: commands.Context) -> None:
        await self.response.perform(ctx)
        print(self.debug_output)

    def is_handled(self) -> bool:
        return self.response.is_handled()

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
    elif isinstance(error, commands.BadUnionArgument):
        for err in error.errors:
            h = appropriate_response(ctx, err)
            if h.is_handled():
                return h
        return Unhandled(error)
    elif isinstance(error, commands.CheckFailure):
        return Handled("You don't have permission to do that.")
    elif isinstance(error, UnmanagedRole):
        return Handled("I'm not managing that role. You'll need to have an admin use `!role manage` if you want me to manage it.")
    elif isinstance(error, InputsTooLarge):
        return Handled("Stahp!").with_debug_output(f"{ctx.author} exceeded the limit using command {ctx.invoked_with}!")
    elif isinstance(error, DeckNotFound):
        return Handled(f"I don't know of any deck called '{error.argument}'.")
    elif isinstance(error, DeckTemplateNotFound):
        return Handled(f"I don't know of any deck template called '{error.argument}'.")
    elif isinstance(error, BadFaceArgument):
        return Handled(f"I was expecting faceup or facedown, but got '{error.argument}'.")
    return Unhandled(error)
