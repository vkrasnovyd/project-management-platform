from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """View function for the home page of the site."""

    return render(request, "task_manager/index.html")
