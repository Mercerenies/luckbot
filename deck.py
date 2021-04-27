
from storage import json_data, DeckData
from error import DeckNotFound, DeckTemplateNotFound

import random
from discord.ext import commands
import json

from typing import Iterator, Optional, List, TypeVar, Type, Dict

_T = TypeVar('_T', bound='Deck')
_S = TypeVar('_S', bound='DeckTemplate')

_TEMPLATES: Dict[str, List[str]] = {}

# This wrapper class provides conventional "deck of cards"
# functionality such as shuffling and drawing cards. If you're looking
# for administrative functionality like ownership and permissions, use
# DeckData directly.
class Deck:
    data: DeckData

    def __init__(self, data: DeckData) -> None:
        self.data = data

    def total_cards(self) -> int:
        return len(self.data.draw_pile) + len(self.data.discard_pile)

    def shuffle(self) -> None:
        random.shuffle(self.data.draw_pile)

    def replace_discard_pile(self) -> None:
        self.data.draw_pile += list(reversed(self.data.discard_pile))
        self.data.discard_pile = []

    def _draw_one(self) -> Optional[str]:
        if self.data.draw_pile:
            return self.data.draw_pile.pop()
        if self.data.autoreplenish and self.data.discard_pile:
            self.data.draw_pile, self.data.discard_pile = self.data.discard_pile, []
            self.shuffle()
            return self.data.draw_pile.pop()
        return None

    def draw_cards(self, n: int) -> Optional[List[str]]:
        if len(self.data.draw_pile) == len(self.data.discard_pile) == 0:
            return None # Deck is empty
        if len(self.data.draw_pile) < n and not self.data.autoreplenish:
            return None
        cards = []
        for _i in range(n):
            card = self._draw_one()
            if card is None:
                break
            cards.append(card)
            self.data.discard_pile.append(card)
        return cards

    def place_atop_deck(self, card: str) -> None:
        self.data.draw_pile.append(card)

    def remove_card(self, card: str) -> bool:
        """Returns true if the card was successfully removed, false if there
        was no such card. Favors the draw pile.

        """
        if card in self.data.draw_pile:
            self.data.draw_pile.remove(card)
            return True
        elif card in self.data.discard_pile:
            self.data.discard_pile.remove(card)
            return True
        else:
            return False

    def remove_all_cards(self, card: str) -> int:
        """Removes all of the cards with the given name from the deck. Returns
        the number of cards removed.

        """
        n = 0
        while self.remove_card(card):
            n += 1
        return n

    # This method allows us to use Deck as a Discord.py converter.
    @classmethod
    async def convert(cls: Type[_T], ctx: commands.Context, argument: str) -> _T:
        decks = json_data.decks
        for id in decks:
            if decks[id].name == argument:
                return cls(decks[id])
        raise DeckNotFound(argument)

class DeckTemplate:
    name: str
    cards: List[str]

    def __init__(self, name: str, cards: List[str]) -> None:
        self.name = name
        self.cards = cards

    @classmethod
    async def convert(cls: Type[_S], ctx: commands.Context, argument: str) -> _S:
        if argument.lower() in _TEMPLATES:
            return cls(argument.lower(), _TEMPLATES[argument.lower()])
        raise DeckTemplateNotFound(argument)

    @staticmethod
    def all() -> Iterator['DeckTemplate']:
        for k, v in _TEMPLATES.items():
            yield DeckTemplate(k, v)

with open('deck_templates.json') as f:
    _TEMPLATES = json.load(f)
    # Validate the information we just loaded
    for k in _TEMPLATES:
        if not isinstance(_TEMPLATES[k], list):
            print("Invalid format in deck_templates.json at", k)
            exit(1)
        for x in _TEMPLATES[k]:
            if not isinstance(x, str):
                print("Invalid format in deck_templates.json at", k)
                exit(1)
