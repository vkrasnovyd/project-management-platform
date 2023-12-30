from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import TaskType

TASK_TYPE_LIST_VIEW = "/task_types/"
TASK_TYPE_CREATE_VIEW = "/task_types/create/"
TASK_TYPE_UPDATE_VIEW = "/task_types/1/update/"
TASK_TYPE_DELETE_VIEW = "/task_types/1/delete/"


class PublicTaskTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        TaskType.objects.create(name="New feature")

    def test_task_type_list_page_requires_login(self):
        response = self.client.get(TASK_TYPE_LIST_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_type_create_page_requires_login(self):
        response = self.client.get(TASK_TYPE_CREATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_type_update_page_requires_login(self):
        response = self.client.get(TASK_TYPE_UPDATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_type_delete_page_requires_login(self):
        response = self.client.get(TASK_TYPE_DELETE_VIEW)
        self.assertNotEqual(response.status_code, 200)


class PrivateTaskTypeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        TaskType.objects.create(name="Bug fix")
        TaskType.objects.create(name="New feature")

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            username="test_user",
            password="t8yLKoZty5XQx3"
        )
        self.client.force_login(user)

    # Test if all the pages are accessible
    def test_retrieve_task_type_list(self):
        response = self.client.get(TASK_TYPE_LIST_VIEW)
        task_types_list = TaskType.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["tasktype_list"]),
            list(task_types_list)
        )

    def test_retrieve_task_type_create_page(self):
        response = self.client.get(TASK_TYPE_CREATE_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_type_update_page(self):
        response = self.client.get(TASK_TYPE_UPDATE_VIEW)
        task_type = TaskType.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tasktype"], task_type)

    def test_retrieve_task_type_delete_page(self):
        response = self.client.get(TASK_TYPE_DELETE_VIEW)
        task_type = TaskType.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tasktype"], task_type)

    # Test if all the pages are accessible by their name
    def test_retrieve_task_type_list_by_name(self):
        response = self.client.get(reverse("task_manager:task-type-list"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_type_create_page_by_name(self):
        response = self.client.get(reverse("task_manager:task-type-create"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_type_update_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:task-type-update", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_type_delete_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:task-type-delete", args=[1])
        )
        self.assertEqual(response.status_code, 200)
