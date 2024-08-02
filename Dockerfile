# Utiliser une image de base officielle de Python
FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Installer ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY app/requirements.txt ./
COPY app/app.py .


# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
# COPY . .
COPY app/.env .

# Commande par défaut pour exécuter le script Python
CMD ["python", "app.py"]
