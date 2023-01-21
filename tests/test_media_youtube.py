from datetime import timedelta

import pytest
from pysubs.exceptions.media import UnsupportedMediaDownloadError, UnsupportedMediaConversionError
from pysubs.utils.conversion import convert_to_mp3 as convert_to_mp3
from pysubs.utils.models import Media, MediaSource, MediaType, ConvertedFile
from pysubs.utils.media.youtube import YouTubeMediaManager
from tests.mock_functions import mock_download_from_youtube, mock_convert_to_mp3, mock_ffmpeg_convert, mock_convert


class TestYTMediaManager:
    mp4_media = Media(
        id="1",
        title="title",
        content=b"test content",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP4,
        source_url="https://youtube.com/testvideo",
        local_storage_path="/file.mp5",
        duration=timedelta(minutes=2),
        thumbnail_url="https://yt.com/be.jpg"
    )
    mp3_media = Media(
        id="1",
        title="title",
        content=b"test content",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP3,
        local_storage_path=None,
        source_url="https://youtube.com/testvideo",
        duration=timedelta(minutes=2),
        thumbnail_url="https://yt.com/be.jpg"
    )
    unsupported_media = Media(
        id="1",
        title="title",
        content=b"test content",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.UNKNOWN,
        local_storage_path=None,
        source_url="https://youtube.com/testvideo",
        duration=timedelta(minutes=2),
        thumbnail_url="https://yt.com/be.jpg"
    )

    def test_mp4_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        result = obj.download(media=self.mp4_media)
        assert result.title == "test title"
        assert result.content == b"test content"

    def test_mp3_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaDownloadError):
            _ = obj.download(media=self.mp3_media)

    def test_unsupported_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.media.youtube.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaDownloadError):
            _ = obj.download(media=self.unsupported_media)

    def test_mp4_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.conversion.convert_to_mp3",
            mock_convert_to_mp3
        )
        monkeypatch.setattr(
            "pysubs.utils.conversion.ffmpeg_convert",
            mock_ffmpeg_convert
        )
        obj = YouTubeMediaManager()
        result = obj.convert(media=self.mp4_media, to_type=MediaType.MP3)
        assert result.title == "test title"
        assert result.file_type == MediaType.MP3

    def test_mp3_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.conversion.convert_to_mp3",
            mock_convert
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaConversionError):
            _ = obj.convert(media=self.mp3_media, to_type=MediaType.MP4)

    def test_unknown_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.conversion.convert_to_mp3",
            mock_convert
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaConversionError):
            _ = obj.convert(media=self.unsupported_media, to_type=MediaType.UNKNOWN)

    def test_convert_to_mp3(self, monkeypatch):
        audio = Media(
            id="123456",
            title="",
            content=b"",
            source=MediaSource.YOUTUBE,
            file_type=MediaType.UNKNOWN,
            source_url="https://youtube.com/testvideo",
            duration=timedelta(minutes=2),
            local_storage_path="/file.mp5",
            thumbnail_url="https://yt.com/be.jpg"
        )
        _ = YouTubeMediaManager()
        monkeypatch.setattr(
            "pysubs.utils.conversion.ffmpeg_convert",
            mock_ffmpeg_convert
        )
        with pytest.raises(UnsupportedMediaConversionError):
            convert_to_mp3(media=audio)
        audio.file_type = MediaType.MP4
        audio.local_storage_path = "/file.mp4"
        result = convert_to_mp3(media=audio)
        assert type(result) == ConvertedFile
