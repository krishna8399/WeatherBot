# Web UI container for serving the static chat and Flask app
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## All app files will be placed here
WORKDIR /app

## Static assets
COPY web/ /app/web/
## Flask server entry
COPY web_server.py /app/

## Minimal dependencies
RUN pip install --no-cache-dir flask flask-cors

## Flask listens on 8080
EXPOSE 8080

## Start the web server
CMD ["python", "web_server.py"]
