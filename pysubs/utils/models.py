from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from datetime import timedelta, datetime

from pydantic import BaseModel


# Responses
class GeneralResponse(BaseModel):
    status: str


class VideoMetadataResponse(GeneralResponse):
    video_url: str
    title: str
    video_length: int
    thumbnail: str


class GenerationStatusResponse(GeneralResponse):
    subtitle_id: Optional[str]
    video_id: Optional[str]
    video_url: Optional[str]
    title: Optional[str]
    video_length: Optional[int]
    thumbnail: Optional[str]
    subtitle: Optional[str]
    created_at: Optional[datetime]


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
    language: str
    media_id: str


class User(BaseModel):
    id: Optional[str]
    email: Optional[str]


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
