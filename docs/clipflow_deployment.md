# ClipFlow - Guide de Déploiement

Ce guide détaille les étapes nécessaires pour installer, configurer et exécuter ClipFlow sur un environnement local ou en production.

## 1. Prérequis Système

Pour fonctionner, ClipFlow nécessite les outils suivants installés sur votre machine ou serveur :

*   **Python 3.10+** (Langage de programmation principal).
*   **pip** (Gestionnaire de paquets Python).
*   **FFmpeg** (Moteur de traitement vidéo - **Critique**).
    *   *Ubuntu/Debian :* `sudo apt install ffmpeg`
    *   *macOS :* `brew install ffmpeg`
    *   *Windows :* Télécharger les binaires et ajouter au PATH.
*   **Git** (Pour cloner le dépôt).

## 2. Installation Locale (Standard)

### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/votre-utilisateur/clipflow.git
cd clipflow
```

### Étape 2 : Créer un environnement virtuel
Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances.
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou
venv\Scripts\activate     # Sur Windows
```

### Étape 3 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 : Configuration (Optionnel)
L'application utilise des valeurs par défaut (`sqlite:///test.db`), mais vous pouvez créer un fichier `.env` à la racine pour surcharger la configuration :

```ini
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/clipflow
PORT=8000
SECRET_KEY=votre_clé_secrète_pour_flask
```

### Étape 5 : Lancer l'application
```bash
python main.py
```
Le serveur démarrera sur `http://0.0.0.0:5000` (ou le port défini).

## 3. Déploiement avec Docker (Recommandé)

Docker simplifie grandement l'installation car il inclut FFmpeg et Python dans un conteneur isolé.

### Créer le `Dockerfile`
Créez un fichier nommé `Dockerfile` à la racine :

```dockerfile
FROM python:3.10-slim

# Installation des dépendances système (FFmpeg est obligatoire)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des fichiers requirements et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p uploads outputs

# Exposition du port
EXPOSE 5000

# Commande de démarrage avec Gunicorn (Production)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Construire et Lancer
```bash
docker build -t clipflow .
docker run -p 5000:5000 clipflow
```

## 4. Déploiement en Production (Serveur VPS)

Pour un déploiement robuste sur un serveur Linux (Ubuntu 22.04 LTS) :

1.  **Installer Nginx :** Utilisé comme reverse proxy pour gérer le SSL et servir les fichiers statiques si nécessaire.
2.  **Installer Gunicorn :** Serveur WSGI de production (déjà dans le Dockerfile ci-dessus).
3.  **Configurer Systemd :** Pour lancer l'application au démarrage.

Exemple de service systemd (`/etc/systemd/system/clipflow.service`) :
```ini
[Unit]
Description=Gunicorn instance to serve ClipFlow
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/clipflow
Environment="PATH=/var/www/clipflow/venv/bin"
ExecStart=/var/www/clipflow/venv/bin/gunicorn --workers 3 --bind unix:clipflow.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

## 5. Résolution des Problèmes Courants

*   **Erreur `ffmpeg not found` :**
    *   Assurez-vous que FFmpeg est installé et accessible via la commande `ffmpeg -version` dans votre terminal.
*   **Erreur `psycopg2` :**
    *   Si vous utilisez PostgreSQL, vous aurez besoin des paquets de développement (`libpq-dev` sur Linux).
*   **Upload échoue (413 Request Entity Too Large) :**
    *   Vérifiez la configuration de Nginx (`client_max_body_size 500M;`).
    *   Vérifiez la variable `MAX_FILE_SIZE` dans `config.py`.
