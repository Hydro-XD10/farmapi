from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """GET /api/plants/stats/ — totals for the user's plants: counts and bunch
        (عذوق) sums, overall and per type. Reuses get_queryset, so it is owner-scoped
        and honors ?crop=; add ?type= to narrow to one type."""
        qs = self.get_queryset()
        type_ = request.query_params.get('type')
        if type_:
            qs = qs.filter(type=type_)
        totals = qs.aggregate(total_plants=Count('id'), total_bunches=Sum('bunch'))
        by_type = (qs.values('type')
                     .annotate(plants=Count('id'), bunches=Sum('bunch'))
                     .order_by('-plants'))
        return Response({
            'total_plants': totals['total_plants'],
            'total_bunches': totals['total_bunches'] or 0,
            'by_type': [
                {'type': r['type'], 'plants': r['plants'], 'bunches': r['bunches'] or 0}
                for r in by_type
            ],
        })


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
