# Image Python officielle
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# =========================================================
# IMPORTANT :
# permet :
#
# from app.database import ...
#
# dans tous les scripts Python
# =========================================================
ENV PYTHONPATH=/app

# Copie des dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Port exposé
EXPOSE 8000

# Commande de lancement
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]