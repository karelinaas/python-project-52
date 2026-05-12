from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "author",
        "executor",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "author", "executor", "created_at", "updated_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Task]:
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def has_change_permission(
        self,
        request: HttpRequest,
        task: Task = None,
    ) -> bool:
        return task is None or (
            request.user.is_superuser or task.author == request.user
        )
    
    def has_delete_permission(
        self,
        request: HttpRequest,
        task: Task = None,
    ) -> bool:
        return task is None or (
            request.user.is_superuser or task.author == request.user
        )
