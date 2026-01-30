import subprocess
import json
import os
import concurrent.futures
from typing import Optional, Dict, List, Tuple
from config import FFMPEG_VIDEO_CODEC, FFMPEG_AUDIO_CODEC, FFMPEG_PRESET, FFMPEG_CRF


class FFmpegHelper:
    
    @staticmethod
    def _run_split_cmd(cmd: List[str], output_file: str) -> Optional[str]:
        """Helper to run a split command in a thread"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0 and os.path.exists(output_file):
                return os.path.basename(output_file)
            else:
                print(f"FFmpeg split error: {result.stderr}")
        except Exception as e:
            print(f"FFmpeg execution error: {e}")
        return None

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
                             segment_duration: int, total_duration: float, fps: int = 30) -> List[str]:
        """Split video with frame-accurate cuts at 30fps for seamless merging.
        Always re-encodes to ensure exact frame boundaries - stream copy cannot guarantee frame accuracy."""
        frame_duration = 1.0 / fps
        
        num_segments = int(total_duration // segment_duration)
        last_segment_duration = total_duration - (num_segments * segment_duration)
        
        if last_segment_duration > frame_duration:
            num_segments += 1
        
        cmds = []
        output_files = []

        for i in range(num_segments):
            start_frame = i * segment_duration * fps
            start_time = start_frame / fps
            
            output_file = output_pattern.format(index=i + 1)
            
            if i == num_segments - 1 and last_segment_duration > frame_duration:
                duration = last_segment_duration
            else:
                duration = segment_duration
            
            num_frames = int(duration * fps)
            actual_duration = num_frames / fps
            
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", f"{start_time:.6f}",
                "-i", input_path,
                "-t", f"{actual_duration:.6f}",
                "-c:v", FFMPEG_VIDEO_CODEC,
                "-preset", FFMPEG_PRESET,
                "-crf", FFMPEG_CRF,
                "-r", str(fps),
                "-g", str(fps),
                "-force_key_frames", f"expr:eq(mod(n,{fps}),0)",
                "-c:a", FFMPEG_AUDIO_CODEC,
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-fflags", "+genpts",
                "-avoid_negative_ts", "make_zero",
                "-threads", "1",
                output_file
            ]
            
            cmds.append(cmd)
            output_files.append(output_file)
            
        # Execute in parallel
        results = [None] * len(cmds)
        max_workers = min(os.cpu_count() or 1, 4)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(FFmpegHelper._run_split_cmd, cmds[i], output_files[i]): i
                for i in range(len(cmds))
            }

            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as exc:
                    print(f'Segment {index} generated an exception: {exc}')
        
        return [r for r in results if r is not None]
    
    @staticmethod
    def _split_with_reencode(input_path: str, output_file: str, 
                             start_time: float, duration: float) -> List[str]:
        return FFmpegHelper._split_with_reencode_precise(input_path, output_file, start_time, duration, 30)
    
    @staticmethod
    def _split_with_reencode_precise(input_path: str, output_file: str, 
                                     start_time: float, duration: float, fps: int = 30) -> List[str]:
        """Re-encode with frame-accurate timing at specified FPS"""
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", f"{start_time:.6f}",
            "-i", input_path,
            "-t", f"{duration:.6f}",
            "-c:v", FFMPEG_VIDEO_CODEC,
            "-preset", FFMPEG_PRESET,
            "-crf", FFMPEG_CRF,
            "-r", str(fps),
            "-g", str(fps),
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-fflags", "+genpts",
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_file):
            return [os.path.basename(output_file)]
        return []
    
    @staticmethod
    def merge_videos_lossless(input_files: List[str], output_path: str, 
                              temp_dir: str) -> bool:
        """Merge videos losslessly - works best when all segments have same codec/fps"""
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
            "-fflags", "+genpts",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True
        
        return FFmpegHelper._merge_with_reencode(input_files, output_path, temp_dir)
    
    @staticmethod
    def _merge_with_reencode(input_files: List[str], output_path: str, 
                             temp_dir: str, fps: int = 30) -> bool:
        """Re-encode and merge at consistent FPS for seamless playback"""
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
            "-r", str(fps),
            "-g", str(fps),
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-fflags", "+genpts",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        
        return result.returncode == 0 and os.path.exists(output_path)
    
    @staticmethod
    def split_video_720p(input_path: str, output_pattern: str, 
                         segment_duration: int, total_duration: float, fps: int = 30) -> List[str]:
        """Split video with 720p conversion and frame-accurate cuts at 30fps for seamless merging."""
        frame_duration = 1.0 / fps
        
        num_segments = int(total_duration // segment_duration)
        last_segment_duration = total_duration - (num_segments * segment_duration)
        
        if last_segment_duration > frame_duration:
            num_segments += 1
        
        cmds = []
        output_files = []

        for i in range(num_segments):
            start_frame = i * segment_duration * fps
            start_time = start_frame / fps
            
            output_file = output_pattern.format(index=i + 1)
            
            if i == num_segments - 1 and last_segment_duration > frame_duration:
                duration = last_segment_duration
            else:
                duration = segment_duration
            
            num_frames = int(duration * fps)
            actual_duration = num_frames / fps
            
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", f"{start_time:.6f}",
                "-i", input_path,
                "-t", f"{actual_duration:.6f}",
                "-vf", "scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'",
                "-c:v", FFMPEG_VIDEO_CODEC,
                "-preset", FFMPEG_PRESET,
                "-crf", FFMPEG_CRF,
                "-r", str(fps),
                "-g", str(fps),
                "-force_key_frames", f"expr:eq(mod(n,{fps}),0)",
                "-c:a", FFMPEG_AUDIO_CODEC,
                "-b:a", "192k",
                "-movflags", "+faststart",
                "-fflags", "+genpts",
                "-avoid_negative_ts", "make_zero",
                "-threads", "1",
                output_file
            ]
            
            cmds.append(cmd)
            output_files.append(output_file)
            
        # Execute in parallel
        results = [None] * len(cmds)
        max_workers = min(os.cpu_count() or 1, 4)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(FFmpegHelper._run_split_cmd, cmds[i], output_files[i]): i
                for i in range(len(cmds))
            }

            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as exc:
                    print(f'Segment {index} generated an exception: {exc}')
        
        return [r for r in results if r is not None]
    
    @staticmethod
    def merge_videos_720p(input_files: List[str], output_path: str, 
                          temp_dir: str, fps: int = 30) -> bool:
        """Merge videos with 720p conversion at consistent FPS for seamless playback"""
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
            "-vf", "scale='if(lt(iw,ih),720,trunc(720*iw/ih/2)*2)':'if(lt(iw,ih),trunc(720*ih/iw/2)*2,720)'",
            "-c:v", FFMPEG_VIDEO_CODEC,
            "-preset", FFMPEG_PRESET,
            "-crf", FFMPEG_CRF,
            "-r", str(fps),
            "-g", str(fps),
            "-c:a", FFMPEG_AUDIO_CODEC,
            "-b:a", "192k",
            "-movflags", "+faststart",
            "-fflags", "+genpts",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        
        return result.returncode == 0 and os.path.exists(output_path)
