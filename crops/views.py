from rest_framework import viewsets
from .models import Crop, CropBasemap, Plant, PlantAttribute, PlantAttributeValue
from .serializers import (CropSerializer, CropBasemapSerializer, PlantSerializer,
                          PlantAttributeSerializer, PlantAttributeValueSerializer)


class CropViewSet(viewsets.ModelViewSet):
    """CRUD for crops. Scoped to the logged-in user via the farm's owner.
    Optional ?farm=<id> filter to narrow to one of the user's farms."""
    queryset = Crop.objects.all()
    serializer_class = CropSerializer

    def get_queryset(self):
        # Only crops whose farm belongs to the current user. This controls what
        # can be listed, retrieved, updated, or deleted.
        qs = super().get_queryset().filter(farm__owner=self.request.user)
        # /api/crops/?farm=<uuid> — further narrow to a single farm when provided.
        farm = self.request.query_params.get('farm')
        if farm:
            qs = qs.filter(farm_id=farm)
        return qs


class CropBasemapViewSet(viewsets.ModelViewSet):
    """CRUD for crop basemaps. Scoped to the user via crop -> farm -> owner.
    Optional ?crop=<id> filter."""
    queryset = CropBasemap.objects.all()
    serializer_class = CropBasemapSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(crop__farm__owner=self.request.user)
        # /api/basemaps/?crop=<uuid> — fetch the basemap(s) for one crop.
        crop = self.request.query_params.get('crop')
        if crop:
            qs = qs.filter(crop_id=crop)
        return qs


class PlantViewSet(viewsets.ModelViewSet):
    """CRUD for plants positioned on a crop's basemap. Scoped to the user via
    crop -> farm -> owner. Optional ?crop=<id> filter."""
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(crop__farm__owner=self.request.user)
        # /api/plants/?crop=<uuid> — load all plant pins for one crop.
        crop = self.request.query_params.get('crop')
        if crop:
            qs = qs.filter(crop_id=crop)
        return qs


class PlantAttributeViewSet(viewsets.ModelViewSet):
    """CRUD for user-defined plant attributes (definitions). ?crop=<id> filter."""
    queryset = PlantAttribute.objects.all()
    serializer_class = PlantAttributeSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(crop__farm__owner=self.request.user)
        crop = self.request.query_params.get('crop')
        if crop:
            qs = qs.filter(crop_id=crop)
        return qs


class PlantAttributeValueViewSet(viewsets.ModelViewSet):
    """CRUD for attribute values on plants. Filters: ?plant=<id>, ?attribute=<id>."""
    queryset = PlantAttributeValue.objects.all()
    serializer_class = PlantAttributeValueSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(plant__crop__farm__owner=self.request.user)
        plant = self.request.query_params.get('plant')
        attribute = self.request.query_params.get('attribute')
        if plant:
            qs = qs.filter(plant_id=plant)
        if attribute:
            qs = qs.filter(attribute_id=attribute)
        return qs
