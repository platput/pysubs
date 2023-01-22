import hashlib
import json
import uuid
from collections import OrderedDict
from datetime import timedelta, datetime
from typing import BinaryIO

import pytest
from fastapi import UploadFile

from pysubs.dal.datastore_models import UserModel
from pysubs.exceptions.media import NotEnoughCreditsToPerformGenerationError
from pysubs.utils.pysubs_manager import get_audio_from_yt_video, get_subtitles_from_audio, generate_transcription_id, \
    check_if_user_can_generate, get_audio_from_video_file, get_remaining_credits, get_history
from pysubs.utils.models import Media, MediaType, MediaSource
from tests.mock_functions import mock_download, mock_convert, mock_process_audio, mock_generate_subtitles, \
    mock_firestore_instance, mock_get_history_for_user, mock_get_media_info_for_yt, \
    mock_get_media_info_for_file

sample_file = BinaryIO()
sample_file.write(b"12354")
uploaded_file = UploadFile(filename="test.mp4", file=sample_file)
sample_file.close()


class TestPySubsManager:
    def test_get_audio_from_yt_video(self, monkeypatch):
        video_url = "https://youtube.com/testvideo"
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager.download",
            mock_download
        )
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager.convert",
            mock_convert
        )
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager.get_media_info",
            mock_get_media_info_for_yt
        )
        user = UserModel(
            id="",
            credits=1,
            displayName="",
            email="",
            createdAt=datetime.now()
        )
        video = Media(
            id="123456",
            source=MediaSource.YOUTUBE,
            file_type=MediaType.MP4,
            source_url="https://youtube.com/testvideo"
        )
        media = get_audio_from_yt_video(video=video, user=user)
        assert media.file_type == MediaType.MP3
        assert media.source_url == video_url

    def test_get_audio_from_video_file(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.media.file.FileMediaManager.get_media_info",
            mock_get_media_info_for_file
        )
        monkeypatch.setattr(
            "pysubs.utils.media.file.FileMediaManager.download",
            mock_download
        )
        monkeypatch.setattr(
            "pysubs.utils.media.file.FileMediaManager.convert",
            mock_convert
        )
        user = UserModel(
            id="",
            credits=1,
            displayName="",
            email="",
            createdAt=datetime.now()
        )
        video = Media(
            id="123456",
            source=MediaSource.RAW_FILE,
            file_type=MediaType.MP4,
        )
        media = get_audio_from_video_file(video=video, user=user)
        assert media.file_type == MediaType.MP3

    def test_get_subtitles_from_audio(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.transcriber.WhisperTranscriber.process_audio",
            mock_process_audio
        )
        monkeypatch.setattr(
            "pysubs.utils.transcriber.WhisperTranscriber.generate_subtitles",
            mock_generate_subtitles
        )
        audio = Media(
            id="123456",
            title="",
            content=b"",
            source=MediaSource.YOUTUBE,
            file_type=MediaType.MP3,
            source_url="https://youtube.com/testvideo",
            duration=timedelta(minutes=2),
            local_storage_path="/file.mp3",
            thumbnail_url="https://yt.com/be.jpg"
        )
        transcription = get_subtitles_from_audio(audio=audio)
        assert transcription.media_id == audio.id

    def test_generate_transcription_id(self):
        media_id = "1234"
        language = "french"
        key_helper_dict = OrderedDict({
            "media_id": media_id,
            "language": language
        })
        key_helper = json.dumps(key_helper_dict).encode("utf-8")
        key = hashlib.sha256(key_helper).hexdigest()
        assert key == generate_transcription_id(media_id=media_id, language=language)

    media = Media(
        id=None,
        title=None,
        content=None,
        thumbnail_url=None,
        source_url="",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP4,
        duration=timedelta(hours=1),
        local_storage_path=None,
    )
    user = UserModel(
        id=str(uuid.uuid4()),
        credits=0,
        displayName="",
        email="",
        createdAt=datetime.now()
    )

    def test_check_if_user_can_generate_has_credits(self):
        self.user.credits = 100
        assert check_if_user_can_generate(media=self.media, user=self.user) is True

    def test_check_if_user_can_generate_no_credits(self):
        self.user.credits = 0
        assert check_if_user_can_generate(media=self.media, user=self.user) is False

    def test_check_if_user_can_generate_not_enough_credits(self):
        self.user.credits = 5
        assert check_if_user_can_generate(media=self.media, user=self.user) is False

    def test_get_remaining_credits(self):
        self.media.duration = timedelta(minutes=5)
        self.user.credits = 1
        assert get_remaining_credits(media=self.media, user=self.user) == 0
        self.media.duration = timedelta(minutes=10)
        self.user.credits = 1
        with pytest.raises(NotEnoughCreditsToPerformGenerationError):
            get_remaining_credits(media=self.media, user=self.user)
        self.media.duration = timedelta(minutes=10)
        self.user.credits = 3
        assert get_remaining_credits(media=self.media, user=self.user) == 1

    def test_get_history(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.dal.firestore.FirestoreDatastore.instance",
            mock_firestore_instance
        )
        monkeypatch.setattr(
            "pysubs.dal.firestore.FirestoreDatastore.get_history_for_user",
            mock_get_history_for_user
        )
        current_datetime = datetime.now()
        history = get_history(last_created_at=current_datetime, count=1, user=self.user)
        assert len(history) == 1
        assert history[0].created_at == current_datetime
