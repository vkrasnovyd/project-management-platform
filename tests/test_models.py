from django.test import TestCase

from task_manager.models import Position, TaskType


class PositionModelTest(TestCase):
    def test_position_str(self):
        position = Position.objects.create(name="Python Developer")
        self.assertEqual(str(position), position.name)


class TaskTypeModelTest(TestCase):
    def test_task_type_str(self):
        task_type = TaskType.objects.create(name="New feature")
        self.assertEqual(str(task_type), task_type.name)
