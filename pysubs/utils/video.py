import logging
import os.path
import tempfile
import uuid

import ffmpeg
from pytube import YouTube
from pysubs.utils import awss3
from pysubs.utils.constants import LogConstants
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
        media.title, media.content, media.local_storage_path = YouTubeMediaManager._download_from_youtube(
            video_url=media.source_url,
            media_format=media_format
        )
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        if to_type == MediaType.MP3:
            media_format = "mp3"
        else:
            raise UnsupportedMediaConversionError(f"Converting to {to_type} is not supported at this moment.")
        _, content, local_filepath = YouTubeMediaManager._download_from_youtube(
            video_url=media.source_url, media_format=media_format
        )
        converted_media = Media(
            id=str(uuid.uuid4()),
            title=media.title,
            content=content,
            source=MediaSource.YOUTUBE,
            file_type=to_type,
            local_storage_path=local_filepath
        )
        converted_media.source_url = media.source_url
        return converted_media

    @staticmethod
    def _download_from_youtube(video_url: str, media_format: str) -> tuple[str, bytes, str]:
        try:
            yt = YouTube(video_url)
            title = yt.title
            downloader = yt.streams.filter(
                progressive=True, file_extension="mp4"
            ).order_by('resolution').desc().first()
            filepath = downloader.download(
                output_path=tempfile.gettempdir(),
            )
            if media_format == "mp4":
                pass
            elif media_format == "mp3":
                filepath = YouTubeMediaManager._convert_mp4_to_mp3(mp4_filepath=filepath)
            else:
                raise UnsupportedMediaDownloadError(f"Downloading media with format: `{media_format}` is not supported")
            with open(filepath, "rb") as mediafile:
                content = mediafile.read()
            return title, content, filepath
        except AttributeError as e:
            logging.getLogger(LogConstants.LOGGER_NAME).error(
                f"Downloading youtube video from the url: {video_url} failed with error: {e}"
            )
            raise

    @staticmethod
    def _convert_mp4_to_mp3(mp4_filepath: str) -> str:
        mp3_filename = f"{str(uuid.uuid4())}.mp3"
        temp_audio_filepath = os.path.join(tempfile.gettempdir(), mp3_filename)
        ffmpeg.input(mp4_filepath).output(temp_audio_filepath, acodec='mp3').run()
        return temp_audio_filepath
