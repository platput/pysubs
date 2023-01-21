import logging
import tempfile
from datetime import timedelta
from typing import Optional

from fastapi import UploadFile
from pytube import YouTube
from pysubs.utils.constants import LogConstants
from pysubs.exceptions.media import UnsupportedMediaConversionError, UnsupportedMediaDownloadError
from pysubs.interfaces.media import MediaManager
from pysubs.utils.conversion import convert_to_mp3
from pysubs.utils.models import MediaType, Media, YouTubeVideo, ConvertedFile, MediaSource


class YouTubeMediaManager(MediaManager):
    def get_media_info(self, video_url: Optional[str] = None, video_file: Optional[UploadFile] = None) -> Media:
        """
        Gets the information about the video located at the YouTube video url
        :param video_url:
        :param video_file:
        :return:
        """
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
        """
        Downloads the video from YouTube for further processing
        :param media:
        :return:
        """
        if media.file_type != MediaType.MP4:
            raise UnsupportedMediaDownloadError(f"Downloading media with format: `{media.file_type}` is not supported")
        video_metadata: YouTubeVideo = YouTubeMediaManager._download_from_youtube(video_url=media.source_url)
        media.title = video_metadata.title
        media.duration = video_metadata.duration
        media.local_storage_path = video_metadata.local_storage_path
        media.thumbnail_url = video_metadata.thumbnail_url
        return media

    def convert(self, media: Media, to_type: MediaType) -> Media:
        """
        Converts the video to mp3 for further processing
        :param media:
        :param to_type:
        :return:
        """
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
        """
        This helper function contains the logic to download the video from YouTube
        :param video_url:
        :return:
        """
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

