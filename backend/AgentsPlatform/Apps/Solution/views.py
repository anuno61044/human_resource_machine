from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import execute_no_native
import socket

@api_view(['GET'])
def get_ip(request):
    
    # Obtener la dirección IP del servidor
    server_ip = socket.gethostbyname(socket.gethostname())
    
    return Response(server_ip)

@api_view(['POST'])
def execute_agent(request):
    
    answer = execute_no_native(request.data["agents"], request.data["input"])
    return Response(answer)

