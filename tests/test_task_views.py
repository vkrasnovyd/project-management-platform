from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Task, Project, TaskType, Position

TASK_LIST_VIEW = "/tasks/"
TASK_CREATE_VIEW = "/projects/1/new_task/"
TASK_DETAIL_VIEW = "/tasks/1/"
TASK_UPDATE_VIEW = "/tasks/1/update/"


class PublicTaskTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        position = Position.objects.create(name="Project manager")
        project_manager = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi",
            position=position
        )
        project = Project.objects.create(
            name="Mate Academy - Android App",
            author=project_manager
        )
        task_type = TaskType.objects.create(name="Marketing")

        Task.objects.create(
            name="Discuss case for our website with the client",
            project=project,
            deadline="2023-12-15 14:00:00",
            description="""
            Remind Julie that her company allowed to use this case on our website (e-mail from Julie from 09.10.2023).
            1. Discuss what can we show and describe.
            2. Get feedback.
            3. Create tasks for the marketing team.
            """,
            author=project_manager,
            responsible=project_manager,
            task_type=task_type
        )

    def test_task_list_page_requires_login(self):
        response = self.client.get(TASK_LIST_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_create_page_requires_login(self):
        response = self.client.get(TASK_CREATE_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_detail_page_requires_login(self):
        response = self.client.get(TASK_DETAIL_VIEW)
        self.assertNotEqual(response.status_code, 200)

    def test_task_update_page_requires_login(self):
        response = self.client.get(TASK_UPDATE_VIEW)
        self.assertNotEqual(response.status_code, 200)


class PrivateTaskTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        position1 = Position.objects.create(name="Project manager")
        position2 = Position.objects.create(name="Copywriter")
        position3 = Position.objects.create(name="Lawyer")
        project_manager = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi",
            position=position1
        )
        copywriter = get_user_model().objects.create_user(
            first_name="Jack",
            last_name="Smith",
            username="jack.smith",
            password="6NdqA6xsfBCcdG",
            position=position2
        )
        lawyer = get_user_model().objects.create_user(
            first_name="Erika",
            last_name="Rogers",
            username="erika.rogers",
            password="vkrCHt7eTUMxh7",
            position=position3
        )
        project = Project.objects.create(
            name="Mate Academy - Android App",
            author=project_manager
        )
        task_type1 = TaskType.objects.create(name="Copywriting")
        task_type2 = TaskType.objects.create(name="Legal")
        task1 = Task.objects.create(
            name="Info for 'Prices' page",
            project=project,
            deadline="2023-11-12 10:00:00",
            description="""
            Hey Erika,
            have you already read the new laws in the client's industry?
            He asked to update the texts and I need you to explain me the changes in simple words.
            """,
            author=copywriter,
            responsible=lawyer,
            task_type=task_type2
        )
        task2 = Task.objects.create(
            name="Closing documents",
            project=project,
            deadline="2023-12-10 10:00:00",
            description="""
            Let's have a quick call in the morning to discuss this question.
            """,
            author=lawyer,
            responsible=project_manager,
            task_type=task_type2
        )
        task3 = Task.objects.create(
            name="Text for 'About us' page",
            project=project,
            deadline="2023-11-12 17:00:00",
            description="""
            Hi, John!
            The client has filled in our form with the info about the company: https://example.com/about-us-brief.
            Check his answers as soon as you can and let me know if you need any extra info for 'About us' text.
            """,
            author=project_manager,
            responsible=copywriter,
            task_type=task_type1,
            is_completed=True,
            status="completed"
        )
        task1.followers.add(lawyer)
        task1.followers.add(copywriter)
        task2.followers.add(project_manager)
        task2.followers.add(lawyer)
        task3.followers.add(project_manager)
        task3.followers.add(copywriter)

    def setUp(self) -> None:
        user = get_user_model().objects.get(id=1)
        self.client.force_login(user)

    # Test if all the pages are accessible
    def test_retrieve_task_list(self):
        response = self.client.get(TASK_LIST_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_create_page(self):
        response = self.client.get(TASK_CREATE_VIEW)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_detail_page(self):
        response = self.client.get(TASK_DETAIL_VIEW)
        task = Task.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], task)

    def test_retrieve_task_update_page(self):
        response = self.client.get(TASK_UPDATE_VIEW)
        task = Task.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], task)

    # Test if all the pages are accessible by their name
    def test_retrieve_task_list_by_name(self):
        response = self.client.get(reverse("task_manager:task-list"))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_create_page_by_name(self):
        response = self.client.get(reverse("task_manager:task-create", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_detail_page_by_name(self):
        response = self.client.get(reverse("task_manager:task-detail", args=[1]))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_task_update_page_by_name(self):
        response = self.client.get(reverse("task_manager:task-update", args=[1]))
        self.assertEqual(response.status_code, 200)

    # Test if user can see only the tasks he is assigned to
    def test_retrieve_task_list_if_user_is_assigned_to_task(self):
        response = self.client.get(TASK_LIST_VIEW)
        user = response.wsgi_request.user
        tasks_list = Task.objects.filter(followers=user)

        self.assertEqual(
            list(response.context["task_list"]),
            list(tasks_list)
        )

    # Test filter field 'is_completed' on the list view
    def test_filter_tasks_by_is_completed(self):
        search_field = "is_completed"
        search_value = "False"
        url = f"{TASK_LIST_VIEW}?{search_field}={search_value}"
        response = self.client.get(url)
        user = response.wsgi_request.user

        expected_queryset = Task.objects.filter(
            is_completed=search_value,
            followers=user
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["task_list"]),
            list(expected_queryset)
        )

    # Test filter field 'task_type' on the list view
    def test_filter_tasks_by_task_type(self):
        search_field = "task_type"
        search_value = TaskType.objects.get(id=1).name
        url = f"{TASK_LIST_VIEW}?{search_field}={search_value}"
        response = self.client.get(url)
        user = response.wsgi_request.user

        expected_queryset = Task.objects.filter(
            task_type=TaskType.objects.get(id=1),
            followers=user
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["task_list"]),
            list(expected_queryset)
        )

    # Test filter field 'role' on the list view
    def test_filter_tasks_by_role(self):
        search_field = "role"
        search_value = "author"
        url = f"{TASK_LIST_VIEW}?{search_field}={search_value}"
        response = self.client.get(url)
        user = response.wsgi_request.user

        expected_queryset = Task.objects.filter(
            author=user
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["task_list"]),
            list(expected_queryset)
        )
