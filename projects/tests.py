"""Тесты приложения projects."""
import json
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User

from .models import Project


class PublicPagesTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_user(
            email="boss@x.ru", password="qwerty12345",
            name="Boss", surname="Man",
        )
        cls.proj = Project.objects.create(
            name="Test", description="d", owner=cls.boss,
        )

    def test_anon_sees_list(self):
        r = self.client.get(reverse("projects:list"))
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_sees_detail(self):
        r = self.client.get(
            reverse("projects:detail", args=[self.proj.pk])
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_cant_create(self):
        r = self.client.get(reverse("projects:create"))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("users:login"), r["Location"])


class CreateProjectTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.maker = User.objects.create_user(
            email="maker@x.ru", password="qwerty12345",
            name="Mk", surname="Mr",
        )
        cls.maker_client = Client()
        cls.maker_client.force_login(cls.maker)

    def test_create_assigns_owner_and_participant(self):
        r = self.maker_client.post(reverse("projects:create"), {
            "name": "New shiny",
            "description": "w/e",
            "github_url": "https://github.com/maker/repo",
            "status": Project.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        proj = Project.objects.get(name="New shiny")
        self.assertEqual(proj.owner, self.maker)
        self.assertIn(self.maker, proj.participants.all())

    def test_create_rejects_non_github_url(self):
        r = self.maker_client.post(reverse("projects:create"), {
            "name": "Bad",
            "description": "w/e",
            "github_url": "https://gitlab.com/foo",
            "status": Project.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "github")


class AjaxTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_user(
            email="ajax_boss@x.ru", password="qwerty12345",
            name="A", surname="B",
        )
        cls.guest = User.objects.create_user(
            email="ajax_guest@x.ru", password="qwerty12345",
            name="C", surname="D",
        )
        cls.boss_client = Client()
        cls.boss_client.force_login(cls.boss)
        cls.guest_client = Client()
        cls.guest_client.force_login(cls.guest)

    def setUp(self):
        # Свежий проект на каждый тест — статус мутируется в test_complete.
        self.proj = Project.objects.create(
            name="Target", owner=self.boss,
        )

    def _ajax(self, client, url):
        r = client.post(url)
        self.assertEqual(r["Content-Type"], "application/json")
        return r.status_code, json.loads(r.content)

    def test_toggle_favorite(self):
        url = reverse("projects:toggle_favorite", args=[self.proj.pk])
        status, data = self._ajax(self.guest_client, url)
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["favorited"])
        status, data = self._ajax(self.guest_client, url)
        self.assertFalse(data["favorited"])

    def test_toggle_participate(self):
        url = reverse("projects:toggle_participate", args=[self.proj.pk])
        status, data = self._ajax(self.guest_client, url)
        self.assertTrue(data["participant"])
        status, data = self._ajax(self.guest_client, url)
        self.assertFalse(data["participant"])

    def test_complete_owner_only(self):
        url = reverse("projects:complete", args=[self.proj.pk])
        r = self.guest_client.post(url)
        self.assertEqual(r.status_code, HTTPStatus.FORBIDDEN)
        r = self.boss_client.post(url)
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.proj.refresh_from_db()
        self.assertEqual(self.proj.status, Project.CLOSED)


class FavFilterTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.me = User.objects.create_user(
            email="me@x.ru", password="qwerty12345",
            name="Me", surname="Self",
        )
        cls.peer = User.objects.create_user(
            email="peer@x.ru", password="qwerty12345",
            name="UniquePeerLabel", surname="Peer",
        )
        cls.peer_proj = Project.objects.create(
            name="Peer thing", owner=cls.peer,
        )
        cls.me_client = Client()
        cls.me_client.force_login(cls.me)

    def test_favorites_page_lists_added(self):
        self.me.favorites.add(self.peer_proj)
        r = self.me_client.get(reverse("projects:favorites"))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "Peer thing")

    def test_filter_owners_of_favorite_projects(self):
        self.me.favorites.add(self.peer_proj)
        r = self.me_client.get(
            reverse("users:list") + "?filter=owners-of-favorite-projects"
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "UniquePeerLabel")
