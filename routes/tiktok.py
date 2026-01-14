from flask import Blueprint, request, jsonify

from services.social_service import SocialVideoService

tiktok_bp = Blueprint('tiktok', __name__)


@tiktok_bp.route('/api/tiktok/download', methods=['POST'])
def download_tiktok():
    data = request.get_json()
    url = data.get('url', '').strip()
    convert_720 = data.get('convert720', False)
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    result, error = SocialVideoService.download_media(url, convert_720)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(result)


@tiktok_bp.route('/api/social/download', methods=['POST'])
def download_social():
    data = request.get_json()
    url = data.get('url', '').strip()
    convert_720 = data.get('convert720', False)
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    result, error = SocialVideoService.download_media(url, convert_720)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(result)
