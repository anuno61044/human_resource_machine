# Flujo para probar los clientes y servidores en redes distintas en docker

## Crear las redes en docker
```
docker network create --subnet=10.0.10.0/24 clients
docker network create --subnet=10.0.11.0/24 servers
```

## Router

El trabajo con el router es la infraestructura que mandó el profe

## Construir imagenes cliente y servidor

```
docker build -t client_hrm -f frontend.Dockerfile ./docker
docker build -t server_hrm -f backend.Dockerfile ./docker
```

## Ejecutar los clientes y servidores en sus redes
```
docker run -itd --name client1 --cap-add NET_ADMIN -p 8080:8080 --network clients -v "$(pwd)/frontend/src:/app/src" client_hrm
docker run -itd --rm --name server1 --cap-add NET_ADMIN --network servers -v "$(pwd)/server.py:/app/server.py" server
```
