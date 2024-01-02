import django_filters
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, Case, When
from django.forms import RadioSelect, CheckboxSelectMultiple
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views import generic

from task_manager.forms import WorkerCreationForm, WorkerChangeForm, PositionForm, TaskTypeForm, ProjectForm
from task_manager.models import Task, Project, Position, TaskType


@login_required
def index(request):
    """View function for the home page of the site."""

    return render(request, "task_manager/index.html")


class WorkerListView(LoginRequiredMixin, generic.ListView):
    """View class for the page with a list of all workers grouped by position."""

    model = get_user_model()
    paginate_by = 20
    queryset = get_user_model().objects.select_related("position").all().filter(is_active=True)


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
        ).order_by("deadline")
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
    template_name = "task_manager/worker_creation_form.html"


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating user info."""

    model = get_user_model()
    form_class = WorkerChangeForm
    template_name = "task_manager/worker_update_form.html"


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


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating existing positions."""

    model = Position
    form_class = PositionForm
    success_url = reverse_lazy("task_manager:position-list")


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


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View class for the page for updating existing task type."""

    model = TaskType
    form_class = TaskTypeForm
    template_name = "task_manager/task_type_form.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    """View class for the page for deleting user info from the DB."""

    model = TaskType
    template_name = "task_manager/task_type_confirm_delete.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class ProjectFilterSet(django_filters.FilterSet):
    is_active = django_filters.BooleanFilter()

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
        context = super().get_context_data(**kwargs)
        project_id = context.get("project").id
        context["participants"] = get_user_model().objects.filter(all_projects=project_id).select_related("position")

        num_tasks = len(Task.objects.filter(project__id=project_id))
        context["num_tasks"] = num_tasks

        context["can_be_deleted"] = False
        if num_tasks == 0:
            context["can_be_deleted"] = True

        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new project."""

    model = Project
    form_class = ProjectForm

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

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdateView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        project = Project.objects.get(id=self.object.id)

        project.assignees.set([project.author])
        assignees = form.cleaned_data["assignees"]
        for assignee in assignees:
            project.assignees.add(assignee)

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


TASK_IS_COMPLETED_CHOICES = (
    (True, "Completed"),
    (False, "Active"),
)


class TaskFilterSet(django_filters.FilterSet):
    is_completed = django_filters.ChoiceFilter(
        field_name="is_completed",
        choices=TASK_IS_COMPLETED_CHOICES,
        widget=RadioSelect,
        empty_label="All"
    )
    task_type = django_filters.AllValuesMultipleFilter(
        field_name="task_type__name",
        widget=CheckboxSelectMultiple
    )

    class Meta:
        model = Task
        fields = ["is_completed", "task_type"]


class TaskListView(LoginRequiredMixin, generic.ListView):
    """View class for the page with a list of all tasks assigned to the logged-in user."""

    model = Task
    paginate_by = 15
    filterset_class = TaskFilterSet

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(followers=user).select_related("project", "author", "responsible", "task_type")
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    """View class for the page with the key information about the task."""
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = context.get("task").id
        context["followers"] = get_user_model().objects.filter(followed_tasks=task_id).select_related("position")
        return context
