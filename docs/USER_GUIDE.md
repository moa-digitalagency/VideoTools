# Guide utilisateur

## Présentation

ClipFlow est un outil de traitement vidéo accessible depuis n'importe quel navigateur. L'interface est conçue pour les appareils mobiles mais fonctionne également sur ordinateur.

## Navigation

L'application comporte 5 sections accessibles depuis la barre de navigation en bas de l'écran :

1. **Accueil** : présentation des fonctionnalités et instructions
2. **Découper** : division d'une vidéo en segments
3. **Fusionner** : assemblage de plusieurs vidéos
4. **Download** : téléchargement depuis les réseaux sociaux
5. **Frames** : extraction des première et dernière images

Les statistiques d'utilisation restent accessibles via l'API mais ne sont plus affichées dans la navigation principale.

## Découper une vidéo

Cette fonction permet de diviser une longue vidéo en plusieurs segments de durée égale.

### Étapes

1. Cliquer sur l'onglet **Découper** ou le bloc correspondant sur l'accueil
2. Cliquer sur la zone d'upload ou glisser-déposer un fichier vidéo
3. Attendre l'analyse du fichier (durée, résolution, codec)
4. Définir la durée souhaitée pour chaque segment (en secondes)
5. Activer l'option **Convertir en 720p** si désiré
6. Cliquer sur **Découper la vidéo**
7. Patienter pendant le traitement
8. Télécharger les segments individuellement ou tous à la fois

### Précision des coupures

Les coupures sont effectuées avec une précision à l'image près (1/30e de seconde). Cela garantit que si vous fusionnez les segments, le résultat sera identique à l'original sans saut ni duplication de frame.

### Option 720p

Lorsque cette option est activée :
- Les vidéos portrait sont redimensionnées à 720 pixels de largeur
- Les vidéos paysage sont redimensionnées à 720 pixels de hauteur
- Le ratio d'aspect original est préservé

## Fusionner des vidéos

Cette fonction permet d'assembler plusieurs vidéos en un seul fichier.

### Étapes

1. Cliquer sur l'onglet **Fusionner**
2. Uploader les vidéos à assembler (une par une)
3. Supprimer ou ré-uploader pour modifier l'ordre
4. Activer l'option **Convertir en 720p** si désiré
5. Cliquer sur **Fusionner les vidéos**
6. Patienter pendant le traitement
7. Télécharger le fichier fusionné

### Compatibilité des formats

La fusion fonctionne mieux lorsque les vidéos ont le même codec, la même résolution et le même framerate. Si les formats diffèrent, l'application réencode automatiquement pour garantir un résultat cohérent.

## Télécharger depuis les réseaux sociaux

Cette fonction permet de sauvegarder des images et vidéos depuis 10 plateformes populaires.

### Plateformes supportées

| Plateforme | Types de contenus |
|------------|-------------------|
| TikTok | Vidéos, Live |
| Instagram | Posts, Reels, Stories, IGTV |
| Facebook | Vidéos, Reels, Stories, Photos de groupe |
| YouTube | Vidéos, Shorts |
| Twitter/X | Vidéos, GIFs |
| Snapchat | Spotlight |
| Threads | Posts vidéo |
| LinkedIn | Vidéos, Posts |
| Pinterest | Épingles vidéo et image |
| Vimeo | Vidéos |

### Étapes

1. Copier l'URL du contenu à télécharger depuis l'application sociale
2. Cliquer sur l'onglet **Download**
3. Coller l'URL dans le champ prévu
4. Activer l'option **Convertir en 720p** si désiré (vidéos uniquement)
5. Cliquer sur **Télécharger**
6. Attendre la fin du téléchargement
7. Cliquer sur le bouton de téléchargement pour sauvegarder le fichier

### Informations affichées

Pour chaque téléchargement, l'application affiche :
- Titre du contenu
- Nom du créateur
- Durée (pour les vidéos)
- Nombre de vues
- Nombre de likes
- Plateforme d'origine
- Badge 720p si la conversion a été appliquée
- Badge Image/Vidéo selon le type

## Extraire des frames

Cette fonction permet de capturer la première et la dernière image d'une vidéo.

### Utilisations courantes

- Créer des miniatures pour des publications
- Vérifier le contenu d'une vidéo sans la lire
- Extraire des images fixes de qualité

### Étapes

1. Cliquer sur l'onglet **Frames**
2. Uploader une vidéo
3. Cliquer sur **Extraire les Frames**
4. Télécharger les images (première et dernière)

### Format de sortie

Les images sont exportées en JPEG avec une qualité élevée (paramètre -q:v 2 de FFmpeg).

## Mode sombre

L'application propose un mode sombre et un mode clair. Cliquer sur l'icône lune/soleil en haut à droite pour basculer. Le choix est mémorisé pour les visites suivantes.

## Nettoyage automatique

Pour libérer l'espace de stockage, tous les fichiers sont automatiquement supprimés lorsque vous rafraîchissez la page. Pensez à télécharger vos fichiers avant de quitter.

## Limites

| Limite | Valeur |
|--------|--------|
| Taille maximale par fichier | 500 Mo |
| Formats acceptés | MP4, MOV, AVI, MKV, WebM, FLV, WMV, M4V |
| Durée minimale d'un segment | 1 seconde |

## Résolution des problèmes

### Le fichier n'est pas accepté

- Vérifier que le format est dans la liste des formats supportés
- Vérifier que la taille ne dépasse pas 500 Mo
- Essayer de convertir le fichier dans un autre format

### Le téléchargement social échoue

- Vérifier que l'URL est complète et valide
- Certains contenus privés ne sont pas accessibles
- Essayer avec une URL différente du même contenu

### Le traitement est lent

- Les fichiers volumineux prennent plus de temps
- La conversion 720p ajoute du temps de traitement
- La fusion de nombreuses vidéos peut être longue

## Raccourcis clavier

L'application ne dispose pas de raccourcis clavier spécifiques. La navigation se fait uniquement via les boutons et la barre de navigation.
