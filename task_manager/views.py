from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from task_manager.forms import WorkerCreationForm
from task_manager.models import Task


@login_required
def index(request):
    """View function for the home page of the site."""

    return render(request, "task_manager/index.html")


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
        ).order_by("deadline")
        context["common_tasks_in_progress"] = common_tasks_in_progress
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    """View class for the page for creating a new user."""

    model = get_user_model()
    form_class = WorkerCreationForm
    template_name = "task_manager/worker_creation_form.html"
