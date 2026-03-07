# Utiliser Python comme base
FROM python:3.9-slim

# Installer les compilateurs pour C, C++ et Octave
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    octave \
    liboctave-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Port utilisé par Render
EXPOSE 10000

# Lancer l'application avec Gunicorn (le plus stable)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]