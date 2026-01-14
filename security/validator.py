import os
import subprocess
from typing import Tuple, Optional
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class FileValidator:
    
    MIME_TYPES = {
        'mp4': ['video/mp4'],
        'mov': ['video/quicktime'],
        'avi': ['video/x-msvideo', 'video/avi'],
        'mkv': ['video/x-matroska'],
        'webm': ['video/webm'],
        'flv': ['video/x-flv'],
        'wmv': ['video/x-ms-wmv'],
        'm4v': ['video/x-m4v', 'video/mp4'],
    }
    
    @staticmethod
    def validate_extension(filename: str) -> Tuple[bool, Optional[str]]:
        if '.' not in filename:
            return False, "File must have an extension"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"Extension .{ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        return True, None
    
    @staticmethod
    def validate_size(file_size: int) -> Tuple[bool, Optional[str]]:
        if file_size <= 0:
            return False, "File is empty"
        
        if file_size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE // (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb}MB"
        
        return True, None
    
    @staticmethod
    def validate_video_file(file_path: str) -> Tuple[bool, Optional[str]]:
        if not os.path.exists(file_path):
            return False, "File not found"
        
        try:
            result = subprocess.run([
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, "Invalid video file"
            
            import json
            data = json.loads(result.stdout)
            streams = data.get("streams", [])
            
            has_video = any(s.get("codec_type") == "video" for s in streams)
            if not has_video:
                return False, "No video stream found"
            
            return True, None
            
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        dangerous_chars = ['..', '/', '\\', '\x00', '<', '>', ':', '"', '|', '?', '*']
        result = filename
        for char in dangerous_chars:
            result = result.replace(char, '_')
        return result
