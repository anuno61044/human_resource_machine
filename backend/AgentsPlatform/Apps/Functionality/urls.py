from django.urls import path
from .views import get_functionalities, create_functionality, functionality_detail, get_hello

urlpatterns = [
    path('functionality/', get_functionalities, name='get_functionalities'),
    path('functionality/hello', get_hello, name='get_hello'),
    path("functionality/create/", create_functionality, name="create_functionality"),
    path("functionality/<str:pk>", functionality_detail, name="functionality_detail")
]
