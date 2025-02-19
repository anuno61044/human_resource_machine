FROM node:20-alpine

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install

COPY ./frontend/. ./
COPY ./docker/frontend.sh ./

RUN chmod +x ./frontend.sh

ENTRYPOINT ["sh", "-c", "sh /app/frontend.sh && node proxy.js & npm run dev"]
