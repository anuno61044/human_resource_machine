from django.urls import path
from .views import get_agents, create_agent, agent_detail, chord

urlpatterns = [
    path('agent/', get_agents, name='get_agents'),
    path('agent/create/', create_agent, name='create_agent'),
    path("agent/<str:pk>", agent_detail, name="agent_detail"),
    path("agent/chord/", chord, name="chord")
]