import hashlib
import json
import logging
import tempfile
from datetime import timedelta
from typing import Optional
from collections import OrderedDict

from fastapi import UploadFile
from pytube import YouTube

from pysubs.dal.datastore_models import UserModel
from pysubs.utils.constants import LogConstants
from pysubs.exceptions.media import UnsupportedMediaConversionError, UnsupportedMediaDownloadError
from pysubs.interfaces.media import MediaManager
from pysubs.utils.conversion import convert_to_mp3
from pysubs.utils.models import MediaType, Media, YouTubeVideo, ConvertedFile, MediaSource


class YouTubeMediaManager(MediaManager):
    @staticmethod
    def create_media(video_source: Optional[str | UploadFile], user: UserModel) -> Media:
        """
        Creates the media object which can be passed around until the subtitle is generated
        :param video_source:
        :param user:
        :return:
        """
        media = Media(
            id=None,
            source=MediaSource.YOUTUBE,
            file_type=MediaType.MP4,
            source_url=video_source
        )
        media.id = YouTubeMediaManager.generate_media_id(media=media, user=user)
        return media

    @staticmethod
    def generate_media_id(
            media: Media,
            user: UserModel
    ) -> str:
        """
        Generates the media id using the user and the video url
        :param media:
        :param user:
        :return:
        """
        key_helper_dict = OrderedDict({
            "media_url": media.source_url,
            "user_id": user.id
        })
        key_helper = json.dumps(key_helper_dict).encode("utf-8")
        return hashlib.sha256(key_helper).hexdigest()

    def get_media_info(
            self,
            media: Media,
            user: UserModel
    ) -> Media:
        """
        Gets the information about the video located at the YouTube video url
        :param media:
        :param user:
        :return:
        """
        video_url = media.source_url
        yt = YouTube(video_url)
        media_id = media.id if media.id else YouTubeMediaManager.generate_media_id(media, user)
        return Media(
            id=media_id,
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

