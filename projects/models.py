from django.conf import settings
from django.db import models
from django.urls import reverse

from users.models import github_validator


class Project(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Открыт"
        CLOSED = "closed", "Закрыт"

    # Удобные алиасы — чтобы старые места кода (`Project.OPEN`/`Project.CLOSED`)
    # продолжали работать после перехода на TextChoices.
    OPEN = Status.OPEN
    CLOSED = Status.CLOSED
    STATUSES = Status.choices

    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True, default="")
    github_url = models.URLField(
        "GitHub",
        blank=True,
        default="",
        validators=[github_validator],
    )
    status = models.CharField(
        "Статус",
        max_length=max(len(value) for value, _ in Status.choices),
        choices=Status.choices,
        default=Status.OPEN,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )
    created_at = models.DateTimeField(
        "Дата создания", auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.pk])
