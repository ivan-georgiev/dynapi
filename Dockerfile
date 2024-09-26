FROM python:3.9-slim

ENV DYNAPP_VERSION="0.0.0"
ENV DYNAPP_ERROR_FILE_PATH="/app/error_file"

WORKDIR /app

COPY dynapi/main.py .
COPY config.json .
COPY requirements.txt .
COPY version.txt .
COPY start.sh .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["/bin/bash", "/app/start.sh"]
