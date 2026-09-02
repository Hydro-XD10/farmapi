from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FarmViewSet, DashboardView

# DRF router auto-generates the list/detail routes (GET/POST/PUT/PATCH/DELETE)
# for the viewset. These get mounted under /api/ by the project's urls.py.
router = DefaultRouter()
router.register('farms', FarmViewSet, basename='farm')

urlpatterns = router.urls + [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
