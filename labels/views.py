from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseForm
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

from labels.forms import LabelForm
from labels.models import Label


class LabelListView(LoginRequiredMixin, ListView):
    model = Label
    template_name = "labels/list.html"
    context_object_name = "labels"
    extra_context = {"title": _("Labels")}


class LabelCreateView(LoginRequiredMixin, CreateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/create.html"
    success_url = reverse_lazy("labels:list")
    extra_context = {"title": _("Create label"), "button_text": _("Create")}

    def form_valid(self, form: LabelForm) -> HttpResponse:
        messages.success(self.request, _("Label created successfully"))
        return super().form_valid(form)


class LabelUpdateView(LoginRequiredMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = "labels/update.html"
    success_url = reverse_lazy("labels:list")
    extra_context = {"title": _("Update label"), "button_text": _("Update")}

    def form_valid(self, form: LabelForm) -> HttpResponse:
        messages.success(self.request, _("Label updated successfully"))
        return super().form_valid(form)


class LabelDeleteView(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels:list")
    extra_context = {
        "title": _("Delete label"),
        "button_text": _("Yes, delete"),
    }

    def form_valid(self, form: BaseForm) -> HttpResponse:
        label = self.get_object()
        if label.tasks.exists():
            messages.error(
                self.request,
                _("Cannot delete label because it is in use"),
            )
            return redirect("labels:list")
        
        response = super().form_valid(form)
        messages.success(self.request, _("Label deleted successfully"))
        return response
