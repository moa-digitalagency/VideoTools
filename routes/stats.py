from flask import Blueprint, jsonify

from services.video_service import VideoService

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/api/stats', methods=['GET'])
def get_stats():
    stats = VideoService.get_stats()
    return jsonify(stats)
