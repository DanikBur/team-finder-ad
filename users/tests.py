"""Тесты приложения users."""
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from .models import User, to_e164


class UserModelTC(TestCase):
    def test_create_user_creates_avatar(self):
        u = User.objects.create_user(
            email="alpha@x.ru", password="qwerty12345",
            name="Alpha", surname="One",
        )
        self.assertTrue(u.avatar.name)
        self.assertTrue(u.check_password("qwerty12345"))

    def test_phone_norm_on_save(self):
        u = User.objects.create_user(
            email="beta@x.ru", password="qwerty12345",
            name="B", surname="Two", phone="89001234567",
        )
        self.assertEqual(u.phone, "+79001234567")

    def test_to_e164_helper(self):
        self.assertEqual(to_e164("89001234567"), "+79001234567")
        self.assertEqual(to_e164("+79001234567"), "+79001234567")
        self.assertIsNone(to_e164(None))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="boss@x.ru", password="qwerty12345",
            name="Boss", surname="Of All",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class AuthFlowTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing = User.objects.create_user(
            email="existing@x.ru", password="qwerty12345",
            name="Old", surname="User",
        )

    def test_signup_redirects_to_login(self):
        r = self.client.post(reverse("users:register"), {
            "name": "New", "surname": "Guy",
            "email": "new@x.ru", "password": "qwerty12345",
        })
        self.assertRedirects(r, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="new@x.ru").exists())

    def test_signup_blocks_duplicate_email(self):
        r = self.client.post(reverse("users:register"), {
            "name": "Dup", "surname": "Name",
            "email": "existing@x.ru", "password": "qwerty12345",
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "уже существует")

    def test_signin_signout(self):
        r = self.client.post(reverse("users:login"), {
            "email": "existing@x.ru", "password": "qwerty12345",
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        r = self.client.get(reverse("users:logout"))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)

    def test_signin_wrong_password(self):
        r = self.client.post(reverse("users:login"), {
            "email": "existing@x.ru", "password": "nope",
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "Неверный")


class ProfileEditTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="me@x.ru", password="qwerty12345",
            name="Me", surname="Self",
        )
        cls.me = Client()
        cls.me.force_login(cls.user)

    def test_reject_non_github_url(self):
        r = self.me.post(reverse("users:edit_profile"), {
            "name": "Me", "surname": "Self",
            "github_url": "https://gitlab.com/me",
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "github")

    def test_normalizes_phone_on_edit(self):
        self.me.post(reverse("users:edit_profile"), {
            "name": "Me", "surname": "Self",
            "phone": "89998887766",
            "github_url": "https://github.com/me",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79998887766")
