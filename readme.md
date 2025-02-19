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

## Construir las imagenes a partir de archivos .tar
```
docker load -i client_hrm.tar
docker load -i server_hrm.tar
```

## Ejecutar los clientes y servidores en sus redes
```
docker run -itd --name client1 --cap-add NET_ADMIN -e CONTAINER_IP=10.0.10.2 --ip 10.0.10.2 -p 8080:8080 -p 8000:8000 --network clients -v "$(pwd)/frontend/src:/app/src" -v "$(pwd)/frontend/proxy.js:/app/proxy.js" client_hrm

docker run -itd --name server1 --cap-add NET_ADMIN --network servers --ip 10.0.11.2 -p 8012:8000 -v "$(pwd)/backend:/app/backend" -e DATABASE_NAME=db1.sqlite3 server_hrm

docker run -itd --name server2 --cap-add NET_ADMIN --network servers --ip 10.0.11.3 -p 8013:8000 -v "$(pwd)/backend:/app/backend" -e DATABASE_NAME=db2.sqlite3 server_hrm

docker run -itd --name server3 --cap-add NET_ADMIN --network servers --ip 10.0.11.4 -p 8014:8000 -v "$(pwd)/backend:/app/backend" -e DATABASE_NAME=db3.sqlite3 server_hrm
```
