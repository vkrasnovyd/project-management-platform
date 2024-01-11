from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

WORKER_LIST_VIEW = "/workers/"
WORKER_CREATE_VIEW = "/workers/create/"
WORKER_DETAIL_VIEW = "/workers/1/"
WORKER_UPDATE_VIEW = "/workers/1/update/"
WORKER_DELETE_VIEW = "/workers/1/delete/"
WORKER_TOGGLE_IS_ACTIVE_VIEW = "/workers/1/toggle-is-active/"


class PublicWorkerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )

    def test_worker_list_page_requires_login(self):
        response = self.client.get(WORKER_LIST_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_worker_create_page_requires_login(self):
        response = self.client.get(WORKER_CREATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_worker_detail_page_requires_login(self):
        response = self.client.get(WORKER_DETAIL_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_worker_update_page_requires_login(self):
        response = self.client.get(WORKER_UPDATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_worker_delete_page_requires_login(self):
        response = self.client.get(WORKER_DELETE_VIEW)
        self.assertNotEqual(response.status_code, 200)


class PrivateWorkerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            username="test_user",
            password="WP9ctvh5yCtwgH",
            first_name="Jane",
            last_name="Smith"
        )
        self.client.force_login(user)

    # Test if all the pages are accessible
    def test_retrieve_worker_list(self):
        response = self.client.get(WORKER_LIST_VIEW)
        workers_list = get_user_model().objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["worker_list"]),
            list(workers_list)
        )

    def test_retrieve_worker_create_page(self):
        response = self.client.get(WORKER_CREATE_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_worker_detail_page(self):
        response = self.client.get(WORKER_DETAIL_VIEW)
        worker = get_user_model().objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["worker"], worker)

    def test_retrieve_worker_update_page(self):
        response = self.client.get(WORKER_UPDATE_VIEW)
        worker = get_user_model().objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["worker"], worker)

    def test_retrieve_worker_delete_page(self):
        response = self.client.get(WORKER_DELETE_VIEW)
        worker = get_user_model().objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["worker"], worker)

    # Test if all the pages are accessible by their name
    def test_retrieve_worker_list_by_name(self):
        response = self.client.get(reverse("task_manager:worker-list"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_worker_create_page_by_name(self):
        response = self.client.get(reverse("task_manager:worker-create"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_worker_detail_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:worker-detail", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_worker_update_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:worker-update", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_worker_delete_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:worker-delete", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_toggle_is_active(self):
        # Test deactivating user profile
        self.assertTrue(get_user_model().objects.get(id=1).is_active)
        self.client.get(WORKER_TOGGLE_IS_ACTIVE_VIEW)
        self.assertFalse(get_user_model().objects.get(id=1).is_active)

        # Test re-activating user profile
        self.client.get(WORKER_TOGGLE_IS_ACTIVE_VIEW)
        self.assertTrue(get_user_model().objects.get(id=1).is_active)
