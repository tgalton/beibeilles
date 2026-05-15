# Image Python officielle
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copie des dépendances
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Port exposé
EXPOSE 8000

# Commande de lancement
# On met 0.0.0.0 pour que localhost ne soit pas visible que dans le contener
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]