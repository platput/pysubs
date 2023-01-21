from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Optional

from pysubs.dal.datastore_models import MediaModel, SubtitleModel, UserModel, MediaSubtitlesModel


class Datastore(metaclass=ABCMeta):
    """
    Abstract class which has to be implemented by all data stores
    """
    @abstractmethod
    def upsert_media(self, media: MediaModel) -> MediaModel:
        """
        upserts the media
        :param media:
        :return:
        """
        pass

    @abstractmethod
    def upsert_subtitle(self, subtitle: SubtitleModel) -> SubtitleModel:
        """
        upserts the subtitle
        :param subtitle:
        :return:
        """
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[UserModel]:
        """
        gets the user data from the datastore for a given user id
        :param user_id:
        :return:
        """
        pass

    @abstractmethod
    def upsert_user(self, user: UserModel) -> UserModel:
        """
        upserts the user
        :param user:
        :return:
        """
        pass

    @abstractmethod
    def get_media(self, media_id: str) -> MediaModel:
        """
        gets the media data for a given media id from the database
        :param media_id:
        :return:
        """
        pass

    @abstractmethod
    def get_subtitle_for_media(self, media_id: str) -> SubtitleModel:
        """
        gets the subtitle for a given media id
        TODO: a media can have multiple subtitles, this method has to be updated to provision that later.
        :param media_id:
        :return:
        """
        pass

    @abstractmethod
    def get_history_for_user(
            self,
            user_id: str,
            last_created_at: Optional[datetime] = None,
            count: int = 100
    ) -> list[MediaSubtitlesModel]:
        """
        gets the history for a given user
        can be paginated by using count and last created at
        :param user_id:
        :param last_created_at:
        :param count:
        :return:
        """
        pass
