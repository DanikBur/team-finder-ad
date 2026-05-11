"""Модель пользователя."""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from . import avatar
from .constants import (
    ABOUT_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
)
from .managers import UserManager
from .utils import github_validator, phone_validator, to_e164


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        "Email", unique=True, max_length=EMAIL_MAX_LENGTH,
    )
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=SURNAME_MAX_LENGTH)
    about = models.TextField(
        "О себе", max_length=ABOUT_MAX_LENGTH, blank=True, default="",
    )
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        validators=[phone_validator],
        blank=True,
        null=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
        default="",
        validators=[github_validator],
    )
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    date_joined = models.DateTimeField(
        "Дата регистрации", auto_now_add=True,
    )
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Избранные проекты",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

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
