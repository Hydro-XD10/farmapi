import uuid
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator, MaxValueValidator


class Crop(models.Model):
    """المحصول / الحقل — a crop/field belonging to a farm."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey('farm.Farm', on_delete=models.CASCADE, related_name='crops')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CropBasemap(models.Model):
    """صورة الخلفية — frozen background photo for a crop. Plants are positioned on this image."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='basemaps')
    image_uri = models.CharField(max_length=500)   # external URI; switch to ImageField for direct uploads
    source = models.CharField(max_length=50, blank=True, null=True)  # 'user_upload', 'mapbox'...
    width_px = models.IntegerField(null=True, blank=True)
    height_px = models.IntegerField(null=True, blank=True)
    center_lat = models.FloatField(null=True, blank=True)
    center_lng = models.FloatField(null=True, blank=True)
    zoom = models.FloatField(null=True, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-captured_at']
        constraints = [
            models.UniqueConstraint(
                fields=['crop'], condition=Q(is_active=True),
                name='one_active_basemap_per_crop',
            )
        ]

    def __str__(self):
        return f'Basemap for {self.crop} ({self.source or "unknown"})'


class Plant(models.Model):
    """النبتة — a free point on the crop's basemap photo. img_x/img_y normalized 0..1."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='plants')
    label = models.CharField(max_length=255, blank=True, null=True)
    img_x = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    img_y = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    color = models.CharField(max_length=9, default='#4F8F2C')
    type = models.CharField(max_length=255, blank=True, null=True)
    age_months = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    is_special = models.BooleanField(default=False)
    needs_care = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    srblh = models.BooleanField(default=False) # سربله ولا لا
    bunch = models.IntegerField(default=0,null=True,blank=True) #عذوق 
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.label or f'Plant {self.id}'


class PlantAttribute(models.Model):
    """خاصية نبات — a user-DEFINED per-plant field (e.g. مسربل: yes/no,
    عدد العذوق: whole number). Users pick the name AND the value type, since we
    can't predict what they want to track. Replaces the old fixed PlantCategory."""
    BOOL, INT, FLOAT, TEXT = 'bool', 'int', 'float', 'text'
    TYPE_CHOICES = [(BOOL, 'Yes/No'), (INT, 'Whole number'),
                    (FLOAT, 'Decimal number'), (TEXT, 'Text')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='plant_attributes')
    name = models.CharField(max_length=255)   # EN/AR
    value_type = models.CharField(max_length=5, choices=TYPE_CHOICES)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['crop', 'name'],
                                    name='unique_attribute_per_crop'),
        ]

    def __str__(self):
        return f'{self.name} ({self.value_type})'


class PlantAttributeValue(models.Model):
    """The value of one attribute for one plant. JSONField holds any JSON type
    (true / 12 / 2.5 / "نص"); the serializer enforces it matches the attribute's
    declared value_type."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(PlantAttribute, on_delete=models.CASCADE, related_name='values')
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='attribute_values')
    value = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['attribute', 'plant'],
                                    name='one_value_per_plant_per_attribute'),
        ]

    def __str__(self):
        return f'{self.plant}: {self.attribute.name} = {self.value!r}'