# Spécifications fonctionnelles

## Découpe vidéo

### Description
Division d'une vidéo source en plusieurs segments consécutifs de durée égale.

### Paramètres d'entrée
- Fichier vidéo (formats supportés : MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V)
- Durée de segment en secondes (minimum 1 seconde)
- Option de conversion 720p (booléen)

### Comportement
1. La durée totale est divisée par la durée de segment demandée
2. Le dernier segment peut être plus court si la durée totale n'est pas un multiple exact
3. Chaque segment est traité de manière indépendante
4. Les segments sont nommés selon le pattern : `split_{job_id}_segment_{index}.{ext}`

### Précision technique
- Framerate de référence : 30 fps
- Calcul des timestamps basé sur les numéros de frame
- Réencodage systématique pour garantir les limites exactes
- Keyframes forcées toutes les secondes
- Paramètres FFmpeg : libx264, CRF 23, preset medium, AAC 192kbps

### Sortie
- Liste de fichiers segments
- Chaque segment téléchargeable individuellement

## Fusion vidéo

### Description
Assemblage de plusieurs fichiers vidéo en un seul fichier continu.

### Paramètres d'entrée
- Liste ordonnée de fichiers vidéo (minimum 2)
- Option de conversion 720p (booléen)

### Ordre des vidéos
Les vidéos sont fusionnées dans l'ordre où elles ont été uploadées. Pour modifier l'ordre, supprimer les vidéos et les uploader à nouveau dans l'ordre souhaité.

### Comportement
1. Les vidéos sont concaténées dans l'ordre fourni
2. Tentative de fusion lossless (copie de stream)
3. Si la fusion lossless échoue (codecs différents), réencodage automatique
4. Le fichier fusionné est nommé : `merged_{job_id}.mp4`

### Précision technique
- Mode lossless : `-c copy` avec FFmpeg
- Mode réencodage : mêmes paramètres que la découpe
- Utilisation d'un fichier concat.txt pour la liste des sources
- Génération de PTS pour synchronisation

### Sortie
- Fichier unique contenant toutes les vidéos

## Extraction de frames

### Description
Capture de la première et dernière image d'une vidéo sous forme de fichiers JPEG.

### Paramètres d'entrée
- Fichier vidéo

### Comportement
1. Extraction de la frame à t=0 (première image)
2. Extraction de la frame à t=(durée - 0.1s) (dernière image)
3. Export en JPEG avec qualité maximale

### Paramètres FFmpeg
- `-vf "select=eq(n\,0)"` pour la première frame
- `-ss {duration-0.1}` pour la dernière frame
- `-q:v 2` pour la qualité JPEG
- `-vframes 1` pour extraire une seule image

### Sortie
- Deux fichiers JPEG : `frame_{id}_first.jpg` et `frame_{id}_last.jpg`

## Téléchargement de contenus sociaux

### Description
Téléchargement d'images et de vidéos depuis les principales plateformes de réseaux sociaux.

### Plateformes supportées

| Plateforme | Patterns d'URL |
|------------|----------------|
| TikTok | tiktok.com/, vm.tiktok.com/, vt.tiktok.com/ |
| Instagram | instagram.com/reel/, instagram.com/p/, instagram.com/stories/, instagram.com/tv/ |
| Facebook | facebook.com/watch, facebook.com/reel/, fb.watch/, facebook.com/video, facebook.com/photo |
| YouTube | youtube.com/shorts/, youtu.be/, youtube.com/watch |
| Twitter/X | twitter.com/, x.com/, t.co/ |
| Snapchat | snapchat.com/spotlight/, story.snapchat.com/ |
| Threads | threads.net/ |
| LinkedIn | linkedin.com/posts/, linkedin.com/video/ |
| Pinterest | pinterest.com/pin/, pin.it/, pinterest.fr/pin/ |
| Vimeo | vimeo.com/ |

### Paramètres d'entrée
- URL du contenu
- Option de conversion 720p (booléen, vidéos uniquement)

### Comportement
1. Détection automatique de la plateforme via l'URL
2. Configuration yt-dlp spécifique à chaque plateforme
3. Téléchargement du contenu
4. Extraction des métadonnées (titre, auteur, durée, vues, likes)
5. Renommage avec titre sanitisé
6. Conversion 720p optionnelle (vidéos uniquement)

### Options yt-dlp par plateforme
- Instagram : User-Agent mobile, extraction directe
- Facebook : User-Agent desktop Chrome
- Pinterest : User-Agent desktop Chrome
- Autres : configuration par défaut

### Sortie
- Fichier média (vidéo ou image)
- Métadonnées affichées dans l'interface

## Conversion 720p

### Description
Redimensionnement des vidéos pour que la plus petite dimension soit de 720 pixels.

### Logique de redimensionnement
- Vidéo portrait (hauteur > largeur) : largeur = 720px
- Vidéo paysage (largeur > hauteur) : hauteur = 720px
- Dimensions paires pour compatibilité codec

### Filtre FFmpeg
```
scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'
```

### Applications
- Découpe vidéo
- Fusion vidéo
- Téléchargements sociaux (vidéos uniquement)

## Statistiques

### Métriques suivies
- Nombre de vidéos découpées
- Nombre de segments créés
- Nombre de vidéos fusionnées
- Durée totale traitée (en secondes)
- Nombre de téléchargements sociaux

### Achievements
Le système attribue des badges selon l'utilisation :
- Premier découpage
- Première fusion
- 10 segments créés
- 5 vidéos traitées
- 10 minutes de vidéo traitées

## Nettoyage automatique

### Déclencheurs
- Rafraîchissement de la page (appel API /api/cleanup)
- Après téléchargement (fichiers temporaires sociaux et frames)

### Données supprimées
- Table videos (base de données)
- Table jobs (base de données)
- Table tiktok_downloads (base de données)
- Fichiers dans uploads/
- Fichiers dans outputs/

### Données conservées
- Table stats (compteurs globaux)

## Validation des fichiers

### Contrôles effectués
1. Extension dans la liste autorisée
2. Taille inférieure à 500 Mo
3. Présence d'un flux vidéo (FFprobe)

### Extensions autorisées
MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V

### Sanitisation des noms
Caractères supprimés : `< > : " / \ | ? * # % & { } $ ! ' \` @ ^ + = [ ]`

## Traitement asynchrone

### Jobs
Les opérations de découpe et fusion créent un job en base de données avec les états :
- `pending` : créé, en attente
- `processing` : en cours de traitement
- `completed` : terminé avec succès
- `error` : échec

### Polling
Le frontend interroge le statut des jobs toutes les 2 secondes via GET /api/jobs.

### Timeout
- Découpe : 600 secondes par segment
- Fusion : 1200 secondes total
