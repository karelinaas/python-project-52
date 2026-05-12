from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from statuses.forms import StatusForm
from statuses.models import Status


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/list.html"
    context_object_name = "statuses"
    extra_context = {"title": _("Statuses")}


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/create.html"
    success_url = reverse_lazy("statuses:list")
    extra_context = {"title": _("Create a status"), "button_text": _("Create")}

    def form_valid(self, form: StatusForm) -> HttpResponse:
        messages.success(self.request, _("Status created successfully"))
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/update.html"
    success_url = reverse_lazy("statuses:list")
    extra_context = {"title": _("Change a status"), "button_text": _("Change")}

    def form_valid(self, form: StatusForm) -> HttpResponse:
        messages.success(self.request, _("Status changed successfully"))
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("statuses:list")
    extra_context = {
        "title": _("Delete a status"),
        "button_text": _("Yes, delete"),
    }

    def form_valid(self, form: BaseForm) -> HttpResponse:
        try:
            response = super().form_valid(form)
            messages.success(self.request, _("Status deleted successfully"))
            return response
        except Exception:
            messages.error(self.request, _("Cannot be deleted"))
            return redirect("statuses:list")
