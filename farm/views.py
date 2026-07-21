from rest_framework import viewsets
from .models import Farm
from .serializers import FarmSerializer

class FarmViewSet(viewsets.ModelViewSet):
    """CRUD for farms, scoped to the logged-in user."""
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer

    def get_queryset(self):
        # Only the current user's farms — controls list/retrieve/update/delete.
        return super().get_queryset().filter(owner=self.request.user)

    def perform_create(self, serializer):
        # New farms are automatically owned by whoever created them.
        serializer.save(owner=self.request.user)