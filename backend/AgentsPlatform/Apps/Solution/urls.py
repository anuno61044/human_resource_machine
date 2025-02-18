from django.urls import path
from .views import execute_agent, get_ip

urlpatterns = [
    path('solution/', execute_agent, name='execute_agent'),
    path('solution/ip', get_ip, name='get_ip')
]
