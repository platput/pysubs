from abc import ABCMeta, abstractmethod
from typing import Optional

from fastapi import UploadFile

from pysubs.utils.models import MediaType, Media


class MediaManager(metaclass=ABCMeta):
    @abstractmethod
    def get_media_info(self, video_url: Optional[str] = None, video_file: Optional[UploadFile] = None) -> Media:
        pass

    @abstractmethod
    def download(self, media: Media) -> Media:
        pass

    @abstractmethod
    def upload(self, media: Media) -> Media:
        pass

    @abstractmethod
    def convert(self, media: Media, to_type: MediaType) -> Media:
        pass
