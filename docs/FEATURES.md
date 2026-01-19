# Specifications fonctionnelles

## Decoupe video

### Entrees

- Fichier video (MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V)
- Duree de segment en secondes (minimum 1)
- Option 720p (oui/non)

### Fonctionnement

Le nombre de segments est calcule par division entiere de la duree totale par la duree demandee. Si le reste est superieur a une frame (1/30e de seconde), un segment supplementaire est cree avec ce reste.

Exemple :
- Video de 95 secondes, segments de 30 secondes
- 95 / 30 = 3 segments de 30s + 1 segment de 5s
- Total : 4 segments

Chaque segment est traite independamment avec les parametres FFmpeg suivants :
- Codec video : libx264
- Codec audio : AAC 192 kbps
- Preset : medium
- CRF : 23
- Framerate : 30 fps
- Keyframes : toutes les secondes

Les noms de fichiers suivent le pattern : `split_{job_id}_segment_{numero}.{extension}`

### Precision

Les coupures se font sur des limites exactes de frames. Pas de copie de stream (qui ne garantit pas la precision) mais un reencodage systematique. Le dernier frame du segment N est immediatement suivi par le premier frame du segment N+1.

### Sortie

Liste de fichiers segments, chacun telechargeable individuellement.

## Fusion video

### Entrees

- Liste d'au moins 2 fichiers video
- Option 720p (oui/non)

### Fonctionnement

Les videos sont concatenees dans l'ordre fourni. L'application tente d'abord une fusion sans reencodage (copie de stream) via un fichier concat.txt. Si les codecs ou parametres different entre les fichiers, la fusion echoue et un reencodage est lance automatiquement.

Le fichier de sortie s'appelle `merged_{job_id}.mp4`.

### Considerations

La fusion fonctionne mieux quand les videos ont :
- Le meme codec
- La meme resolution
- Le meme framerate
- Les memes parametres audio

Si ce n'est pas le cas, le reencodage harmonise tout mais prend plus de temps.

### Sortie

Un fichier video unique.

## Extraction de frames

### Entrees

- Fichier video

### Fonctionnement

1. Upload du fichier dans un emplacement temporaire
2. Validation (extension, taille, presence d'un flux video)
3. Extraction de la premiere frame via FFmpeg
4. Extraction de la derniere frame via FFmpeg (seek a duree - 0.1s)
5. Suppression du fichier video temporaire
6. Retour des deux images

### Parametres FFmpeg

Premiere frame :
```
-vf "select=eq(n\,0)" -vframes 1 -q:v 2
```

Derniere frame :
```
-ss {duree-0.1} -vframes 1 -q:v 2
```

### Sortie

Deux fichiers JPEG : `frame_{id}_first.jpg` et `frame_{id}_last.jpg`

## Telechargement social

### Entrees

- URL du contenu
- Option 720p (oui/non, videos uniquement)

### Plateformes

| Plateforme | Patterns reconnus |
|------------|-------------------|
| TikTok | tiktok.com/, vm.tiktok.com/, vt.tiktok.com/ |
| Instagram | instagram.com/reel/, instagram.com/p/, instagram.com/stories/, instagram.com/tv/, instagram.com/s/ |
| Facebook | facebook.com/watch, facebook.com/reel/, fb.watch/, facebook.com/video, facebook.com/photo, facebook.com/share, facebook.com/story, facebook.com/groups/, fb.gg/ |
| YouTube | youtube.com/shorts/, youtu.be/, youtube.com/watch |
| Twitter/X | twitter.com/, x.com/, t.co/ |
| Snapchat | snapchat.com/spotlight/, snapchat.com/add/, story.snapchat.com/ |
| Threads | threads.net/ |
| LinkedIn | linkedin.com/posts/, linkedin.com/feed/, linkedin.com/video/ |
| Pinterest | pinterest.com/pin/, pin.it/, variantes locales (.fr, .co.uk, .de, .es) |
| Vimeo | vimeo.com/ |

### Fonctionnement

1. Detection de la plateforme via les patterns d'URL
2. Configuration yt-dlp specifique (User-Agent, options d'extraction)
3. Telechargement dans outputs/ avec un nom temporaire
4. Extraction des metadonnees (titre, auteur, duree, vues, likes)
5. Nettoyage du titre (suppression des caracteres speciaux)
6. Renommage du fichier avec le titre nettoye
7. Si option 720p : conversion via FFmpeg
8. Enregistrement en base de donnees

### Sortie

Fichier media (video ou image) renomme avec le titre du contenu.

## Conversion 720p

### Logique

La plus petite dimension passe a 720 pixels. L'autre dimension suit proportionnellement.

- Video portrait (1080x1920) : devient 720x1280
- Video paysage (1920x1080) : devient 1280x720
- Video carree (1080x1080) : devient 720x720

Les dimensions sont arrondies au multiple de 2 pour la compatibilite avec le codec H.264.

### Filtre FFmpeg

```
scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'
```

### Applications

- Decoupe avec option 720p
- Fusion avec option 720p
- Telechargement social avec option 720p (videos uniquement)

## Statistiques

### Metriques suivies

- total_videos_split : nombre de videos decoupees
- total_segments_created : nombre total de segments produits
- total_videos_merged : nombre de fusions effectuees
- total_time_saved : duree cumulee des videos traitees (secondes)
- total_tiktok_downloads : nombre de telechargements sociaux

### Persistance

Les statistiques survivent au nettoyage automatique. Elles sont conservees tant que la base de donnees existe.

## Nettoyage

### Declencheurs

1. Au chargement de la page : le JavaScript appelle POST /api/cleanup
2. Apres telechargement : les fichiers temporaires (social, frames) sont supprimes

### Donnees supprimees

- Table videos
- Table jobs
- Table tiktok_downloads
- Fichiers dans uploads/
- Fichiers dans outputs/

### Donnees conservees

- Table stats

## Validation des fichiers

### Extensions autorisees

MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V

### Taille maximale

500 Mo (524 288 000 octets)

### Verification du contenu

FFprobe analyse le fichier et verifie la presence d'au moins un flux de type video.

### Nettoyage des noms

Caracteres supprimes : `< > : " / \ | ? * # % & { } $ ! ' ` @ ^ + = [ ]`
Les espaces deviennent des underscores. Les caracteres speciaux sont retires. Le nom est tronque a 80 caracteres.

## Traitement asynchrone

### Principe

Les operations de decoupe et fusion prennent du temps. Pour ne pas bloquer le serveur, elles tournent dans des threads separes.

### Etats d'un job

1. pending : cree, en attente
2. processing : en cours d'execution
3. completed : termine avec succes
4. error : echec

### Suivi

Le frontend interroge GET /api/jobs toutes les 2 secondes tant qu'un job est en pending ou processing.

### Timeouts

- Validation FFprobe : 30 secondes
- Decoupe par segment : 600 secondes
- Fusion totale : 1200 secondes
