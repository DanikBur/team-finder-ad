"""Генерация placeholder-аватарки на буквах для новых пользователей."""
import io
import secrets

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

# Палитра фоновых заливок — пастельные оттенки.
COLORS = (
    "#6F8AB7", "#8C7BB6", "#5DAE92", "#D69460",
    "#C66E80", "#5FA6A6", "#82909F", "#A88AAB",
    "#6B9468", "#BB7E58",
)


def make(letter, side=256):
    """Возвращает PNG-файл с одной заглавной буквой на цветном фоне."""
    bg = secrets.choice(COLORS)
    canvas = Image.new("RGB", (side, side), color=bg)
    pen = ImageDraw.Draw(canvas)

    char = (letter or "?")[0].upper()
    try:
        font = ImageFont.truetype("arial.ttf", size=int(side * 0.55))
    except OSError:
        font = ImageFont.load_default()

    box = pen.textbbox((0, 0), char, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    pen.text(
        ((side - w) / 2 - box[0], (side - h) / 2 - box[1]),
        char,
        fill="white",
        font=font,
    )

    blob = io.BytesIO()
    canvas.save(blob, format="PNG")
    blob.seek(0)
    return ContentFile(blob.getvalue())
