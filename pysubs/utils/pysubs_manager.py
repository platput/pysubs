import hashlib
import json
import logging
import threading
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Optional

from google.api_core.exceptions import PermissionDenied
from pysubs.dal.datastore_models import MediaModel, SubtitleModel
from pysubs.dal.firestore import FirestoreDatastore
from pysubs.interfaces.asr import ASR
from pysubs.interfaces.media import MediaManager
from pysubs.utils.models import Media, MediaSource, MediaType, Transcription, User, Subtitle
from pysubs.utils.transcriber import WhisperTranscriber
from pysubs.utils.video import YouTubeMediaManager
from pysubs.utils.constants import LogConstants

logger = logging.getLogger(LogConstants.LOGGER_NAME)


def process_yt_video_url_and_generate_subtitles(video_url: str, user: User):
    audio = get_audio_from_yt_video(video_url=video_url, user=user)
    logger.info(f"Audio generated for the video url: {video_url}")
    transcription = get_subtitles_from_audio(audio=audio)
    logger.info(f"Audio transcription finished for the video url: {video_url}")
    save_transcription_attempt(audio, transcription, user)
    logger.info(f"Saved data to datastore.")


def get_audio_from_yt_video(video_url: str, user: User) -> Media:
    mgr: MediaManager = YouTubeMediaManager()
    media: Media = Media(
        id=generate_media_id(media_url=video_url, user=user),
        title=None,
        content=None,
        duration=None,
        source=MediaSource.YOUTUBE,
        file_type=MediaType.MP4,
        local_storage_path=None,
        source_url=video_url,
        thumbnail_url=None
    )
    video = mgr.download(media=media)
    audio = mgr.convert(media=video, to_type=MediaType.MP3)
    return audio


def generate_transcription_id(media_id: str, language: str) -> str:
    key_helper_dict = OrderedDict({
        "media_id": media_id,
        "language": language
    })
    key_helper = json.dumps(key_helper_dict).encode("utf-8")
    return hashlib.sha256(key_helper).hexdigest()


def generate_media_id(media_url: str, user: User) -> str:
    key_helper_dict = OrderedDict({
        "media_url": media_url,
        "user_id": user.id
    })
    key_helper = json.dumps(key_helper_dict).encode("utf-8")
    return hashlib.sha256(key_helper).hexdigest()


def get_subtitles_from_audio(audio: Media) -> Transcription:
    transcriber: ASR = WhisperTranscriber()
    result = transcriber.process_audio(audio=audio)
    language = transcriber.get_detected_language(processed_data=result)
    content = transcriber.generate_subtitles(processed_data=result)
    return Transcription(
        id=generate_transcription_id(media_id=audio.id, language=language),
        content=content,
        language=language,
        media_id=audio.id
    )


def start_transcribe_worker(video_url: str, user: User) -> None:
    thr = threading.Thread(target=process_yt_video_url_and_generate_subtitles, args=(video_url, user,))
    thr.start()


def save_transcription_attempt(audio: Media, transcription: Transcription, user: User) -> None:
    current_time = datetime.utcnow()
    fs = FirestoreDatastore.instance()
    ds_media = MediaModel(
        id=audio.id,
        user_id=user.id,
        title=audio.title,
        duration=audio.duration.seconds,
        media_url=audio.source_url,
        media_source=audio.source.value,
        thumbnail_url=audio.thumbnail_url,
        created_at=current_time
    )
    expire_at = current_time + timedelta(days=10)
    ds_subtitle = SubtitleModel(
        id=transcription.id,
        media_id=transcription.media_id,
        content=transcription.content,
        created_at=current_time,
        expire_at=expire_at
    )
    try:
        fs.upsert_media(ds_media)
        fs.upsert_subtitle(ds_subtitle)
    except PermissionDenied as e:
        logger.error(f"Error due to insufficient permissions for adding data to Firestore, error: {e}")


def get_subtitle_generation_status(video_url: str, user: User) -> tuple[Optional[MediaModel], Optional[SubtitleModel]]:
    media_id = generate_media_id(video_url, user)
    fs = FirestoreDatastore.instance()
    if media := fs.get_media(media_id=media_id):
        if subtitle := fs.get_subtitle_for_media(media_id=media_id):
            return media, subtitle
    else:
        return None, None


def get_history(last_created_at: Optional[datetime], count: int, user: User) -> list[Subtitle]:
    fs = FirestoreDatastore.instance()
    history = fs.get_history_for_user(user_id=user.id, last_created_at=last_created_at, count=count)
    resp: list[Subtitle] = []
    for item in history:
        media = item.media
        subtitles = item.subtitles
        for sub in subtitles:
            resp.append(
                Subtitle(
                    subtitle_id=sub.id,
                    video_url=media.media_url,
                    title=media.title,
                    video_length=media.duration,
                    thumbnail=media.thumbnail_url,
                    subtitle=sub.content,
                    created_at=media.created_at
                )
            )
    return resp
