"""Вспомогательные хелперы и валидаторы приложения users."""
from django.core.validators import RegexValidator


PHONE_REGEX = r"^(\+7|8)\d{10}$"
GITHUB_URL_REGEX = r"^https?://(www\.)?github\.com/.+"

PHONE_LOCAL_PREFIX = "8"
PHONE_INTERNATIONAL_PREFIX = "+7"
PHONE_LOCAL_LENGTH = 11

phone_validator = RegexValidator(
    regex=PHONE_REGEX,
    message="Телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX",
)
github_validator = RegexValidator(
    regex=GITHUB_URL_REGEX,
    message="Ссылка должна вести на github.com",
)


def to_e164(phone):
    """Приводит локальный номер 8XXXXXXXXXX к международному +7XXXXXXXXXX."""
    if (
        phone
        and phone.startswith(PHONE_LOCAL_PREFIX)
        and len(phone) == PHONE_LOCAL_LENGTH
    ):
        return PHONE_INTERNATIONAL_PREFIX + phone[1:]
    return phone
