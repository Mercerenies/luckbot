
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
    NamedDieImages("d4_basic", 4),
    NamedDieImages("d6_basic", 6),
    NamedDieImages("d8_fireglow", 8),
    NamedDieImages("d12_coldglow", 12),
]


DICE_MAP = {d.die_name: d for d in ALL_DICE}
