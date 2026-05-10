"""Загрузка демо-данных из JSON.

Файл по умолчанию: users/management/commands/data/seed.json.
Можно подсунуть свой файл флагом --file <path>.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from projects.models import Project
from users.models import User

DEFAULT = Path(__file__).parent / "data" / "seed.json"


class Command(BaseCommand):
    help = "Заполнить БД демо-пользователями и проектами из JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", type=Path, default=DEFAULT,
            help="Путь до JSON-файла",
        )

    def handle(self, *args, **opts):
        path = opts["file"]
        if not path.exists():
            raise CommandError(f"Не найден файл: {path}")

        payload = json.loads(path.read_text(encoding="utf-8"))

        for u in payload.get("users", []):
            self._make_user(u)
        for p in payload.get("projects", []):
            self._make_project(p)
        if payload.get("superuser"):
            self._make_admin(payload["superuser"])

        self.stdout.write(self.style.SUCCESS("Готово."))

    def _make_user(self, data):
        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "name": data["name"],
                "surname": data["surname"],
                "phone": data.get("phone") or None,
                "about": data.get("about", ""),
                "github_url": data.get("github_url", ""),
            },
        )
        if created:
            user.set_password(data["password"])
            user.save()
            self._ok(f"Юзер {user.email}")
        else:
            self.stdout.write(f"Юзер {user.email} уже есть")

    def _make_project(self, data):
        owner = User.objects.get(email=data["owner_email"])
        project, created = Project.objects.get_or_create(
            name=data["name"], owner=owner,
            defaults={
                "description": data.get("description", ""),
                "status": data.get("status", "open"),
                "github_url": data.get("github_url", ""),
            },
        )
        project.participants.add(owner)
        if created:
            self._ok(f"Проект «{project.name}»")
        else:
            self.stdout.write(f"Проект «{project.name}» уже есть")

    def _make_admin(self, data):
        if User.objects.filter(is_superuser=True).exists():
            return
        User.objects.create_superuser(
            email=data["email"],
            password=data["password"],
            name=data["name"],
            surname=data["surname"],
        )
        self._ok(f"Суперюзер {data['email']} / {data['password']}")

    def _ok(self, line):
        self.stdout.write(self.style.SUCCESS(line))
