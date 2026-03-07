# On part d'une base Python
FROM python:3.9-slim

# On installe Octave et les outils système nécessaires
RUN apt-get update && apt-get install -y \
    octave \
    liboctave-dev \
    && apt-get clean

# On définit le dossier de travail
WORKDIR /app

# On copie les fichiers de ton projet
COPY . .

# On installe tes bibliothèques Python (Flask, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# On lance l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]