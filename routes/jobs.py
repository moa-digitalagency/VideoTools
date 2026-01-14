from flask import Blueprint, jsonify

from services import VideoService

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = VideoService.get_all_jobs()
    return jsonify(jobs)
