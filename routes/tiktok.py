from flask import Blueprint, request, jsonify

from services.tiktok_service import TikTokService

tiktok_bp = Blueprint('tiktok', __name__)


@tiktok_bp.route('/api/tiktok/download', methods=['POST'])
def download_tiktok():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    result, error = TikTokService.download_video(url)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(result)
