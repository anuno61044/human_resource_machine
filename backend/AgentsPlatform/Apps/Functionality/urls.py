from django.urls import path
from .views import get_functionalities, create_functionality, functionality_detail, replicate_functionalities, delte_funcionality, create1,delete1, get_all_funcionalities, update_succ, update_pred

urlpatterns = [
    path('functionality/', get_all_funcionalities, name='get_all_funcionalities'),
    path('functionality_server/', get_functionalities, name='get_functionalities'),
    path("functionality/create/", create_functionality, name="create_functionality"),
    path("functionality/create1/", create1, name="create1"),
    path("functionality/<str:pk>", functionality_detail, name="functionality_detail"),
    path("functionality/replicate/", replicate_functionalities, name="replicate_functionalities"),
    path("functionality/delfuncionality/", delte_funcionality, name="delte_funcionality"),
    path("functionality/delete1/<str:pk>", delete1, name="delete1"),
    path("functionality/update_succ/", update_succ, name="update_succ"),
    path("functionality/update_pred/", update_pred, name="update_pred")
]
