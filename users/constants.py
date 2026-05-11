"""Константы приложения users."""

# Длины полей модели User.
EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 124
SURNAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256

# Пагинация списка пользователей.
USERS_PAGE_SIZE = 12

# Параметры формы редактирования профиля.
PROFILE_ABOUT_ROWS = 3

# Параметры генерации placeholder-аватара.
AVATAR_SIZE_PX = 256
AVATAR_FONT_RATIO = 0.55
AVATAR_TEXT_COLOR = "white"
AVATAR_FALLBACK_LETTER = "?"
AVATAR_FONT_NAME = "arial.ttf"

# Размер миниатюры аватара в админке.
ADMIN_AVATAR_THUMB_PX = 32
