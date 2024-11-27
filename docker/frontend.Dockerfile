FROM node:20-alpine
WORKDIR /app
COPY docker/frontend.sh .
CMD app/frontend.sh && ping 10.0.11.2