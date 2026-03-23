"""URL-e REST API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'kategorie', views.CategoryViewSet)
router.register(r'skladniki', views.IngredientViewSet)
router.register(r'przepisy', views.RecipeViewSet)
router.register(r'preferencje', views.DietaryPreferenceViewSet)

urlpatterns = [
    # Endpointy API
    path('', include(router.urls)),
    path('szukaj/', views.search_by_ingredients, name='search'),

    # Dokumentacja Swagger / OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
]