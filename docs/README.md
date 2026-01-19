# ClipFlow

Application web mobile-first de traitement de contenus multimédias. ClipFlow permet de découper des vidéos en segments, fusionner plusieurs vidéos, extraire des images (frames) et télécharger des contenus depuis les principales plateformes sociales.

## Fonctionnalités principales

**Découpe vidéo**
- Division d'une vidéo en segments de durée égale
- Précision à l'image près (30 fps) pour des transitions fluides
- Option de conversion en 720p

**Fusion vidéo**
- Assemblage de plusieurs vidéos en un seul fichier
- Fusion sans perte avec repli automatique sur réencodage si nécessaire
- Option de conversion en 720p

**Extraction de frames**
- Capture de la première et dernière image d'une vidéo
- Export en JPEG haute qualité
- Utile pour créer des miniatures ou vérifier le contenu

**Téléchargement depuis les réseaux sociaux**
- 10 plateformes supportées : TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest, Vimeo
- Support des images et vidéos
- Option de conversion en 720p pour les vidéos

## Démarrage rapide

1. Accéder à l'application via le navigateur
2. Choisir une fonctionnalité depuis l'écran d'accueil
3. Uploader un fichier ou coller une URL
4. Lancer le traitement
5. Télécharger le résultat

## Configuration requise

- Python 3.11+
- FFmpeg (installé via Nix)
- PostgreSQL (base de données Replit)
- yt-dlp (pour les téléchargements sociaux)

## Structure du projet

```
ClipFlow/
├── main.py              # Point d'entrée
├── app.py               # Factory Flask
├── config.py            # Configuration
├── database.py          # Modèles SQLAlchemy
├── models/              # Définitions de données
├── routes/              # Endpoints API
├── services/            # Logique métier
├── utils/               # Utilitaires (FFmpeg, fichiers)
├── security/            # Validation et sécurité
├── templates/           # Interface utilisateur
└── docs/                # Documentation
```

## Limites techniques

- Taille maximale des fichiers : 500 Mo
- Formats supportés : MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V
- Nettoyage automatique des fichiers à chaque rafraîchissement de page

## Licence

Projet privé - Tous droits réservés
