# ClipFlow - Architecture Technique

Ce document détaille l'architecture logicielle et les flux de données de l'application ClipFlow.

## 1. Vue d'Ensemble

ClipFlow suit une architecture MVC (Modèle-Vue-Contrôleur) adaptée pour une Single Page Application (SPA) simulée.

```mermaid
graph TD
    User[Utilisateur] -->|HTTP/HTTPS| Frontend[Frontend (Vanilla JS + Tailwind)]
    Frontend -->|AJAX / Fetch API| API[API Backend (Flask)]
    API -->|Validation & Routing| Controllers[Blueprints (routes/)]
    Controllers -->|Logique Métier| Services[Services (services/)]
    Services -->|FFmpeg / yt-dlp| Processing[Traitement Vidéo]
    Services -->|CRUD| DB[(Base de Données SQLAlchemy)]
    Processing -->|Fichiers Temporaires| Storage[Système de Fichiers (uploads/outputs)]
```

## 2. Structure du Code

L'application est organisée de manière modulaire :

*   **`app.py`** : Point d'entrée principal. Initialise l'application Flask, configure les extensions (CORS), et enregistre les Blueprints.
*   **`config.py`** : Configuration centralisée (chemins des dossiers, limites d'upload, constantes FFmpeg).
*   **`routes/`** : Contrôleurs API divisés par domaine fonctionnel.
    *   `videos.py` : Gestion des uploads et suppression.
    *   `jobs.py` : Suivi de l'état des traitements asynchrones.
    *   `tiktok.py` : Téléchargement social.
    *   `stats.py` : Statistiques d'utilisation.
    *   `cleanup.py` : Maintenance système.
*   **`services/`** : Contient toute la logique métier complexe.
    *   `video_service.py` : Wrappers FFmpeg pour le découpage, la fusion et l'extraction de frames.
    *   `social_service.py` : Intégration avec `yt-dlp` pour le téléchargement.
*   **`models/`** (dans `database.py`) : Définitions des tables SQLAlchemy.
*   **`templates/`** : Frontend.
    *   `index.html` : Structure HTML unique de l'application.
    *   `js/app.js` : Logique client (routeur, gestion des événements, appels API).
    *   `css/style.css` : Styles personnalisés (complémentaires à Tailwind).

## 3. Flux de Données Principal : Traitement Asynchrone

Pour éviter de bloquer le serveur lors de lourds traitements vidéo (découpage/fusion), ClipFlow utilise un modèle basé sur les Jobs.

1.  **Initiation :**
    *   Le client envoie une requête (ex: `POST /api/videos/split`).
    *   Le serveur crée une entrée dans la table `jobs` avec le statut `pending`.
    *   Le serveur retourne immédiatement l'ID du job (`202 Accepted` implicite).

2.  **Traitement (Actuellement Synchrone dans le Thread - *Note Technique*) :**
    *   *Observation:* Dans la version actuelle, les services exécutent le traitement avant de retourner la réponse HTTP, ce qui peut causer des timeouts sur de très gros fichiers.
    *   *Architecture Cible:* L'implémentation actuelle utilise des threads ou processus via `subprocess` mais attend souvent la fin. Le frontend poll tout de même pour la compatibilité future avec des workers type Celery/Redis.

3.  **Polling (Frontend) :**
    *   Le client interroge `GET /api/jobs` toutes les 2 secondes.
    *   Il met à jour la barre de progression selon le champ `progress` du job.

4.  **Finalisation :**
    *   Une fois le job `completed`, le serveur fournit les liens de téléchargement dans le champ `outputs` (JSON).

## 4. Gestion des Fichiers

*   **Uploads Temporaires (`uploads/`) :**
    *   Stockage des fichiers bruts envoyés par l'utilisateur.
    *   Nettoyés au redémarrage du serveur ou via l'API de cleanup.
*   **Sorties (`outputs/`) :**
    *   Stockage des résultats de traitement (segments, vidéos fusionnées).
    *   Servis via la route `/api/download/<filename>`.
    *   Les fichiers sociaux sont supprimés *immédiatement* après le téléchargement réussi via un middleware `after_this_request`.

## 5. Sécurité

*   **Validation des Fichiers :** Vérification stricte des extensions autorisées (liste blanche dans `config.py`).
*   **Nettoyage des Chemins :** Utilisation de `werkzeug.utils.secure_filename` pour éviter les attaques par traversée de répertoires.
*   **CORS :** Configuré pour autoriser les requêtes cross-origin si nécessaire (via `flask-cors`).
