from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import execute_no_native

@api_view(['POST'])
def execute_agent(request):
    
    answer = execute_no_native(request.data["agents"], request.data["input"])
    return Response(answer)

