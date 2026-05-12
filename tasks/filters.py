import django_filters
from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from labels.models import Label
from statuses.models import Status
from tasks.models import Task
from users.models import User


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        field_name="status",
        label=_("Status"),
        empty_label=_("All statuses"),
    )
    
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name="executor",
        label=_("Executor"),
        empty_label=_("All executors"),
    )
    
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        field_name="labels",
        label=_("Label"),
        empty_label=_("All labels"),
    )
    
    own_tasks = django_filters.BooleanFilter(
        method="filter_own_tasks",
        label=_("Only own tasks"),
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = ["status", "executor", "labels", "own_tasks"]

    def filter_own_tasks(
        self,
        queryset: QuerySet[Task],
        _: str,
        value: bool,
    ) -> QuerySet[Task]:
        if value:
            user = getattr(self.request, "user", None)
            if user and user.is_authenticated:
                return queryset.filter(author=user)
        return queryset
