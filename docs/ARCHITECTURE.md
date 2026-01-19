# Architecture technique

## Vue d'ensemble

ClipFlow suit une architecture client-serveur classique avec un frontend HTML/CSS/JavaScript pur et un backend Python Flask. Le traitement vidéo est délégué à FFmpeg via subprocess.

## Stack technique

### Frontend
- HTML5 sémantique
- Tailwind CSS (CDN) avec thème personnalisé
- JavaScript vanilla (ES6+)
- Lottie pour les animations
- Mode sombre/clair avec persistance localStorage

### Backend
- Flask 2.x comme framework web
- Flask-CORS pour les requêtes cross-origin
- SQLAlchemy comme ORM
- PostgreSQL comme base de données
- yt-dlp pour les téléchargements sociaux

### Traitement vidéo
- FFmpeg pour toutes les opérations vidéo
- FFprobe pour l'analyse des métadonnées
- libx264 pour l'encodage vidéo
- AAC pour l'encodage audio

## Architecture des composants

### Couche de présentation (templates/)
```
templates/
├── index.html       # Page unique SPA
├── css/style.css    # Styles personnalisés
└── js/app.js        # Logique frontend
```

L'interface est une Single Page Application (SPA) avec navigation par onglets. Chaque page est un div caché/affiché selon la navigation.

### Couche API (routes/)
```
routes/
├── __init__.py      # Export des blueprints
├── videos.py        # CRUD vidéos, split, merge, frames
├── jobs.py          # Statut des traitements
├── stats.py         # Statistiques utilisateur
├── tiktok.py        # Téléchargements sociaux
└── cleanup.py       # Nettoyage des données
```

Chaque fichier expose un Blueprint Flask regroupant les endpoints par domaine fonctionnel.

### Couche services (services/)
```
services/
├── __init__.py
├── video_service.py   # Logique de traitement vidéo
└── social_service.py  # Logique de téléchargement social
```

Les services encapsulent la logique métier et interagissent avec la base de données et les utilitaires.

### Couche utilitaires (utils/)
```
utils/
├── __init__.py
├── ffmpeg.py          # Wrapper FFmpeg
└── file_handler.py    # Gestion des fichiers
```

### Couche sécurité (security/)
```
security/
├── __init__.py
└── validator.py       # Validation des fichiers
```

## Modèle de données

### VideoModel
Stocke les métadonnées des vidéos uploadées.
- id (UUID)
- filename, original_name
- size, duration
- path (chemin physique)
- codec, resolution, bitrate
- is_temporary (flag de nettoyage)

### JobModel
Représente une tâche de traitement asynchrone.
- id (UUID)
- type (split/merge)
- status (pending/processing/completed/error)
- progress (0-100)
- outputs/output (résultats)
- convert_720 (flag de conversion)

### TikTokDownloadModel
Historique des téléchargements sociaux.
- id (UUID)
- url, filename
- title, uploader
- duration, view_count, like_count
- path, is_downloaded

### StatsModel
Compteurs globaux pour les statistiques.
- total_videos_split
- total_segments_created
- total_videos_merged
- total_time_saved
- total_tiktok_downloads

## Flux de traitement

### Découpe vidéo
1. Upload du fichier via POST multipart
2. Validation (extension, taille, codec)
3. Enregistrement en base de données
4. Création d'un Job asynchrone
5. Traitement FFmpeg en thread séparé
6. Mise à jour du statut via polling
7. Téléchargement des segments

### Fusion vidéo
1. Sélection des vidéos à fusionner
2. Validation de l'existence des fichiers
3. Création d'un Job asynchrone
4. Génération du fichier concat.txt
5. Traitement FFmpeg (lossless puis fallback reencode)
6. Téléchargement du fichier fusionné

### Téléchargement social
1. Soumission de l'URL
2. Détection de la plateforme
3. Configuration yt-dlp spécifique
4. Téléchargement et extraction des métadonnées
5. Renommage avec titre sanitisé
6. Conversion 720p optionnelle
7. Enregistrement en base

## Précision de découpe

La découpe vidéo utilise un algorithme frame-accurate à 30 fps :
- Calcul des timestamps basé sur les numéros de frame
- Réencodage systématique pour garantir les limites exactes
- Force des keyframes toutes les secondes
- Génération de PTS pour éviter les problèmes de synchronisation

Cette approche garantit que le dernier frame du segment N est immédiatement suivi par le premier frame du segment N+1, permettant une fusion sans saut ni duplication.

## Gestion des fichiers

### Répertoires
- `uploads/` : fichiers uploadés par l'utilisateur
- `outputs/` : segments, fichiers fusionnés, téléchargements

### Nettoyage
- Automatique au rafraîchissement de la page (cleanup_all)
- Après téléchargement pour les fichiers temporaires (social, frames)
- Préfixes utilisés pour identifier les types : tiktok_, instagram_, frame_, etc.

## Configuration FFmpeg

| Paramètre | Valeur |
|-----------|--------|
| Codec vidéo | libx264 |
| Codec audio | AAC |
| Preset | medium |
| CRF | 23 |
| FPS | 30 |
| Audio bitrate | 192 kbps |

### Conversion 720p
La conversion adapte la résolution selon l'orientation :
- Portrait : largeur = 720px, hauteur proportionnelle
- Paysage : hauteur = 720px, largeur proportionnelle

## Sécurité

### Validation des uploads
- Extension dans la liste blanche
- Taille maximale 500 Mo
- Analyse FFprobe pour vérifier la présence d'un flux vidéo
- Sanitisation des noms de fichiers

### Protection des chemins
- Pas de traversée de répertoire (../)
- Caractères dangereux supprimés des noms

## Performance

### Traitement asynchrone
Les opérations longues (split, merge) sont exécutées dans des threads daemon pour ne pas bloquer les requêtes HTTP.

### Polling des jobs
Le frontend interroge le statut des jobs toutes les 2 secondes jusqu'à complétion.

### Timeouts
- Validation FFprobe : 30s
- Split par segment : 600s
- Merge total : 1200s
