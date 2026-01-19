# Reference API

Base : toutes les routes commencent par /api.

## Videos

### GET /api/videos

Liste les videos uploadees (hors fichiers temporaires).

Reponse :
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "abc12345_ma_video.mp4",
    "originalName": "ma_video.mp4",
    "size": 15728640,
    "duration": 125.4,
    "codec": "h264",
    "resolution": "1920x1080",
    "bitrate": 8500000
  }
]
```

### POST /api/videos/upload

Upload un fichier video.

Corps : multipart/form-data avec un champ "video" contenant le fichier.

Reponse succes :
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "abc12345_ma_video.mp4",
  "originalName": "ma_video.mp4",
  "size": 15728640,
  "duration": 125.4,
  "codec": "h264",
  "resolution": "1920x1080",
  "bitrate": 8500000
}
```

Erreurs possibles :
- 400 "No video file provided" : pas de fichier dans la requete
- 400 "No file selected" : fichier vide
- 400 "Extension .xyz not allowed" : format non supporte
- 400 "File too large" : depasse 500 Mo
- 400 "Invalid video file" : FFprobe ne trouve pas de flux video

### DELETE /api/videos/{id}

Supprime une video uploadee.

Reponse : `{"success": true}` ou 404 si introuvable.

### GET /api/videos/{id}/download

Telecharge le fichier video original.

### POST /api/videos/split

Lance une decoupe video.

Corps :
```json
{
  "videoId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "segmentDuration": 30,
  "convert720": false
}
```

- videoId : identifiant de la video uploadee
- segmentDuration : duree de chaque segment en secondes (entier positif, minimum 1)
- convert720 : optionnel, redimensionne en 720p si true

Reponse :
```json
{
  "jobId": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "type": "split",
  "status": "pending"
}
```

Erreurs possibles :
- 400 `{"error": "videoId is required"}` : parametre videoId absent
- 400 `{"error": "segmentDuration must be a positive integer"}` : segmentDuration absent ou non entier
- 400 `{"error": "Video not found"}` : videoId ne correspond a aucune video
- 400 `{"error": "Segment duration must be at least 1 second"}` : duree trop courte
- 400 `{"error": "Segment duration exceeds video length"}` : duree depasse la video

Le traitement se fait en arriere-plan. Interrogez /api/jobs pour suivre l'avancement.

### POST /api/videos/merge

Lance une fusion video.

Corps :
```json
{
  "videoIds": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "c3d4e5f6-a7b8-9012-cdef-345678901234"
  ],
  "convert720": false
}
```

- videoIds : liste ordonnee des identifiants (minimum 2)
- convert720 : optionnel, redimensionne en 720p si true

Reponse : meme format que split.

Erreurs possibles :
- 400 `{"error": "videoIds must be a list"}` : parametre videoIds absent ou mal forme
- 400 `{"error": "Need at least 2 videos to merge"}` : moins de 2 videos
- 400 `{"error": "Video {id} not found"}` : une video n'existe pas

### POST /api/videos/extract-frames

Extrait la premiere et derniere image d'une video.

Corps : multipart/form-data avec un champ "video" contenant le fichier.

Reponse :
```json
{
  "firstFrame": "frame_abc12345_first.jpg",
  "lastFrame": "frame_abc12345_last.jpg",
  "duration": 125.4
}
```

### GET /api/download/{filename}

Telecharge un fichier de sortie (segment, fichier fusionne, telechargement social, frame).

Les fichiers sont automatiquement supprimes apres telechargement si leur nom contient l'un de ces prefixes : tiktok_, instagram_, facebook_, youtube_, twitter_, snapchat_, threads_, linkedin_, pinterest_, vimeo_, frame_. Les segments de decoupe et fichiers de fusion ne sont pas supprimes automatiquement.

## Jobs

### GET /api/jobs

Liste toutes les taches de traitement.

Reponse :
```json
[
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "type": "split",
    "status": "completed",
    "progress": 100,
    "outputs": ["split_xyz_segment_1.mp4", "split_xyz_segment_2.mp4"],
    "output": null,
    "error": null
  },
  {
    "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "type": "merge",
    "status": "processing",
    "progress": 45,
    "outputs": null,
    "output": null,
    "error": null
  }
]
```

Statuts :
- pending : en attente
- processing : en cours
- completed : termine
- error : echec (voir champ error)

Pour un job split, outputs contient la liste des noms de fichiers.
Pour un job merge, output contient le nom du fichier fusionne.

## Statistiques

### GET /api/stats

Retourne les compteurs d'utilisation.

Reponse :
```json
{
  "totalVideosSplit": 42,
  "totalSegmentsCreated": 156,
  "totalVideosMerged": 18,
  "totalTimeSaved": 7200.5,
  "totalTikTokDownloads": 89
}
```

totalTimeSaved est en secondes (duree cumulee des videos traitees).

## Telechargement social

### POST /api/tiktok/download

### POST /api/social/download

Ces deux endpoints font exactement la meme chose. Le second est un alias.

Corps :
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890",
  "convert720": false
}
```

Reponse :
```json
{
  "id": "abc12345",
  "filename": "Titre_de_la_video.mp4",
  "title": "Titre de la video",
  "uploader": "username",
  "duration": 45,
  "view_count": 150000,
  "like_count": 5000,
  "platform": "TikTok",
  "media_type": "video",
  "converted_720p": false
}
```

media_type peut valoir "video" ou "image" selon le contenu.

Plateformes supportees :
- TikTok : tiktok.com, vm.tiktok.com, vt.tiktok.com
- Instagram : instagram.com/reel/, instagram.com/p/, instagram.com/stories/, instagram.com/tv/
- Facebook : facebook.com/watch, facebook.com/reel/, fb.watch/, facebook.com/video, facebook.com/photo
- YouTube : youtube.com/shorts/, youtu.be/, youtube.com/watch
- Twitter/X : twitter.com/, x.com/, t.co/
- Snapchat : snapchat.com/spotlight/, story.snapchat.com/
- Threads : threads.net/
- LinkedIn : linkedin.com/posts/, linkedin.com/video/
- Pinterest : pinterest.com/pin/, pin.it/
- Vimeo : vimeo.com/

Erreur si URL non reconnue :
```json
{
  "error": "URL not supported. Supported: TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest, Vimeo"
}
```

## Nettoyage

### POST /api/cleanup

Supprime toutes les videos, jobs et telechargements. Vide les dossiers uploads/ et outputs/. Conserve les statistiques.

Reponse :
```json
{
  "success": true,
  "message": "Cleanup completed"
}
```

En cas d'erreur :
```json
{
  "success": false,
  "error": "description de l'erreur"
}
```

## Codes HTTP

- 200 : succes
- 400 : requete invalide (parametres manquants, validation echouee)
- 404 : ressource introuvable
- 500 : erreur serveur
