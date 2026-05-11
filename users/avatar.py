"""Генерация placeholder-аватарки на буквах для новых пользователей."""
import io
import secrets

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_FALLBACK_LETTER,
    AVATAR_FONT_NAME,
    AVATAR_FONT_RATIO,
    AVATAR_SIZE_PX,
    AVATAR_TEXT_COLOR,
)

# Палитра фоновых заливок — пастельные оттенки. Каждое имя описывает
# базовый оттенок, чтобы можно было сразу понять, что это за цвет.
SOFT_BLUE = "#6F8AB7"
DUSTY_PURPLE = "#8C7BB6"
MUTED_GREEN = "#5DAE92"
WARM_OCHRE = "#D69460"
PINK_CORAL = "#C66E80"
SEAFOAM = "#5FA6A6"
COOL_GRAY = "#82909F"
LAVENDER_GRAY = "#A88AAB"
MOSS_GREEN = "#6B9468"
BURNT_ORANGE = "#BB7E58"

# Готовый набор для secrets.choice — порядок не важен.
COLORS = (
    SOFT_BLUE,
    DUSTY_PURPLE,
    MUTED_GREEN,
    WARM_OCHRE,
    PINK_CORAL,
    SEAFOAM,
    COOL_GRAY,
    LAVENDER_GRAY,
    MOSS_GREEN,
    BURNT_ORANGE,
)

# Координаты якоря для расчёта bounding box текста — всегда из (0, 0).
TEXT_ANCHOR = (0, 0)


def make(letter, side=AVATAR_SIZE_PX):
    """Возвращает PNG-файл с одной заглавной буквой на цветном фоне."""
    bg = secrets.choice(COLORS)
    canvas = Image.new("RGB", (side, side), color=bg)
    pen = ImageDraw.Draw(canvas)

    char = (letter or AVATAR_FALLBACK_LETTER)[0].upper()
    try:
        font = ImageFont.truetype(
            AVATAR_FONT_NAME, size=int(side * AVATAR_FONT_RATIO),
        )
    except OSError:
        font = ImageFont.load_default()

    box = pen.textbbox(TEXT_ANCHOR, char, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    pen.text(
        ((side - w) / 2 - box[0], (side - h) / 2 - box[1]),
        char,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    blob = io.BytesIO()
    canvas.save(blob, format="PNG")
    blob.seek(0)
    return ContentFile(blob.getvalue())
