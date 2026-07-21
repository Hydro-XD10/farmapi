from django.contrib import admin
from .models import Farm


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    # Admin is for staff data inspection. name/location may be English or Arabic;
    # Django's admin renders both fine, and search works across either script.
    list_display = ['name', 'location', 'lat', 'lng', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['id', 'created_at']  # server-managed, not editable here
