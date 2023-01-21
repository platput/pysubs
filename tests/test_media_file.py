import os
import tempfile
from datetime import datetime
from typing import BinaryIO
from fastapi import UploadFile

from pysubs.utils.media.file import FileMediaManager
from pysubs.utils.models import MediaSource, MediaType
from tests.mock_functions import mock_write_content_to_file, mock_get_media_duration, mock_create_thumbnail, mock_get_base64_src_for_image

file = BinaryIO()
file.write(b"12354")
uploaded_file = UploadFile(filename="test.mp4", file=file)
file.close()


class TestFileMediaManager:
    def test_get_media_info(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.file_helper.write_content_to_file",
            mock_write_content_to_file
        )
        monkeypatch.setattr(
            "pysubs.utils.ffmpeg_utils.get_media_duration",
            mock_get_media_duration
        )
        monkeypatch.setattr(
            "pysubs.utils.ffmpeg_utils.create_thumbnail",
            mock_create_thumbnail
        )
        monkeypatch.setattr(
            "pysubs.utils.conversion.get_base64_src_for_image",
            mock_get_base64_src_for_image
        )
        uploaded_filename = os.path.splitext(uploaded_file.filename)
        sanitized_filename = uploaded_filename[0].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "").replace("-", "_")
        sanitized_ext = uploaded_filename[1].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "").replace("-", "_")
        current_timestamp = int(round(datetime.now().timestamp()))
        video_filename = f"{sanitized_filename}-{current_timestamp}{sanitized_ext}"
        temp_dir = tempfile.gettempdir()
        local_storage_path = os.path.join(temp_dir, video_filename)
        org_title = os.path.basename(local_storage_path)
        org_bef_timestamp = org_title.split("-")[0]
        org_aft_timestamp = org_title.split("-")[1]
        fm = FileMediaManager()
        media = fm.get_media_info(video_file=uploaded_file)
        media_title = media.title
        title_bef_timestamp = media_title.split("-")[0]
        title_aft_timestamp = media_title.split("-")[1]
        assert title_bef_timestamp == org_bef_timestamp
        assert title_aft_timestamp == org_aft_timestamp
        assert "data:image/jpeg;base64," in media.thumbnail_url
        assert media.source == MediaSource.RAW_FILE
        assert media.file_type == MediaType.MP4
        assert media.local_storage_path == local_storage_path
        assert media.source_url == local_storage_path

