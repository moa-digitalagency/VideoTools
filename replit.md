# VideoSplit - Video Split & Merge Web Application

## Overview

VideoSplit is a mobile-first web application for splitting and merging video files. Users can upload videos, split them into segments of configurable duration (exactly N seconds each), or merge multiple videos into one seamless file. The app features a gamification layer with achievements and statistics tracking.

## Architecture

**Frontend**: Pure HTML/CSS/Tailwind/JavaScript
- Located in `server/templates/` directory
- `server/templates/index.html` - Main HTML page
- `server/templates/css/style.css` - Custom CSS styles
- `server/templates/js/app.js` - All JavaScript logic

**Backend**: Python Flask with modular architecture
- `server/app.py` - Flask application factory
- `server/config.py` - Configuration settings
- `server/models/` - Data models (Video, Job, Stats)
- `server/routes/` - API route handlers
- `server/services/` - Business logic (VideoService)
- `server/utils/` - Utilities (FFmpeg, FileHandler)
- `server/security/` - Validation and security

## User Preferences

Preferred communication style: Simple, everyday language.

## Project Structure

```
server/
├── app.py              # Flask app factory
├── config.py           # Configuration
├── __init__.py         # Package init
├── models/
│   ├── __init__.py
│   ├── video.py        # Video data model
│   ├── job.py          # Job data model
│   └── stats.py        # Stats data model
├── routes/
│   ├── __init__.py
│   ├── videos.py       # Video API routes
│   ├── jobs.py         # Jobs API routes
│   └── stats.py        # Stats API routes
├── services/
│   ├── __init__.py
│   └── video_service.py # Video processing logic
├── utils/
│   ├── __init__.py
│   ├── ffmpeg.py       # FFmpeg helper
│   └── file_handler.py # File operations
├── security/
│   ├── __init__.py
│   └── validator.py    # Input validation
└── templates/
    ├── index.html      # Main page
    ├── css/style.css   # Styles
    └── js/app.js       # JavaScript
```

## API Endpoints

- `GET /` - Serve main HTML page
- `GET /api/videos` - List uploaded videos
- `POST /api/videos/upload` - Upload video file
- `DELETE /api/videos/<id>` - Delete video
- `GET /api/videos/<id>/download` - Download video
- `POST /api/videos/split` - Split video into segments
- `POST /api/videos/merge` - Merge multiple videos
- `GET /api/jobs` - List processing jobs
- `GET /api/stats` - Get statistics
- `GET /api/download/<filename>` - Download processed file

## Video Processing

### FFmpeg Configuration
- **Lossless mode first**: Uses `-c copy` to preserve original quality
- **Fallback to re-encoding**: Uses libx264/aac if lossless fails
- **Preset**: medium (balance of speed/quality)
- **CRF**: 23 (high quality)
- **Audio**: AAC at 192kbps

### Split Algorithm
1. Calculate exact segment count based on duration
2. Handle last segment duration precisely
3. Use stream copy for lossless splitting
4. Fall back to re-encoding if needed

### Merge Algorithm
1. Validate all input videos exist
2. Create job-specific temp directory (avoids race conditions)
3. Generate concat file list
4. Attempt lossless concat first
5. Fall back to re-encoding if codecs differ

## External Dependencies

### Video Processing
- **FFmpeg**: Installed via Nix for video operations

### Python Dependencies
- `flask` - Web framework
- `flask-cors` - CORS support
- `werkzeug` - File upload handling

## File Storage
- `uploads/` - Uploaded video files
- `outputs/` - Processed video segments and merged files
