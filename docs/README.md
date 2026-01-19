# ClipFlow

ClipFlow est une application web de traitement de contenus multimedias. Elle tourne sur mobile comme sur ordinateur. Quatre fonctions principales : decouper des videos en morceaux, fusionner plusieurs videos, telecharger depuis les reseaux sociaux, extraire des images fixes.

## Ce que fait l'application

**Decoupe video** - Vous avez une video de 10 minutes et vous voulez la poster sur TikTok qui accepte 60 secondes max ? Uploadez-la, indiquez 60 secondes, et recuperez vos 10 segments. La decoupe respecte les limites exactes des images (frames) pour eviter les sauts ou les doublons quand vous refusionnez.

**Fusion video** - Prenez 5 clips et combinez-les en un seul fichier. L'ordre de fusion correspond a l'ordre d'upload.

**Telechargement social** - Collez une URL TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest ou Vimeo. L'application recupere la video ou l'image et vous la propose au telechargement.

**Extraction de frames** - Uploadez une video, recuperez sa premiere et sa derniere image en JPEG. Pratique pour creer des miniatures.

## Demarrer

L'application tourne sur Flask. Au chargement de la page, elle appelle automatiquement /api/cleanup qui supprime les fichiers temporaires dans uploads/ et outputs/. Si PostgreSQL est configure (DATABASE_URL), les tables videos, jobs et tiktok_downloads sont aussi videes. Les stats sont conservees.

```bash
python main.py
```

Le serveur ecoute sur le port 5000.

## Contraintes techniques

- Fichiers de 500 Mo maximum
- Formats acceptes : MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V
- Tous les fichiers sont supprimes au rafraichissement de la page
- PostgreSQL optionnel mais recommande (variable DATABASE_URL) pour la persistance des metadonnees

## Organisation du code

```
main.py              Point d'entree
app.py               Creation de l'application Flask
config.py            Chemins, limites, parametres FFmpeg
database.py          Modeles SQLAlchemy et fonctions de base

routes/              Endpoints HTTP
  videos.py          Upload, split, merge, frames, download
  jobs.py            Liste des taches en cours
  stats.py           Compteurs d'utilisation
  tiktok.py          Telechargement depuis les reseaux sociaux
  cleanup.py         Remise a zero

services/            Logique metier
  video_service.py   Traitement video (split, merge, frames)
  social_service.py  Telechargement yt-dlp

utils/               Outils
  ffmpeg.py          Appels FFmpeg/FFprobe
  file_handler.py    Gestion des fichiers sur disque

security/            Validation
  validator.py       Verification des extensions, tailles, contenus

templates/           Interface utilisateur
  index.html         Page HTML unique
  css/style.css      Styles
  js/app.js          JavaScript client
```

## Dependances

Python : flask, flask-cors, sqlalchemy, werkzeug, yt-dlp
Systeme : ffmpeg (installe via Nix)
