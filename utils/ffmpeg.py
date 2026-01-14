import subprocess
import json
import os
from typing import Optional, Dict, List, Tuple
from config import FFMPEG_VIDEO_CODEC, FFMPEG_AUDIO_CODEC, FFMPEG_PRESET, FFMPEG_CRF


class FFmpegHelper:
    
    @staticmethod
    def get_video_info(file_path: str) -> Dict:
        try:
            result = subprocess.run([
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {}
            
            return json.loads(result.stdout)
        except Exception as e:
            print(f"FFprobe error: {e}")
            return {}
    
    @staticmethod
    def get_duration(file_path: str) -> float:
        info = FFmpegHelper.get_video_info(file_path)
        try:
            return float(info.get("format", {}).get("duration", 0))
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def get_codec_info(file_path: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        info = FFmpegHelper.get_video_info(file_path)
        video_codec = None
        resolution = None
        bitrate = None
        
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                video_codec = stream.get("codec_name")
                width = stream.get("width")
                height = stream.get("height")
                if width and height:
                    resolution = f"{width}x{height}"
                break
        
        try:
            bitrate = int(info.get("format", {}).get("bit_rate", 0))
        except (ValueError, TypeError):
            pass
        
        return video_codec, resolution, bitrate
    
    @staticmethod
    def split_video_lossless(input_path: str, output_pattern: str, 
                             segment_duration: int, total_duration: float) -> List[str]:
        outputs = []
        num_segments = int(total_duration // segment_duration)
        last_segment_duration = total_duration - (num_segments * segment_duration)
        
        if last_segment_duration > 0.1:
            num_segments += 1
        
        for i in range(num_segments):
            start_time = i * segment_duration
            output_file = output_pattern.format(index=i + 1)
            
            if i == num_segments - 1 and last_segment_duration > 0.1:
                duration = last_segment_duration
            else:
                duration = segment_duration
            
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start_time),
                "-i", input_path,
                "-t", str(duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                "-map", "0",
                "-reset_timestamps", "1",
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_file):
                outputs.append(os.path.basename(output_file))
            else:
                outputs.extend(FFmpegHelper._split_with_reencode(
                    input_path, output_file, start_time, duration
                ))
        
        return outputs
    
    @staticmethod
    def _split_with_reencode(input_path: str, output_file: str, 
                             start_time: float, duration: float) -> List[str]:
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", input_path,
            "-t", str(duration),
            "-c:v", FFMPEG_VIDEO_CODEC,
            "-preset", FFMPEG_PRESET,
            "-crf", FFMPEG_CRF,
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_file):
            return [os.path.basename(output_file)]
        return []
    
    @staticmethod
    def merge_videos_lossless(input_files: List[str], output_path: str, 
                              temp_dir: str) -> bool:
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        
        with open(concat_file, "w") as f:
            for file_path in input_files:
                escaped_path = file_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        
        return FFmpegHelper._merge_with_reencode(input_files, output_path, temp_dir)
    
    @staticmethod
    def _merge_with_reencode(input_files: List[str], output_path: str, 
                             temp_dir: str) -> bool:
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        
        with open(concat_file, "w") as f:
            for file_path in input_files:
                escaped_path = file_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", FFMPEG_VIDEO_CODEC,
            "-preset", FFMPEG_PRESET,
            "-crf", FFMPEG_CRF,
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        
        return result.returncode == 0 and os.path.exists(output_path)
    
    @staticmethod
    def split_video_720p(input_path: str, output_pattern: str, 
                         segment_duration: int, total_duration: float) -> List[str]:
        outputs = []
        num_segments = int(total_duration // segment_duration)
        last_segment_duration = total_duration - (num_segments * segment_duration)
        
        if last_segment_duration > 0.1:
            num_segments += 1
        
        for i in range(num_segments):
            start_time = i * segment_duration
            output_file = output_pattern.format(index=i + 1)
            
            if i == num_segments - 1 and last_segment_duration > 0.1:
                duration = last_segment_duration
            else:
                duration = segment_duration
            
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start_time),
                "-i", input_path,
                "-t", str(duration),
                "-vf", "scale=-2:720",
                "-c:v", FFMPEG_VIDEO_CODEC,
                "-preset", FFMPEG_PRESET,
                "-crf", FFMPEG_CRF,
                "-c:a", FFMPEG_AUDIO_CODEC,
                "-b:a", "192k",
                "-movflags", "+faststart",
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and os.path.exists(output_file):
                outputs.append(os.path.basename(output_file))
        
        return outputs
    
    @staticmethod
    def merge_videos_720p(input_files: List[str], output_path: str, 
                          temp_dir: str) -> bool:
        concat_file = os.path.join(temp_dir, "concat_list.txt")
        
        with open(concat_file, "w") as f:
            for file_path in input_files:
                escaped_path = file_path.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-vf", "scale=-2:720",
            "-c:v", FFMPEG_VIDEO_CODEC,
            "-preset", FFMPEG_PRESET,
            "-crf", FFMPEG_CRF,
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        
        return result.returncode == 0 and os.path.exists(output_path)
