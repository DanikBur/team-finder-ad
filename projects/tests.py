"""Тесты приложения projects."""
import json
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User
from .models import Project

# --- Константы тестовых данных ------------------------------------------

PASSWORD = "qwerty12345"

EMAIL_BOSS = "boss@x.ru"
EMAIL_MAKER = "maker@x.ru"
EMAIL_AJAX_BOSS = "ajax_boss@x.ru"
EMAIL_AJAX_GUEST = "ajax_guest@x.ru"
EMAIL_ME = "me@x.ru"
EMAIL_PEER = "peer@x.ru"

PROJECT_TEST = "Test"
PROJECT_NEW = "New shiny"
PROJECT_BAD = "Bad"
PROJECT_AJAX = "Target"
PROJECT_PEER = "Peer thing"

GITHUB_OK = "https://github.com/maker/repo"
GITHUB_BAD = "https://gitlab.com/foo"

# --- URL-имена ---------------------------------------------------------

URL_PROJECT_LIST = "projects:list"
URL_PROJECT_DETAIL = "projects:detail"
URL_PROJECT_CREATE = "projects:create"
URL_PROJECT_FAVS = "projects:favorites"
URL_PROJECT_COMPLETE = "projects:complete"
URL_PROJECT_TOGGLE_FAV = "projects:toggle_favorite"
URL_PROJECT_TOGGLE_PARTICIPATE = "projects:toggle_participate"
URL_USERS_LOGIN = "users:login"
URL_USERS_LIST = "users:list"


class PublicPagesTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_user(
            email=EMAIL_BOSS, password=PASSWORD,
            name="Boss", surname="Man",
        )
        cls.proj = Project.objects.create(
            name=PROJECT_TEST, description="d", owner=cls.boss,
        )

    def test_anon_sees_list(self):
        r = self.client.get(reverse(URL_PROJECT_LIST))
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_sees_detail(self):
        r = self.client.get(
            reverse(URL_PROJECT_DETAIL, args=[self.proj.pk]),
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)

    def test_anon_cant_create(self):
        r = self.client.get(reverse(URL_PROJECT_CREATE))
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse(URL_USERS_LOGIN), r["Location"])


class CreateProjectTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.maker = User.objects.create_user(
            email=EMAIL_MAKER, password=PASSWORD,
            name="Mk", surname="Mr",
        )
        cls.maker_client = Client()
        cls.maker_client.force_login(cls.maker)

    def test_create_assigns_owner_and_participant(self):
        r = self.maker_client.post(reverse(URL_PROJECT_CREATE), {
            "name": PROJECT_NEW,
            "description": "w/e",
            "github_url": GITHUB_OK,
            "status": Project.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.FOUND)
        proj = Project.objects.get(name=PROJECT_NEW)
        self.assertEqual(proj.owner, self.maker)
        self.assertIn(self.maker, proj.participants.all())

    def test_create_rejects_non_github_url(self):
        r = self.maker_client.post(reverse(URL_PROJECT_CREATE), {
            "name": PROJECT_BAD,
            "description": "w/e",
            "github_url": GITHUB_BAD,
            "status": Project.OPEN,
        })
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "github")


class AjaxTC(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_user(
            email=EMAIL_AJAX_BOSS, password=PASSWORD,
            name="A", surname="B",
        )
        cls.guest = User.objects.create_user(
            email=EMAIL_AJAX_GUEST, password=PASSWORD,
            name="C", surname="D",
        )
        cls.boss_client = Client()
        cls.boss_client.force_login(cls.boss)
        cls.guest_client = Client()
        cls.guest_client.force_login(cls.guest)

    def setUp(self):
        # Свежий проект на каждый тест — статус мутируется в test_complete.
        self.proj = Project.objects.create(
            name=PROJECT_AJAX, owner=self.boss,
        )

    def _ajax(self, client, url):
        r = client.post(url)
        self.assertEqual(r["Content-Type"], "application/json")
        return r.status_code, json.loads(r.content)

    def test_toggle_favorite(self):
        url = reverse(URL_PROJECT_TOGGLE_FAV, args=[self.proj.pk])
        status, data = self._ajax(self.guest_client, url)
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["favorited"])
        status, data = self._ajax(self.guest_client, url)
        self.assertFalse(data["favorited"])

    def test_toggle_participate(self):
        url = reverse(URL_PROJECT_TOGGLE_PARTICIPATE, args=[self.proj.pk])
        status, data = self._ajax(self.guest_client, url)
        self.assertTrue(data["participant"])
        status, data = self._ajax(self.guest_client, url)
        self.assertFalse(data["participant"])

    def test_complete_owner_only(self):
        url = reverse(URL_PROJECT_COMPLETE, args=[self.proj.pk])
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
            email=EMAIL_ME, password=PASSWORD,
            name="Me", surname="Self",
        )
        cls.peer = User.objects.create_user(
            email=EMAIL_PEER, password=PASSWORD,
            name="UniquePeerLabel", surname="Peer",
        )
        cls.peer_proj = Project.objects.create(
            name=PROJECT_PEER, owner=cls.peer,
        )
        cls.me_client = Client()
        cls.me_client.force_login(cls.me)

    def test_favorites_page_lists_added(self):
        self.me.favorites.add(self.peer_proj)
        r = self.me_client.get(reverse(URL_PROJECT_FAVS))
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, PROJECT_PEER)

    def test_filter_owners_of_favorite_projects(self):
        self.me.favorites.add(self.peer_proj)
        r = self.me_client.get(
            reverse(URL_USERS_LIST)
            + "?filter=owners-of-favorite-projects",
        )
        self.assertEqual(r.status_code, HTTPStatus.OK)
        self.assertContains(r, "UniquePeerLabel")
