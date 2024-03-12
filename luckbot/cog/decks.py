
from luckbot.storage import json_data, DeckData, DEFAULT_MAX_DECK
from luckbot.permission import is_admin_check, is_admin_or_deck_owner, is_admin_or_deck_owner_check
from luckbot.util import find_member, Context, expand_roles
import luckbot.error as error
from luckbot.deck import Deck, DeckTemplate

import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5
import sys

from typing import Union, List, TYPE_CHECKING, Optional, cast

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

class _FaceConverter:
    @classmethod
    async def convert(_cls, ctx: Context, argument: str) -> Literal["faceup", "facedown"]:
        if argument in ["faceup", "facedown"]:
            return cast(Literal["faceup", "facedown"], argument)
        raise error.BadFaceArgument(argument)

if TYPE_CHECKING:
    Face = Literal["faceup", "facedown"]
else:
    Face = _FaceConverter

MAX_DRAW = 100
MAX_CARD_LEN = 64

def owner_list(server: discord.Guild, deck: Deck) -> List[discord.Member]:
    return zz.of(deck.data.owners).map(server.get_member).filter(_1).list()

class DeckManagement(commands.Cog, name="Deck Management"):

    def __init__(self, _bot) -> None:
        pass

    @commands.group(invoke_without_command=True)
    async def deck(self, ctx: Context) -> None:
        """Commands to manage and draw from decks of cards."""
        await ctx.send_help(ctx.command)

    @deck.command()
    @is_admin_check()
    async def new(self, ctx: Context, name: str) -> None:
        """Make a new deck.

        Admin only."""
        if name in json_data.decks:
            await ctx.send("There's already a deck with that name.")
        json_data.decks[name] = DeckData(name)
        await ctx.send(f"Alright, I made a deck called '{name}' with maximum size {DEFAULT_MAX_DECK}.")

    @deck.command()
    @is_admin_check()
    async def delete(self, ctx: Context, deck: Deck) -> None:
        """Delete a deck.

        Admin only."""
        name = deck.data.name
        del json_data.decks[name]
        await ctx.send(f"The deck '{name}' has been deleted.")

    @deck.command()
    @is_admin_check()
    async def list(self, ctx: Context) -> None:
        """List all decks currently managed by Luckbot.

        Admin only."""
        decks = list(json_data.decks)
        await ctx.send(f"I'm currently managing the following decks: {', '.join(decks)}")

    @deck.command()
    @is_admin_check()
    async def setlimit(self, ctx: Context, deck: Deck, limit: int) -> None:
        """Set the maximum number of cards allowed in the deck.

        Admin only."""
        deck.data.max_deck_size = limit
        await ctx.send(f"Okay, the deck '{deck.data.name}' has limit {limit} now.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def show(self, ctx: Context, deck: Deck) -> None:
        """Shows the current status of the deck, including all cards in the
        draw pile and the discard pile.

        Admins and deck owners only.

        """
        name = deck.data.name
        draw_pile = list(reversed(deck.data.draw_pile))
        discard_pile = list(reversed(deck.data.discard_pile))
        await ctx.send(f"The draw pile for '{name}' is: {', '.join(draw_pile)}")
        await ctx.send(f"The discard pile for '{name}' is: {', '.join(discard_pile)}")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def shuffle(self, ctx: Context, deck: Deck) -> None:
        """Shuffles the deck.

        Admins and deck owners only.

        """
        deck.shuffle()
        await ctx.send("Shuffled successfully.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def replenish(self, ctx: Context, deck: Deck) -> None:
        """Adds the discard pile to the bottom of the draw pile.

        Admins and deck owners only.

        """
        deck.data.draw_pile = list(reversed(deck.data.discard_pile)) + deck.data.draw_pile
        deck.data.discard_pile = []
        await ctx.send("Deck replenished successfully.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def autoreplenish(self, ctx: Context, deck: Deck, b: bool) -> None:
        """Sets whether or not the deck automatically replenishes.

        The default behavior is to not automatically replenish.

        Admins and deck owners only.

        """
        deck.data.autoreplenish = b
        if b:
            await ctx.send("Deck is set to automatically replenish now.")
        else:
            await ctx.send("Deck is set to no longer automatically replenish.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def freedeal(self, ctx: Context, deck: Deck, b: bool) -> None:
        """Sets whether or not any player is allowed to deal from the deck.

        The default behavior (false) only allows the owner to deal
        from the deck.

        Admins and deck owners only.

        """
        deck.data.freedeal = b
        if b:
            await ctx.send("Anyone can deal cards from this deck now.")
        else:
            await ctx.send("Only deck owners can deal from this deck now.")

    @deck.group(invoke_without_command=True)
    async def template(self, ctx: Context) -> None:
        """Commands to load predefined deck templates."""
        await ctx.send_help(ctx.command)

    @template.command(name='load')
    @is_admin_or_deck_owner_check()
    async def template_load(self, ctx: Context, deck: Deck, template: DeckTemplate) -> None:
        """Load a template into a deck.

        Adds all of the cards from the given template into the deck's
        draw pile. There must be enough room in the deck to use this command.

        Admins and deck owners only.

        """
        if deck.total_cards() + len(template.cards) > deck.data.max_deck_size:
            await ctx.send(f"The limit on this deck is {deck.data.max_deck_size}. If you need more cards, you can ask an admin to increase the limit.")
            return
        for card in template.cards:
            deck.place_atop_deck(card)
        await ctx.send("Okay, I added those cards.")

    @template.command(name='list')
    async def template_list(self, ctx: Context) -> None:
        """List all available deck templates."""
        templates = zz.of(DeckTemplate.all()).map(lambda t: f"{t.name} ({len(t.cards)})").list()
        await ctx.send("The following deck templates are available:\n```\n" + '\n'.join(templates) + "\n```")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def add(self, ctx: Context, deck: Deck, *cards: str) -> None:

        """Add one or more cards to a deck.

        This adds several cards to the top of the deck in order, so
        that the last card listed will be at the top of the deck. If
        you want to add several copies of the same card, then you may
        find '!deck addmany' more convenient.

        Admins and deck owners only.

        """
        if zz.of(cards).any(lambda x: len(x) > MAX_CARD_LEN):
            raise error.InputsTooLarge()
        if deck.total_cards() + len(cards) > deck.data.max_deck_size:
            await ctx.send(f"The limit on this deck is {deck.data.max_deck_size}. If you need more cards, you can ask an admin to increase the limit.")
            return
        for card in cards:
            deck.place_atop_deck(card)
        if len(cards) == 0:
            await ctx.send("You didn't specify any cards.")
        elif len(cards) == 1:
            await ctx.send("Okay, I added that card.")
        else:
            await ctx.send("Okay, I added those cards.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def addmany(self, ctx: Context, deck: Deck, card: str, count: int) -> None:
        """Add several copies of the same card to the top of the deck.

        Admins and deck owners only.

        """
        if len(card) > MAX_CARD_LEN:
            raise error.InputsTooLarge()
        if deck.total_cards() + count > deck.data.max_deck_size:
            await ctx.send(f"The limit on this deck is {deck.data.max_deck_size}. If you need more cards, you can ask an admin to increase the limit.")
            return
        for _i in range(count):
            deck.place_atop_deck(card)
        await ctx.send("Okay, I added those cards.")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def remove(self, ctx: Context, deck: Deck, *cards: str) -> None:
        """Removes one or more cards from a deck.

        This command will remove a single card matching each argument
        from the deck, so if there are multiple copies of a card in
        the deck, only the first will be removed. '!deck removeall'
        will remove all copies of a given card. Note that, if a card
        is in both the draw pile and the discard pile, this command
        will search the draw pile first.

        Admins and deck owners only.

        """
        matches = 0
        for card in cards:
            if deck.remove_card(card):
                matches += 1
        await ctx.send(f"Removed a total of {matches} card(s).")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def removeall(self, ctx: Context, deck: Deck, *cards: str) -> None:
        """Removes all cards with the given names from the deck.

        Cards are removed from both the draw pile and the discard
        pile.

        Admins and deck owners only.

        """
        matches = 0
        for card in cards:
            matches += deck.remove_all_cards(card)
        await ctx.send(f"Removed a total of {matches} card(s).")

    @deck.command()
    @is_admin_or_deck_owner_check()
    async def clear(self, ctx: Context, deck: Deck) -> None:
        """Removes all cards from the deck.

        The discard pile and draw pile are both completely emptied.

        Admins and deck owners only.

        """
        matches = len(deck.data.draw_pile) + len(deck.data.discard_pile)
        deck.data.draw_pile = []
        deck.data.discard_pile = []
        await ctx.send(f"Removed a total of {matches} card(s).")

    @deck.command()
    async def draw(self, ctx: Context, deck: Deck, face: Optional[Face] = 'faceup', count: Optional[int] = 1) -> None:
        """Draws several cards from the deck.

        If a count is not provided, it defaults to 1.

        By default, cards are drawn face-up, which means the results
        are posted in the same chat the command was executed. If you
        wish to draw face-down, use '!deck draw <deck> facedown
        [count]' and you'll be DMed the results.

        """
        if face is None:
            face = 'faceup'
        if count is None:
            count = 1
        if count > MAX_DRAW:
            raise error.InputsTooLarge()
        cards = deck.draw_cards(count)
        if cards is None:
            await ctx.send("There aren't enough cards in the deck to draw.")
        elif face == 'faceup':
            await ctx.send(f"{ctx.author} drew: {', '.join(cards)}")
        else:
            await ctx.send(f"{ctx.author} drew card(s).")
            await ctx.author.send(f"You drew: {', '.join(cards)}")

    @deck.command()
    async def deal(self, ctx: Context, deck: Deck, face: Optional[Face] = 'facedown', count: Optional[int] = 1, *targets: discord.Member):
        """Deal cards to players.

        By default, cards are dealt face-down, which means that the
        players are DMed about their cards. If you wish for cards to
        be dealt face-up, use '!deal <deck> faceup [count]
        <members>...'. The players will still be DMed, but Luckbot
        will also announce the cards dealt in the channel where the
        command was issued. This is especially useful if the "deal"
        command is issued via DM, as the member issuing the command
        will be made aware of all cards dealt in this manner.

        """
        if not deck.data.freedeal:
            # Need to be admin or deck owner
            if not is_admin_or_deck_owner(ctx):
                raise commands.CheckFailure()

        if face is None:
            face = 'facedown'
        if count is None:
            count = 1
        if count > MAX_DRAW:
            raise error.InputsTooLarge()

        for target in targets:
            cards = deck.draw_cards(count)
            if cards is None:
                await ctx.send(f"There aren't enough cards in the deck to deal to {target}")
            else:
                await target.send(f"{ctx.author} dealt you the following cards: {', '.join(cards)}")
                if face == 'faceup':
                    await ctx.send(f"{target} was dealt the following cards: {', '.join(cards)}")
                else:
                    await ctx.send(f"{target} was dealt card(s).")

    @deck.command()
    async def peek(self, ctx: Context, deck: Deck, *positions: int) -> None:
        """Peek at a card at a given position in the draw pile."""
        draw_pile = deck.data.draw_pile
        peeks: List[str] = []
        for position in positions:
            if 1 <= position <= len(draw_pile):
                peeks.append(draw_pile[- position])
            else:
                await ctx.send(f"There are {len(draw_pile)} cards in the deck. You can't peek the card at position {position}")
                return
        await ctx.send(f"{ctx.author} peeked and saw: {', '.join(peeks)}")

    @deck.command()
    async def count(self, ctx: Context, deck: Deck) -> None:
        """Show the number of cards in the draw pile and the discard pile."""
        name = deck.data.name
        draw_pile = list(reversed(deck.data.draw_pile))
        discard_pile = list(reversed(deck.data.discard_pile))
        await ctx.send(f"The draw pile for '{name}' has {len(draw_pile)} card(s).")
        await ctx.send(f"The discard pile for '{name}' has {len(discard_pile)} card(s).")

    @deck.group(invoke_without_command=True)
    async def owner(self, ctx: Context):
        """Manage the owner(s) of a deck."""
        await ctx.send_help(ctx.command)

    @owner.command(name='list')
    async def owner_list(self, ctx: Context, deck: Deck) -> None:
        """List all owners of a deck."""
        if ctx.message.guild:
            result = zz.of(owner_list(ctx.message.guild, deck)).map(_1.display_name).list()
        else:
            result = []
        await ctx.send("Members who own the deck {}: {}".format(deck.data.name, ', '.join(result)))

    @owner.command(name='add')
    @is_admin_or_deck_owner_check()
    async def owner_add(self, ctx: Context, deck: Deck, *members: str) -> None:
        """Add owner(s) to a deck. Admins and deck owners only."""
        author = ctx.message.author
        # Add
        for arg in members:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in deck.data.owners:
                await ctx.send("{} already owns {}".format(member.display_name, deck.data.name))
            else:
                deck.data.owners.append(member.id)
                await ctx.send("{} is now an owner of {}".format(member.display_name, deck.data.name))

    @owner.command(name='remove')
    @is_admin_or_deck_owner_check()
    async def owner_remove(self, ctx: Context, deck: Deck, *members: str) -> None:
        """Removes owner(s) to a deck. Admins and deck owners only."""
        author = ctx.message.author
        # Remove
        for arg in members:
            member = ctx.message.guild and find_member(ctx.message.guild, arg)
            if not member:
                await ctx.send("I don't know a {}".format(arg))
            elif member.id in deck.data.owners:
                deck.data.owners.remove(member.id)
                await ctx.send("{} no longer owns {}".format(member.display_name, deck.data.name))
            else:
                await ctx.send("{} doesn't own {}".format(member.display_name, deck.data.name))
