FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY docker/backend.sh /app
RUN chmod +x ./backend.sh

ENTRYPOINT ["sh", "-c", "sh /app/backend.sh && python backend/AgentsPlatform/manage.py runserver 0.0.0.0:8000"]
