# Dockerfile pour le serveur FastAPI
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Repertoire de travail
WORKDIR /app

# Installation des dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dependances
COPY requirements.txt .

# Installation des dependances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Port expose
EXPOSE 8000

# Commande de demarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
