from flask import Blueprint, request, jsonify, send_file, after_this_request
import os

from services.video_service import VideoService
from config import OUTPUT_DIR

videos_bp = Blueprint('videos', __name__)


@videos_bp.route('/api/videos', methods=['GET'])
def get_videos():
    videos = VideoService.get_all_videos()
    return jsonify(videos)


@videos_bp.route('/api/videos/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filename = file.filename or "video.mp4"
    video, error = VideoService.upload_video(file, filename)
    
    if error or not video:
        return jsonify({"error": error or "Upload failed"}), 400
    
    return jsonify(video)


@videos_bp.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    success = VideoService.delete_video(video_id)
    
    if not success:
        return jsonify({"error": "Video not found"}), 404
    
    return jsonify({"success": True})


@videos_bp.route('/api/videos/<video_id>/download', methods=['GET'])
def download_video(video_id):
    video = VideoService.get_video(video_id)
    
    if not video:
        return jsonify({"error": "Video not found"}), 404
    
    if not os.path.exists(video.path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(
        video.path,
        as_attachment=True,
        download_name=video.original_name
    )


@videos_bp.route('/api/videos/split', methods=['POST'])
def split_video():
    data = request.get_json()
    video_id = data.get('videoId')
    segment_duration = data.get('segmentDuration')
    convert_720 = data.get('convert720', False)
    
    if not video_id:
        return jsonify({"error": "videoId is required"}), 400
    
    if not segment_duration or not isinstance(segment_duration, int):
        return jsonify({"error": "segmentDuration must be a positive integer"}), 400
    
    job, error = VideoService.split_video(video_id, segment_duration, convert_720)
    
    if error or not job:
        return jsonify({"error": error or "Split failed"}), 400
    
    return jsonify({"jobId": job['id'], **job})


@videos_bp.route('/api/videos/merge', methods=['POST'])
def merge_videos():
    data = request.get_json()
    video_ids = data.get('videoIds')
    convert_720 = data.get('convert720', False)
    
    if not video_ids or not isinstance(video_ids, list):
        return jsonify({"error": "videoIds must be a list"}), 400
    
    job, error = VideoService.merge_videos(video_ids, convert_720)
    
    if error or not job:
        return jsonify({"error": error or "Merge failed"}), 400
    
    return jsonify({"jobId": job['id'], **job})


@videos_bp.route('/api/videos/extract-frames', methods=['POST'])
def extract_frames():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filename = file.filename or "video.mp4"
    result, error = VideoService.extract_frames(file, filename)
    
    if error or not result:
        return jsonify({"error": error or "Frame extraction failed"}), 400
    
    return jsonify(result)


@videos_bp.route('/api/download/<path:filename>', methods=['GET'])
def download_output(filename):
    from urllib.parse import unquote
    decoded_filename = unquote(filename)
    file_path = os.path.join(OUTPUT_DIR, decoded_filename)
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    @after_this_request
    def cleanup(response):
        if any(prefix in decoded_filename for prefix in ['tiktok_', 'instagram_', 'facebook_', 'youtube_', 'twitter_', 'snapchat_', 'threads_', 'linkedin_', 'pinterest_', 'vimeo_', 'frame_']):
            VideoService.cleanup_file_after_download(file_path)
        return response
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=decoded_filename
    )
