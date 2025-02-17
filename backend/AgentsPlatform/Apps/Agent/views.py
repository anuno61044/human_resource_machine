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

BROADCAST_PORT = 50000 # Puedes cambiarlo
SERVER_IP = socket.gethostbyname(socket.gethostname())
BROADCAST_ADDRESS = '<broadcast>' 

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
            agent.delete()
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    elif request.method == 'DELETE':
        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
  
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
        print("node_pred: ", node.pred)
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


#######################################################################################
def send_data(node_ip, **kwargs):
    #try:
    url = f"http://{node_ip}:8000/appAgent/agent/chord/"
    response = requests.post(url, json=kwargs)
    return response
    #except:
    #    logger.error(f"Error en Remote Call")
        #return None

# Operation codes
FIND_SUCCESSOR = 1
FIND_PREDECESSOR = 2
GET_SUCCESSOR = 3
GET_PREDECESSOR = 4
NOTIFY = 5
CLOSEST_PRECEDING_FINGER = 7
IS_ALIVE = 8
NOTIFY1 = 9
STORE_KEY = 10

def getShaRepr(data: str):
    return int(hashlib.sha1(data.encode()).hexdigest(),16)

class ChordNodeReference:
    def __init__(self, ip: str, port: int = 4001):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port

    def find_successor(self, id: int) -> 'ChordNodeReference':
        response = send_data(self.ip, op=FIND_SUCCESSOR,data=str(id)).json().split(',')
        #logger.error(f"find_succesor: {response.data}")
        
        return ChordNodeReference(response[1], self.port)

    def find_predecessor(self, id: int) -> 'ChordNodeReference':
        response = send_data(self.ip,op=FIND_PREDECESSOR,data=str(id)).json().split(',')
        return ChordNodeReference(response[1], self.port)

    @property
    def succ(self) -> 'ChordNodeReference':
        response = send_data(self.ip, op= GET_SUCCESSOR, data = None).json().split(',')
        return ChordNodeReference(response[1], self.port)

    @property
    def pred(self) -> 'ChordNodeReference':
        response = send_data(self.ip, op=GET_PREDECESSOR, data=None).json().split(',')
        return ChordNodeReference(response[1], self.port)

    def notify(self, node: 'ChordNodeReference'):
        send_data(self.ip, op=NOTIFY, data=f'{node.id},{node.ip}')

    def notify1(self, node: 'ChordNodeReference'):
        send_data(self.ip, op=NOTIFY1, data=f'{node.id},{node.ip}')

    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        response = send_data(self.ip, op=CLOSEST_PRECEDING_FINGER, data=str(id)).json().split(',')
        return ChordNodeReference(response[1], self.port)

    def alive(self):
        response = send_data(self.ip, op=IS_ALIVE).json().split(',')
        return response
    
    def store_key(self, key: str, value: str):
        send_data(self.ip, op=STORE_KEY, data=f'{key},{value}')

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return self.__str__()

