from rest_framework import serializers
from farm.models import Farm
from farmapi.scoping import OwnerScopedSerializerMixin
from .models import Crop, CropBasemap, Plant, PlantAttribute, PlantAttributeValue

# Text fields across these models (name, type, label, notes) accept either
# English or Arabic — the bilingual app sends the farmer's input as typed and
# the API stores it unchanged. There are no separate per-language columns.

# owner_scoped_fields (via OwnerScopedSerializerMixin) restrict which parent ids a
# client may reference on create/update — you can only attach to your own farm/crop.


class CropSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    owner_scoped_fields = {'farm': lambda u: Farm.objects.filter(owner=u)}

    class Meta:
        model = Crop
        fields = '__all__'
        read_only_fields = ['id', 'created_at']  # set by the server, not the client


class CropBasemapSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    owner_scoped_fields = {'crop': lambda u: Crop.objects.filter(farm__owner=u)}

    class Meta:
        model = CropBasemap
        fields = '__all__'
        read_only_fields = ['id', 'captured_at']

    def validate(self, attrs):
        """Enforce 'one active basemap per crop' as a clean 400 instead of a DB-level 500.

        The model's partial UniqueConstraint is the integrity backstop; this surfaces the
        same rule to API clients with a helpful message.
        """
        # Fall back to the existing instance's values on partial (PATCH) updates,
        # where is_active / crop may not be present in the payload.
        is_active = attrs.get('is_active', getattr(self.instance, 'is_active', True))
        crop = attrs.get('crop', getattr(self.instance, 'crop', None))
        if is_active and crop is not None:
            clashing = CropBasemap.objects.filter(crop=crop, is_active=True)
            if self.instance is not None:
                # On update, don't count the row we're editing as a clash with itself.
                clashing = clashing.exclude(pk=self.instance.pk)
            if clashing.exists():
                raise serializers.ValidationError({
                    'is_active': 'This crop already has an active basemap. '
                                 'Deactivate it first, or create this one with is_active=false.'
                })
        return attrs


class PlantSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    owner_scoped_fields = {'crop': lambda u: Crop.objects.filter(farm__owner=u)}

    class Meta:
        model = Plant
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PlantAttributeSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    """A user-defined per-plant field: the user names it and picks its value type."""
    owner_scoped_fields = {'crop': lambda u: Crop.objects.filter(farm__owner=u)}

    class Meta:
        model = PlantAttribute
        fields = '__all__'
        read_only_fields = ['id']


class PlantAttributeValueSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    owner_scoped_fields = {
        'attribute': lambda u: PlantAttribute.objects.filter(crop__farm__owner=u),
        'plant': lambda u: Plant.objects.filter(crop__farm__owner=u),
    }

    class Meta:
        model = PlantAttributeValue
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, attrs):
        """The stored JSON value must match the attribute's declared type, and the
        attribute must belong to the same crop as the plant."""
        # Fall back to instance values on partial (PATCH) updates.
        attribute = attrs.get('attribute', getattr(self.instance, 'attribute', None))
        plant = attrs.get('plant', getattr(self.instance, 'plant', None))
        value = attrs.get('value', getattr(self.instance, 'value', None))

        t = attribute.value_type
        # NB: bool is a subclass of int in Python, so exclude it explicitly for
        # the numeric types (True would otherwise pass as an int).
        ok = (
            (t == PlantAttribute.BOOL and isinstance(value, bool)) or
            (t == PlantAttribute.INT and isinstance(value, int) and not isinstance(value, bool)) or
            (t == PlantAttribute.FLOAT and isinstance(value, (int, float)) and not isinstance(value, bool)) or
            (t == PlantAttribute.TEXT and isinstance(value, str))
        )
        if not ok:
            raise serializers.ValidationError(
                {'value': f'This attribute expects a {t} value.'})

        if attribute.crop_id != plant.crop_id:
            raise serializers.ValidationError(
                'Attribute and plant belong to different crops.')
        return attrs
