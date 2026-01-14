# VideoSplit - Video Split & Merge Web Application

## Overview

VideoSplit is a mobile-first web application for splitting and merging video files. Users can upload videos, split them into segments of configurable duration (exactly N seconds each), or merge multiple videos into one seamless file. The app features a gamification layer with achievements and statistics tracking.

## Architecture

**Frontend**: Pure HTML/CSS/Tailwind/JavaScript (NO React, NO TypeScript)
- Located in `static/` directory
- `static/index.html` - Main HTML page with all UI
- `static/css/style.css` - Custom CSS styles
- `static/js/app.js` - All JavaScript logic

**Backend**: Python Flask with FFmpeg
- Located in `server/app.py`
- Handles video upload, split, merge operations
- Serves static files directly

**Note**: Express (`server/routes.ts`) acts as a launcher/proxy due to workflow constraints, but all actual logic is in Flask.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend (Pure HTML/CSS/JS)
- **No frameworks** - Vanilla JavaScript only
- **Tailwind CSS** via CDN for styling
- **Mobile-first** design with bottom navigation
- **Gamification** - Achievements and statistics tracking

**Key Files**:
- `static/index.html` - Single page application
- `static/css/style.css` - Custom styles
- `static/js/app.js` - All JavaScript logic

### Backend (Python Flask)
- **Framework**: Flask with CORS support
- **Video Processing**: FFmpeg via subprocess
- **File Uploads**: Werkzeug secure file handling
- **Storage**: In-memory dictionaries for metadata/jobs

**Key Endpoints**:
- `POST /api/videos/upload` - Upload video files
- `POST /api/videos/split` - Split video into exact segments
- `POST /api/videos/merge` - Merge multiple videos
- `GET /api/videos` - List uploaded videos
- `GET /api/jobs` - Track processing jobs
- `GET /api/stats` - User statistics
- `GET /api/download/<filename>` - Download processed files

### File Storage
- `uploads/` - Uploaded video files
- `outputs/` - Processed video segments and merged files

## External Dependencies

### Video Processing
- **FFmpeg**: System-level dependency for video splitting and merging (installed via Nix)

### Python Dependencies
- `flask` - Web framework
- `flask-cors` - CORS support
- `werkzeug` - File upload handling

### Third-Party Services
- None - The application operates entirely locally