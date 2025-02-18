import hashlib
import socket
import time
from venv import logger
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Functionality
from .serializer import FunctionalitySerializer
from ..Agent.views import node
ip = socket.gethostbyname(socket.gethostname())

@api_view(['GET'])
def get_functionalities(request):
    functionalities = Functionality.objects.all()
    serializer = FunctionalitySerializer(functionalities, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_all_funcionalities(request):
    all_functionalities = []
    seen_names = set()  # Para rastrear funcionalidades ya vistas
    
    local_functionalities = Functionality.objects.all()  # Obtener todos los objetos
    for func in local_functionalities:
        if func.name not in seen_names:
            all_functionalities.append(FunctionalitySerializer(func).data)
            seen_names.add(func.name)
    current_node_ip = node.ip
    next_node_ip = node.succ
    logger.error("entro en el get de funcionality")
    while next_node_ip.ip != current_node_ip:
        logger.error(f"ip en get: {next_node_ip.ip}")
        try:
            next_node_ip.succ
        except:
            next_node_ip = node.succ
            time.sleep(3)
            continue
        remote_functionalities = get_func_from_server(next_node_ip.ip)
        # Agregar funcionalidades únicas a la lista
        for func_data in remote_functionalities:
            if func_data['name'] not in seen_names:
                all_functionalities.append(func_data)
                seen_names.add(func_data['name'])
        next_node_ip = next_node_ip.succ
    return Response(all_functionalities)

@api_view(['POST'])
def create_functionality(request):
    serializer = FunctionalitySerializer(data=request.data)
    logger.error("create function")
    if serializer.is_valid():
        key_hash = getShaRepr(request.data['name'])
        logger.error(f"key_hash: {key_hash}")
        if node._inrange(key_hash, node.id, node.succ.id):
            logger.error("entro en inrange")
            funcionality = serializer.save()
            if node.pred.ip != node.ip:
                while True:
                    try:
                        response = send_funcionality1(node.pred.ip, name= request.data['name'], belongs="2")
                    except:
                        time.sleep(1)
                        continue
                    break
            if node.pred2.ip != node.ip:
                while True:
                    try:
                        response = send_funcionality1(node.pred2.ip, name= request.data['name'], belongs="3")
                    except:
                        time.sleep(1)
                        continue
                    break
        else:
            node1 = node.closest_preceding_finger(key_hash)
            logger.error("no estaba en el rango")
            logger.error(f"node1: {node1}")
            url3 = f'http://{node1.ip}:8000/appFunctionality/functionality/create/'
            response = requests.post(url3, json=request.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create1(request):
    name = request.data.get('name')  # Obtener el nombre de la funcionalidad
    belongs = request.data.get('belongs') # Obtener el belongs

    if not name or not belongs:
        return Response({'error': 'Name and belongs are required.'}, status=status.HTTP_400_BAD_REQUEST)
    logger.error(f"entro en create1 con func_name: {name}")
    try:
        # Intentar obtener la funcionalidad existente
        functionality = Functionality.objects.get(pk=name)

        if functionality.belongs == belongs:
            # Ya existe y tiene el mismo belongs, no hacer nada
            serializer = FunctionalitySerializer(functionality) # Serializar la funcionalidad existente
            return Response(serializer.data, status=status.HTTP_200_OK)  # o status.HTTP_204_NO_CONTENT

        else:
            # Ya existe pero con diferente belongs, actualizar
            functionality.belongs = belongs
            functionality.save()  # Guardar la funcionalidad actualizada
            serializer = FunctionalitySerializer(functionality) # Serializar la funcionalidad actualizada
            return Response(serializer.data, status=status.HTTP_200_OK)

    except Functionality.DoesNotExist:
        # La funcionalidad no existe, crearla
        serializer = FunctionalitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.error(f"se creo la funcion: {name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def functionality_detail(request,pk):
    
    key_hash = getShaRepr(pk)
    if request.method == 'GET':
        
        if node._inrange(key_hash, node.id, node.succ.id):
            functionality = Functionality.objects.get(pk=pk)
            serializer = FunctionalitySerializer(functionality)
            return Response(serializer.data)
        else:
            node1 = node.closest_preceding_finger(key_hash)
            url = f'http://{node1.ip}:8000/appFunctionality/functionality/{pk}'
            response = requests.get(url)
            return response
    
    #elif request.method == 'PUT':
    #    serializer = FunctionalitySerializer(functionality, data=request.data)
    #    if serializer.is_valid():
    #        functionality.delete()
    #        serializer.save()
    #        return Response(serializer.data)
    #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if node._inrange(key_hash, node.id, node.succ.id):
            functionality = Functionality.objects.get(pk=pk)
            functionality.delete()
            url = f'http://{node.pred.ip}:8000/appFunctionality/functionality/delete1/{pk}'
            requests.delete(url)
            url = f'http://{node.pred2.ip}:8000/appFunctionality/functionality/delete1/{pk}'
            requests.delete(url)
        else:
            node1 = node.closest_preceding_finger(key_hash)
            url = f'http://{node1.ip}:8000/appFunctionality/functionality/{pk}'
            response = requests.delete(url)
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def delete1(request,pk):
    functionality = Functionality.objects.get(pk=pk)
    functionality.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(), 16)


@api_view(['POST'])
def replicate_functionalities(request):
    """
    Replicates functionalities to another server based on SHA-1 hash and updates 'pertenece' to "1".

    Args:
        target_ip (str): The IP address of the server to replicate to.
        threshold (int): The minimum SHA-1 hash value for replication.
    """
    target_ip, threshold = request.data['target_ip'], request.data['threshold']
    id = getShaRepr(ip)
    functionalities = Functionality.objects.all()  # Get all functionalities

    for functionality in functionalities:
        sha_repr = getShaRepr(functionality.name)
        if sha_repr > threshold or sha_repr < id:
            # Prepare the data for the POST request
            data = FunctionalitySerializer(functionality).data  # Serialize the object
            #data['pertenece'] = '1'  # Set pertenece to "1" *before* sending

            # Construct the URL for the POST endpoint on the target server
            url = f"http://{target_ip}:8000/appFunctionality/functionality/create1"

            try:
                logger.exception("entro en replicate")
                # Send the POST request
                response = requests.post(url, json=data)  # Use json=data for sending JSON

                # Check the response status
                if response.status_code == 201:
                    print(f"Functionality '{functionality.name}' replicated successfully to {target_ip} and pertenece set to '1'")
                else:
                    print(f"Error replicating functionality '{functionality.name}' to {target_ip}: {response.status_code} - {response.text}")  # Imprime el texto de la respuesta
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to {target_ip}: {e}")
            
            if functionality.belongs == "3":
                functionality.delete()
            elif functionality.belongs == "2":
                functionality.belongs = "3"
                functionality.save()
            elif functionality.belongs == "1":
                functionality.belongs = "2"
                functionality.save()

    return Response(status=status.HTTP_200_OK)
    
@api_view(['POST'])
def delte_funcionality(request):
    threshold = request.data['threshold']
    functionalities = Functionality.objects.all()

    for funcionality in functionalities:
        id = getShaRepr(funcionality.name)
        if funcionality.belongs == "3":
            funcionality.delete()
        elif funcionality.belongs == "2" and id > threshold:
            funcionality.belongs = "3"
            funcionality.save() 

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def update_succ(request):
    local_functionalities = Functionality.objects.all()  # Obtener todos los objetos
    a = 0
    for func in local_functionalities:

        if func.belongs == "2":
            if a <= 18:
                a = 0
                while True:
                    try:
                        logger.error(f"intentando enviar func a : {node.pred2.ip}")
                        send_funcionality1(node.pred2.ip, name=func.name, belongs= "3")
                        break
                    except:
                        time.sleep(3)
                        a = a + 3
                        if a >= 18:
                            break
                a = 0
                while True:
                    try:
                        logger.error(f"intentando enviar func a : {node.pred.ip}")
                        send_funcionality1(node.pred.ip, name=func.name, belongs= "2")
                        break
                    except:
                        time.sleep(3)
                        a = a + 3
                        if a >= 18:
                            break

            func.belongs = "1"
            func.save()
        elif func.belongs == "3":
            func.belongs = "2"
            func.save()
    
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def update_pred(request):
    local_functionalities = Functionality.objects.all()  # Obtener todos los objetos
    for func in local_functionalities:
        logger.error("entro en update_pred")
        logger.error(f"se va a enviar la func: {func.name}")
        logger.error(f"func_belongs: {func.belongs}")
        if func.belongs == "1":
            while True:
                try:
                    send_funcionality1(node.pred2.ip, name=func.name, belongs= "3")
                    logger.error(f"se envio a : {node.pred2.ip}")
                    break
                except:
                    time.sleep(1)
            while True:
                try:
                    send_funcionality1(node.pred.ip, name=func.name, belongs= "2")
                    break
                except:
                    time.sleep(1)

            func.belongs = "1"
            func.save()
        elif func.belongs == "3":
            func.belongs = "2"
            func.save()
    
    return Response(status=status.HTTP_200_OK)

def send_funcionality1(node_ip, **kwargs):
    url = f'http://{node_ip}:8000/appFunctionality/functionality/create1/'
    response = requests.post(url, json=kwargs)
    return response

def get_func_from_server(ip):
    """Obtiene funcionalidades de un servidor específico."""
    try:
        url = f"http://{ip}:8000/appFunctionality/functionality_server/"  # Ajusta el puerto si es diferente
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener funcionalidades de {ip}: {e}")
        return []  # En caso de error, devuelve una lista vacía.
