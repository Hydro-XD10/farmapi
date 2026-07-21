from rest_framework.routers import DefaultRouter
from .views import (CropViewSet, CropBasemapViewSet, PlantViewSet,
                    PlantAttributeViewSet, PlantAttributeValueViewSet)

# Mounted under /api/ by the project's urls.py.
router = DefaultRouter()
router.register('crops', CropViewSet, basename='crop')
router.register('basemaps', CropBasemapViewSet, basename='basemap')
router.register('plants', PlantViewSet, basename='plant')
router.register('plant-attributes', PlantAttributeViewSet, basename='plant-attribute')
router.register('plant-attribute-values', PlantAttributeValueViewSet, basename='plant-attribute-value')

urlpatterns = router.urls
