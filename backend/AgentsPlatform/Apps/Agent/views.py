import hashlib
import socket
import sys
import threading
import time
from venv import logger
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Agent
from .serializer import AgentSerializer
from .Util import ChordNode, ChordNodeReference, getShaRepr

BROADCAST_PORT = 50000 # Puedes cambiarlo
SERVER_IP = socket.gethostbyname(socket.gethostname())
BROADCAST_ADDRESS = '<broadcast>' 
FIND_SUCCESSOR = 1
FIND_PREDECESSOR = 2
GET_SUCCESSOR = 3
GET_PREDECESSOR = 4
NOTIFY = 5
CLOSEST_PRECEDING_FINGER = 7
IS_ALIVE = 8
NOTIFY1 = 9
STORE_KEY = 10

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

@api_view(['GET'])
def get_all_agents(request):
    all_agents = []
    seen_names = set()  # Para rastrear agentes ya vistos
    
    local_agents = Agent.objects.all()  # Obtener todos los objetos
    for agent in local_agents:
        if agent.name not in seen_names:
            all_agents.append(AgentSerializer(agent).data)
            seen_names.add(agent.name)
    current_node_ip = node.ip
    next_node_ip = node.succ

    while next_node_ip.ip != current_node_ip:
        logger.error(f"ip en get_agent: {next_node_ip.ip}")
        try:
            next_node_ip.succ
        except:
            next_node_ip = node.succ
            time.sleep(3)
            continue
        remote_agents = get_agent_from_server(next_node_ip.ip)
        # Agregar funcionalidades únicas a la lista
        for agent_data in remote_agents:
            if agent_data['name'] not in seen_names:
                all_agents.append(agent_data)
                seen_names.add(agent_data['name'])
        next_node_ip = next_node_ip.succ
    return Response(all_agents)

