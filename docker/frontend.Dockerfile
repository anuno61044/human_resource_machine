# Usa una imagen oficial de Node.js como base
FROM node:20-alpine

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos package.json y package-lock.json
COPY ./frontend/package*.json ./

# Instala las dependencias
RUN npm install

# Copia el resto de los archivos del proyecto
COPY ./frontend .

COPY docker/frontend.sh .
CMD app/frontend.sh
