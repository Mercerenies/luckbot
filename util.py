
import alakazam as zz
import discord

from typing import Optional

def find_member(server: discord.Guild, name: str) -> Optional[discord.Member]:
    name = name.lower()
    def match(person: discord.Member) -> bool:
        return (person.name.lower() == name or person.display_name.lower() == name)
    return zz.of(server.members).find(match)
