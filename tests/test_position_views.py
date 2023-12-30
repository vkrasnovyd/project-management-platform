from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position

POSITION_LIST_VIEW = "/positions/"
POSITION_CREATE_VIEW = "/positions/create/"
POSITION_UPDATE_VIEW = "/positions/1/update/"
POSITION_DELETE_VIEW = "/positions/1/delete/"


class PublicPositionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Position.objects.create(name="QA")

    def test_position_list_page_requires_login(self):
        response = self.client.get(POSITION_LIST_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_position_create_page_requires_login(self):
        response = self.client.get(POSITION_CREATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_position_update_page_requires_login(self):
        response = self.client.get(POSITION_UPDATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_position_delete_page_requires_login(self):
        response = self.client.get(POSITION_DELETE_VIEW)
        self.assertNotEqual(response.status_code, 200)


class PrivatePositionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Position.objects.create(name="Python developer")
        Position.objects.create(name="QA")

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            username="test_user",
            password="t8yLKoZty5XQx3"
        )
        self.client.force_login(user)

    # Test if all the pages are accessible
    def test_retrieve_position_list(self):
        response = self.client.get(POSITION_LIST_VIEW)
        positions_list = Position.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["position_list"]),
            list(positions_list)
        )

    def test_retrieve_position_create_page(self):
        response = self.client.get(POSITION_CREATE_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_position_update_page(self):
        response = self.client.get(POSITION_UPDATE_VIEW)
        position = Position.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["position"], position)

    def test_retrieve_position_delete_page(self):
        response = self.client.get(POSITION_DELETE_VIEW)
        position = Position.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["position"], position)

    # Test if all the pages are accessible by their name
    def test_retrieve_position_list_by_name(self):
        response = self.client.get(reverse("task_manager:position-list"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_position_create_page_by_name(self):
        response = self.client.get(reverse("task_manager:position-create"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_position_update_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:position-update", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_position_delete_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:position-delete", args=[1])
        )
        self.assertEqual(response.status_code, 200)
