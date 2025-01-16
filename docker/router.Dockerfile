FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .
COPY ./router .

RUN echo "net.ipv4.ip_forward=1" | tee -a /etc/sysctl.conf
RUN sysctl -p
RUN pip install -r requirements.txt

#CMD /bin/sh

CMD ["python", "router.py"]