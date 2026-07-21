from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCategoryViewSet

# Mounted under /api/ by the project urls.py -> /api/tasks/, /api/task-categories/
router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')
router.register('task-categories', TaskCategoryViewSet, basename='task-category')

urlpatterns = router.urls