class ChordNode:
    def __init__(self, ip: str, peerId = None, port: int = 8000, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.pred = self.ref  # Initial predecessor is itself
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.lock = threading.Lock()
        self.succ2 = self.ref
        self.succ3 = self.ref
        self.data = {}

        threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
        threading.Thread(target=self.fix_fingers, daemon=True).start()  # Start fix fingers thread

        #if peerId is not None:
        #    threading.Thread(target=self.join, args=(ChordNodeReference(peerId, self.port),), daemon=True).start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar la dirección
        sock.bind(('', BROADCAST_PORT))

        discovery_thread = threading.Thread(target=self.handle_discovery, args=(sock,))
        discovery_thread.daemon = True  # El hilo se cierra cuando el programa principal termina
        discovery_thread.start()
        self.new_ip = self.discover_server()
        print("discovery_ip: ", self.new_ip)
        if self.new_ip is not None:
            threading.Thread(target=self.join, args=(ChordNodeReference(self.new_ip, self.port),), daemon=True).start()
    @property
    def succ(self):
        return self.finger[0]
    
    @succ.setter
    def succ(self, node: 'ChordNodeReference'):
        with self.lock:
            self.finger[0] = node

    def _inbetween(self, k: int, start: int, end: int) -> bool:
        """Check if k is in the interval [start, end)."""
        #print(end < start, start <= k, k < end)

        k = k % 2 ** self.m
        start = start % 2 ** self.m
        end = end % 2 ** self.m
        if start < end:
            return start <= k < end
        return start <= k or k < end
    
    def _inrange(self, k: int, start: int, end: int) -> bool:
        """Check if k is in the interval (start, end)."""
        _start = (start + 1) % 2 ** self.m
        return self._inbetween(k, _start, end)
    
    def _inbetweencomp(self, k: int, start: int, end: int) -> bool:
        """Check if k is in the interval (start, end]."""
        _end = (end - 1) % 2 ** self.m 
        return self._inbetween(k, start, _end)

    def find_succ(self, id: int) -> 'ChordNodeReference':
        node = self.find_pred(id)  # Find predecessor of id
        return node.succ  # Return successor of that node

    def find_pred(self, id: int) -> 'ChordNodeReference':
        node = self
        try:
            if node.id == self.succ.id:
                return node
        except:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        x, a = node.succ.ip, node.succ.id
        #print('x: ', x)
        #print(f"in bteween {id}, {node.id} {node.succ.id} {self._inbetweencomp(id, node.id, node.succ.id)}")
        while not self._inbetweencomp(id, node.id, node.succ.id):
            node = node.closest_preceding_finger(id)
            if node.id == self.id:
                break
            
        #print(f"closest finger: {node.id} {node.ip}")
        return node

    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        node = None
        for i in range(self.m - 1, -1, -1):
            #if self.finger[i].id != self.id and self._inrange(self.finger[i].id, self.id, id):
            try:
                if node == self.finger[i]:
                    continue
                self.finger[i].succ
                if self._inrange(self.finger[i].id, self.id, id):
                    return self.finger[i] if self.finger[i].id != self.id else self
            except:
                node = self.finger[i]
                continue    
        return self

    def join(self, node: 'ChordNodeReference'):
        time.sleep(5)
        """Join a Chord network using 'node' as an entry point."""
        self.pred = self.ref
        logger.error("before find succc")
        self.succ = node.find_successor(self.id)
        self.succ2 = self.succ.succ
        self.succ3 = self.succ2.succ
        #print(self.succ)
        logger.error(f"self.succ: {self.succ} self.succ2: {self.succ2}")

    def stabilize(self):
        time.sleep(5)

        """Regular check for correct Chord structure."""
        while True:
            logger.error(f'self.succ: {self.succ}')
            try:
                if self.succ:
                    print(self.succ)
                    x = self.succ.pred
                    if x.id != self.id:
                        if self.succ.id == self.id or self._inrange(x.id, self.id, self.succ.id):
                            self.succ = x
                    self.succ2 = self.succ.succ
                    self.succ.notify(self.ref)
            except Exception as e:
                try:
                    logger.error("entro en el try")
                    x = self.succ2
                    self.succ = x
                    self.succ2 = self.succ.succ
                    #self.succ2 = x.succ
                    self.succ.notify1(ChordNodeReference(self.ip, self.port))
                except:
                    try:
                        x = self.succ3
                        self.succ = x
                        self.succ2 = self.succ.succ
                        self.succ3.notify1(self.ref)
                    except:
                        print(f"Error in stabilize: {e}")
            try:
                #self.succ2 = self.succ.succ
                self.succ3 = self.succ.succ.succ
            except:
                try:
                    self.succ3 = self.succ3.succ
                except:
                    time.sleep(1)
                    continue

            logger.error(f"successor : {self.succ}  succ2 {self.succ2} succ3 {self.succ3} predecessor {self.pred}")
            time.sleep(5)

    def notify(self, node: 'ChordNodeReference'):
        logger.error(f"en notify, yo: {self.ip} el entrante: {node.ip}")
        if node.id == self.id:
            return
        print(f"notify with node {node} self {self.ref} pred {self.pred}")
        if (self.pred.id == self.id) or self._inrange(node.id, self.pred.id, self.id):
            self.pred = node
    
    def notify1(self, node: 'ChordNodeReference'):
        self.pred = node
        logger.error(f"new notify por node {node} pred {self.pred}")
    
    def fix_fingers(self):
        time.sleep(5)
        while True:
            for i in range(self.m - 1, -1, -1):
                self.next = i
                with self.lock:
                    self.finger[self.next] = self.find_succ((self.id + 2 ** self.next) % (2 ** self.m))
            time.sleep(10)
    
    def store_key(self, key, value):
        key_hash = getShaRepr(key)
        print("key: ", key, "hash: ", key_hash)
        if self._inrange(key_hash, self.id, self.succ.id):
            self.data[key] = value
        else:
            node = self.closest_preceding_finger(key_hash)
            print("node_succ_key: ", node.id)
            node.store_key(key, value)

    def handle_discovery(self, sock):
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"Recibido mensaje de broadcast: {message} de {addr}")

                # Si el mensaje es una solicitud de descubrimiento, responde
                if message == "DISCOVER_REQUEST":
                    response = f"SERVER_IP:{SERVER_IP}"
                    sock.sendto(response.encode('utf-8'), addr)
            except Exception as e:
                print(f"Error en el hilo de descubrimiento: {e}")
                break
    def discover_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #Permite broadcast

        sock.settimeout(5)  # Tiempo máximo para esperar una respuesta

        message = "DISCOVER_REQUEST"
        try:
            sock.sendto(message.encode('utf-8'), (BROADCAST_ADDRESS, BROADCAST_PORT))
            print("Enviando solicitud de descubrimiento por broadcast...")
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode('utf-8')
                    print(f"Recibido respuesta de {addr}: {response}")

                    if response.startswith("SERVER_IP:"):
                        server_ip = response.split(":")[1]
                        if server_ip == self.ip:
                            continue
                        print("server_ip: ", server_ip, "self.ip: ", self.ip)
                        print(f"Servidor encontrado en la IP: {server_ip}")
                        return server_ip # Devuelve la IP del primer servidor encontrado

                except socket.timeout:
                    print("No se encontraron servidores en el tiempo especificado.")
                    return None  # No se encontró ningún servidor
        except Exception as e:
            print(f"Error durante el descubrimiento: {e}")
            return None
        finally:
            sock.close()

ip = socket.gethostbyname(socket.gethostname())
#print(sys.argv)
#if ip != '10.0.11.2':
#    other_ip = '10.0.11.2'
#    node = ChordNode(ip, other_ip)
#else:
#node = ChordNode(ip)