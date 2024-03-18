
"""Images for the different die faces, available for some dice rolls."""

from dataclasses import dataclass


@dataclass
class NamedDieImages:
    die_name: str
    die_faces: int

    def to_path(self, face: int) -> str:
        if face < 1 or face > self.die_faces:
            raise ValueError(f"Face {face} not in range 1..{self.die_faces}")
        return f"res/dice/{self.die_name}_{face}.jpg"


ALL_DICE = [
    NamedDieImages("d3_purpleglow", 3),
    NamedDieImages("d3_boxy_fireglow", 3),
    NamedDieImages("d4_basic", 4),
    NamedDieImages("d4_magicopal", 4),
    NamedDieImages("d6_basic_inverted", 6),
    NamedDieImages("d6_basic", 6),
    NamedDieImages("d6_magmatic", 6),
    NamedDieImages("d6_marbled", 6),
    NamedDieImages("d6_translucent", 6),
    NamedDieImages("d8_simple", 8),
    NamedDieImages("d8_fireglow", 8),
    NamedDieImages("d10_bluecrystal", 10),
    NamedDieImages("d10_fireglow", 10),
    NamedDieImages("d12_coldglow", 12),
    NamedDieImages("d20_simple", 20),
]


DICE_MAP = {d.die_name: d for d in ALL_DICE}
