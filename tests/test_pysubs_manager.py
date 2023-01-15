import hashlib
import json
import uuid
from collections import OrderedDict
from datetime import timedelta

import pytest
from pysubs.exceptions.youtube import UnsupportedMediaConversionError
from pysubs.utils.pysubs_manager import get_audio_from_yt_video, get_subtitles_from_audio, generate_transcription_id, \
    generate_media_id
from pysubs.utils.models import Media, MediaType, MediaSource, User


def mock_download(self, media: Media) -> Media:
    media.title = "video_metadata.title"
    media.duration = timedelta(minutes=2)
    media.local_storage_path = "/file.mp4"
    media.thumbnail_url = "https://yt.com/be.jpg"
    return media


def mock_convert(self, media: Media, to_type: MediaType) -> Media:
    media.id = str(uuid.uuid4())
    media.file_type = to_type
    media.local_storage_path = "/file.mp3"
    return media


def mock_process_audio(self, audio: Media) -> dict:
    return {"text": "subtitle"}


def mock_generate_subtitles(self, processed_data: dict) -> str:
    return "subtitle"


class TestPySubsManager:
    def test_get_audio_from_yt_video(self, monkeypatch):
        video_url = "https://youtube.com/testvideo"
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager.download",
            mock_download
        )
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager.convert",
            mock_convert
        )
        media = get_audio_from_yt_video(video_url=video_url, user=User())
        assert media.file_type == MediaType.MP3
        assert media.source_url == video_url
        assert media.local_storage_path == "/file.mp3"

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

    def test_generate_media_id(self):
        media_url = "https://mediaurl.com"
        user_id = "1"
        key_helper_dict = OrderedDict({
            "media_url": media_url,
            "user_id": user_id
        })
        key_helper = json.dumps(key_helper_dict).encode("utf-8")
        key = hashlib.sha256(key_helper).hexdigest()
        assert key == generate_media_id(media_url=media_url, user=User(id=user_id))
