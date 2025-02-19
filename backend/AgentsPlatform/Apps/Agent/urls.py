from django.urls import path
from .views import get_agents, create_agent, agent_detail, chord, create1, replicate_agents, delte_agent, update_succ, update_pred, get_all_agents, put1, delete1

urlpatterns = [
    path('agent/', get_all_agents, name='get_all_agents'),
    path('agent_server/', get_agents, name='get_agents'),
    path('agent/create/', create_agent, name='create_agent'),
    path("agent/create1/", create1, name="create1"),
    path("agent/<str:pk>", agent_detail, name="agent_detail"),
    path("agent/put1/<str:pk>", put1, name="put1"),
    path("agent/chord/", chord, name="chord"),
    path("agent/replicate/", replicate_agents, name="replicate_agents"),
    path("agent/delagent/", delte_agent, name="delte_agent"),
    path("agent/delete1/<str:pk>", delete1, name="delete1"),
    path("agent/update_succ/", update_succ, name="update_succ"),
    path("agent/update_pred/", update_pred, name="update_pred")
]