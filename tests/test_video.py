import pytest
from pysubs.utils.exceptions.awss3 import S3InvalidUploadSource
from pysubs.utils.exceptions.youtube import UnsupportedMediaDownloadError, UnsupportedMediaConversionError
from pysubs.utils.models import Media, MediaSource, MediaType
from pysubs.utils.video import AwsS3MediaManager, YouTubeMediaManager


class TestAwsS3MediaManager:
    media = Media(
        id="1",
        title="title",
        content=b"",
        source=MediaSource.AWS,
        file_type=MediaType.MP4,
        local_storage_path=None
    )

    def test_init(self):
        obj = AwsS3MediaManager()
        assert type(obj) == AwsS3MediaManager

    def test_upload(self):
        obj = AwsS3MediaManager()
        with pytest.raises(S3InvalidUploadSource):
            obj.upload(media=self.media)

    def test_convert(self):
        pass


def mock_download_from_youtube(*_, **__) -> tuple[str, bytes, str]:
    return "test title", b"test content", ""


def mock_convert(*_, **__) -> tuple[str, bytes, str]:
    return "test title", b"test content", ""


class TestYTMediaManager:
    mp4_media = Media(
        id="1",
        title="title",
        content=b"",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP4,
        local_storage_path=None,
        _source_url="https://youtube.com/testvideo"
    )
    mp3_media = Media(
        id="1",
        title="title",
        content=b"",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP3,
        local_storage_path=None,
        _source_url="https://youtube.com/testvideo"
    )
    unsupported_media = Media(
        id="1",
        title="title",
        content=b"",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.UNKNOWN,
        local_storage_path=None,
        _source_url="https://youtube.com/testvideo"
    )

    def test_mp4_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        result = obj.download(media=self.mp4_media)
        assert result.title == "test title"
        assert result.content == b"test content"

    def test_mp3_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        result = obj.download(media=self.mp3_media)
        assert result.title == "test title"
        assert result.content == b"test content"

    def test_unsupported_download(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_download_from_youtube
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaDownloadError):
            _ = obj.download(media=self.unsupported_media)

    def test_mp4_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_convert
        )
        obj = YouTubeMediaManager()
        result = obj.convert(media=self.mp4_media, to_type=MediaType.MP3)
        assert result.title == "test title"
        assert result.content == b"test content"
        assert result.file_type == MediaType.MP3
        assert result.source == MediaSource.YOUTUBE

    def test_mp3_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_convert
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaConversionError):
            _ = obj.convert(media=self.mp3_media, to_type=MediaType.MP4)

    def test_unknown_convert(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._download_from_youtube",
            mock_convert
        )
        obj = YouTubeMediaManager()
        with pytest.raises(UnsupportedMediaConversionError):
            _ = obj.convert(media=self.unsupported_media, to_type=MediaType.UNKNOWN)

