import hashlib
import json
import os
import tempfile
from collections import OrderedDict
from datetime import datetime
from typing import BinaryIO
from fastapi import UploadFile

from pysubs.dal.datastore_models import UserModel
from pysubs.utils.media.file import FileMediaManager
from pysubs.utils.models import MediaSource, MediaType, Media
from tests.mock_functions import mock_write_content_to_file, mock_get_media_duration, mock_create_thumbnail, \
    mock_get_base64_src_for_image, mock_convert_to_mp3, mock_make_filename_unique

file = BinaryIO()
file.write(b"12354")
uploaded_file = UploadFile(filename="test.mp4", file=file)
file.close()

sample_media = Media(
    id=None,
    source=MediaSource.RAW_FILE,
    file_type=MediaType.MP4,
    source_file=uploaded_file
)

sample_user = UserModel(
    id="1",
    credits="100",
    displayName="pla",
    email="str@str.com",
    createdAt=datetime.now()
)


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
        fm = FileMediaManager()
        media = fm.get_media_info(media=sample_media, user=sample_user)
        assert "data:image/jpeg;base64," in media.thumbnail_url
        assert media.source == MediaSource.RAW_FILE
        assert media.file_type == MediaType.MP4

    def test_make_filename_unique(self):
        filename = "test.mp4"
        org_bef_uuid = os.path.splitext(filename)[0]
        org_aft_uuid = os.path.splitext(filename)[1]
        unique_filename = FileMediaManager.make_filename_unique(filename)
        new_bef_uuid = unique_filename.split("-")[0]
        new_aft_uuid = os.path.splitext(unique_filename.split("-")[1])[1]
        assert org_bef_uuid == new_bef_uuid
        assert org_aft_uuid == new_aft_uuid

    def test_download(self):
        mgr = FileMediaManager()
        media = mgr.download(media=sample_media)
        assert media.source == sample_media.source
        assert media.file_type == sample_media.file_type
        assert media.source_file == sample_media.source_file

    def test_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.conversion.convert_to_mp3",
            mock_convert_to_mp3
        )
        mgr = FileMediaManager()
        result = mgr.convert(media=sample_media, to_type=MediaType.MP3)
        assert result.file_type == MediaType.MP3

    def test_generate_media_id(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.media.file.FileMediaManager.make_filename_unique",
            mock_make_filename_unique
        )
        media_id = FileMediaManager.generate_media_id(sample_media, sample_user)
        key_helper_dict = OrderedDict({
            "unique_file_id": sample_media.source_file.filename,
            "user_id": sample_user.id
        })
        key_helper = json.dumps(key_helper_dict).encode("utf-8")
        assert hashlib.sha256(key_helper).hexdigest() == media_id
