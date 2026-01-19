# Historique des modifications

## Janvier 2026

### Nouvelles fonctionnalites

**Extraction de frames** - Nouvelle section permettant d'extraire la premiere et la derniere image d'une video. Les fichiers sont exportes en JPEG. L'endpoint POST /api/videos/extract-frames gere l'upload, l'extraction et la suppression automatique du fichier source.

**Support Vimeo** - Dixieme plateforme ajoutee au telechargement social. Les URLs vimeo.com/ sont desormais reconnues et traitees.

**Decoupe frame-accurate** - Refonte complete de l'algorithme de decoupe. Abandon du stream copy au profit d'un reencodage systematique a 30 fps. Les segments produits peuvent etre refusionnes sans perte de frame ni duplication.

### Modifications techniques

- Parametres FFmpeg pour la decoupe : ajout de -force_key_frames, -fflags +genpts, -r 30, -g 30, -avoid_negative_ts make_zero
- Suppression des frames et fichiers sociaux apres telechargement (nettoyage automatique dans /api/download/)
- Prefixes de fichiers pour le nettoyage : tiktok_, instagram_, facebook_, youtube_, twitter_, snapchat_, threads_, linkedin_, pinterest_, vimeo_, frame_

### Corrections

- Message d'erreur pour URL non supportee mis a jour pour lister les 10 plateformes
- Validation des fichiers avant extraction de frames
- Gestion des caracteres speciaux dans les titres de telechargement

### Documentation

- Ajout des messages d'erreur exacts pour /api/videos/split et /api/videos/merge dans API.md
- Clarification du comportement optionnel de PostgreSQL (DATABASE_URL) dans README et ARCHITECTURE
- Description precise du nettoyage automatique par prefixes dans /api/download
- Documentation de l'alias SocialVideoService pour SocialMediaService
- Correction des sections dupliquees dans ARCHITECTURE.md

### Renommage

- Application renommee de VideoSplit a ClipFlow
- Titre de la page, texte d'accueil et documentation mis a jour

---

## Decembre 2025

### Version initiale

**Decoupe video** - Upload d'une video, choix de la duree des segments, production de N fichiers. Option de conversion 720p.

**Fusion video** - Upload de plusieurs videos, assemblage dans l'ordre d'upload. Option de conversion 720p.

**Telechargement social** - Support de 9 plateformes : TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest. Detection automatique de la plateforme via l'URL. Option de conversion 720p.

**Interface utilisateur** - Design mobile-first avec theme bleu nuit. Mode sombre et mode clair. Animations Lottie. Barre de navigation en bas de l'ecran.

**Infrastructure** - Backend Flask avec PostgreSQL. Traitement asynchrone des operations longues. Nettoyage automatique au chargement de la page.

### Stack technique

- Frontend : HTML, Tailwind CSS (CDN), JavaScript vanilla
- Backend : Python Flask, SQLAlchemy
- Base de donnees : PostgreSQL
- Traitement video : FFmpeg
- Telechargement social : yt-dlp
