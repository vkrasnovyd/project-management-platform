from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Project

PROJECT_LIST_VIEW = "/projects/"
PROJECT_CREATE_VIEW = "/projects/create/"
PROJECT_DETAIL_VIEW = "/projects/1/"
PROJECT_UPDATE_VIEW = "/projects/1/update/"
PROJECT_DELETE_VIEW = "/projects/1/delete/"


class PublicProjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )
        Project.objects.create(
            name="Mate Academy - Android App",
            author=author
        )

    def test_project_list_page_requires_login(self):
        response = self.client.get(PROJECT_LIST_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_project_create_page_requires_login(self):
        response = self.client.get(PROJECT_CREATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_project_detail_page_requires_login(self):
        response = self.client.get(PROJECT_DETAIL_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_project_update_page_requires_login(self):
        response = self.client.get(PROJECT_UPDATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_project_delete_page_requires_login(self):
        response = self.client.get(PROJECT_DELETE_VIEW)
        self.assertNotEqual(response.status_code, 200)


class PrivateProjectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_1 = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )
        user_2 = get_user_model().objects.create_user(
            username="jack.rogers",
            first_name="Jack",
            last_name="Rogers",
            password="xgE7YjV4DBzrRH"
        )

        project_1 = Project.objects.create(
            name="Mate Academy - Android app",
            author=user_1,
            is_active=False
        )
        project_2 = Project.objects.create(
            name="Mate Academy - Platform for teenagers",
            author=user_2
        )
        Project.objects.create(
            name="Mate Academy - iOS app",
            author=user_2
        )
        project_1.assignees.add(user_1)
        project_2.assignees.add(user_1)

    def setUp(self) -> None:
        user = get_user_model().objects.get(id=1)
        self.client.force_login(user)

    # Test if all the pages are accessible
    def test_retrieve_project_list(self):
        response = self.client.get(PROJECT_LIST_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_create_page(self):
        response = self.client.get(PROJECT_CREATE_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_detail_page(self):
        response = self.client.get(PROJECT_DETAIL_VIEW)
        project = Project.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)

    def test_retrieve_project_update_page(self):
        response = self.client.get(PROJECT_UPDATE_VIEW)
        project = Project.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)

    def test_retrieve_project_delete_page(self):
        response = self.client.get(PROJECT_DELETE_VIEW)
        project = Project.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)

    # Test if all the pages are accessible by their name
    def test_retrieve_project_list_by_name(self):
        response = self.client.get(reverse("task_manager:project-list"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_create_page_by_name(self):
        response = self.client.get(reverse("task_manager:project-create"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_detail_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:project-detail", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_update_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:project-update", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    def test_retrieve_project_delete_page_by_name(self):
        response = self.client.get(
            reverse("task_manager:project-delete", args=[1])
        )
        self.assertEqual(response.status_code, 200)

    # Test if user can see only the projects he is assigned to
    def test_retrieve_project_list_if_user_is_assigned_to_project(self):
        response = self.client.get(PROJECT_LIST_VIEW)
        user = response.wsgi_request.user
        projects_list = Project.objects.filter(assignees=user)

        self.assertEqual(
            list(response.context["project_list"]),
            list(projects_list)
        )

    # Test filter field 'is_active' on the list view
    def test_filter_projects_by_is_active(self):
        search_field = "is_active"
        search_value = "false"
        url = f"{PROJECT_LIST_VIEW}?{search_field}={search_value}"
        response = self.client.get(url)
        user = response.wsgi_request.user

        expected_queryset = Project.objects.filter(
            is_active=False,
            assignees=user
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["project_list"]),
            list(expected_queryset)
        )
