from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Position, TaskType, Project, Task


class PositionModelTest(TestCase):
    def test_position_str(self):
        position = Position.objects.create(name="Python Developer")
        self.assertEqual(str(position), position.name)


class TaskTypeModelTest(TestCase):
    def test_task_type_str(self):
        task_type = TaskType.objects.create(name="New feature")
        self.assertEqual(str(task_type), task_type.name)


class WorkerModelTest(TestCase):
    def test_worker_str(self):
        worker = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )
        self.assertEqual(
            str(worker),
            f"{worker.first_name} {worker.last_name}"
        )


class ProjectModelTest(TestCase):
    def test_project_str(self):
        worker = get_user_model().objects.create_user(
            username="john.doe",
            first_name="John",
            last_name="Doe",
            password="C3MhYzYotrurMi"
        )
        project = Project.objects.create(
            name="NewClient website",
            author=worker
        )
        self.assertEqual(str(project), project.name)


class TaskModelTest(TestCase):
    def test_task_str(self):
        position1 = Position.objects.create(name="Project manager")
        position2 = Position.objects.create(name="Copywriter")
        project_manager = get_user_model().objects.create_user(
            first_name="Jack",
            last_name="Smith",
            username="jack.smith",
            password="6NdqA6xsfBCcdG",
            position=position1
        )
        copywriter = get_user_model().objects.create_user(
            first_name="John",
            last_name="Doe",
            username="john.doe",
            password="C3MhYzYotrurMi",
            position=position2
        )
        task_type = TaskType.objects.create(name="Copywriting")
        project = Project.objects.create(
            name="NewClient website",
            author=project_manager
        )

        task = Task.objects.create(
            name="NewClient - Text for 'About us' page",
            project=project,
            deadline="2023-11-12",
            description="""
            Hi, John!
            The client has filled in our form with the info about the company: https://example.com/about-us-brief.
            Check his answers as soon as you can and let me know if you need any extra info for 'About us' text.
            """,
            author=project_manager,
            responsible=copywriter,
            task_type=task_type
        )
        self.assertEqual(str(task), task.name)
