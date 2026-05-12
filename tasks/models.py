from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name"),
    )
    description = models.TextField(verbose_name=_("Description"), blank=True)
    status = models.ForeignKey(
        "statuses.Status",
        on_delete=models.PROTECT,
        verbose_name=_("Status"),
    )
    author = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="authored_tasks",
        verbose_name=_("Author"),
    )
    executor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executed_tasks",
        verbose_name=_("Executor"),
    )
    labels = models.ManyToManyField(
        "labels.Label",
        blank=True,
        related_name="tasks",
        verbose_name=_("Labels"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tasks:detail", kwargs={"pk": self.pk})
