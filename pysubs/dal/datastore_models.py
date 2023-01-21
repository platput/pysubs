from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class MediaModel(BaseModel):
    """
    datastore model to store the media, which can either be audio or video
    """
    id: str
    user_id: Optional[str]
    title: str
    duration: int
    media_url: Optional[str]
    media_source: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime = datetime.utcnow()


class SubtitleModel(BaseModel):
    """
    datastore model to store the subtitles
    """
    id: str
    media_id: str
    content: str
    language: str = "en"
    created_at: datetime
    expire_at: datetime


class MediaSubtitlesModel(BaseModel):
    """A helper model to get the data from firestore which will contain all the medias and the subtitles each media has"""
    media: MediaModel
    subtitles: list[SubtitleModel]


class UserModel(BaseModel):
    """Data store representation of the user model"""
    id: str
    credits: int
    displayName: str
    email: str
    createdAt: datetime
