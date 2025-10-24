# Web UI container
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY web/ /app/web/
COPY web_server.py /app/

RUN pip install --no-cache-dir flask flask-cors

EXPOSE 8080

CMD ["python", "web_server.py"]
