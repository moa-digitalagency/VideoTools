# Architecture technique de ClipFlow

## Stack

Frontend : HTML + Tailwind CSS (CDN) + JavaScript vanilla. Pas de framework, pas de build, tout tourne dans le navigateur. La page est unique, la navigation se fait en affichant/masquant des divs.

Backend : Flask avec Blueprints pour separer les routes par domaine. SQLAlchemy pour la base PostgreSQL (optionnel : si DATABASE_URL n'est pas defini, certaines fonctionnalites sont limitees). Les operations longues (split, merge) tournent dans des threads separes.

Traitement video : FFmpeg appele via subprocess. Pas de binding Python, juste des appels en ligne de commande avec capture de la sortie.

## Structure des composants

### Routes (routes/)

Cinq fichiers, cinq blueprints :

- **videos.py** : tout ce qui touche aux fichiers video. Upload via multipart/form-data, suppression, telechargement, split, merge, extraction de frames.

- **jobs.py** : un seul endpoint GET /api/jobs qui retourne la liste des taches. Le frontend l'interroge toutes les 2 secondes pour suivre l'avancement.

- **stats.py** : GET /api/stats retourne les compteurs (videos decoupees, segments crees, fusions, etc).

- **tiktok.py** : deux endpoints identiques, /api/tiktok/download et /api/social/download, pour la compatibilite avec le code existant. Les deux font la meme chose.

- **cleanup.py** : POST /api/cleanup vide tout sauf les stats.

### Services (services/)

- **video_service.py** : gere l'upload (validation, enregistrement, extraction des metadonnees), le split (creation du job, lancement du thread), le merge (idem), l'extraction de frames. Chaque methode retourne soit un resultat soit un tuple (None, erreur).

- **social_service.py** : contient la classe SocialMediaService (alias SocialVideoService). Detecte la plateforme via des patterns d'URL, configure yt-dlp avec des options specifiques selon la plateforme, telecharge, renomme le fichier avec le titre nettoye, et optionnellement convertit en 720p. Note : le fichier tiktok_service.py existe aussi mais n'est plus utilise (code legacy).

### Base de donnees (database.py)

Quatre tables SQLAlchemy :

**VideoModel** : les videos uploadees. Champs : id (UUID), filename, original_name, size, duration, path, codec, resolution, bitrate, is_temporary, created_at.

**JobModel** : les taches de traitement. Champs : id, type (split ou merge), status (pending, processing, completed, error), progress, video_id (pour split), video_ids (JSON pour merge), segment_duration, outputs (JSON des noms de fichiers), output (nom du fichier fusionne), error, convert_720, created_at.

**TikTokDownloadModel** : l'historique des telechargements. Meme si le nom dit TikTok, ca stocke tous les telechargements sociaux. Champs : id, url, filename, title, uploader, duration, view_count, like_count, path, is_downloaded, created_at.

**StatsModel** : une seule ligne avec les compteurs. total_videos_split, total_segments_created, total_videos_merged, total_time_saved, total_tiktok_downloads.

### Utilitaires

**ffmpeg.py** contient FFmpegHelper avec :
- get_video_info : appelle ffprobe en JSON
- get_duration : extrait la duree depuis les metadonnees
- get_codec_info : retourne codec, resolution, bitrate
- split_video_lossless : decoupe avec reencodage systematique a 30 fps
- split_video_720p : pareil avec redimensionnement
- merge_videos_lossless : fusion via fichier concat, fallback sur reencodage
- merge_videos_720p : fusion avec reencodage et redimensionnement

**file_handler.py** gere les operations fichier : generation de noms uniques, sauvegarde, suppression, creation de repertoires temporaires.

### Validation (security/validator.py)

FileValidator verifie :
- que l'extension est dans la liste autorisee (ALLOWED_EXTENSIONS)
- que la taille ne depasse pas MAX_FILE_SIZE (500 Mo)
- que FFprobe trouve un flux video dans le fichier
- et sanitise les noms de fichiers en remplacant les caracteres dangereux (.. / \ < > : " | ? *) par des underscores

## Flux de traitement

### Decoupe video

1. L'utilisateur uploade via le formulaire
2. Le frontend envoie le fichier en POST multipart sur /api/videos/upload
3. Le backend valide, sauvegarde, extrait les metadonnees avec FFprobe
4. Le frontend affiche les infos de la video
5. L'utilisateur choisit une duree de segment et clique sur Decouper
6. POST /api/videos/split avec videoId et segmentDuration
7. Le backend cree un JobModel et lance un thread
8. Le thread appelle FFmpegHelper.split_video_lossless ou split_video_720p
9. Le frontend poll /api/jobs toutes les 2 secondes
10. Quand le job passe en completed, le frontend affiche les liens de telechargement

### Fusion video

1. L'utilisateur uploade plusieurs fichiers un par un
2. Chaque fichier passe par /api/videos/upload
3. Le frontend maintient une liste ordonnee (mergeQueue)
4. Clic sur Fusionner : POST /api/videos/merge avec la liste des IDs
5. Le backend cree un job et lance un thread
6. Le thread cree un fichier concat.txt et appelle ffmpeg -f concat
7. Polling et telechargement comme pour le split

### Telechargement social

1. L'utilisateur colle une URL
2. POST /api/social/download avec l'URL
3. La classe SocialMediaService (exportee aussi sous le nom SocialVideoService) detecte la plateforme via des patterns d'URL
4. Configuration yt-dlp specifique a la plateforme
5. Telechargement dans outputs/ avec un nom temporaire
6. Renommage avec le titre nettoye
7. Optionnellement, conversion 720p
8. Retour des metadonnees au frontend
9. L'utilisateur clique pour telecharger le fichier

### Extraction de frames

1. Upload via /api/videos/extract-frames
2. Sauvegarde temporaire
3. FFmpeg extrait la premiere frame (select=eq(n,0))
4. FFmpeg extrait la derniere frame (seek a duration - 0.1s)
5. Suppression du fichier video temporaire
6. Retour des noms des deux images JPEG

## Precision de decoupe

La decoupe utilise un reencodage systematique a 30 fps. Pas de stream copy, qui ne garantit pas les limites exactes des segments. Les parametres :

```
-r 30                        Framerate de sortie
-g 30                        Un keyframe par seconde
-force_key_frames expr:...   Keyframes aux positions exactes
-fflags +genpts              Generation des timestamps
-avoid_negative_ts make_zero Evite les timestamps negatifs
```

Resultat : si vous decoupez une video en segments puis les refusionnez, vous obtenez exactement l'original. La derniere frame du segment N est immediatement suivie par la premiere frame du segment N+1.

## Conversion 720p

La formule de redimensionnement adapte le ratio :

```
scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'
```

Si la video est en portrait (hauteur > largeur), la largeur passe a 720px. Si elle est en paysage, la hauteur passe a 720px. Les dimensions sont arrondies au multiple de 2 pour la compatibilite codec.

## Nettoyage

Au chargement de la page, le JavaScript appelle POST /api/cleanup. Ca vide :
- la table videos
- la table jobs
- la table tiktok_downloads
- tous les fichiers dans uploads/
- tous les fichiers dans outputs/

Les stats sont conservees.

Note : si DATABASE_URL n'est pas defini, les tables n'existent pas et seuls les fichiers sont supprimes.

La route /api/download supprime automatiquement les fichiers apres telechargement si leur nom commence par l'un de ces prefixes : tiktok_, instagram_, facebook_, youtube_, twitter_, snapchat_, threads_, linkedin_, pinterest_, vimeo_, frame_. Les segments de decoupe et fichiers de fusion restent sur le serveur jusqu'au prochain nettoyage.

## Gestion des erreurs

Les operations FFmpeg ont des timeouts :
- FFprobe : 30 secondes
- Split par segment : 600 secondes (10 minutes)
- Merge total : 1200 secondes (20 minutes)

Si une operation echoue, le job passe en status error avec le message dans le champ error.