@api_view(['POST'])
def create_agent(request):
    serializer = AgentSerializer(data=request.data)
    logger.error("entro en create Agent")
    serializer.is_valid()
    try:
        logger.error("fue valido")
        key_hash = getShaRepr(request.data['name'])
        logger.error(f"key_hash_agent: {key_hash}")
        if node._inrange(key_hash, node.id, node.succ.id):
            logger.error("entro en inrange_agent")
            if serializer.is_valid():
                agent = serializer.save()
            if node.pred.ip != node.ip:
                while True:
                    try:
                        response = send_agent1(node.pred.ip, name= request.data['name'], belongs="2")
                    except:
                        time.sleep(1)
                        continue
                    break
            if node.pred2.ip != node.ip:
                while True:
                    try:
                        response = send_agent1(node.pred2.ip, name= request.data['name'], belongs="3")
                    except:
                        time.sleep(1)
                        continue
                    break
        else:
            node1 = node.closest_preceding_finger(key_hash)
            logger.error("no estaba en el rango_agent")
            logger.error(f"node1: {node1}")
            url3 = f'http://{node1.ip}:8000/appAgent/agent/create/'
            response = requests.post(url3, json=request.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create1(request):
    name = request.data.get('name')  # Obtener el nombre del agente
    belongs = request.data.get('belongs') # Obtener el belongs

    if not name or not belongs:
        return Response({'error': 'Name and belongs are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Intentar obtener la funcionalidad existente
        agent = Agent.objects.get(pk=name)

        if agent.belongs == belongs:
            # Ya existe y tiene el mismo belongs, no hacer nada
            serializer = AgentSerializer(agent) # Serializar el agente existente
            return Response(serializer.data, status=status.HTTP_200_OK)  # o status.HTTP_204_NO_CONTENT

        else:
            # Ya existe pero con diferente belongs, actualizar
            agent.belongs = belongs
            agent.save()  # Guardar la funcionalidad actualizada
            serializer = AgentSerializer(agent) # Serializar la funcionalidad actualizada
            return Response(serializer.data, status=status.HTTP_200_OK)

    except Agent.DoesNotExist:
        # El agente no existe, crearlo
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def agent_detail(request,pk):
    key_hash = getShaRepr(pk)
    
    if request.method == 'GET':
        if node._inrange(key_hash, node.id, node.succ.id):
            agent = Agent.objects.get(pk=pk)
            serializer = AgentSerializer(agent)
            return Response(serializer.data)
        else:
            node1 = node.closest_preceding_finger(key_hash)
            url = f'http://{node1.ip}:8000/appAgent/agent/{pk}'
            response = requests.get(url)
            return Response(response)
    
    elif request.method == 'PUT':
        if node._inrange(key_hash, node.id, node.succ.id):
            agent = Agent.objects.get(pk=pk)
            serializer = AgentSerializer(agent, data=request.data)
            if serializer.is_valid():
                agent.delete()
                serializer.save()
                url = f'http://{node.pred.ip}:8000/appAgent/agent/put1/{pk}'
                requests.put(url)
                url = f'http://{node.pred2.ip}:8000/appAgent/agent/put1/{pk}'
                requests.put(url)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            node1 = node.closest_preceding_finger(key_hash)
            url = f'http://{node1.ip}:8000/appAgent/agent/{pk}'
            response = requests.put(url)
            return Response(response)
    
    elif request.method == 'DELETE':
        if node._inrange(key_hash, node.id, node.succ.id):
            agent = Agent.objects.get(pk=pk)
            agent.delete()
            url = f'http://{node.pred.ip}:8000/appAgent/agent/delete1/{pk}'
            requests.delete(url)
            url = f'http://{node.pred2.ip}:8000/appAgent/agent/delete1/{pk}'
            requests.delete(url)
        else:
            node1 = node.closest_preceding_finger(key_hash)
            url = f'http://{node1.ip}:8000/appAgent/agent/{pk}'
            response = requests.delete(url)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def delete1(request,pk):
    agent = Agent.objects.get(pk=pk)
    agent.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
def put1(request,pk):
    agent = Agent.objects.get(pk=pk)
    serializer = AgentSerializer(agent, data=request.data)
    if serializer.is_valid():
        agent.delete()
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def replicate_agents(request):
    """
    Replicates agents to another server based on SHA-1 hash and updates 'pertenece' to "1".

    Args:
        target_ip (str): The IP address of the server to replicate to.
        threshold (int): The minimum SHA-1 hash value for replication.
    """
    target_ip, threshold = request.data['target_ip'], request.data['threshold']
    id = getShaRepr(ip)
    agents = Agent.objects.all()  # Get all Agents
    for agent in agents:
        sha_repr = getShaRepr(agent.name)
        if sha_repr > threshold or sha_repr < id:
            # Prepare the data for the POST request
            data = AgentSerializer(agent).data  # Serialize the object
            #data['pertenece'] = '1'  # Set pertenece to "1" *before* sending

            # Construct the URL for the POST endpoint on the target server
            url = f"http://{target_ip}:8000/appAgent/agent/create1"

            try:
                # Send the POST request
                response = requests.post(url, json=data)  # Use json=data for sending JSON

                # Check the response status
                if response.status_code == 201:
                    print(f"Agnet '{agent.name}' replicated successfully to {target_ip} and pertenece set to '1'")
                else:
                    print(f"Error replicating functionality '{agent.name}' to {target_ip}: {response.status_code} - {response.text}")  # Imprime el texto de la respuesta
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {target_ip}: {e}")
            
            if agent.belongs == "3":
                agent.delete()
            elif agent.belongs == "2":
                agent.belongs = "3"
                agent.save()
            elif agent.belongs == "1":
                agent.belongs = "2"
                agent.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def delte_agent(request):
    threshold = request.data['threshold']
    agents = Agent.objects.all()

    for agent in agents:
        id = getShaRepr(agent.name)
        if agent.belongs == "3":
            agent.delete()
        elif agent.belongs == "2" and id > threshold:
            agent.belongs = "3"
            agent.save() 

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def update_succ(request):
    local_agents = Agent.objects.all()  # Obtener todos los objetos
    for agent in local_agents:
        if agent.belongs == "2":
            while True:
                try:
                    send_agent1(node.pred2.ip, name=agent.name, belongs= "3")
                    break
                except:
                    time.sleep(1)
            while True:
                try:
                    send_agent1(node.pred.ip, name=agent.name, belongs= "2")
                    break
                except:
                    time.sleep(1)

            agent.belongs = "1"
            agent.save()
        elif agent.belongs == "3":
            agent.belongs = "2"
            agent.save()
    
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def update_pred(request):
    local_agents = Agent.objects.all()  # Obtener todos los objetos
    for agent in local_agents:
        if agent.belongs == "1":
            while True:
                try:
                    send_agent1(node.pred2.ip, name=agent.name, belongs= "3")
                    break
                except:
                    time.sleep(1)
            while True:
                try:
                    send_agent1(node.pred.ip, name=agent.name, belongs= "2")
                    break
                except:
                    time.sleep(1)

            agent.belongs = "1"
            agent.save()
        elif agent.belongs == "3":
            agent.belongs = "2"
            agent.save()
    
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def chord(request):

    option = int(request.data['op'])
    data = request.data['data']
    data_resp = None
    
    if data != None:
        data = data.split(',')
    logger.error(f"option: {option}")
    if option == FIND_SUCCESSOR:
        id = int(data[0])
        data_resp = node.find_succ(id)
    elif option == FIND_PREDECESSOR:
        id = int(data[0])
        data_resp = node.find_pred(id)
    elif option == GET_SUCCESSOR:
        data_resp = node.succ
    elif option == GET_PREDECESSOR:
        data_resp = node.pred
    elif option == NOTIFY:
        id = int(data[0])
        ip = data[1]
        node.notify(ChordNodeReference(ip, node.port))
    elif option == CLOSEST_PRECEDING_FINGER:
        id = int(data[0])
        data_resp = node.closest_preceding_finger(id)
    elif option == NOTIFY1:
        id = int(data[0])
        ip = data[1]
        node.notify1(ChordNodeReference(ip, node.port))
    elif option == IS_ALIVE:
        data_resp = 'alive'
    elif option == STORE_KEY:
        print(data)
        key, value = data[1], data[2]
        node.store_key(key, value)
        print(node.data)
        return node.data
    if data_resp == 'alive':
        response = data_resp
        return Response(response)
    elif data_resp:
        #logger.error(data_resp)
        response = Response(f'{data_resp.id},{data_resp.ip}')
        return response
    return Response(data_resp) 


########################################################################################
def send_agent1(node_ip, **kwargs):
    url = f'http://{node_ip}:8000/appAgent/agent/create1/'
    response = requests.post(url, json=kwargs)
    return response

def get_agent_from_server(ip):
    """Obtiene agentes de un servidor específico."""
    try:
        url = f"http://{ip}:8000/appAgent/agent_server/"  # Ajusta el puerto si es diferente
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener agentes de {ip}: {e}")
        return []  # En caso de error, devuelve una lista vacía.


#######################################################################################

from django.core.management import call_command
print("Resetting the database...")
call_command('flush', interactive=False)  # Limpia la base de datos
call_command('migrate')  # Aplica las migraciones
#Opcional: Cargar datos de prueba
#call_command('loaddata', 'tu_archivo_initial_data.json') #Reemplaza tu_archivo_initial_data.json
print("Database reset complete.")
ip = socket.gethostbyname(socket.gethostname())
node = ChordNode(ip)