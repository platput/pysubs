import uuid
from datetime import timedelta

import pytest
from pysubs.exceptions.awss3 import S3InvalidUploadSource
from pysubs.exceptions.youtube import UnsupportedMediaDownloadError, UnsupportedMediaConversionError
from pysubs.utils.models import Media, MediaSource, MediaType, ConvertedFile, YouTubeVideo
from pysubs.utils.video import AwsS3MediaManager, YouTubeMediaManager


class TestAwsS3MediaManager:
    media = Media(
        id="1",
        title="title",
        content=b"",
        source=MediaSource.AWS,
        file_type=MediaType.MP4,
        local_storage_path=None,
        source_url="https://youtube.com/testvideo",
        duration=timedelta(minutes=2),
        thumbnail_url="https://yt.com/be.jpg"
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


def mock_ffmpeg_convert(**_) -> None:
    return None


def mock_convert_to_mp3(media: Media) -> ConvertedFile:
    return ConvertedFile(local_storage_path="/file.mp3")


def mock_download_from_youtube(*_, **__) -> YouTubeVideo:
    return YouTubeVideo(
        title="test title",
        video_link="https://yt.com/v",
        duration=timedelta(seconds=123),
        content=b"test content",
        local_storage_path="/file.mp4",
        thumbnail_url="https://yt.com/v.jpg"
    )


def mock_convert(self, media: Media, to_type: MediaType) -> Media:
    converted_media = Media(
        id=str(uuid.uuid4()),
        title=media.title,
        content=None,
        duration=media.duration,
        source=media.source,
        file_type=to_type,
        local_storage_path="/file.mp3",
        source_url=media.source_url,
        thumbnail_url=media.thumbnail_url
    )
    return converted_media


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
        with pytest.raises(UnsupportedMediaDownloadError):
            result = obj.download(media=self.mp3_media)

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
            "pysubs.utils.video.YouTubeMediaManager._convert_to_mp3",
            mock_convert_to_mp3
        )
        obj = YouTubeMediaManager()
        result = obj.convert(media=self.mp4_media, to_type=MediaType.MP3)
        assert result.title == "test title"
        assert result.file_type == MediaType.MP3
        assert result.local_storage_path == "/file.mp3"

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
        obj = YouTubeMediaManager()
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager._ffmpeg_convert",
            mock_ffmpeg_convert
        )
        with pytest.raises(UnsupportedMediaConversionError):
            obj.__class__._convert_to_mp3(media=audio)
        audio.file_type = MediaType.MP4
        audio.local_storage_path = "/file.mp4"
        result = obj.__class__._convert_to_mp3(media=audio)
        assert type(result) == ConvertedFile
