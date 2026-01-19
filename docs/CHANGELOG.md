# Historique des versions

## Version actuelle

### Janvier 2026

**Nouvelles fonctionnalites**
- Extraction de frames : capture de la premiere et derniere image d'une video
- Support Vimeo ajoute au telechargement social (10 plateformes au total)
- Onglet Frames dans la navigation principale (Stats accessible via API uniquement)

**Ameliorations techniques**
- Decoupe video frame-accurate a 30 fps pour fusion sans saut
- Reencodage systematique pour garantir les limites exactes des segments
- Force des keyframes toutes les secondes
- Generation de PTS pour synchronisation audio/video

**Corrections**
- Validation des fichiers avant extraction de frames
- Nettoyage des frames apres telechargement
- Message d'erreur incluant toutes les plateformes supportees

**Renommage**
- Application renommee de VideoSplit a ClipFlow

---

## Versions precedentes

### Decembre 2025

**Fonctionnalites initiales**
- Decoupe video en segments de duree egale
- Fusion de plusieurs videos
- Telechargement depuis 9 plateformes sociales
- Conversion 720p optionnelle
- Interface mobile-first avec mode sombre
- Statistiques et achievements
- Nettoyage automatique au rafraichissement

**Plateformes sociales supportees**
- TikTok
- Instagram (posts, reels, stories, IGTV)
- Facebook (videos, reels, stories, photos)
- YouTube (videos, shorts)
- Twitter/X
- Snapchat (spotlight)
- Threads
- LinkedIn
- Pinterest

**Stack technique**
- Frontend : HTML, Tailwind CSS, JavaScript vanilla
- Backend : Python Flask
- Base de donnees : PostgreSQL
- Traitement video : FFmpeg
- Telechargement social : yt-dlp
