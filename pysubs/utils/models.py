from dataclasses import dataclass
from enum import Enum, auto
from typing import TypedDict, Optional
from datetime import timedelta


# Responses
class GeneralResponse(TypedDict):
    status: str


class VideoMetadataResponse(GeneralResponse):
    video_url: str
    title: str
    video_length: timedelta
    thumbnail: bytes


# Enums
class MediaType(Enum):
    MP3 = auto()
    MP4 = auto()
    UNKNOWN = auto()


class MediaSource(Enum):
    AWS = "AWS"
    YOUTUBE = "YOUTUBE"


# Data
@dataclass
class Media:
    id: str
    title: Optional[str]
    content: Optional[bytes]
    thumbnail_url: Optional[str]
    source_url: str
    source: MediaSource
    file_type: MediaType
    duration: Optional[timedelta]
    local_storage_path: Optional[str]

    @property
    def filename(self) -> str:
        return f"{self.id}.{self.file_type}"


@dataclass
class Transcription:
    id: str
    content: str
    parent_id: str


@dataclass
class User:
    id: Optional[str]


@dataclass
class YouTubeVideo:
    title: str
    video_link: str
    duration: timedelta
    content: Optional[bytes]
    thumbnail_url: Optional[str]
    local_storage_path: str


@dataclass
class ConvertedFile:
    local_storage_path: str
