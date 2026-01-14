from flask import Blueprint, jsonify
import os
import shutil

from database import cleanup_all
from config import UPLOAD_DIR, OUTPUT_DIR

cleanup_bp = Blueprint('cleanup', __name__)


@cleanup_bp.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Clean up all database entries and files."""
    try:
        cleanup_all()
        
        for folder in [UPLOAD_DIR, OUTPUT_DIR]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        return jsonify({"success": True, "message": "Cleanup completed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
