import os
import shutil
import uuid
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
from ..config import UPLOAD_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class FileHandler:
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_extension(filename: str) -> str:
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    @staticmethod
    def generate_unique_filename(original_name: str) -> str:
        ext = FileHandler.get_extension(original_name)
        safe_name = secure_filename(original_name)
        unique_id = str(uuid.uuid4())[:8]
        return f"{unique_id}_{safe_name}"
    
    @staticmethod
    def save_upload(file, original_name: str) -> Tuple[str, str]:
        filename = FileHandler.generate_unique_filename(original_name)
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)
        return filename, file_path
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except OSError:
            pass
        return False
    
    @staticmethod
    def create_temp_dir(prefix: str = "job_") -> str:
        temp_dir = os.path.join(OUTPUT_DIR, f"{prefix}{uuid.uuid4().hex[:8]}")
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    
    @staticmethod
    def cleanup_temp_dir(temp_dir: str):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except OSError:
            pass
    
    @staticmethod
    def get_output_path(filename: str) -> str:
        return os.path.join(OUTPUT_DIR, filename)
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        return os.path.exists(file_path)
