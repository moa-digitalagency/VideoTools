import os
import re
import uuid
from typing import Optional, Tuple, Dict

from database import SessionLocal, TikTokDownloadModel, StatsModel
from config import OUTPUT_DIR

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


class SocialVideoService:
    
    PLATFORMS = {
        'tiktok': {
            'patterns': ['tiktok.com/', 'vm.tiktok.com/', 'vt.tiktok.com/'],
            'prefix': 'tiktok',
            'name': 'TikTok'
        },
        'instagram': {
            'patterns': ['instagram.com/reel/', 'instagram.com/p/', 'instagram.com/tv/'],
            'prefix': 'instagram',
            'name': 'Instagram'
        },
        'facebook': {
            'patterns': ['facebook.com/watch', 'facebook.com/reel/', 'fb.watch/', 'facebook.com/video'],
            'prefix': 'facebook',
            'name': 'Facebook'
        },
        'youtube': {
            'patterns': ['youtube.com/shorts/', 'youtu.be/', 'youtube.com/watch'],
            'prefix': 'youtube',
            'name': 'YouTube'
        }
    }
    
    @staticmethod
    def get_db():
        return SessionLocal()
    
    @staticmethod
    def detect_platform(url: str) -> Optional[str]:
        url_lower = url.lower()
        for platform, config in SocialVideoService.PLATFORMS.items():
            if any(pattern in url_lower for pattern in config['patterns']):
                return platform
        return None
    
    @staticmethod
    def sanitize_filename(title: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*#%&{}$!\'`@^+=\[\]]', '', title)
        sanitized = re.sub(r'\s+', '_', sanitized)
        sanitized = re.sub(r'\.+', '.', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('._')
        sanitized = sanitized[:80]
        return sanitized if sanitized else 'video'
    
    @staticmethod
    def download_video(url: str) -> Tuple[Optional[Dict], Optional[str]]:
        if yt_dlp is None:
            return None, "yt-dlp not installed"
        
        platform = SocialVideoService.detect_platform(url)
        if not platform:
            return None, "URL not supported. Supported platforms: TikTok, Instagram, Facebook, YouTube Shorts"
        
        try:
            video_id = str(uuid.uuid4())[:8]
            platform_prefix = SocialVideoService.PLATFORMS[platform]['prefix']
            platform_name = SocialVideoService.PLATFORMS[platform]['name']
            
            temp_template = os.path.join(OUTPUT_DIR, f"{platform_prefix}_{video_id}_temp.%(ext)s")
            
            ydl_opts = {
                'outtmpl': temp_template,
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'cookiefile': None,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    return None, "Could not extract video info"
                
                temp_filename = ydl.prepare_filename(info)
                
                if not os.path.exists(temp_filename):
                    for ext in ['mp4', 'webm', 'mkv']:
                        possible = os.path.join(OUTPUT_DIR, f"{platform_prefix}_{video_id}_temp.{ext}")
                        if os.path.exists(possible):
                            temp_filename = possible
                            break
                
                if not os.path.exists(temp_filename):
                    return None, "Download failed - file not found"
                
                title = info.get('title', f'{platform_name} Video')
                sanitized_title = SocialVideoService.sanitize_filename(title)
                ext = os.path.splitext(temp_filename)[1]
                final_filename = f"{sanitized_title}{ext}"
                final_path = os.path.join(OUTPUT_DIR, final_filename)
                
                counter = 1
                while os.path.exists(final_path):
                    final_filename = f"{sanitized_title}_{counter}{ext}"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    counter += 1
                
                os.rename(temp_filename, final_path)
                
                result = {
                    'id': video_id,
                    'filename': final_filename,
                    'title': title,
                    'uploader': info.get('uploader', info.get('channel', 'Unknown')),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'platform': platform_name,
                }
                
                db = SocialVideoService.get_db()
                try:
                    download = TikTokDownloadModel(
                        id=video_id,
                        url=url,
                        filename=final_filename,
                        title=result['title'],
                        uploader=result['uploader'],
                        duration=result['duration'],
                        view_count=result['view_count'],
                        like_count=result['like_count'],
                        path=final_path,
                        is_downloaded=False
                    )
                    db.add(download)
                    
                    stats = db.query(StatsModel).first()
                    if stats:
                        stats.total_tiktok_downloads += 1
                    
                    db.commit()
                finally:
                    db.close()
                
                return result, None
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_downloads():
        db = SocialVideoService.get_db()
        try:
            downloads = db.query(TikTokDownloadModel).order_by(TikTokDownloadModel.created_at.desc()).all()
            return [{
                'id': d.id,
                'filename': d.filename,
                'title': d.title,
                'uploader': d.uploader,
                'duration': d.duration,
                'view_count': d.view_count,
                'like_count': d.like_count
            } for d in downloads]
        finally:
            db.close()
