from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import WorkerCreationForm, WorkerChangeForm, PositionForm, TaskTypeForm
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
def toggle_is_active(request, pk):
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
