from abc import ABCMeta, abstractmethod

from pysubs.dal.datastore_models import MediaModel, SubtitleModel


class Datastore(metaclass=ABCMeta):
    @abstractmethod
    def upsert_media(self, media: MediaModel) -> MediaModel:
        pass

    @abstractmethod
    def upsert_subtitle(self, subtitle: SubtitleModel) -> SubtitleModel:
        pass
