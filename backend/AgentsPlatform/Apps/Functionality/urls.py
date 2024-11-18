from django.urls import path
from .views import get_functionalities, create_functionality, functionality_detail

urlpatterns = [
    path('functionality/', get_functionalities, name='get_functionalities'),
    path("functionality/create/", create_functionality, name="create_functionality"),
    path("functionality/<int:pk>", functionality_detail, name="functionality_detail")
]
