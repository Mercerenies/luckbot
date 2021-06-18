
import discord
import error

import json
from dataclasses import dataclass
import random

from typing import Dict, List, Iterator, Tuple

_SPYFALL_DATA: Dict[str, List[str]] = {}

SPY_ROLE = "Spy"

@dataclass(frozen=True)
class Location:
    name: str
    roles: List[str]

    @staticmethod
    def all() -> 'Iterator[Location]':
        for k, v in _SPYFALL_DATA.items():
            yield Location(name=k, roles=v)

    @staticmethod
    def random() -> 'Location':
        choices = list(Location.all())
        return random.choice(choices)

    def role_card(self, *, role: str, member_name: str) -> discord.Embed:
        return role_card(location=self.name, role=role, member_name=member_name)

    def choose_roles(self, members: List[discord.Member]) -> List[Tuple[discord.Member, str]]:
        if len(members) > len(self.roles) + 1:
            raise error.TooManyMembers(f"Too many members to play Spyfall")
        roles = self.roles[:]
        random.shuffle(roles)
        roles = [SPY_ROLE] + roles
        return list(zip(members, roles))

def role_card(*, location: str, role: str, member_name: str) -> discord.Embed:
    embed = discord.Embed(title=f"Spyfall Role - {member_name}", description="", color=0x000000)
    embed.add_field(name="Location", value="???" if role == SPY_ROLE else location)
    embed.add_field(name="Role", value=role)
    return embed

with open("spyfall.json") as f:
    _SPYFALL_DATA = json.load(f)
    # Validate
    for k in _SPYFALL_DATA:
        if not isinstance(_SPYFALL_DATA[k], list):
            print("Invalid format in spyfall.json at", k)
            exit(1)
        if len(_SPYFALL_DATA[k]) != 7:
            print("Invalid format in spyfall.json at", k)
            exit(1)
        for x in _SPYFALL_DATA[k]:
            if not isinstance(x, str):
                print("Invalid format in spyfall.json at", k)
                exit(1)

