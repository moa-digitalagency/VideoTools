import os
import uuid
from typing import Optional, Tuple, Dict

from database import SessionLocal, TikTokDownloadModel, StatsModel
from config import OUTPUT_DIR

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


class TikTokService:
    
    @staticmethod
    def get_db():
        return SessionLocal()
    
    @staticmethod
    def download_video(url: str) -> Tuple[Optional[Dict], Optional[str]]:
        if yt_dlp is None:
            return None, "yt-dlp not installed"
        
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
                
                db = TikTokService.get_db()
                try:
                    download = TikTokDownloadModel(
                        id=video_id,
                        url=url,
                        filename=os.path.basename(filename),
                        title=result['title'],
                        uploader=result['uploader'],
                        duration=result['duration'],
                        view_count=result['view_count'],
                        like_count=result['like_count'],
                        path=filename,
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
    def mark_as_downloaded(video_id: str):
        """Mark a TikTok video as downloaded and schedule for cleanup"""
        db = TikTokService.get_db()
        try:
            download = db.query(TikTokDownloadModel).filter(TikTokDownloadModel.id == video_id).first()
            if download:
                download.is_downloaded = True
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def get_all_downloads():
        db = TikTokService.get_db()
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
    
    @staticmethod
    def _is_valid_tiktok_url(url: str) -> bool:
        tiktok_patterns = [
            'tiktok.com/',
            'vm.tiktok.com/',
            'vt.tiktok.com/',
        ]
        return any(pattern in url.lower() for pattern in tiktok_patterns)
