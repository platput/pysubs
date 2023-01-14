import uuid
from datetime import timedelta

import pytest
from pysubs.exceptions.youtube import UnsupportedMediaConversionError
from pysubs.utils.pysubs_manager import get_audio_from_yt_video, get_subtitles_from_audio
from pysubs.utils.models import Media, MediaType, MediaSource


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
        media = get_audio_from_yt_video(video_url=video_url)
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
        assert transcription.parent_id == audio.id
