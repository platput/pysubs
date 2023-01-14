from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class MediaModel(BaseModel):
    id: str
    user_id: Optional[str]
    title: str
    duration: int
    media_url: Optional[str]
    media_source: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime = datetime.utcnow()


class SubtitleModel(BaseModel):
    id: str
    media_id: str
    content: str
    created_at: datetime
    expire_at: datetime


class UserModel(BaseModel):
    id: str
    credits: int
    created_at: datetime
