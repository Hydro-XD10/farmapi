from rest_framework import viewsets
from .models import Task, TaskCategory
from .serializers import TaskSerializer, TaskCategorySerializer


class TaskCategoryViewSet(viewsets.ModelViewSet):
    """CRUD for user-made task categories, scoped to the logged-in user.
    Optional ?farm=<id> filter."""
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(farm__owner=self.request.user)
        farm = self.request.query_params.get('farm')
        if farm:
            qs = qs.filter(farm_id=farm)
        return qs


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for tasks, scoped to the logged-in user via the farm's owner.
    Optional filters: ?farm=<id>, ?crop=<id>, ?is_done=true|false."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Only tasks whose farm belongs to the current user.
        qs = super().get_queryset().filter(farm__owner=self.request.user)
        farm = self.request.query_params.get('farm')
        crop = self.request.query_params.get('crop')
        is_done = self.request.query_params.get('is_done')
        if farm:
            qs = qs.filter(farm_id=farm)
        if crop:
            qs = qs.filter(crop_id=crop)
        if is_done is not None:
            qs = qs.filter(is_done=(is_done.lower() == 'true'))
        return qs
