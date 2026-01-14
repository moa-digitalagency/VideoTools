import os
import uuid
from typing import Optional, Tuple, Dict
import yt_dlp

from config import OUTPUT_DIR


class TikTokService:
    
    @staticmethod
    def download_video(url: str) -> Tuple[Optional[Dict], Optional[str]]:
        if not TikTokService._is_valid_tiktok_url(url):
            return None, "Invalid TikTok URL"
        
        try:
            video_id = str(uuid.uuid4())[:8]
            output_template = os.path.join(OUTPUT_DIR, f"tiktok_{video_id}.%(ext)s")
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    return None, "Could not extract video info"
                
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    for ext in ['mp4', 'webm', 'mkv']:
                        possible = os.path.join(OUTPUT_DIR, f"tiktok_{video_id}.{ext}")
                        if os.path.exists(possible):
                            filename = possible
                            break
                
                if not os.path.exists(filename):
                    return None, "Download failed - file not found"
                
                result = {
                    'id': video_id,
                    'filename': os.path.basename(filename),
                    'title': info.get('title', 'TikTok Video'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                }
                
                return result, None
                
        except yt_dlp.DownloadError as e:
            return None, f"Download error: {str(e)}"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    @staticmethod
    def _is_valid_tiktok_url(url: str) -> bool:
        tiktok_patterns = [
            'tiktok.com/',
            'vm.tiktok.com/',
            'vt.tiktok.com/',
        ]
        return any(pattern in url.lower() for pattern in tiktok_patterns)
