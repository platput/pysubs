from io import StringIO

from pysubs.interfaces.asr import ASR
import whisper
from whisper.utils import write_srt

from pysubs.utils.models import Media


class WhisperTranscriber(ASR):
    """
    Transcription class based on off Whisper
    """
    def __init__(self):
        """
        Initializer sets the model as base
        """
        self.model = whisper.load_model("base")

    def process_audio(self, audio: Media) -> dict[str, list | dict]:
        """
        processes the audio content form the media file
        :param audio:
        :return:
        """
        return self.model.transcribe(audio.local_storage_path)

    def get_detected_language(self, processed_data: dict) -> str:
        """
        detects the language from the processed data and returns it
        :param processed_data:
        :return:
        """
        return processed_data.get("language")

    def generate_subtitles(self, processed_data: dict) -> str:
        """
        generates the subtitles from the processed data.
        :param processed_data:
        :return:
        """
        content = StringIO()
        write_srt(processed_data["segments"], file=content)
        return content.getvalue()
