import hashlib
import hmac
import struct
from colorsys import hsv_to_rgb
from typing import Tuple, Union

from django.conf import settings
from django.utils.encoding import force_bytes

from paikkala.models import Program

STYLE_SECRET_SAUCE = force_bytes(getattr(settings, 'PAIKKALA_STYLE_SECRET_SAUCE', ''))


# TODO(3.7): dataclass-ify
class ProgramStyle:
    def __init__(
        self,
        *,
        accent_color: str,
        angle: float,
        color1: str,
        color2: str,
    ) -> None:
        self.accent_color = accent_color
        self.angle = angle
        self.color1 = color1
        self.color2 = color2


def decimal_rgb_to_hex(rgb: Tuple[Union[int, float], Union[int, float], Union[int, float]]) -> str:
    return '#{:02x}{:02x}{:02x}'.format(
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255),
    )


def compute_program_style(program: Program) -> ProgramStyle:
    noise = hmac.HMAC(key=STYLE_SECRET_SAUCE, msg=force_bytes(program.name), digestmod=hashlib.sha256).digest()
    random_values = [v / (2 << 31) for v in struct.unpack('<IIIIIIII', noise)]
    hue1 = random_values[0]
    hue2 = (hue1 + 0.8) % 1.0
    sat1 = 0.6 + random_values[1] * 0.4
    sat2 = 0.6 + random_values[2] * 0.4
    val1 = 0.6 + random_values[3] * 0.3
    val2 = 0.6 + random_values[4] * 0.3
    color1 = hsv_to_rgb(hue1, sat1, val1)
    color2 = hsv_to_rgb(hue2, sat2, val2)
    accent_color = hsv_to_rgb(hue2, 1, min(1, val2 * 1.5))
    return ProgramStyle(
        accent_color=decimal_rgb_to_hex(accent_color),
        angle=random_values[5] * 360,
        color1=decimal_rgb_to_hex(color1),
        color2=decimal_rgb_to_hex(color2),
    )
