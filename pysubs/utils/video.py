import base64
import logging
import os.path
import tempfile
import uuid
from datetime import timedelta, datetime
from typing import Optional

import ffmpeg
from fastapi import UploadFile
from pytube import YouTube
from pysubs.utils.constants import LogConstants
from pysubs.exceptions.media import UnsupportedMediaConversionError, UnsupportedMediaDownloadError, \
    DecodingMediaDurationError
from pysubs.interfaces.media import MediaManager
from pysubs.utils.conversion import convert_to_mp3
from pysubs.utils.models import MediaType, Media, YouTubeVideo, ConvertedFile, MediaSource


class YouTubeMediaManager(MediaManager):
    def get_media_info(self, video_url: Optional[str] = None, video_file: Optional[UploadFile] = None) -> Media:
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
        converted: ConvertedFile = convert_to_mp3(media=media)
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


class FileMediaManager(MediaManager):
    def upload(self, media: Media) -> Media:
        pass

    def get_media_info(self, video_url: Optional[str] = None, video_file: Optional[UploadFile] = None) -> Media:
        with video_file.file as video:
            content = video.read()
        temp_dir = tempfile.gettempdir()
        uploaded_filename = os.path.splitext(video_file.filename)
        current_timestamp = int(round(datetime.now().timestamp()))
        # Sanitizing the user inputted filename
        # TODO: To be improved later using regex
        sanitized_filename = uploaded_filename[0].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "")
        sanitized_ext = uploaded_filename[1].replace("&", "").replace(" ", "_").replace("|", "").replace(";", "")
        video_filename = f"{sanitized_filename}-{current_timestamp}.{sanitized_ext}"
        local_storage_path = os.path.join(temp_dir, video_filename)
        with open(local_storage_path, "wb") as video:
            video.write(content)
        # Get duration
        media_details = ffmpeg.probe(local_storage_path)
        try:
            duration = media_details["format"]["duration"]
        except KeyError:
            raise DecodingMediaDurationError(f"Unknown error in decoding media duration: {media_details}")
        # Get thumbnail
        # https://github.com/kkroening/ffmpeg-python/blob/master/examples/README.md
        thumbnail_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        ffmpeg.input(
            thumbnail_path, ss=1
        ).filter(
            'scale', 300, -1
        ).output(
            "abc.jpg", vframes=1
        ).overwrite_output().run(quiet=True)
        # Convert image to base 64 format and save it as url
        with open(thumbnail_path, "rb") as image_file:
            content = image_file.read()
            thumbnail_url = f"data:image/jpeg;base64,{base64.b64encode(content)}"
        return Media(
            id=None,
            title=os.path.basename(local_storage_path),
            thumbnail_url=thumbnail_url,
            duration=timedelta(seconds=duration),
            content=None,
            source=MediaSource.RAW_FILE,
            file_type=MediaType.MP4,
            local_storage_path=local_storage_path,
            source_url=local_storage_path,
        )

    def download(self, media: Media) -> Media:
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        if to_type != MediaType.MP3:
            raise UnsupportedMediaConversionError(f"Converting to {to_type} is not supported at this moment.")
        converted: ConvertedFile = convert_to_mp3(media=media)
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
