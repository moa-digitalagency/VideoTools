# ClipFlow - Stack Technique

Ce document liste les technologies, bibliothèques et outils utilisés pour le développement et le déploiement de ClipFlow.

## 1. Backend (Serveur)

*   **Langage :** Python 3.10+
*   **Framework Web :** Flask 3.0.0
    *   Micro-framework léger et flexible.
    *   Utilisation des *Blueprints* pour la modularité.
*   **Serveur WSGI :** Gunicorn (recommandé pour la production) ou Werkzeug (dev).
*   **Utilitaires :**
    *   `python-dotenv` : Gestion des variables d'environnement.
    *   `flask-cors` : Gestion des en-têtes Cross-Origin Resource Sharing.

## 2. Traitement Multimédia

*   **FFmpeg :**
    *   Outil en ligne de commande (CLI) invoqué via le module `subprocess` de Python.
    *   Responsable du découpage (segmentation), de la fusion (concatenation) et de l'extraction d'images.
    *   Codecs utilisés : `libx264` (vidéo), `aac` (audio).
*   **yt-dlp :**
    *   Fork performant de `youtube-dl`.
    *   Gère le téléchargement depuis les réseaux sociaux (TikTok, YouTube, Instagram, etc.).

## 3. Base de Données

*   **ORM :** SQLAlchemy 1.4+
    *   Abstraction de la base de données.
    *   Gestion des sessions et des transactions.
*   **SGBD :**
    *   **Développement :** SQLite (`sqlite:///test.db`). Simple fichier, zéro configuration.
    *   **Production :** PostgreSQL (`psycopg2-binary`). Robuste et performant pour la gestion concurrente.
*   **Migration :**
    *   Script personnalisé (`init_db.py`) utilisant l'introspection SQLAlchemy pour ajouter automatiquement les colonnes manquantes sans perte de données.

## 4. Frontend (Client)

*   **Structure :** HTML5 Sémantique.
*   **Style :** TailwindCSS (via CDN).
    *   Approche "Utility-first".
    *   Configuration personnalisée pour le mode sombre et les couleurs de la marque (`config` JS dans le `<head>`).
*   **Logique :** JavaScript Vanilla (ES6+).
    *   Aucun framework lourd (React/Vue/Angular) pour maximiser la performance et la simplicité.
    *   Utilisation de `fetch` pour les appels API asynchrones.
*   **Animations :**
    *   `@lottiefiles/lottie-player` et `@dotlottie/player-component`.
    *   Animations vectorielles légères pour l'UI (chargement, succès).

## 5. Environnement et Déploiement

*   **Gestionnaire de Paquets :** `pip` (Python).
*   **Conteneurisation :** Docker (recommandé).
    *   Isolation des dépendances système (FFmpeg est critique).
*   **Hébergement cible :** Tout VPS Linux (Ubuntu/Debian) ou PaaS supportant Python et FFmpeg (Heroku, Render, Railway, Replit).
