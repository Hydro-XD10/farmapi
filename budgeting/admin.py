from django.contrib import admin
from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm', 'is_user_made']
    list_filter = ['is_user_made']
    search_fields = ['name']
    readonly_fields = ['id']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'amount', 'farm', 'crop', 'category', 'date_gregorian', 'created_at']
    list_filter = ['type', 'from_supplier']
    search_fields = ['notes']
    readonly_fields = ['id', 'created_at']
