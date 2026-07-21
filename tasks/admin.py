from django.contrib import admin
from .models import Task, TaskCategory


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'farm', 'crop', 'category', 'assigned_to', 'priority', 'is_done', 'cost', 'created_at']
    list_filter = ['is_done', 'priority', 'category']
    search_fields = ['title', 'assigned_to']
    readonly_fields = ['id', 'created_at']


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm']
    search_fields = ['name']
