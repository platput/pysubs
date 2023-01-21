import base64
import os
import uuid
from datetime import timedelta, datetime

from fastapi import UploadFile

from pysubs.dal.datastore_models import MediaSubtitlesModel, SubtitleModel, MediaModel
from pysubs.dal.firestore import FirestoreDatastore
from pysubs.utils.models import YouTubeVideo, ConvertedFile, Media, MediaType, MediaSource


def mock_ffmpeg_convert(**_) -> None:
    return None


def mock_convert_to_mp3(_: Media) -> ConvertedFile:
    return ConvertedFile(local_storage_path="/file.mp3")


def mock_download_from_youtube(*_, **__) -> YouTubeVideo:
    return YouTubeVideo(
        title="test title",
        video_link="https://yt.com/v",
        duration=timedelta(seconds=123),
        content=b"test content",
        local_storage_path="/file.mp4",
        thumbnail_url="https://yt.com/v.jpg"
    )


def mock_convert(_, media: Media, to_type: MediaType) -> Media:
    converted_media = Media(
        id=str(uuid.uuid4()),
        title=media.title,
        content=None,
        duration=media.duration,
        source=media.source,
        file_type=to_type,
        local_storage_path="/file.mp3",
        source_url=media.source_url,
        thumbnail_url=media.thumbnail_url
    )
    return converted_media


def mock_write_content_to_file(local_storage_path: str, file_content: str | bytes) -> str:
    return local_storage_path


def mock_get_media_duration(media_file_path: str) -> float:
    return 100.0


def mock_create_thumbnail(media_file_path: str) -> str:
    return f"{os.path.basename(media_file_path)}-thumbnail.{os.path.splitext(media_file_path)[1]}"


def mock_get_base64_src_for_image(image_filepath: str) -> str:
    return f"data:image/jpeg;base64,{base64.b64encode(b'123')}"


def mock_download(_, media: Media) -> Media:
    media.title = "video_metadata.title"
    media.duration = timedelta(minutes=2)
    media.local_storage_path = "/file.mp4"
    media.thumbnail_url = "https://yt.com/be.jpg"
    return media


def mock_process_audio(_, audio: Media) -> dict:
    return {"text": "subtitle"}


def mock_generate_subtitles(_, processed_data: dict) -> str:
    return "subtitle"


def mock_get_media_info(_, video_file: UploadFile) -> Media:
    return Media(
        id=None,
        title="testfile.mp4",
        content=b"test content",
        duration=timedelta(seconds=100),
        source=MediaSource.RAW_FILE,
        file_type=MediaType.MP4,
        local_storage_path="/testfile.mp4",
        source_url="/testfile.mp4",
        thumbnail_url="/testfile.jpg",
    )


def mock_firestore_instance():
    return FirestoreDatastore


def mock_get_history_for_user(user_id, last_created_at, count):
    media_id = str(uuid.uuid4())
    sub_id = str(uuid.uuid4())
    media = MediaModel(
        id=media_id,
        user_id=user_id,
        title="testfile.mp4",
        duration=100,
        media_url="/testfile.mp4",
        media_source="/testfile.mp4",
        thumbnail_url="/testfile.jpg",
        created_at=last_created_at,
    )
    subtitle = SubtitleModel(
        id=sub_id,
        media_id=media_id,
        content="subtitles",
        language="en",
        created_at=datetime.now(),
        expire_at=datetime.now(),
    )
    return [MediaSubtitlesModel(media=media, subtitles=[subtitle])]
