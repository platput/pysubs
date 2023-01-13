import tempfile
import uuid

from pytube import YouTube
from pysubs.utils import awss3
from pysubs.utils.exceptions.awss3 import S3InvalidUploadSource
from pysubs.utils.exceptions.youtube import UnsupportedMediaConversionError, UnsupportedMediaDownloadError
from pysubs.utils.interfaces.media import MediaManager
from pysubs.utils.models import MediaType, Media, MediaSource


class AwsS3MediaManager(MediaManager):
    def __init__(self):
        self.s3 = awss3.AwsS3()

    def upload(self, media: Media) -> Media:
        if media.content:
            self.s3.upload_object(s3_filename=media.filename, file_content=media.content)
            return media
        else:
            raise S3InvalidUploadSource("Filepath to upload is not given")

    def download(self, media: Media) -> Media:
        media.content = bytes(self.s3.download_object(file_url=media.source_url), "utf-8")
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        pass


class YouTubeMediaManager(MediaManager):
    def upload(self, media: Media) -> Media:
        pass

    def download(self, media: Media) -> Media:
        if media.file_type == MediaType.MP3:
            media_format = "mp3"
        elif media.file_type == MediaType.MP4:
            media_format = "mp4"
        else:
            raise UnsupportedMediaDownloadError(f"Downloading media with format: `{media.file_type}` is not supported")
        media.title, media.content = YouTubeMediaManager._download_from_youtube(
            video_url=media.source_url,
            media_format=media_format
        )
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        if to_type == MediaType.MP3:
            media_format = "mp3"
        else:
            raise UnsupportedMediaConversionError(f"Converting to {to_type} is not supported at this moment.")
        _, content = YouTubeMediaManager._download_from_youtube(video_url=media.source_url, media_format=media_format)
        converted_media = Media(
            id=str(uuid.uuid4()),
            title=media.title,
            content=content,
            source=MediaSource.YOUTUBE,
            file_type=to_type,
        )
        converted_media.source_url = media.source_url
        return converted_media

    @staticmethod
    def _download_from_youtube(video_url: str, media_format: str) -> tuple[str, bytes]:
        yt = YouTube(video_url)
        title = yt.title
        filtered_yt = yt.streams.filter(
            progressive=True, file_extension=media_format
        )
        if media_format == "mp4":
            downloader = filtered_yt.order_by('resolution').desc().first()
        elif media_format == "mp3":
            downloader = filtered_yt.first()
        else:
            raise UnsupportedMediaDownloadError(f"Downloading media with format: `{media_format}` is not supported")
        filepath = downloader.download(
            output_path=tempfile.gettempdir(),
        )
        with open(filepath) as mediafile:
            content = mediafile.read()
        return title, content.encode("utf-8")
