from abc import ABCMeta, abstractmethod
from typing import Optional

from fastapi import UploadFile

from pysubs.dal.datastore_models import UserModel
from pysubs.utils.models import MediaType, Media


class MediaManager(metaclass=ABCMeta):
    """
    Media manager abstract class which has to be implemented by all supported media managers like YouTube, file, aws etc.
    """
    @staticmethod
    @abstractmethod
    def create_media(
            video_source: Optional[str | UploadFile],
            user: UserModel
    ) -> Media:
        """
        Creates the media object which can be passed around until the subtitle is generated
        :param video_source:
        :param user:
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def generate_media_id(
            media: Media,
            user: UserModel,
    ) -> str:
        """
        Generates the media id based on the user id and video url/file
        :param media:
        :param user:
        :return:
        """
        pass

    @abstractmethod
    def get_media_info(
            self,
            media: Media,
            user: UserModel
    ) -> Media:
        """
        Get the information about the video as required by the media model
        The input can either be a video url or the actual uploaded video file
        :param media:
        :param user:
        :return:
        """
        pass

    @abstractmethod
    def download(self, media: Media) -> Media:
        """
        In case the video has to be downloaded from a video URL, this method should implement that logic
        :param media:
        :return:
        """
        pass

    @abstractmethod
    def upload(self, media: Media) -> Media:
        """
        In case the media has to be uploaded to someplace, this is the method to add that logic
        :param media:
        :return:
        """
        pass

    @abstractmethod
    def convert(self, media: Media, to_type: MediaType) -> Media:
        """
        Media conversion has to be done here.
        All video files will have to be converted to mp3 so that the ASR can process it.
        :param media:
        :param to_type:
        :return:
        """
        pass
