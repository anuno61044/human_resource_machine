from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Agent
from .serializer import AgentSerializer

@api_view(['GET'])
def get_agents(request):
    # Obtener los valores de la propiedad 'function' desde el parámetro GET
    function_values = request.GET.getlist('function')
    
    if not function_values:
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data)
    
    # Filtrar los agentes por las propiedades 'function'
    filtered_agents = Agent.objects.filter(function__in=function_values)
             
    # Serializar los agentes filtrados
    serializer = AgentSerializer(filtered_agents, many=True)
    
    return Response(serializer.data)

@api_view(['POST'])
def create_agent(request):
    print(request.data["name"])
    serializer = AgentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def agent_detail(request,pk):
    try:
        agent = Agent.objects.get(pk=pk)
    except Agent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        print(agent.pythonCode)
        serializer = AgentSerializer(agent)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AgentSerializer(agent, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
            


