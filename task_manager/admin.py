from django.contrib import admin

from task_manager.models import Position, TaskType, Project

admin.site.register(Position)

admin.site.register(TaskType)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)
