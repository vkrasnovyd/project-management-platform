from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from task_manager.models import Worker, Position, TaskType, Project


class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "first_name",
            "last_name",
            "position"
        )


class WorkerChangeForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = Worker
        fields = (
            "first_name",
            "last_name",
            "email"
        )


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = "__all__"


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Project
        fields = ["name", "description", "assignees"]
