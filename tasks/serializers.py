from rest_framework import serializers
from farm.models import Farm
from crops.models import Crop, Plant
from farmapi.scoping import OwnerScopedSerializerMixin
from .models import Task, TaskCategory


class TaskCategorySerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    # A task category may only attach to the user's own farm.
    owner_scoped_fields = {'farm': lambda u: Farm.objects.filter(owner=u)}

    class Meta:
        model = TaskCategory
        fields = '__all__'
        read_only_fields = ['id']


class TaskSerializer(OwnerScopedSerializerMixin, serializers.ModelSerializer):
    # A task may only reference the user's own farm/crop/plant/category.
    owner_scoped_fields = {
        'farm': lambda u: Farm.objects.filter(owner=u),
        'crop': lambda u: Crop.objects.filter(farm__owner=u),
        'plant': lambda u: Plant.objects.filter(crop__farm__owner=u),
        'category': lambda u: TaskCategory.objects.filter(farm__owner=u),
    }

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at']  # server-managed
