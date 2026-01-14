import os
import re
import uuid
import subprocess
from typing import Optional, Tuple, Dict

from database import SessionLocal, TikTokDownloadModel, StatsModel
from config import OUTPUT_DIR

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


class SocialMediaService:
    
    PLATFORMS = {
        'tiktok': {
            'patterns': ['tiktok.com/', 'vm.tiktok.com/', 'vt.tiktok.com/'],
            'prefix': 'tiktok',
            'name': 'TikTok'
        },
        'instagram': {
            'patterns': ['instagram.com/reel/', 'instagram.com/p/', 'instagram.com/tv/', 'instagram.com/stories/'],
            'prefix': 'instagram',
            'name': 'Instagram'
        },
        'facebook': {
            'patterns': ['facebook.com/watch', 'facebook.com/reel/', 'fb.watch/', 'facebook.com/video', 'facebook.com/photo', 'facebook.com/share'],
            'prefix': 'facebook',
            'name': 'Facebook'
        },
        'youtube': {
            'patterns': ['youtube.com/shorts/', 'youtu.be/', 'youtube.com/watch'],
            'prefix': 'youtube',
            'name': 'YouTube'
        },
        'twitter': {
            'patterns': ['twitter.com/', 'x.com/', 't.co/'],
            'prefix': 'twitter',
            'name': 'Twitter/X'
        },
        'snapchat': {
            'patterns': ['snapchat.com/spotlight/', 'snapchat.com/add/', 'story.snapchat.com/'],
            'prefix': 'snapchat',
            'name': 'Snapchat'
        }
    }
    
    @staticmethod
    def get_db():
        return SessionLocal()
    
    @staticmethod
    def detect_platform(url: str) -> Optional[str]:
        url_lower = url.lower()
        for platform, config in SocialMediaService.PLATFORMS.items():
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
        return sanitized if sanitized else 'media'
    
    @staticmethod
    def convert_to_720p(input_path: str, output_path: str) -> bool:
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", input_path,
                "-vf", "scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return result.returncode == 0 and os.path.exists(output_path)
        except Exception as e:
            print(f"720p conversion error: {e}")
            return False
    
    @staticmethod
    def download_media(url: str, convert_720: bool = False) -> Tuple[Optional[Dict], Optional[str]]:
        if yt_dlp is None:
            return None, "yt-dlp not installed"
        
        platform = SocialMediaService.detect_platform(url)
        if not platform:
            return None, "URL not supported. Supported: TikTok, Instagram, Facebook, YouTube, Twitter/X, Snapchat"
        
        try:
            media_id = str(uuid.uuid4())[:8]
            platform_prefix = SocialMediaService.PLATFORMS[platform]['prefix']
            platform_name = SocialMediaService.PLATFORMS[platform]['name']
            
            temp_template = os.path.join(OUTPUT_DIR, f"{platform_prefix}_{media_id}_temp.%(ext)s")
            
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
                    return None, "Could not extract media info"
                
                temp_filename = ydl.prepare_filename(info)
                
                if not os.path.exists(temp_filename):
                    for ext in ['mp4', 'webm', 'mkv', 'jpg', 'jpeg', 'png', 'webp', 'gif']:
                        possible = os.path.join(OUTPUT_DIR, f"{platform_prefix}_{media_id}_temp.{ext}")
                        if os.path.exists(possible):
                            temp_filename = possible
                            break
                
                if not os.path.exists(temp_filename):
                    return None, "Download failed - file not found"
                
                title = info.get('title', f'{platform_name} Media')
                sanitized_title = SocialMediaService.sanitize_filename(title)
                ext = os.path.splitext(temp_filename)[1].lower()
                
                is_video = ext in ['.mp4', '.webm', '.mkv', '.mov', '.avi']
                is_image = ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']
                media_type = 'video' if is_video else ('image' if is_image else 'media')
                
                conversion_success = False
                if convert_720 and is_video:
                    converted_filename = f"{sanitized_title}_720p.mp4"
                    converted_path = os.path.join(OUTPUT_DIR, converted_filename)
                    
                    counter = 1
                    while os.path.exists(converted_path):
                        converted_filename = f"{sanitized_title}_720p_{counter}.mp4"
                        converted_path = os.path.join(OUTPUT_DIR, converted_filename)
                        counter += 1
                    
                    if SocialMediaService.convert_to_720p(temp_filename, converted_path):
                        os.remove(temp_filename)
                        final_filename = converted_filename
                        final_path = converted_path
                        conversion_success = True
                    else:
                        final_filename = f"{sanitized_title}{ext}"
                        final_path = os.path.join(OUTPUT_DIR, final_filename)
                        counter = 1
                        while os.path.exists(final_path):
                            final_filename = f"{sanitized_title}_{counter}{ext}"
                            final_path = os.path.join(OUTPUT_DIR, final_filename)
                            counter += 1
                        os.rename(temp_filename, final_path)
                else:
                    final_filename = f"{sanitized_title}{ext}"
                    final_path = os.path.join(OUTPUT_DIR, final_filename)
                    
                    counter = 1
                    while os.path.exists(final_path):
                        final_filename = f"{sanitized_title}_{counter}{ext}"
                        final_path = os.path.join(OUTPUT_DIR, final_filename)
                        counter += 1
                    
                    os.rename(temp_filename, final_path)
                
                result = {
                    'id': media_id,
                    'filename': final_filename,
                    'title': title,
                    'uploader': info.get('uploader', info.get('channel', 'Unknown')),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'platform': platform_name,
                    'media_type': media_type,
                    'converted_720p': conversion_success,
                }
                
                db = SocialMediaService.get_db()
                try:
                    download = TikTokDownloadModel(
                        id=media_id,
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
        db = SocialMediaService.get_db()
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


SocialVideoService = SocialMediaService
