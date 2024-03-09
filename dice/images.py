
"""Images for the different die faces, available for some dice rolls."""

from typing import Optional

IMAGES_D6 = {
    1: "res/dice/d6_basic_1.jpg",
    2: "res/dice/d6_basic_2.jpg",
    3: "res/dice/d6_basic_3.jpg",
    4: "res/dice/d6_basic_4.jpg",
    5: "res/dice/d6_basic_5.jpg",
    6: "res/dice/d6_basic_6.jpg",
}

IMAGES_D8 = {
    1: "res/dice/d8_fireglow_1.jpg",
    2: "res/dice/d8_fireglow_2.jpg",
    3: "res/dice/d8_fireglow_3.jpg",
    4: "res/dice/d8_fireglow_4.jpg",
    5: "res/dice/d8_fireglow_5.jpg",
    6: "res/dice/d8_fireglow_6.jpg",
    7: "res/dice/d8_fireglow_7.jpg",
    8: "res/dice/d8_fireglow_8.jpg",
}


def image_for(dice_total: int, dice_face: int) -> Optional[str]:
    if dice_total == 6:
        return IMAGES_D6.get(dice_face)
    elif dice_total == 8:
        return IMAGES_D8.get(dice_face)
    else:
        return None
