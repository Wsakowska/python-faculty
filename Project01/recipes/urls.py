"""URL-e aplikacji recipes."""

from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.home, name='home'),
    path('przepisy/', views.recipe_list, name='recipe_list'),
    path('przepisy/dodaj/', views.recipe_create, name='recipe_create'),
    path('przepisy/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('przepisy/<slug:slug>/edytuj/', views.recipe_edit, name='recipe_edit'),
    path('przepisy/<slug:slug>/usun/', views.recipe_delete, name='recipe_delete'),
]