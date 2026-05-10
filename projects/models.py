from django.conf import settings
from django.db import models
from django.urls import reverse

from users.models import check_github


class Project(models.Model):
    OPEN = "open"
    CLOSED = "closed"
    STATUSES = [
        (OPEN, "Открыт"),
        (CLOSED, "Закрыт"),
    ]

    name = models.CharField(
        "Название", max_length=200
    )
    description = models.TextField("Описание", blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(
        "Дата создания", auto_now_add=True
    )
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[check_github]
    )
    status = models.CharField(
        "Статус",
        max_length=max(len(s) for s, _ in STATUSES),
        choices=STATUSES,
        default=OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="Участники",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", args=[self.pk])
