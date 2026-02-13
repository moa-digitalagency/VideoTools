# ClipFlow 🎥

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)]()

> **La suite d'outils vidéo tout-en-un pour les créateurs de contenu.**
> Découpez, fusionnez, téléchargez et analysez vos médias sociaux en quelques clics via une interface moderne et réactive.

---

## 📑 Table des Matières

*   [Fonctionnalités Clés](#-fonctionnalités-clés)
*   [Stack Technique](#-stack-technique)
*   [Démarrage Rapide](#-démarrage-rapide)
*   [Architecture Sommaire](#-architecture-sommaire)
*   [Documentation Complète](#-documentation-complète)

---

## 🚀 Fonctionnalités Clés

ClipFlow centralise plusieurs outils essentiels pour le workflow des créateurs :

*   ✂️ **Découpage Intelligent (Split) :** Divisez automatiquement une longue vidéo en segments de durée égale (ex: 30s pour WhatsApp/Stories) sans perte de qualité.
*   🔗 **Fusion de Vidéos (Merge) :** Assemblez plusieurs clips en une seule vidéo fluide, avec option de normalisation 720p.
*   ⬇️ **Social Downloader :** Téléchargez des vidéos et images depuis **TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat, Threads, LinkedIn, Pinterest, et Vimeo**.
*   🖼️ **Extraction de Frames :** Récupérez instantanément la première et la dernière image d'une vidéo pour vos miniatures.
*   🏆 **Gamification :** Suivez vos statistiques (temps gagné, vidéos traitées) et débloquez des succès.
*   🎨 **Interface Moderne :** Mode Sombre/Clair automatique, Drag & Drop, animations fluides.

---

## 🛠 Stack Technique

Une architecture robuste et modulaire conçue pour la performance.

| Composant | Technologie | Description |
| :--- | :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3670A0?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) | API RESTful modulaire avec Blueprints. |
| **Data** | ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white) | SQLAlchemy ORM pour la persistance (Jobs, Historique, Stats). |
| **Traitement** | ![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white) | Moteur de traitement vidéo haute performance. |
| **Frontend** | ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) ![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white) | SPA légère en Vanilla JS (ES6+) et Utility-first CSS. |
| **Infra** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Conteneurisation pour un déploiement iso-prod. |

---

## ⚡ Démarrage Rapide

### Prérequis
*   Python 3.10+
*   FFmpeg (Doit être installé et accessible dans le PATH)

### Installation Manuelle

1.  **Cloner le projet**
    ```bash
    git clone https://github.com/votre-user/clipflow.git
    cd clipflow
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Lancer le serveur**
    ```bash
    python main.py
    ```
    Accédez à `http://localhost:5000`.

### Via Docker (Recommandé)

```bash
docker build -t clipflow .
docker run -p 5000:5000 clipflow
```

---

## 🏗 Architecture Sommaire

Le projet suit une structure MVC adaptée :

*   `app.py` : Point d'entrée Flask.
*   `routes/` : Contrôleurs API (`videos`, `jobs`, `tiktok`, `stats`).
*   `services/` : Logique métier et wrappers FFmpeg/yt-dlp.
*   `models/` : Définitions de la base de données.
*   `templates/` : Frontend (HTML/JS/CSS).

Les tâches lourdes (Split/Merge) sont traitées de manière **asynchrone** via un système de Jobs stockés en base de données, permettant au frontend de poller l'avancement sans bloquer l'interface.

---

## 📚 Documentation Complète

Pour aller plus loin, consultez la documentation détaillée dans le dossier `docs/` :

*   📖 **[Liste Exhaustive des Fonctionnalités](docs/clipflow_features_full_list.md)** : La "Bible" du projet.
*   ⚙️ **[Architecture Technique](docs/clipflow_architecture.md)** : Diagrammes et flux de données.
*   💾 **[Base de Données](docs/clipflow_database.md)** : Schéma relationnel et migrations.
*   💻 **[Stack Technique](docs/clipflow_technical_stack.md)** : Détail des technologies utilisées.
*   🚀 **[Guide de Déploiement](docs/clipflow_deployment.md)** : Installation locale et production.
*   👤 **[Guide Utilisateur](docs/clipflow_user_guide.md)** : Manuel d'utilisation pas à pas.
*   🎨 **[Design Guidelines](docs/clipflow_design_guidelines.md)** : Principes de design et typographie.

---

*Développé avec ❤️ par l'équipe ClipFlow.*
