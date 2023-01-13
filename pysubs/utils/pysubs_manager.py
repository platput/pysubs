import threading
import uuid

from pysubs.utils.interfaces.asr import ASR
from pysubs.utils.interfaces.media import MediaManager
from pysubs.utils.models import Media, MediaSource, MediaType, Transcription
from pysubs.utils.transcriber import WhisperTranscriber
from pysubs.utils.video import YouTubeMediaManager


def process_yt_video_url_and_generate_subtitles(video_url: str) -> Transcription:
    audio = get_audio_from_yt_video(video_url=video_url)
    transcription = get_subtitles_from_audio(audio=audio)
    return transcription


def get_audio_from_yt_video(video_url: str) -> Media:
    mgr: MediaManager = YouTubeMediaManager()
    media: Media = Media(
        id=str(uuid.uuid4()),
        title="",
        content=b"",
        source=MediaSource.YOUTUBE,
        file_type=MediaType.UNKNOWN,
        _source_url=video_url
    )
    audio = mgr.convert(media=media, to_type=MediaType.MP3)
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


def start_transcribe_worker(video_url: str) -> None:
    thr = threading.Thread(target=process_yt_video_url_and_generate_subtitles, args=(video_url,))
    thr.start()
