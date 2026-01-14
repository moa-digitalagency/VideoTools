import os
import uuid
import json
from threading import Thread
from typing import List, Optional, Tuple
from datetime import datetime

from database import SessionLocal, VideoModel, JobModel, StatsModel
from utils import FFmpegHelper, FileHandler
from security import FileValidator
from config import OUTPUT_DIR


class VideoService:
    
    @staticmethod
    def get_db():
        return SessionLocal()
    
    @staticmethod
    def upload_video(file, original_name: str, is_temporary: bool = False) -> Tuple[Optional[dict], Optional[str]]:
        valid, error = FileValidator.validate_extension(original_name)
        if not valid:
            return None, error
        
        filename, file_path = FileHandler.save_upload(file, original_name)
        file_size = FileHandler.get_file_size(file_path)
        
        valid, error = FileValidator.validate_size(file_size)
        if not valid:
            FileHandler.delete_file(file_path)
            return None, error
        
        valid, error = FileValidator.validate_video_file(file_path)
        if not valid:
            FileHandler.delete_file(file_path)
            return None, error
        
        duration = FFmpegHelper.get_duration(file_path)
        codec, resolution, bitrate = FFmpegHelper.get_codec_info(file_path)
        
        video_id = str(uuid.uuid4())
        
        db = VideoService.get_db()
        try:
            video = VideoModel(
                id=video_id,
                filename=filename,
                original_name=original_name,
                size=file_size,
                duration=duration,
                path=file_path,
                codec=codec,
                resolution=resolution,
                bitrate=bitrate,
                is_temporary=is_temporary
            )
            db.add(video)
            db.commit()
            
            return {
                "id": video.id,
                "filename": video.filename,
                "originalName": video.original_name,
                "size": video.size,
                "duration": video.duration,
                "codec": video.codec,
                "resolution": video.resolution,
                "bitrate": video.bitrate
            }, None
        finally:
            db.close()
    
    @staticmethod
    def get_all_videos() -> List[dict]:
        db = VideoService.get_db()
        try:
            videos = db.query(VideoModel).filter(VideoModel.is_temporary == False).order_by(VideoModel.created_at.desc()).all()
            return [{
                "id": v.id,
                "filename": v.filename,
                "originalName": v.original_name,
                "size": v.size,
                "duration": v.duration,
                "codec": v.codec,
                "resolution": v.resolution,
                "bitrate": v.bitrate
            } for v in videos]
        finally:
            db.close()
    
    @staticmethod
    def get_video(video_id: str) -> Optional[VideoModel]:
        db = VideoService.get_db()
        try:
            return db.query(VideoModel).filter(VideoModel.id == video_id).first()
        finally:
            db.close()
    
    @staticmethod
    def delete_video(video_id: str) -> bool:
        db = VideoService.get_db()
        try:
            video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
            if not video:
                return False
            
            FileHandler.delete_file(video.path)
            db.delete(video)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def split_video(video_id: str, segment_duration: int) -> Tuple[Optional[dict], Optional[str]]:
        db = VideoService.get_db()
        try:
            video = db.query(VideoModel).filter(VideoModel.id == video_id).first()
            if not video:
                return None, "Video not found"
            
            if segment_duration < 1:
                return None, "Segment duration must be at least 1 second"
            
            if segment_duration > video.duration:
                return None, "Segment duration exceeds video length"
            
            job_id = str(uuid.uuid4())
            job = JobModel(
                id=job_id,
                type='split',
                status='pending',
                video_id=video_id,
                segment_duration=segment_duration
            )
            db.add(job)
            db.commit()
            
            thread = Thread(target=VideoService._process_split, args=(job_id,))
            thread.daemon = True
            thread.start()
            
            return {"id": job_id, "type": "split", "status": "pending"}, None
        finally:
            db.close()
    
    @staticmethod
    def _process_split(job_id: str):
        db = VideoService.get_db()
        try:
            job = db.query(JobModel).filter(JobModel.id == job_id).first()
            if not job:
                return
            
            job.status = 'processing'
            job.progress = 0
            db.commit()
            
            video = db.query(VideoModel).filter(VideoModel.id == job.video_id).first()
            if not video:
                job.status = 'error'
                job.error = 'Video not found'
                db.commit()
                return
            
            ext = FileHandler.get_extension(video.original_name) or "mp4"
            output_pattern = os.path.join(OUTPUT_DIR, f"split_{job.id}_segment_{{index}}.{ext}")
            
            outputs = FFmpegHelper.split_video_lossless(
                video.path,
                output_pattern,
                job.segment_duration,
                video.duration
            )
            
            if not outputs:
                job.status = 'error'
                job.error = 'No segments created'
                db.commit()
                return
            
            job.outputs = json.dumps(outputs)
            job.status = 'completed'
            job.progress = 100
            db.commit()
            
            stats = db.query(StatsModel).first()
            if stats:
                stats.total_videos_split += 1
                stats.total_segments_created += len(outputs)
                stats.total_time_saved += video.duration
                db.commit()
                
        except Exception as e:
            job.status = 'error'
            job.error = str(e)
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def merge_videos(video_ids: List[str]) -> Tuple[Optional[dict], Optional[str]]:
        if len(video_ids) < 2:
            return None, "Need at least 2 videos to merge"
        
        db = VideoService.get_db()
        try:
            for vid in video_ids:
                video = db.query(VideoModel).filter(VideoModel.id == vid).first()
                if not video:
                    return None, f"Video {vid} not found"
            
            job_id = str(uuid.uuid4())
            job = JobModel(
                id=job_id,
                type='merge',
                status='pending',
                video_ids=json.dumps(video_ids)
            )
            db.add(job)
            db.commit()
            
            thread = Thread(target=VideoService._process_merge, args=(job_id,))
            thread.daemon = True
            thread.start()
            
            return {"id": job_id, "type": "merge", "status": "pending"}, None
        finally:
            db.close()
    
    @staticmethod
    def _process_merge(job_id: str):
        db = VideoService.get_db()
        temp_dir = None
        try:
            job = db.query(JobModel).filter(JobModel.id == job_id).first()
            if not job:
                return
            
            job.status = 'processing'
            job.progress = 0
            db.commit()
            
            temp_dir = FileHandler.create_temp_dir(f"merge_{job_id}_")
            
            video_ids = json.loads(job.video_ids) if job.video_ids else []
            input_files = []
            total_duration = 0
            
            for vid in video_ids:
                video = db.query(VideoModel).filter(VideoModel.id == vid).first()
                if not video:
                    job.status = 'error'
                    job.error = f'Video {vid} not found'
                    db.commit()
                    return
                input_files.append(video.path)
                total_duration += video.duration
            
            output_filename = f"merged_{job.id}.mp4"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            success = FFmpegHelper.merge_videos_lossless(input_files, output_path, temp_dir)
            
            if not success:
                job.status = 'error'
                job.error = 'Merge failed'
                db.commit()
                return
            
            job.output = output_filename
            job.status = 'completed'
            job.progress = 100
            db.commit()
            
            stats = db.query(StatsModel).first()
            if stats:
                stats.total_videos_merged += 1
                stats.total_time_saved += total_duration
                db.commit()
                
        except Exception as e:
            job.status = 'error'
            job.error = str(e)
            db.commit()
        finally:
            if temp_dir:
                FileHandler.cleanup_temp_dir(temp_dir)
            db.close()
    
    @staticmethod
    def get_all_jobs() -> List[dict]:
        db = VideoService.get_db()
        try:
            jobs = db.query(JobModel).order_by(JobModel.created_at.desc()).all()
            return [{
                "id": j.id,
                "type": j.type,
                "status": j.status,
                "progress": j.progress,
                "outputs": json.loads(j.outputs) if j.outputs else None,
                "output": j.output,
                "error": j.error
            } for j in jobs]
        finally:
            db.close()
    
    @staticmethod
    def get_stats() -> dict:
        db = VideoService.get_db()
        try:
            stats = db.query(StatsModel).first()
            if not stats:
                return {
                    "totalVideosSplit": 0,
                    "totalSegmentsCreated": 0,
                    "totalVideosMerged": 0,
                    "totalTimeSaved": 0,
                    "totalTikTokDownloads": 0
                }
            return {
                "totalVideosSplit": stats.total_videos_split,
                "totalSegmentsCreated": stats.total_segments_created,
                "totalVideosMerged": stats.total_videos_merged,
                "totalTimeSaved": stats.total_time_saved,
                "totalTikTokDownloads": stats.total_tiktok_downloads
            }
        finally:
            db.close()
    
    @staticmethod
    def cleanup_file_after_download(file_path: str):
        """Delete a file after it has been downloaded (for temporary files)"""
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
