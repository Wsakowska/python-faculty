"""URL-e aplikacji ai_assistant."""

from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.ai_chat, name='chat'),
]