from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Label")
        verbose_name_plural = _("Labels")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("labels:update", kwargs={"pk": self.pk})
