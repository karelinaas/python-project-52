from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
)
from django_filters.views import FilterView

from tasks.filters import TaskFilter
from tasks.forms import TaskForm
from tasks.models import Task


class TaskListView(LoginRequiredMixin, FilterView):
    model = Task
    template_name = "tasks/list.html"
    context_object_name = "tasks"
    extra_context = {"title": _("Tasks")}
    filterset_class = TaskFilter
    paginate_by = 10

    queryset = Task.objects.select_related(
        "author",
        "executor",
        "status",
    ).prefetch_related("labels")


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"
    extra_context = {"title": _("Task detail")}


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/create.html"
    success_url = reverse_lazy("tasks:list")
    extra_context = {"title": _("Create task"), "button_text": _("Create")}

    def form_valid(self, form: TaskForm) -> HttpResponse:
        form.instance.author = self.request.user
        messages.success(self.request, _("Task created successfully"))
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/update.html"
    success_url = reverse_lazy("tasks:list")
    extra_context = {"title": _("Update task"), "button_text": _("Update")}

    def form_valid(self, form: TaskForm) -> HttpResponse:
        messages.success(self.request, _("Task updated successfully"))
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks:list")
    extra_context = {
        "title": _("Delete task"),
        "button_text": _("Yes, delete"),
    }

    def test_func(self) -> bool:
        task = self.get_object()
        return task.author == self.request.user

    def handle_no_permission(self) -> HttpResponse:
        messages.error(self.request, _("Only task author can delete task"))
        return redirect("tasks:list")

    def form_valid(self, form: BaseForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, _("Task deleted successfully"))
        return response
