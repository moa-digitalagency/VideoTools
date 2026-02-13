# ClipFlow - Liste Exhaustive des Fonctionnalités

Ce document recense l'intégralité des fonctionnalités techniques et métier de l'application ClipFlow. Il sert de référence absolue pour le développement et la maintenance.

## 1. Gestion Globale de l'Application

### 1.1 Interface Utilisateur (UI/UX)
*   **Single Page Application (SPA) Simulée :** Navigation fluide sans rechargement de page via masquage/affichage de sections DOM (`.page`).
*   **Thématisation :**
    *   Mode Sombre (Dark) et Clair (Light).
    *   Détection automatique de la préférence système (`prefers-color-scheme`).
    *   Persistance du choix utilisateur via `localStorage` (clé `theme`).
    *   Transition CSS douce (`transition-colors duration-300`) sur le `body` et les composants.
*   **Animations :** Utilisation de fichiers Lottie (`dotlottie-player`) pour les indicateurs de chargement et les illustrations de services.

### 1.2 Maintenance et Nettoyage Automatique
*   **Nettoyage au Démarrage :** À chaque chargement de la page (`DOMContentLoaded`), une requête `POST /api/cleanup` est envoyée.
    *   **Action Backend :** Supprime toutes les entrées des tables `videos`, `jobs`, et `tiktok_downloads` (sauf `stats`).
    *   **Gestion Fichiers :** Supprime physiquement les fichiers temporaires associés pour libérer l'espace disque.
*   **Nettoyage après Téléchargement :**
    *   Middleware `after_this_request` sur la route de téléchargement.
    *   Suppression immédiate du fichier sur le serveur une fois le téléchargement terminé par l'utilisateur (pour les fichiers préfixés `tiktok_`, `instagram_`, etc.).

### 1.3 Système de Jobs Asynchrone
*   **Polling :** Le frontend interroge l'API `GET /api/jobs` toutes les 2 secondes tant que des jobs sont en statut `processing` ou `pending`.
*   **États des Jobs :** `pending` -> `processing` (avec % de progression) -> `completed` ou `error`.
*   **Persistance :** Les jobs sont stockés en base de données (`JobModel`) avec leurs résultats (chemins de fichiers, IDs vidéo).

---

## 2. Module : Découpage Vidéo (Split)

### 2.1 Upload et Entrée
*   **Zone de Drop :** Support du Drag & Drop et du clic classique.
*   **Validation Fichier :** Extensions autorisées (défini dans `config.py`) : `mp4`, `mov`, `avi`, `mkv`, `webm`, `flv`, `wmv`, `m4v`.
*   **Taille Max :** 500 MB (Hardcoded `MAX_FILE_SIZE`).
*   **Feedback Visuel :** Barre de progression d'upload (XMLHttpRequest `upload.onprogress`).

### 2.2 Configuration du Découpage
*   **Paramètres :**
    *   Durée du segment (input numérique, défaut 30s).
    *   Conversion 720p (checkbox).
*   **Prévisualisation Dynamique :** Calcul automatique du nombre de segments estimés (Durée Totale / Durée Segment) affiché avant le lancement.
*   **Information Méta :** Affichage du nom original et de la durée totale formatée (MM:SS).

### 2.3 Traitement (Backend)
*   **Moteur :** FFmpeg via `subprocess`.
*   **Logique :** Découpage précis sans ré-encodage (copie de flux) sauf si l'option 720p est active.
*   **Sortie :** Génération de fichiers nommés `segment_001.mp4`, etc.

### 2.4 Résultat
*   **Affichage :** Carte de job indiquant "Terminé".
*   **Téléchargement :** Liste de boutons individuels pour chaque segment généré.

---

## 3. Module : Fusion Vidéo (Merge)

### 3.1 File d'Attente (Queue)
*   **Gestion Client :** Tableau JavaScript `mergeQueue` maintenant l'état local.
*   **Ordre :** L'ordre d'upload détermine strictement l'ordre de concaténation final.
*   **Modification :** Possibilité de supprimer un élément spécifique de la file avant le lancement.
*   **Validation de Lancement :** Le bouton "Fusionner" est désactivé si moins de 2 vidéos sont présentes.

### 3.2 Traitement (Backend)
*   **Protocole :** Création d'un fichier texte temporaire (file list) pour FFmpeg `concat demuxer`.
*   **Homogénéisation :** Si l'option 720p est active, toutes les vidéos sont normalisées (résolution, codec `libx264`, audio `aac`) avant fusion pour éviter les incompatibilités.

### 3.3 Résultat
*   **Sortie :** Un fichier unique téléchargeable.

---

## 4. Module : Social Downloader

### 4.1 Plateformes Supportées
*   TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest, Vimeo.

### 4.2 Traitement (Backend)
*   **Moteur :** `yt-dlp` (bibliothèque Python).
*   **Extraction de Métadonnées :** Récupération du titre, uploader, durée, nombre de vues/likes.
*   **Logique de Type :** Détection automatique si le média est une vidéo ou une image (ex: Instagram post).
*   **Conversion Optionnelle :** Force le reformatage en 720p MP4 si demandé (utile pour compatibilité mobile stricte).

### 4.3 Historique et Affichage
*   **Historique :** Stocké en base de données (`TikTokDownloadModel`).
*   **Affichage :** Liste antéchronologique (le plus récent en haut).
*   **Badges :** Indicateurs visuels pour la plateforme (couleurs spécifiques), le type (Image/Vidéo), et la qualité (720p).

---

## 5. Module : Extraction de Frames

### 5.1 Fonctionnalité
*   **Objectif :** Extraire la première et la dernière image d'une vidéo pour créer des miniatures ou vérifier le contenu.
*   **Processus :**
    1.  Upload de la vidéo.
    2.  FFmpeg extrait la frame à `00:00:00` (First).
    3.  FFmpeg calcule la durée et extrait la frame à `T-0.1s` (Last).

### 5.2 Résultat
*   **Visuel :** Affichage des deux images directement dans le DOM (`<img src="...">`).
*   **Action :** Boutons de téléchargement direct pour chaque image.

---

## 6. Gamification et Statistiques

### 6.1 Suivi des Statistiques (Global)
*   Table `stats` unique en base de données (singleton pattern).
*   **Métriques :**
    *   Total vidéos découpées.
    *   Total segments créés.
    *   Total vidéos fusionnées.
    *   Temps gagné (Estimation arbitraire basée sur la durée de traitement vs temps humain).
    *   Total téléchargements sociaux.

### 6.2 Système de Succès (Achievements)
*   **Logique Client :** Vérification des seuils statistiques au chargement de la page (`app.js`).
*   **Trophées :**
    *   *Premier Découpage* (1 vidéo split).
    *   *Première Fusion* (1 vidéo merge).
    *   *Maître des Segments* (10+ segments).
    *   *Video Pro* (5+ opérations totales).
    *   *Gain de Temps* (600+ secondes traitées).
*   **UI :** Les cartes de succès changent d'apparence (dégrisées -> colorées) une fois débloquées.

## 7. Base de Données et Migration

### 7.1 Architecture
*   **ORM :** SQLAlchemy.
*   **SGBD :** SQLite (Développement) / Compatible PostgreSQL (Production).

### 7.2 Migration Automatique (`init_db.py`)
*   **Inspection :** Au démarrage, le script inspecte les tables existantes.
*   **Correction :** Si une colonne définie dans le modèle Python est manquante en base (ex: ajout d'une feature), elle est ajoutée via `ALTER TABLE` dynamiquement.
*   **Initialisation Stats :** Crée la ligne de statistiques par défaut si elle n'existe pas.
