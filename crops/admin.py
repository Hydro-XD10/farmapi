from django.contrib import admin
from .models import Crop, CropBasemap, Plant, PlantAttribute, PlantAttributeValue

# Staff-facing admin for inspecting/seeding data. Text fields hold English or
# Arabic as entered; search and filters work across either script.


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'farm', 'created_at']
    list_filter = ['type']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at']


@admin.register(CropBasemap)
class CropBasemapAdmin(admin.ModelAdmin):
    list_display = ['crop', 'source', 'width_px', 'height_px', 'is_active', 'captured_at']
    list_filter = ['is_active', 'source']
    readonly_fields = ['id', 'captured_at']


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['label', 'crop', 'type', 'is_special', 'needs_care', 'created_at']
    list_filter = ['is_special', 'needs_care', 'type']
    search_fields = ['label']
    readonly_fields = ['id', 'created_at']


@admin.register(PlantAttribute)
class PlantAttributeAdmin(admin.ModelAdmin):
    list_display = ['name', 'value_type', 'crop']
    list_filter = ['value_type']
    search_fields = ['name']


@admin.register(PlantAttributeValue)
class PlantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['plant', 'attribute', 'value']
    search_fields = ['attribute__name', 'plant__label']
