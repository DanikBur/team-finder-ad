"""Модель пользователя и связанные с ней проверки."""
import re
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models

from . import avatar
from .managers import UserManager

PHONE_RE = re.compile(r"(\+7|8)\d{10}")
GITHUB_RE = re.compile(r"^https?://(www\.)?github\.com/.+")


def to_e164(phone):
    """Приводит 8XXXXXXXXXX к +7XXXXXXXXXX."""
    if phone and phone.startswith("8") and len(phone) == 11:
        return "+7" + phone[1:]
    return phone


def check_phone(value):
    if not PHONE_RE.fullmatch(value or ""):
        raise ValidationError(
            "Телефон в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )


def check_github(value):
    if value and not GITHUB_RE.match(value):
        raise ValidationError("Ссылка должна вести на github.com")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    name = models.CharField("Имя", max_length=124)
    surname = models.CharField("Фамилия", max_length=124)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=12,
        unique=True,
        validators=[check_phone],
        blank=True,
        null=True,
    )
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[check_github]
    )
    about = models.TextField(
        "О себе", max_length=256, blank=True, default=""
    )
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname} <{self.email}>"

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = to_e164(self.phone)
        if not self.avatar:
            self.avatar.save(
                f"{uuid.uuid4().hex}.png",
                avatar.make(self.name or self.email),
                save=False,
            )
        super().save(*args, **kwargs)
