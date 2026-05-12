from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "status", "executor", "labels"]
        labels = {
            "name": _("Name"),
            "description": _("Description"),
            "status": _("Status"),
            "executor": _("Executor"),
            "labels": _("Labels"),
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Name"),
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Description"),
                    "rows": 3,
                },
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "executor": forms.Select(
                attrs={
                    "class": "form-select",
                },
            ),
            "labels": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].queryset = Status.objects.all()
        self.fields["status"].empty_label = _("---------")
        
        User = get_user_model()
        self.fields["executor"].queryset = User.objects.all()
        self.fields["executor"].empty_label = _("---------")
        
        self.fields["labels"].queryset = Label.objects.all()
        self.fields["labels"].empty_label = _("---------")
