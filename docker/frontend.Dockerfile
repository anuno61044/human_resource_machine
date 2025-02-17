FROM node:20-alpine

WORKDIR /app

COPY ./frontend/package*.json ./
RUN npm install

COPY ./frontend/. ./
COPY ./docker/frontend.sh ./

RUN chmod +x ./frontend.sh

FROM python:3.9-slim
RUN pip install requests
ENTRYPOINT ["sh", "-c", "sh /app/frontend.sh && python proxy.py & exec python -m http.server 80 & npm run dev"]
