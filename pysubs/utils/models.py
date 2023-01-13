from dataclasses import dataclass
from enum import Enum, auto
from typing import TypedDict

from pysubs.utils.constants import Storage
from pysubs.utils.exceptions.models import UnspecifiedMediaSourceTypeError


# Responses
class GeneralResponse(TypedDict):
    id: str
    status: str


# Enums
class MediaType(Enum):
    MP3 = auto()
    MP4 = auto()
    UNKNOWN = auto()


class MediaSource(Enum):
    AWS = auto()
    YOUTUBE = auto()


# Data
@dataclass
class Media:
    id: str
    title: str
    content: bytes
    source: MediaSource
    file_type: MediaType
    _source_url: str = ""

    @property
    def filename(self) -> str:
        return f"{self.id}.{self.file_type}"

    @property
    def source_url(self) -> str:
        if self.source == MediaSource.AWS:
            if not self._source_url:
                if self.file_type == MediaType.MP4:
                    file_type = "mp4"
                elif self.file_type == MediaType.MP3:
                    file_type = "mp3"
                else:
                    file_type = ""
                return f"{Storage.STORAGE_URL_PREFIX}/{self.id}.{file_type}"
            else:
                return self._source_url
        elif self.source == MediaSource.YOUTUBE:
            return self._source_url
        else:
            raise UnspecifiedMediaSourceTypeError("Media dataclass has unset source attribute.")

    @source_url.setter
    def source_url(self, url: str) -> None:
        self._source_url = url


@dataclass
class Transcription:
    id: str
    content: str
    parent_id: str
