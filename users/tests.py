"""Тесты приложения users."""
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from .models import User
from .utils import to_e164

# --- Общие константы для тестовых данных --------------------------------

PASSWORD = "qwerty12345"
WRONG_PASSWORD = "nope"

EMAIL_EXISTING = "existing@x.ru"
EMAIL_NEW = "new@x.ru"
EMAIL_ALPHA = "alpha@x.ru"
EMAIL_BETA = "beta@x.ru"
EMAIL_BOSS = "boss@x.ru"
EMAIL_ME = "me@x.ru"

PHONE_LOCAL = "89001234567"
PHONE_INT = "+79001234567"
PHONE_LOCAL_EDIT = "89998887766"
PHONE_INT_EDIT = "+79998887766"

NAME_ME = "Me"
SURNAME_ME = "Self"

# --- URL-имена ---------------------------------------------------------

URL_REGISTER = "users:register"
URL_LOGIN = "users:login"
URL_LOGOUT = "users:logout"
URL_EDIT_PROFILE = "users:edit_profile"


class UserModelTC(TestCase):
    def test_create_user_creates_avatar(self):
        u = User.objects.create_user(
            email=EMAIL_ALPHA, password=PASSWORD,
            name="Alpha", surname="One",
        )
        self.assertTrue(u.avatar.name)
        self.assertTrue(u.check_password(PASSWORD))

    def test_phone_norm_on_save(self):
        u = User.objects.create_user(
            email=EMAIL_BETA, password=PASSWORD,
            name="B", surname="Two", phone=PHONE_LOCAL,
        )
        self.assertEqual(u.phone, PHONE_INT)

    def test_to_e164_helper(self):
        self.assertEqual(to_e164(PHONE_LOCAL), PHONE_INT)
        self.assertEqual(to_e164(PHONE_INT), PHONE_INT)
        self.assertIsNone(to_e164(None))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email=EMAIL_BOSS, password=PASSWORD,
            name="Boss", surname="Of All",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class AuthFlowTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing = User.objects.create_user(
            email=EMAIL_EXISTING, password=PASSWORD,
            name="Old", surname="User",
        )

    def test_signup_redirects_to_login(self):
        r = self.client.post(reverse(URL_REGISTER), {
            "name": "New", "surname": "Guy",
            "email": EMAIL_NEW, "password": PASSWORD,
        })
        self.assertRedirects(r, reverse(URL_LOGIN))
        self.assertTrue(User.objects.filter(email=EMAIL_NEW).exists())

    def test_signup_blocks_duplicate_email(self):
        r = self.client.post(reverse(URL_REGISTER), {
            "name": "Dup", "surname": "Name",
            "email": EMAIL_EXISTING, "password": PASSWORD,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "уже существует")

    def test_signin_signout(self):
        r = self.client.post(reverse(URL_LOGIN), {
            "email": EMAIL_EXISTING, "password": PASSWORD,
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        r = self.client.get(reverse(URL_LOGOUT))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)

    def test_signin_wrong_password(self):
        r = self.client.post(reverse(URL_LOGIN), {
            "email": EMAIL_EXISTING, "password": WRONG_PASSWORD,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "Неверный")


class ProfileEditTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email=EMAIL_ME, password=PASSWORD,
            name=NAME_ME, surname=SURNAME_ME,
        )
        cls.me = Client()
        cls.me.force_login(cls.user)

    def test_reject_non_github_url(self):
        r = self.me.post(reverse(URL_EDIT_PROFILE), {
            "name": NAME_ME, "surname": SURNAME_ME,
            "github_url": "https://gitlab.com/me",
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "github")

    def test_normalizes_phone_on_edit(self):
        self.me.post(reverse(URL_EDIT_PROFILE), {
            "name": NAME_ME, "surname": SURNAME_ME,
            "phone": PHONE_LOCAL_EDIT,
            "github_url": "https://github.com/me",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, PHONE_INT_EDIT)
