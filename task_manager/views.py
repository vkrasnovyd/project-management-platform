import datetime

from django_filters import FilterSet, BooleanFilter, ChoiceFilter, AllValuesMultipleFilter, views, MultipleChoiceFilter
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, Case, When
from django.forms import RadioSelect, CheckboxSelectMultiple
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic

from task_manager.forms import WorkerCreationForm, WorkerChangeForm, PositionForm, TaskTypeForm, ProjectForm, TaskForm, \
    TaskStatusUpdateForm
from task_manager.models import Task, Project, Position, TaskType


@login_required
def index(request):
    """View function for the home page of the site."""
    today_date = datetime.datetime.today().date()
    user = request.user

    task_list = Task.objects.filter(deadline=today_date, is_completed=False).select_related(
        "project",
        "author",
        "responsible",
        "task_type"
    )
    tasks_to_do = task_list.filter(responsible=user)
    tasks_created = task_list.filter(author=user)

    context = {
        "tasks_to_do": tasks_to_do,
        "tasks_created": tasks_created,
    }

    return render(request, "task_manager/index.html", context=context)


class WorkerListView(LoginRequiredMixin, generic.ListView):
    """View class for the page with a list of all workers grouped by position."""

    model = get_user_model()
    paginate_by = 20
    queryset = get_user_model().objects.select_related("position").all()


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    """View class for the page with the key information about a worker."""

    model = get_user_model()

    def get_context_data(self, **kwargs):
        context = super(WorkerDetailView, self).get_context_data()
        user = self.request.user
        responsible = context.get("worker")
        common_tasks_in_progress = Task.objects.filter(
            author=user,
            responsible=responsible,
            is_completed=False
        ).order_by("deadline").select_related("author", "responsible")
        context["common_tasks_in_progress"] = common_tasks_in_progress

        """
        Code below checks dependencies, that can block the possibility to delete user.
        'Delete' button in the Detail view will be visible only if User doesn't have such blocking dependencies.
        """

        context["can_be_deleted"] = False
        if (
                not Project.objects.all().filter(author=responsible) and
                not Task.objects.all().filter(author=responsible) and
                not Task.objects.all().filter(responsible=responsible)
        ):
            context["can_be_deleted"] = True

        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new user."""

    model = get_user_model()
    form_class = WorkerCreationForm

    def get_context_data(self, **kwargs):
        context = super(WorkerCreateView, self).get_context_data()
        context["form_object_name"] = "user"
        return context


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating user info."""

    model = get_user_model()
    form_class = WorkerChangeForm

    def get_context_data(self, **kwargs):
        context = super(WorkerUpdateView, self).get_context_data()
        context["form_object_name"] = "user"
        return context


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View class for the page for deleting user info from the DB."""

    model = get_user_model()
    success_url = reverse_lazy("task_manager:worker-list")


@login_required
def worker_toggle_is_active(request, pk):
    user = get_user_model().objects.get(id=pk)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    user.save()
    return HttpResponseRedirect(reverse_lazy("task_manager:worker-detail", args=[pk]))


class PositionListView(LoginRequiredMixin, generic.ListView):
    """
    View class for the page with a list of all positions
    with links to the pages for creating, updating and deleting positions.
    """

    model = Position
    paginate_by = 20
    queryset = Position.objects.annotate(num_workers=Count("workers"))


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new position."""

    model = Position
    form_class = PositionForm
    success_url = reverse_lazy("task_manager:position-list")

    def get_context_data(self, **kwargs):
        context = super(PositionCreateView, self).get_context_data()
        context["form_object_name"] = "position"
        return context


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating existing positions."""

    model = Position
    form_class = PositionForm
    success_url = reverse_lazy("task_manager:position-list")

    def get_context_data(self, **kwargs):
        context = super(PositionUpdateView, self).get_context_data()
        context["form_object_name"] = "position"
        return context


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View class for the page for deleting user info from the DB."""

    model = Position
    success_url = reverse_lazy("task_manager:position-list")


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    """
    View class for the page with a list of all task types
    with links to the pages for creating, updating and deleting positions.
    """

    model = TaskType
    paginate_by = 10
    template_name = "task_manager/task_type_list.html"


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new position."""

    model = TaskType
    form_class = TaskTypeForm
    template_name = "task_manager/task_type_form.html"
    success_url = reverse_lazy("task_manager:task-type-list")

    def get_context_data(self, **kwargs):
        context = super(TaskTypeCreateView, self).get_context_data()
        context["form_object_name"] = "task type"
        return context


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating existing task type."""

    model = TaskType
    form_class = TaskTypeForm
    template_name = "task_manager/task_type_form.html"
    success_url = reverse_lazy("task_manager:task-type-list")

    def get_context_data(self, **kwargs):
        context = super(TaskTypeUpdateView, self).get_context_data()
        context["form_object_name"] = "task type"
        return context


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View class for the page for deleting user info from the DB."""

    model = TaskType
    template_name = "task_manager/task_type_confirm_delete.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class ProjectFilterSet(FilterSet):
    is_active = BooleanFilter()

    class Meta:
        model = Project
        fields = ["is_active"]


class ProjectListView(LoginRequiredMixin, generic.ListView):
    """View class for the page with a list of all projects assigned to the logged-in user."""

    model = Project
    paginate_by = 10
    filterset_class = ProjectFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(assignees=user).annotate(
            num_tasks=Count("tasks", filter=Q(tasks__followers=user)),
            num_completed_tasks=Count("tasks", filter=Q(tasks__is_completed=True, tasks__followers=user)),
            progress=Case(
                When(num_tasks__gt=0, then=F("num_completed_tasks") * 100 / F("num_tasks")),
                default=0
            )
        )
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    """View class for the page with the key information about the project."""
    model = Project

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        project_id = context.get("project").id
        context["participants"] = get_user_model().objects.filter(all_projects=project_id).select_related("position")

        num_tasks = len(Task.objects.filter(project__id=project_id))
        context["num_tasks"] = num_tasks

        context["can_be_deleted"] = False
        if num_tasks == 0:
            context["can_be_deleted"] = True

        context["tasks"] = Task.objects.filter(project__id=project_id, followers=user).select_related(
            "author",
            "responsible",
            "task_type"
        )

        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new project."""

    model = Project
    form_class = ProjectForm

    def get_context_data(self, **kwargs):
        context = super(ProjectCreateView, self).get_context_data()
        context["form_object_name"] = "project"
        return context

    def get_form_kwargs(self):
        kwargs = super(ProjectCreateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        author = self.request.user
        name = form.cleaned_data["name"]
        description = form.cleaned_data["description"]

        project = Project.objects.create(name=name, description=description, author=author)
        project.save()

        assignees = form.cleaned_data["assignees"]
        for assignee in assignees:
            project.assignees.add(assignee)
        project.assignees.add(author)
        return HttpResponseRedirect(reverse("task_manager:project-detail", args=[project.id]))


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating a project."""
    model = Project
    form_class = ProjectForm

    def get_context_data(self, **kwargs):
        context = super(ProjectUpdateView, self).get_context_data()
        context["form_object_name"] = "project"
        return context

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        project = form.save(commit=False)
        project.assignees.set([project.author])
        assignees = form.cleaned_data["assignees"]
        for assignee in assignees:
            project.assignees.add(assignee)
        project.save()
        return HttpResponseRedirect(reverse("task_manager:project-detail", args=[project.id]))


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View class for the page for deleting project from the DB."""

    model = Project
    success_url = reverse_lazy("task_manager:project-list")


@login_required
def project_toggle_is_active(request, pk):
    project = Project.objects.get(id=pk)
    if project.is_active:
        project.is_active = False
    else:
        project.is_active = True
    project.save()
    return HttpResponseRedirect(reverse_lazy("task_manager:project-detail", args=[pk]))


class TaskFilterSet(FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["task_type"].extra["choices"] = self.get_task_type_filter_choices()

    is_completed_choices = (
        (True, "Completed"),
        (False, "Active"),
    )
    role_choices = (
        ("author", "Author"),
        ("responsible", "Responsible")
    )

    is_completed = ChoiceFilter(
        field_name="is_completed",
        label="Task status",
        choices=is_completed_choices,
        widget=RadioSelect,
        empty_label="All"
    )
    task_type = MultipleChoiceFilter(
        choices=[],
        widget=CheckboxSelectMultiple
    )
    role = ChoiceFilter(
        label="My role",
        choices=role_choices,
        method="filter_by_role",
        widget=RadioSelect,
        empty_label="All"
    )

    class Meta:
        model = Task
        fields = ["is_completed", "task_type", "role"]

    def get_task_type_filter_choices(self):
        task_type_list = TaskType.objects.filter(tasks__followers=self.request.user).values_list("name", flat=True).distinct()
        return [(task_type, task_type) for task_type in task_type_list]

    def filter_by_role(self, queryset, name, value):
        if self.request is None:
            return Task.objects.none()
        user = self.request.user
        if value == "author":
            return queryset.filter(author=user)
        if value == "responsible":
            return queryset.filter(responsible=user)
        return queryset


class TaskListView(LoginRequiredMixin, views.FilterView):
    """View class for the page with a list of all tasks assigned to the logged-in user."""

    model = Task
    paginate_by = 15
    filterset_class = TaskFilterSet
    template_name = "task_manager/task_list.html"

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(followers=user).select_related(
            "project",
            "author",
            "responsible",
            "task_type"
        )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class TaskDetailView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page with the key information about the task."""
    model = Task
    form_class = TaskStatusUpdateForm
    template_name = "task_manager/task_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        task = context.get("task")
        user = self.request.user

        object = self.get_object()
        context["object"] = context["task"] = object

        task_id = task.id
        context["followers"] = get_user_model().objects.filter(followed_tasks=task_id).select_related("position")

        user_can_activate_task = False
        if task.author == user and task.is_completed:
            user_can_activate_task = True
        if task.responsible == user and task.status == "completed":
            user_can_activate_task = True
        context["user_can_activate_task"] = user_can_activate_task

        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new task."""

    model = Task
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data()
        context["form_object_name"] = "task"
        return context

    def get_form_kwargs(self):
        project = Project.objects.get(pk=self.kwargs["pk"])
        kwargs = super(TaskCreateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["project"] = project
        return kwargs

    def form_valid(self, form):
        author = self.request.user
        project = Project.objects.get(pk=self.kwargs["pk"])

        form_data = form.cleaned_data

        task = Task.objects.create(
            name=form_data["name"],
            description=form_data["description"],
            deadline=form_data["deadline"],
            responsible=form_data["responsible"],
            task_type=form_data["task_type"],
            author=author,
            project=project
        )
        task.save()

        responsible = form_data["responsible"]
        followers = form_data.get("followers", [])
        for follower in followers:
            task.followers.add(follower)
        task.followers.add(author)
        task.followers.add(responsible)

        return HttpResponseRedirect(reverse("task_manager:task-detail", args=[task.id]))


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating a task."""
    model = Task
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data()
        context["form_object_name"] = "task"
        return context

    def get_form_kwargs(self):
        project = self.object.project
        kwargs = super(TaskUpdateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["project"] = project
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)
        task.followers.set([task.author])
        followers = form.cleaned_data["followers"]
        for follower in followers:
            task.followers.add(follower)
        task.save()
        return HttpResponseRedirect(reverse("task_manager:task-detail", args=[task.id]))


@login_required
def task_status_toggle(request, pk, new_status):
    task = Task.objects.get(id=pk)
    task.status = new_status
    if new_status == "canceled" or new_status == "completed":
        task.is_completed = True
    else:
        task.is_completed = False
    task.save()
    return HttpResponseRedirect(reverse_lazy("task_manager:task-detail", args=[pk]))
