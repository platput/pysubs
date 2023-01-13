from pysubs.utils.pysubs_manager import get_audio_from_yt_video, get_subtitles_from_audio
from pysubs.utils.models import Media, MediaType, MediaSource


def mock_convert(self, media: Media, to_type: MediaType) -> Media:
    media.file_type = to_type
    return media


def mock_process_audio(self, audio: Media) -> dict:
    return {"text": "subtitle"}


def mock_generate_subtitles(self, processed_data: dict) -> str:
    return "subtitle"


class TestPySubsManager:
    def test_get_audio_from_yt_video(self, monkeypatch):
        video_url = "https://youtube.com/testvideo"
        monkeypatch.setattr(
            "pysubs.utils.video.YouTubeMediaManager.convert",
            mock_convert
        )
        media = get_audio_from_yt_video(video_url=video_url)
        assert media.file_type == MediaType.MP3
        assert media.source_url == video_url

    def test_get_subtitles_from_audio(self, monkeypatch):
        monkeypatch.setattr(
            "pysubs.utils.transcriber.WhisperTranscriber.process_audio",
            mock_process_audio
        )
        monkeypatch.setattr(
            "pysubs.utils.transcriber.WhisperTranscriber.generate_subtitles",
            mock_generate_subtitles
        )
        audio = Media(
            id="123456",
            title="",
            content=b"",
            source=MediaSource.YOUTUBE,
            file_type=MediaType.MP3,
            _source_url="https://youtube.com/testvideo",
            local_storage_path=None
        )
        transcription = get_subtitles_from_audio(audio=audio)
        assert transcription.parent_id == audio.id
