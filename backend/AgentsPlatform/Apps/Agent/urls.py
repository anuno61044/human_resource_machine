from django.urls import path
from .views import get_agents, create_agent, agent_detail

urlpatterns = [
    path('agent/', get_agents, name='get_agents'),
    path('agent/create/', create_agent, name='create_agent'),
    path("agent/<int:pk>", agent_detail, name="agent_detail")
]