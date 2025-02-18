import hashlib
import socket
import threading
import time
from venv import logger
import requests
import struct

BROADCAST_PORT = 50000 # Puedes cambiarlo
SERVER_IP = socket.gethostbyname(socket.gethostname())
BROADCAST_ADDRESS = '<broadcast>' 


def send_funcionality(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appFunctionality/functionality/replicate/"
    response = requests.post(url, json=kwargs)
    return response

def send_agent(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appAgent/agent/replicate/"
    response = requests.post(url, json=kwargs)
    return response

def del_funcionality(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appFunctionality/functionality/delfuncionality/"
    response = requests.post(url, json=kwargs)
    return response

def del_agent(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appAgent/agent/delagent/"
    response = requests.post(url, json=kwargs)
    return response

def update_funcionality(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appFunctionality/functionality/update_succ/"
    response = requests.post(url, json=kwargs)
    return response

def update_agent(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appAgent/agent/update_succ/"
    response = requests.post(url, json=kwargs)
    return response

def update_funcionality_pred(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appFunctionality/functionality/update_pred/"
    response = requests.post(url, json=kwargs)
    return response

def update_agent_pred(node_ip, **kwargs):
    url = f"http://{node_ip}:8000/appAgent/agent/update_pred/"
    response = requests.post(url, json=kwargs)
    return response

def send_data(node_ip, **kwargs):
    #try:
    url = f"http://{node_ip}:8000/appAgent/agent/chord/"
    response = requests.post(url, json=kwargs, timeout= 5)
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
        self.pred2 = self.ref
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
        logger.error(f"discovery_ip: {self.new_ip}")
        if self.new_ip is not None:
            threading.Thread(target=self.join, args=(ChordNodeReference(self.new_ip, self.port),), daemon=True).start()
            
            
            
            
            
            
            
        # ***********************************************************************************************************
        #                                          COSAS DE MULTICAST
        # ***********************************************************************************************************
        
        # Configurar IP y puerto multicast
        MULTICAST_GROUP = "224.0.0.1"
        PORT = 10000

        # Crear socket UDP
        sock_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock_multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_multicast.bind(("", PORT))

        # Unirse al grupo multicast
        mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"Servidor escuchando en {MULTICAST_GROUP}:{PORT}")

        # Configuración del servidor
        CLIENT_PORT = 8000  # Puerto para clientes
        SERVER_PORT = 9000  # Puerto para comunicación entre servidores

        # Lista de direcciones IP de los servidores en la red (actualízalas con tus IPs)
        SERVERS = [("10.0.11.2", SERVER_PORT), ("10.0.11.3", SERVER_PORT), ("10.0.11.4", SERVER_PORT)]

        # Crear socket UDP para clientes
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.bind(("0.0.0.0", CLIENT_PORT))

        # Crear socket UDP para comunicación entre servidores
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind(("0.0.0.0", SERVER_PORT))

        # Obtener la dirección IP del servidor
        server_ip = socket.gethostbyname(socket.gethostname())

        # Variable de control para saber si el servidor principal sigue enviando heartbeats
        last_heartbeat_time = time.time()
        processing_request = False
        principal_server_did = False
        
        # Iniciar hilo para enviar heartbeats
        multicast_thread = threading.Thread(target=self.multicast, daemon=True, args=(sock_multicast,))
        multicast_thread.start()
        
        # # Iniciar hilo para enviar heartbeats
        # heartbeat_thread = threading.Thread(target=send_heartbeats, daemon=True)
        # heartbeat_thread.start()

        # # Iniciar hilo para escuchar mensajes de otros servidores
        # listener_thread = threading.Thread(target=listen_for_messages, daemon=True)
        # listener_thread.start()
        
        # ************************************************************************************************************
        # 
        # ************************************************************************************************************
        
        
        
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
        self.pred2 = self.ref
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
                            send_funcionality(self.ip, target_ip= self.succ.ip, threshold = self.succ.id)
                            send_agent(self.ip, target_ip= self.succ.ip, threshold = self.succ.id)
                            del_funcionality(self.pred.ip, threshold= self.id)
                            del_agent(self.pred.ip, threshold= self.id)
                            
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
                    update_funcionality(self.ip)
                    update_agent(self.ip)
                except:
                    try:
                        logger.error("entro en el try mas abajo")
                        x = self.succ3
                        self.succ = x
                        self.succ2 = self.succ.succ
                        self.succ3.notify1(self.ref)
                        update_funcionality(self.ip)
                        update_agent(self.ip)
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

            logger.error(f"successor : {self.succ}  succ2 {self.succ2} succ3 {self.succ3} predecessor {self.pred} pred2 {self.pred2}")
            time.sleep(5)

    def notify(self, node: 'ChordNodeReference'):
        logger.error(f"en notify, yo: {self.ip} el entrante: {node.ip}")
        a = False
        if node.id == self.id:
            return
        print(f"notify with node {node} self {self.ref} pred {self.pred}")
        
        if (self.pred.id == self.id) or self._inrange(node.id, self.pred.id, self.id):
            self.pred = node
            a = True
        while True:
            try:
                self.pred.pred
                self.pred2 = self.pred.pred
                break
            except:
                time.sleep(1)
        if self.pred.ip != self.ip and a == True:
            update_funcionality_pred(self.ip)
            update_agent_pred(self.ip)

    def notify1(self, node: 'ChordNodeReference'):
        self.pred = node
        a = False
        if self.pred.ip != node.ip:
            a = True
        while True:
            try:
                node.pred
                self.pred2 = node.pred
                break
            except:
                time.sleep(1)
        if self.pred.ip != self.ip and a == True:
            update_funcionality_pred(self.ip)
            update_agent_pred(self.ip)
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
            





# ***********************************************************************************************************************
# 
# ***********************************************************************************************************************

    def multicast(self, sock_multicast):
        while True:
            logger.error("\nmulticast trabajando\n")
            # Recibir solicitud
            data, addr = sock_multicast.recvfrom(1024)
            message = data.decode()
            logger.error(f"\n ************************************* \nSolicitud recibida de {addr}: {message} \n ************************************* \n")

            # Extraer puerto del cliente del mensaje
            try:
                client_port = 8001
                client_address = message
            except ValueError:
                print("Error: No se pudo extraer el puerto del mensaje.")
                continue

            # Responder directamente al cliente en su IP y puerto
            response = f"Confirmacion desde {self.ip}"
            sock_multicast.sendto(response.encode(), (client_address, client_port))
            print(f"Confirmación enviada a {client_address}:{client_port}")

    # def send_heartbeats():
    # """Envía señales de vida a los demás servidores mientras se procesa una solicitud."""
    # global processing_request
    # while True:
    #     if processing_request:
    #         for server in SERVERS:
    #             if server[0] != server_ip:  # No enviarse a sí mismo
    #                 server_sock.sendto("HEARTBEAT".encode(), server)
    #         time.sleep(2)
    #     else:
    #         time.sleep(1)  # Esperar antes de verificar nuevamente

    # def listen_for_messages():
    #     """Escucha mensajes de otros servidores y maneja heartbeats y confirmaciones."""
    #     global last_heartbeat_time, principal_server_did
    #     while True:
    #         data, addr = server_sock.recvfrom(1024)
    #         message = data.decode()
    #         if message == "HEARTBEAT":
    #             print(f"Heartbeat recibido de {addr}")
    #             last_heartbeat_time = time.time()
    #         elif message.startswith("SOLICITUD:"):
    #             parts = message.split(":")
    #             if len(parts) == 4:
    #                 solicitud = parts[1]
    #                 client_ip = parts[2]
    #                 client_port = int(parts[3])
    #                 print(f"Solicitud recibida de otro servidor {addr}: {solicitud} para el cliente ({client_ip}, {client_port})")
    #                 thread = threading.Thread(target=process_request_backup, args=(solicitud, (client_ip, client_port)))
    #                 thread.start()
    #         elif message == "CONFIRMACION_PROCESO":
    #             print(f"Confirmación de proceso recibida de {addr}")
    #             principal_server_did = True

    # def handle_client_request(data, addr):
    #     """Maneja la solicitud del cliente, distribuyéndola y detectando fallos en el servidor principal."""
    #     global processing_request, last_heartbeat_time
        
    #     # Extraer datos del cliente
    #     client_ip, client_port = addr

    #     # Enviar la solicitud a los otros servidores junto con la dirección del cliente
    #     for server in SERVERS:
    #         if server[0] != server_ip:
    #             solicitud_mensaje = f"SOLICITUD:{data.decode()}:{client_ip}:{client_port}"
    #             server_sock.sendto(solicitud_mensaje.encode(), server)
        
    #     # Iniciar procesamiento inmediato
    #     processing_request = True
    #     print(f"El servidor {server_ip} ha empezado a procesar la solicitud del cliente {addr}")
    #     time.sleep(20)  # Simular procesamiento
    #     print(f"El servidor {server_ip} ha terminado de procesar la solicitud del cliente {addr}")
        
    #     response = f"Hola cliente, soy el servidor {server_ip} y terminé de procesar tu solicitud"
    #     client_sock.sendto(response.encode(), addr)
        
    #     # Notificar a los otros servidores que se terminó el procesamiento
    #     for server in SERVERS:
    #         if server[0] != server_ip:
    #             server_sock.sendto("CONFIRMACION_PROCESO".encode(), server)
        
    #     processing_request = False

    # def process_request_backup(data, client_addr):
    #     """Procesa la solicitud en servidores de respaldo en caso de falla del principal y devuelve un resultado."""
    #     global principal_server_did
        
    #     print(f"Servidor en respaldo procesando solicitud: {data} para el cliente {client_addr}")
    #     time.sleep(20)  # Simular procesamiento en respaldo
    #     print(f"Servidor en respaldo finalizó el procesamiento: {data}")
        
    #     if principal_server_did:
    #         principal_server_did = False
    #         return
        
    #     # Monitorear heartbeats del servidor principal
    #     while True:
    #         time.sleep(3)
    #         if time.time() - last_heartbeat_time > 6:
    #             print(f"No se recibieron heartbeats recientes ni confirmación. Enviando respuesta al cliente {client_addr}.")
    #             response = f"Hola cliente, soy el servidor {server_ip} y terminé de procesar la solicitud por fallo"
    #             client_sock.sendto(response.encode(), client_addr)
    #             break

        