# ClipFlow - Schéma de Base de Données

Ce document décrit la structure de la base de données relationnelle utilisée par ClipFlow.

## 1. Modèles de Données

### 1.1 Table `videos`
Stocke les métadonnées des fichiers uploadés par les utilisateurs avant traitement.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Clé primaire (UUID). |
| `filename` | VARCHAR(255) | Nom du fichier sur le disque (sécurisé). |
| `original_name` | VARCHAR(255) | Nom du fichier d'origine uploadé. |
| `size` | INTEGER | Taille en octets. |
| `duration` | FLOAT | Durée en secondes. |
| `path` | VARCHAR(500) | Chemin absolu sur le serveur. |
| `codec` | VARCHAR(50) | Codec vidéo détecté (ex: h264). |
| `resolution` | VARCHAR(20) | Résolution (ex: 1920x1080). |
| `bitrate` | INTEGER | Débit binaire. |
| `created_at` | DATETIME | Date d'upload (UTC). |
| `is_temporary` | BOOLEAN | Indicateur pour le nettoyage automatique. |

### 1.2 Table `jobs`
Suit l'état des tâches de traitement asynchrone (split, merge).

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Clé primaire (UUID). |
| `type` | VARCHAR(20) | Type de job (`split` ou `merge`). |
| `status` | VARCHAR(20) | État : `pending`, `processing`, `completed`, `error`. |
| `progress` | INTEGER | Pourcentage d'avancement (0-100). |
| `video_id` | VARCHAR(36) | ID de la vidéo source (pour Split). |
| `video_ids` | TEXT | JSON Array des IDs sources (pour Merge). |
| `segment_duration` | INTEGER | Paramètre de durée (pour Split). |
| `outputs` | TEXT | JSON Array des noms de fichiers générés. |
| `output` | VARCHAR(255) | Nom du fichier unique généré (pour Merge). |
| `error` | TEXT | Message d'erreur en cas d'échec. |
| `convert_720` | BOOLEAN | Option de conversion activée ou non. |
| `created_at` | DATETIME | Date de création du job. |

### 1.3 Table `tiktok_downloads`
Historique des téléchargements depuis les réseaux sociaux.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | VARCHAR(36) | Clé primaire (UUID). |
| `url` | VARCHAR(500) | URL source. |
| `filename` | VARCHAR(255) | Nom du fichier téléchargé. |
| `title` | TEXT | Titre de la vidéo/post. |
| `uploader` | VARCHAR(255) | Nom de l'auteur. |
| `duration` | FLOAT | Durée en secondes. |
| `view_count` | INTEGER | Nombre de vues. |
| `like_count` | INTEGER | Nombre de likes. |
| `path` | VARCHAR(500) | Chemin du fichier. |
| `platform` | VARCHAR(50) | Plateforme détectée (TikTok, YouTube...). |
| `media_type` | VARCHAR(20) | `video` ou `image`. |
| `is_downloaded` | BOOLEAN | État du téléchargement. |
| `created_at` | DATETIME | Date de l'action. |

### 1.4 Table `stats`
Singleton (une seule ligne) stockant les statistiques globales de l'instance.

| Colonne | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Clé primaire (toujours 1). |
| `total_videos_split` | INTEGER | Compteur de vidéos découpées. |
| `total_segments_created` | INTEGER | Compteur de segments générés. |
| `total_videos_merged` | INTEGER | Compteur de vidéos fusionnées. |
| `total_time_saved` | FLOAT | Estimation du temps économisé (en secondes). |
| `total_tiktok_downloads` | INTEGER | Compteur de téléchargements sociaux. |

## 2. Système de Migration et Initialisation

Le fichier `database.py` contient la logique d'initialisation (`init_db`).

*   **Création :** Utilise `Base.metadata.create_all(bind=engine)` pour créer les tables inexistantes.
*   **Migration "Soft" :**
    *   Un inspecteur (`sqlalchemy.inspect`) vérifie les colonnes existantes dans la base réelle.
    *   Il compare avec le modèle défini dans le code Python.
    *   Si une colonne manque (ex: nouvelle feature ajoutée au code), une commande `ALTER TABLE ... ADD COLUMN` est exécutée dynamiquement.
    *   *Note :* Ce système remplace des outils lourds comme Alembic pour ce projet, permettant des mises à jour fluides sans perte de données manuelles.
*   **Initialisation des Stats :** Si la table `stats` est vide, une ligne initialisée à 0 est insérée automatiquement.
