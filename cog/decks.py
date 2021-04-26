
from storage import json_data, DeckData
from permission import is_admin_check, is_admin_or_deck_owner_check
from util import find_member, Context
import error
from deck import Deck

import discord
from discord.ext import commands
import alakazam as zz
from alakazam import _1, _2, _3, _4, _5

from typing import Union, List, TYPE_CHECKING

MAX_DRAW = 100

# ///// Maximum deck size (configurable by an admin)

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
        await ctx.send(f"Alright, I made a deck called '{name}'.")

    @deck.command()
    @is_admin_check()
    async def delete(self, ctx: Context, deck: Deck) -> None:
        """Delete a deck.

        Admin only."""
        name = deck.data.name
        del json_data.decks[name]
        await ctx.send(f"The deck '{name}' has been deleted.")

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
    async def add(self, ctx: Context, deck: Deck, *cards: str) -> None:
        """Add one or more cards to a deck.

        This adds several cards to the top of the deck in order, so
        that the last card listed will be at the top of the deck. If
        you want to add several copies of the same card, then you may
        find '!deck addmany' more convenient.

        Admins and deck owners only.

        """
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
    async def draw(self, ctx: Context, deck: Deck, count: int = 1) -> None:
        """Draws several cards from the deck.

        If a count is not provided, it defaults to 1."""
        if count > MAX_DRAW:
            raise error.InputsTooLarge()
        cards = deck.draw_cards(count)
        if cards is None:
            await ctx.send("There aren't enough cards in the deck to draw.")
        else:
            await ctx.send(f"{ctx.author} drew: {', '.join(cards)}")

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
