from django.contrib import admin

from task_manager.models import Position, TaskType, Project, Task

admin.site.register(Position)

admin.site.register(TaskType)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_type",
        "is_completed",
        "status", "deadline",
        "author",
        "responsible"
    )
    search_fields = ("name", "author", "responsible")
    list_filter = ("is_completed", "status", "task_type")
