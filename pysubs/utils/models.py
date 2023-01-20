from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from datetime import timedelta, datetime

from pydantic import BaseModel

from pysubs.dal.datastore_models import UserModel


# Responses
class GeneralResponse(BaseModel):
    status: str


class VideoMetadataResponse(GeneralResponse):
    video_url: str
    title: str
    video_length: int
    thumbnail: str


class Subtitle(BaseModel):
    subtitle_id: Optional[str]
    video_url: Optional[str]
    title: Optional[str]
    video_length: Optional[int]
    thumbnail: Optional[str]
    subtitle: Optional[str]
    created_at: Optional[datetime]


class SubtitleResponse(GeneralResponse, Subtitle):
    pass


class UserResponse(GeneralResponse, UserModel):
    pass


class HistoryResponse(GeneralResponse):
    subtitles: list[Subtitle]


# Enums
class MediaType(Enum):
    MP3 = auto()
    MP4 = auto()
    UNKNOWN = auto()


class MediaSource(Enum):
    AWS = "AWS"
    YOUTUBE = "YOUTUBE"
    RAW_FILE = "RAW_FILE"


# Data
@dataclass
class Media:
    id: Optional[str]
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
    language: str
    media_id: str


@dataclass
class YouTubeVideo:
    title: str
    video_link: str
    duration: timedelta
    content: Optional[bytes]
    thumbnail_url: Optional[str]
    local_storage_path: str


@dataclass
class VideoFile:
    title: str
    video_link: str
    duration: timedelta
    content: Optional[bytes]
    thumbnail_url: Optional[str]
    local_storage_path: str

@dataclass
class ConvertedFile:
    local_storage_path: str
