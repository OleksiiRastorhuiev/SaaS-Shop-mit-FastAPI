# Dockerfile (angepasst)
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Systempakete für bcrypt
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Dateien kopieren
COPY . /app

# Python-Pakete installieren
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Port freigeben
EXPOSE 8000

# Startbefehl
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]