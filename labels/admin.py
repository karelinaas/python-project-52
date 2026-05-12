from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from labels.models import Label


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    ordering = ("name",)
    
    fieldsets = (
        (
            None,
            {
                "fields": ("name",),
            },
        ),
        (
            _("Additional information"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )
    
    readonly_fields = ("created_at",)
