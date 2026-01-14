import os
import uuid
from threading import Thread
from typing import List, Optional, Tuple

from models import Video, videos_store, Job, jobs_store, stats_store
from models.job import JobStatus, JobType
from utils import FFmpegHelper, FileHandler
from security import FileValidator
from config import OUTPUT_DIR


class VideoService:
    
    @staticmethod
    def upload_video(file, original_name: str) -> Tuple[Optional[Video], Optional[str]]:
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
        
        video = Video.create(
            filename=filename,
            original_name=original_name,
            size=file_size,
            duration=duration,
            path=file_path,
            codec=codec,
            resolution=resolution,
            bitrate=bitrate,
        )
        
        videos_store[video.id] = video
        return video, None
    
    @staticmethod
    def get_all_videos() -> List[dict]:
        videos = sorted(videos_store.values(), key=lambda v: v.created_at, reverse=True)
        return [v.to_dict() for v in videos]
    
    @staticmethod
    def get_video(video_id: str) -> Optional[Video]:
        return videos_store.get(video_id)
    
    @staticmethod
    def delete_video(video_id: str) -> bool:
        video = videos_store.get(video_id)
        if not video:
            return False
        
        FileHandler.delete_file(video.path)
        del videos_store[video_id]
        return True
    
    @staticmethod
    def split_video(video_id: str, segment_duration: int) -> Tuple[Optional[Job], Optional[str]]:
        video = videos_store.get(video_id)
        if not video:
            return None, "Video not found"
        
        if segment_duration < 1:
            return None, "Segment duration must be at least 1 second"
        
        if segment_duration > video.duration:
            return None, "Segment duration exceeds video length"
        
        job = Job.create_split_job(video_id, segment_duration)
        jobs_store[job.id] = job
        
        thread = Thread(target=VideoService._process_split, args=(job.id,))
        thread.daemon = True
        thread.start()
        
        return job, None
    
    @staticmethod
    def _process_split(job_id: str):
        job = jobs_store.get(job_id)
        if not job:
            return
        
        job.status = JobStatus.PROCESSING
        job.progress = 0
        
        try:
            if not job.video_id:
                raise Exception("No video ID")
            video = videos_store.get(job.video_id)
            if not video:
                raise Exception("Video not found")
            
            ext = FileHandler.get_extension(video.original_name) or "mp4"
            output_pattern = os.path.join(
                OUTPUT_DIR, 
                f"split_{job.id}_segment_{{index}}.{ext}"
            )
            
            segment_dur = job.segment_duration or 10
            outputs = FFmpegHelper.split_video_lossless(
                video.path,
                output_pattern,
                segment_dur,
                video.duration
            )
            
            if not outputs:
                raise Exception("No segments created")
            
            job.outputs = outputs
            job.status = JobStatus.COMPLETED
            job.progress = 100
            
            stats_store.add_split(len(outputs), video.duration)
            
        except Exception as e:
            job.status = JobStatus.ERROR
            job.error = str(e)
    
    @staticmethod
    def merge_videos(video_ids: List[str]) -> Tuple[Optional[Job], Optional[str]]:
        if len(video_ids) < 2:
            return None, "Need at least 2 videos to merge"
        
        for vid in video_ids:
            if vid not in videos_store:
                return None, f"Video {vid} not found"
        
        job = Job.create_merge_job(video_ids)
        jobs_store[job.id] = job
        
        thread = Thread(target=VideoService._process_merge, args=(job.id,))
        thread.daemon = True
        thread.start()
        
        return job, None
    
    @staticmethod
    def _process_merge(job_id: str):
        job = jobs_store.get(job_id)
        if not job:
            return
        
        job.status = JobStatus.PROCESSING
        job.progress = 0
        
        temp_dir = FileHandler.create_temp_dir(f"merge_{job_id}_")
        
        try:
            input_files = []
            total_duration = 0
            
            video_ids = job.video_ids or []
            for vid in video_ids:
                video = videos_store.get(vid)
                if not video:
                    raise Exception(f"Video {vid} not found")
                input_files.append(video.path)
                total_duration += video.duration
            
            output_filename = f"merged_{job.id}.mp4"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            success = FFmpegHelper.merge_videos_lossless(
                input_files, output_path, temp_dir
            )
            
            if not success:
                raise Exception("Merge failed")
            
            job.output = output_filename
            job.status = JobStatus.COMPLETED
            job.progress = 100
            
            stats_store.add_merge(total_duration)
            
        except Exception as e:
            job.status = JobStatus.ERROR
            job.error = str(e)
        finally:
            FileHandler.cleanup_temp_dir(temp_dir)
    
    @staticmethod
    def get_all_jobs() -> List[dict]:
        jobs = sorted(jobs_store.values(), key=lambda j: j.created_at, reverse=True)
        return [j.to_dict() for j in jobs]
    
    @staticmethod
    def get_stats() -> dict:
        return stats_store.to_dict()
