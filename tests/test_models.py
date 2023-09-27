from django.test import TestCase

from task_manager.models import Position


class PositionModelTest(TestCase):
    def test_position_str(self):
        position = Position.objects.create(name="Python Developer")
        self.assertEqual(str(position), position.name)
