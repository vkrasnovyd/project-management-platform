from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Position, TaskType, Project


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
        position = Position.objects.create(name="Python Developer")
        worker = get_user_model().objects.create(
            first_name="John",
            last_name="Doe",
            password="Test1234",
            position=position
        )
        self.assertEqual(
            str(worker),
            f"{worker.first_name} {worker.last_name}"
        )


class ProjectModelTest(TestCase):
    def test_project_str(self):
        project = Project.objects.create(
            name="NewClient website"
        )
        self.assertEqual(str(project), project.name)
