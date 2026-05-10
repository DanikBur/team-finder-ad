from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер модели User: вход по email вместо username."""

    use_in_migrations = True

    def _build(self, email, password, **extra):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        user = self._build(email, password, **extra)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("is_staff=True для суперюзера")
        if extra.get("is_superuser") is not True:
            raise ValueError("is_superuser=True для суперюзера")
        user = self._build(email, password, **extra)
        user.save(using=self._db)
        return user
