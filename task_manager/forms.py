from functools import partial
from itertools import groupby
from operator import attrgetter

from django.forms.models import ModelChoiceIterator, ModelMultipleChoiceField

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from task_manager.models import Worker, Position, TaskType, Project, Task


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


class GroupedModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelMultipleChoiceField(ModelMultipleChoiceField):
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields["assignees"].queryset = get_user_model().objects.exclude(id=self.request.user.id).select_related(
            "position"
        )

    class Meta:
        model = Project
        fields = ["name", "description", "assignees"]

    assignees = GroupedModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        choices_groupby="position",
        widget=forms.CheckboxSelectMultiple,
    )


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.project = kwargs.pop("project")
        super(TaskForm, self).__init__(*args, **kwargs)
        parent_project_assignees = get_user_model().objects.filter(all_projects=self.project).select_related("position")
        self.fields["followers"].queryset = parent_project_assignees
        self.fields["responsible"].queryset = parent_project_assignees

    class Meta:
        model = Task
        fields = ["name", "description", "task_type", "responsible", "deadline", "followers"]

    responsible = forms.ModelChoiceField(
        queryset=get_user_model().objects.all()
    )
    followers = GroupedModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        choices_groupby="position",
        widget=forms.CheckboxSelectMultiple
    )
    deadline = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"},
            date_format="%Y-%m-%d",
            time_attrs={"type": "time"},
            time_format="%H:%M",
        )
    )


TASK_STATUS_CHOICES = [
    ("new", "To Do"),
    ("progress", "In progress"),
    ("blocked", "Blocked"),
    ("review", "Under review")
]


class TaskStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["status"]

    status = forms.ChoiceField(choices=TASK_STATUS_CHOICES)
