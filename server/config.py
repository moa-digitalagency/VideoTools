import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'm4v'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

FFMPEG_VIDEO_CODEC = "libx264"
FFMPEG_AUDIO_CODEC = "aac"
FFMPEG_PRESET = "medium"
FFMPEG_CRF = "23"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
