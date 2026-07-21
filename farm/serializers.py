from rest_framework import serializers
from .models import Farm


class FarmSerializer(serializers.ModelSerializer):
    """JSON representation of a Farm.

    Free-text fields (name, location) may hold either English or Arabic — the
    bilingual mobile app sends whatever the farmer typed, and the API stores it
    verbatim. No per-language columns; the client decides what to display.
    """
    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'lat', 'lng', 'created_at']
        # id and created_at are assigned by the server, never accepted from the client.
        read_only_fields = ['id', 'created_at']
