from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Functionality
from .serializer import FunctionalitySerializer

@api_view(['GET'])
def get_functionalities(request):
    functionalities = Functionality.objects.all()
    serializer = FunctionalitySerializer(functionalities, many=True)
    
    return Response(serializer.data)

@api_view(['POST'])
def create_functionality(request):
    serializer = FunctionalitySerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def functionality_detail(request,pk):
    try:
        functionality = Functionality.objects.get(pk=pk)
    except Functionality.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = FunctionalitySerializer(functionality)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = FunctionalitySerializer(functionality, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        functionality.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
            


