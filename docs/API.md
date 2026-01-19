# Documentation API

## Base URL

Toutes les routes API sont préfixées par `/api`.

## Vidéos

### Lister les vidéos

```
GET /api/videos
```

Retourne la liste des vidéos uploadées (non temporaires).

**Réponse**
```json
[
  {
    "id": "uuid",
    "filename": "nom_fichier.mp4",
    "originalName": "nom_original.mp4",
    "size": 12345678,
    "duration": 120.5,
    "codec": "h264",
    "resolution": "1920x1080",
    "bitrate": 5000000
  }
]
```

### Uploader une vidéo

```
POST /api/videos/upload
Content-Type: multipart/form-data
```

**Paramètres**
- `video` (file) : fichier vidéo à uploader

**Réponse**
```json
{
  "id": "uuid",
  "filename": "nom_fichier.mp4",
  "originalName": "nom_original.mp4",
  "size": 12345678,
  "duration": 120.5,
  "codec": "h264",
  "resolution": "1920x1080",
  "bitrate": 5000000
}
```

**Erreurs**
- 400 : fichier manquant, extension non autorisée, fichier trop volumineux, fichier invalide

### Supprimer une vidéo

```
DELETE /api/videos/{video_id}
```

**Réponse**
```json
{
  "success": true
}
```

### Télécharger une vidéo

```
GET /api/videos/{video_id}/download
```

Retourne le fichier vidéo en téléchargement.

### Découper une vidéo

```
POST /api/videos/split
Content-Type: application/json
```

**Corps**
```json
{
  "videoId": "uuid",
  "segmentDuration": 30,
  "convert720": false
}
```

**Paramètres**
- `videoId` (string) : identifiant de la vidéo
- `segmentDuration` (integer) : durée en secondes de chaque segment
- `convert720` (boolean, optionnel) : convertir en 720p

**Réponse**
```json
{
  "jobId": "uuid",
  "id": "uuid",
  "type": "split",
  "status": "pending"
}
```

### Fusionner des vidéos

```
POST /api/videos/merge
Content-Type: application/json
```

**Corps**
```json
{
  "videoIds": ["uuid1", "uuid2", "uuid3"],
  "convert720": false
}
```

**Paramètres**
- `videoIds` (array) : liste ordonnée des identifiants de vidéos (minimum 2)
- `convert720` (boolean, optionnel) : convertir en 720p

**Réponse**
```json
{
  "jobId": "uuid",
  "id": "uuid",
  "type": "merge",
  "status": "pending"
}
```

### Extraire les frames

```
POST /api/videos/extract-frames
Content-Type: multipart/form-data
```

**Paramètres**
- `video` (file) : fichier vidéo

**Réponse**
```json
{
  "firstFrame": "frame_abc123_first.jpg",
  "lastFrame": "frame_abc123_last.jpg",
  "duration": 120.5
}
```

### Télécharger un fichier de sortie

```
GET /api/download/{filename}
```

Télécharge un fichier depuis le répertoire outputs (segments, fichiers fusionnés, téléchargements sociaux, frames).

## Jobs

### Lister les jobs

```
GET /api/jobs
```

Retourne la liste des jobs de traitement.

**Réponse**
```json
[
  {
    "id": "uuid",
    "type": "split",
    "status": "completed",
    "progress": 100,
    "outputs": ["segment_1.mp4", "segment_2.mp4"],
    "output": null,
    "error": null
  }
]
```

**Statuts possibles**
- `pending` : en attente de traitement
- `processing` : en cours de traitement
- `completed` : terminé avec succès
- `error` : échec (voir champ error)

## Statistiques

### Obtenir les statistiques

```
GET /api/stats
```

**Réponse**
```json
{
  "totalVideosSplit": 15,
  "totalSegmentsCreated": 45,
  "totalVideosMerged": 8,
  "totalTimeSaved": 3600.5,
  "totalTikTokDownloads": 23
}
```

## Téléchargements sociaux

### Télécharger depuis une plateforme sociale

```
POST /api/tiktok/download
Content-Type: application/json
```

ou

```
POST /api/social/download
Content-Type: application/json
```

**Corps**
```json
{
  "url": "https://www.tiktok.com/@user/video/123456",
  "convert720": false
}
```

**Paramètres**
- `url` (string) : URL du contenu à télécharger
- `convert720` (boolean, optionnel) : convertir les vidéos en 720p

**Réponse**
```json
{
  "id": "abc123",
  "filename": "titre_video.mp4",
  "title": "Titre de la vidéo",
  "uploader": "Nom du créateur",
  "duration": 60,
  "view_count": 150000,
  "like_count": 5000,
  "platform": "TikTok",
  "media_type": "video",
  "converted_720p": false
}
```

**Plateformes supportées**
- TikTok : tiktok.com, vm.tiktok.com, vt.tiktok.com
- Instagram : instagram.com/reel/, instagram.com/p/, instagram.com/stories/
- Facebook : facebook.com/watch, facebook.com/reel/, fb.watch/
- YouTube : youtube.com/shorts/, youtu.be/, youtube.com/watch
- Twitter/X : twitter.com/, x.com/, t.co/
- Snapchat : snapchat.com/spotlight/, story.snapchat.com/
- Threads : threads.net/
- LinkedIn : linkedin.com/posts/, linkedin.com/video/
- Pinterest : pinterest.com/pin/, pin.it/
- Vimeo : vimeo.com/

## Nettoyage

### Nettoyer les données

```
POST /api/cleanup
```

Supprime toutes les vidéos, jobs et téléchargements de la base de données ainsi que les fichiers associés. Les statistiques sont conservées.

**Réponse succès**
```json
{
  "success": true,
  "message": "Cleanup completed"
}
```

**Réponse erreur**
```json
{
  "success": false,
  "error": "Description de l'erreur"
}
```

## Codes d'erreur

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 400 | Requête invalide (paramètres manquants, validation échouée) |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur interne |

## Format des erreurs

```json
{
  "error": "Description du problème"
}
```
