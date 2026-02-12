import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.tiktok_service import TikTokService
from database import TikTokDownloadModel

class TestTikTokService(unittest.TestCase):
    @patch('services.tiktok_service.yt_dlp')
    @patch('services.tiktok_service.SessionLocal')
    @patch('services.tiktok_service.os.path.exists')
    def test_download_video_truncates_long_title(self, mock_exists, mock_session_local, mock_yt_dlp):
        # Mock yt_dlp
        mock_ydl = MagicMock()
        mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl

        long_title = "A" * 600
        mock_ydl.extract_info.return_value = {
            'title': long_title,
            'uploader': 'Test User',
            'duration': 10,
            'view_count': 100,
            'like_count': 10
        }
        mock_ydl.prepare_filename.return_value = "/tmp/test.mp4"

        # Mock os.path.exists to return True for the file
        mock_exists.return_value = True

        # Mock DB session
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Call the service method
        result, error = TikTokService.download_video("https://www.tiktok.com/@user/video/1234567890")

        # Verify result
        self.assertIsNotNone(result, f"Result is None, error: {error}")
        self.assertIsNone(error)

        # Verify DB add was called with truncated title
        # Find the call to db.add
        add_call = mock_db.add.call_args
        self.assertIsNotNone(add_call)
        download_obj = add_call[0][0]

        self.assertIsInstance(download_obj, TikTokDownloadModel)
        print(f"Title length: {len(download_obj.title)}")
        self.assertLessEqual(len(download_obj.title), 500)

if __name__ == '__main__':
    unittest.main()
