from django.urls import path
from .views import execute_agent

urlpatterns = [
    path('solution/', execute_agent, name='execute_agent')
    ]
