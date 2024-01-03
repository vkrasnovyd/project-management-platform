from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="workers",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"
        ordering = ["position__name", "first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("task_manager:worker-detail", kwargs={"pk": self.pk})


class Project(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    author = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="created_projects"
    )
    assignees = models.ManyToManyField(Worker, related_name="all_projects")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("task_manager:project-detail", kwargs={"pk": self.pk})


class Task(models.Model):
    TASK_STATUS_CHOICES = [
        ("new", "To Do"),
        ("progress", "In progress"),
        ("blocked", "Blocked"),
        ("review", "Under review"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled")
    ]

    name = models.CharField(max_length=255)
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="tasks"
    )
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=255,
        choices=TASK_STATUS_CHOICES,
        default="new"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    description = models.TextField()
    author = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="created_tasks"
    )
    responsible = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name="tasks_to_do"
    )
    followers = models.ManyToManyField(Worker, related_name="followed_tasks")
    task_type = models.ForeignKey(
        TaskType,
        related_name="tasks",
        on_delete=models.SET_DEFAULT,
        default=1
    )

    class Meta:
        ordering = ["deadline"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("task_manager:task-detail", kwargs={"pk": self.pk})
