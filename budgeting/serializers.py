from rest_framework import serializers
from django.db.models import Q
from farm.models import Farm
from crops.models import Crop
from farmapi.scoping import OwnerScopedSerializerMixin
from .models import Category, Transaction


class CategorySerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    # A user-made category may only attach to the user's own farm.
    owner_scoped_fields = {'farm': lambda u: Farm.objects.filter(owner=u)}

    class Meta:
        model = Category
        fields = '__all__'
        # is_user_made is server-controlled (always True for API-created categories);
        # the shared system categories (farm=NULL, is_user_made=False) are created only
        # by the seed migration, never through the API.
        read_only_fields = ['id', 'is_user_made']
        # farm is required so a user can't create a global/system category (farm=NULL)
        # that would leak into every other user's list.
        extra_kwargs = {'farm': {'required': True, 'allow_null': False}}


class TransactionSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    # farm/crop must be the user's own; category may be the user's own OR a shared
    # system category (farm=NULL).
    owner_scoped_fields = {
        'farm': lambda u: Farm.objects.filter(owner=u),
        'crop': lambda u: Crop.objects.filter(farm__owner=u),
        'category': lambda u: Category.objects.filter(Q(farm__owner=u) | Q(farm__isnull=True)),
    }

    class Meta:
        model = Transaction
        fields = '__all__'
        # task is server-managed: it marks the auto-created expense for a Task's
        # cost (tasks/signals.py). Clients must not set or reassign it.
        read_only_fields = ['id', 'created_at', 'task']
