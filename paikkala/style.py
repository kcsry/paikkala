import hashlib
import hmac
import struct
from colorsys import hsv_to_rgb

from django.utils.encoding import force_bytes
from django.conf import settings

STYLE_SECRET_SAUCE = force_bytes(getattr(settings, 'PAIKKALA_STYLE_SECRET_SAUCE', ''))


def decimal_rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (
        int(rgb[0] * 255),
        int(rgb[1] * 255),
        int(rgb[2] * 255),
    )


def compute_program_style(program):
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
    return {
        'accent_color': decimal_rgb_to_hex(accent_color),
        'angle': random_values[5] * 360,
        'color1': decimal_rgb_to_hex(color1),
        'color2': decimal_rgb_to_hex(color2),
    }
