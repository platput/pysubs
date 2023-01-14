import logging
import threading
import uuid
from datetime import datetime, timedelta
from google.api_core.exceptions import PermissionDenied
from pysubs.dal.datastore_models import MediaModel, SubtitleModel
from pysubs.dal.firestore import FirestoreDatastore
from pysubs.interfaces.asr import ASR
from pysubs.interfaces.media import MediaManager
from pysubs.utils.models import Media, MediaSource, MediaType, Transcription, User
from pysubs.utils.transcriber import WhisperTranscriber
from pysubs.utils.video import YouTubeMediaManager
from pysubs.utils.constants import LogConstants

logger = logging.getLogger(LogConstants.LOGGER_NAME)


def process_yt_video_url_and_generate_subtitles(video_url: str, user: User):
    audio = get_audio_from_yt_video(video_url=video_url)
    logger.info(f"Audio generated for the video url: {video_url}")
    transcription = get_subtitles_from_audio(audio=audio)
    logger.info(f"Audio transcription finished for the video url: {video_url}")
    save_transcription_attempt(audio, transcription, user)
    logger.info(f"Saved data to datastore.")


def get_audio_from_yt_video(video_url: str) -> Media:
    mgr: MediaManager = YouTubeMediaManager()
    media: Media = Media(
        id=str(uuid.uuid4()),
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


def get_subtitles_from_audio(audio: Media) -> Transcription:
    transcriber: ASR = WhisperTranscriber()
    result = transcriber.process_audio(audio=audio)
    content = transcriber.generate_subtitles(processed_data=result)
    return Transcription(
        id=str(uuid.uuid4()),
        content=content,
        parent_id=audio.id
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
        media_id=transcription.parent_id,
        content=transcription.content,
        created_at=current_time,
        expire_at=expire_at
    )
    try:
        fs.upsert_media(ds_media)
        fs.upsert_subtitle(ds_subtitle)
    except PermissionDenied as e:
        logger.error(f"Error due to insufficient permissions for adding data to Firestore, error: {e}")

