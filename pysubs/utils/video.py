import logging
import os.path
import tempfile
import uuid
from datetime import timedelta

import ffmpeg
from pytube import YouTube
from pysubs.utils import awss3
from pysubs.utils.constants import LogConstants
from pysubs.exceptions.awss3 import S3InvalidUploadSource
from pysubs.exceptions.media import UnsupportedMediaConversionError, UnsupportedMediaDownloadError
from pysubs.interfaces.media import MediaManager
from pysubs.utils.models import MediaType, Media, YouTubeVideo, ConvertedFile, MediaSource


class AwsS3MediaManager(MediaManager):
    def __init__(self):
        self.s3 = awss3.AwsS3()

    def get_media_info(self, video_url) -> Media:
        pass

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
    def get_media_info(self, video_url) -> Media:
        yt = YouTube(video_url)
        return Media(
            id=None,
            title=yt.title,
            thumbnail_url=yt.thumbnail_url,
            duration=timedelta(seconds=yt.length),
            content=None,
            source=MediaSource.YOUTUBE,
            file_type=MediaType.MP4,
            local_storage_path=None,
            source_url=video_url,
        )

    def upload(self, media: Media) -> Media:
        pass

    def download(self, media: Media) -> Media:
        if media.file_type != MediaType.MP4:
            raise UnsupportedMediaDownloadError(f"Downloading media with format: `{media.file_type}` is not supported")
        video_metadata: YouTubeVideo = YouTubeMediaManager._download_from_youtube(video_url=media.source_url)
        media.title = video_metadata.title
        media.duration = video_metadata.duration
        media.local_storage_path = video_metadata.local_storage_path
        media.thumbnail_url = video_metadata.thumbnail_url
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        if to_type != MediaType.MP3:
            raise UnsupportedMediaConversionError(f"Converting to {to_type} is not supported at this moment.")
        converted: ConvertedFile = YouTubeMediaManager._convert_to_mp3(media=media)
        converted_media = Media(
            id=media.id,
            title=media.title,
            content=None,
            duration=media.duration,
            source=media.source,
            file_type=to_type,
            local_storage_path=converted.local_storage_path,
            source_url=media.source_url,
            thumbnail_url=media.thumbnail_url
        )
        return converted_media

    @staticmethod
    def _download_from_youtube(video_url: str) -> YouTubeVideo:
        try:
            yt = YouTube(video_url)
            title = yt.title
            thumbnail_url = yt.thumbnail_url
            downloader = yt.streams.filter(
                progressive=True, file_extension="mp4"
            ).order_by('resolution').desc().first()
            filepath = downloader.download(
                output_path=tempfile.gettempdir(),
            )
            return YouTubeVideo(
                title=title,
                video_link=video_url,
                duration=timedelta(seconds=yt.length),
                content=None,
                local_storage_path=filepath,
                thumbnail_url=thumbnail_url
            )
        except AttributeError as e:
            logging.getLogger(LogConstants.LOGGER_NAME).error(
                f"Downloading youtube video from the url: {video_url} failed with error: {e}"
            )
            raise

    @staticmethod
    def _convert_to_mp3(media: Media) -> ConvertedFile:
        if media.file_type != MediaType.MP4:
            raise UnsupportedMediaConversionError(f"Unsupported file type conversion tried. {media.file_type}")
        mp3_filename = f"{str(uuid.uuid4())}.mp3"
        temp_audio_filepath = os.path.join(tempfile.gettempdir(), mp3_filename)
        YouTubeMediaManager._ffmpeg_convert(source=media.local_storage_path, dest=temp_audio_filepath, codec="mp3")
        return ConvertedFile(local_storage_path=temp_audio_filepath)

    @staticmethod
    def _ffmpeg_convert(source: str, dest: str, codec: str):
        ffmpeg.input(source).output(dest, acodec=codec).run()
