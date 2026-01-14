import os
import uuid
import subprocess
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from threading import Thread

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
OUTPUT_DIR = os.path.join(os.getcwd(), "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

videos = {}
jobs = {}
stats = {
    "totalVideosSplit": 0,
    "totalVideosMerged": 0,
    "totalSegmentsCreated": 0,
    "totalTimeSaved": 0,
}


def get_video_duration(file_path):
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                file_path
            ],
            capture_output=True,
            text=True
        )
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0))
    except Exception as e:
        print(f"Error getting duration: {e}")
        return 0


@app.route("/api/videos", methods=["GET"])
def get_videos():
    video_list = sorted(videos.values(), key=lambda x: x["createdAt"], reverse=True)
    return jsonify(video_list)


@app.route("/api/videos/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    video_id = str(uuid.uuid4())
    filename = f"{video_id}_{secure_filename(file.filename)}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)
    
    duration = get_video_duration(file_path)
    file_size = os.path.getsize(file_path)
    
    video = {
        "id": video_id,
        "filename": filename,
        "originalName": file.filename,
        "size": file_size,
        "duration": duration,
        "path": file_path,
        "createdAt": int(uuid.uuid1().time),
    }
    
    videos[video_id] = video
    return jsonify(video)


@app.route("/api/videos/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    if video_id not in videos:
        return jsonify({"error": "Video not found"}), 404
    
    video = videos[video_id]
    if os.path.exists(video["path"]):
        os.remove(video["path"])
    
    del videos[video_id]
    return jsonify({"success": True})


@app.route("/api/videos/<video_id>/download", methods=["GET"])
def download_video(video_id):
    if video_id not in videos:
        return jsonify({"error": "Video not found"}), 404
    
    video = videos[video_id]
    if not os.path.exists(video["path"]):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(
        video["path"],
        as_attachment=True,
        download_name=video["originalName"]
    )


@app.route("/api/videos/split", methods=["POST"])
def split_video():
    data = request.get_json()
    video_id = data.get("videoId")
    segment_duration = data.get("segmentDuration")
    
    if not video_id or not segment_duration:
        return jsonify({"error": "Missing videoId or segmentDuration"}), 400
    
    if video_id not in videos:
        return jsonify({"error": "Video not found"}), 404
    
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "type": "split",
        "status": "processing",
        "progress": 0,
        "inputVideos": [video_id],
        "outputVideos": [],
        "createdAt": int(uuid.uuid1().time),
    }
    jobs[job_id] = job
    
    video = videos[video_id]
    thread = Thread(target=process_split_job, args=(job_id, video, segment_duration))
    thread.start()
    
    return jsonify(job)


@app.route("/api/videos/merge", methods=["POST"])
def merge_videos():
    data = request.get_json()
    video_ids = data.get("videoIds", [])
    
    if len(video_ids) < 2:
        return jsonify({"error": "Need at least 2 videos to merge"}), 400
    
    for vid in video_ids:
        if vid not in videos:
            return jsonify({"error": f"Video {vid} not found"}), 404
    
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "type": "merge",
        "status": "processing",
        "progress": 0,
        "inputVideos": video_ids,
        "outputVideos": [],
        "createdAt": int(uuid.uuid1().time),
    }
    jobs[job_id] = job
    
    video_list = [videos[vid] for vid in video_ids]
    thread = Thread(target=process_merge_job, args=(job_id, video_list))
    thread.start()
    
    return jsonify(job)


@app.route("/api/jobs", methods=["GET"])
def get_jobs():
    job_list = sorted(jobs.values(), key=lambda x: x["createdAt"], reverse=True)
    return jsonify(job_list)


@app.route("/api/jobs/<job_id>/download", methods=["GET"])
def download_job_output(job_id):
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404
    
    job = jobs[job_id]
    if job["status"] != "completed" or not job["outputVideos"]:
        return jsonify({"error": "Job not completed or no outputs"}), 400
    
    first_output_id = job["outputVideos"][0]
    if first_output_id not in videos:
        return jsonify({"error": "Output file not found"}), 404
    
    video = videos[first_output_id]
    return send_file(
        video["path"],
        as_attachment=True,
        download_name=video["originalName"]
    )


@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify(stats)


def process_split_job(job_id, video, segment_duration):
    global stats
    try:
        duration = video.get("duration") or get_video_duration(video["path"])
        segment_count = int((duration + segment_duration - 1) // segment_duration)
        output_videos = []
        
        for i in range(segment_count):
            start_time = i * segment_duration
            is_last = i == segment_count - 1
            actual_duration = duration - start_time if is_last else segment_duration
            
            output_filename = f"{job_id}-segment-{i+1}.mp4"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", video["path"],
                "-ss", str(start_time),
                "-t", str(actual_duration),
                "-c", "copy",
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            base_name = os.path.splitext(video["originalName"])[0]
            ext = os.path.splitext(video["originalName"])[1] or ".mp4"
            
            segment_id = str(uuid.uuid4())
            segment_video = {
                "id": segment_id,
                "filename": output_filename,
                "originalName": f"{base_name}_part{i+1}{ext}",
                "size": os.path.getsize(output_path),
                "duration": actual_duration,
                "path": output_path,
                "createdAt": int(uuid.uuid1().time),
            }
            videos[segment_id] = segment_video
            output_videos.append(segment_id)
            
            progress = int(((i + 1) / segment_count) * 100)
            jobs[job_id]["progress"] = progress
            jobs[job_id]["outputVideos"] = output_videos.copy()
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["outputVideos"] = output_videos
        jobs[job_id]["completedAt"] = int(uuid.uuid1().time)
        
        stats["totalVideosSplit"] += 1
        stats["totalSegmentsCreated"] += segment_count
        stats["totalTimeSaved"] += int(duration)
        
    except Exception as e:
        print(f"Split error: {e}")
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


def process_merge_job(job_id, video_list):
    global stats
    job_temp_dir = os.path.join(OUTPUT_DIR, f"job-{job_id}")
    
    try:
        os.makedirs(job_temp_dir, exist_ok=True)
        
        list_path = os.path.join(job_temp_dir, "list.txt")
        with open(list_path, "w") as f:
            for v in video_list:
                f.write(f"file '{v['path']}'\n")
        
        jobs[job_id]["progress"] = 10
        
        output_filename = f"{job_id}-merged.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        import shutil
        shutil.rmtree(job_temp_dir, ignore_errors=True)
        
        duration = get_video_duration(output_path)
        if duration == 0:
            duration = sum(v.get("duration", 0) for v in video_list)
        
        merged_id = str(uuid.uuid4())
        merged_video = {
            "id": merged_id,
            "filename": output_filename,
            "originalName": f"merged_{job_id[:8]}.mp4",
            "size": os.path.getsize(output_path),
            "duration": duration,
            "path": output_path,
            "createdAt": int(uuid.uuid1().time),
        }
        videos[merged_id] = merged_video
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["outputVideos"] = [merged_id]
        jobs[job_id]["completedAt"] = int(uuid.uuid1().time)
        
        stats["totalVideosMerged"] += 1
        stats["totalTimeSaved"] += int(duration)
        
    except Exception as e:
        print(f"Merge error: {e}")
        import shutil
        shutil.rmtree(job_temp_dir, ignore_errors=True)
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
