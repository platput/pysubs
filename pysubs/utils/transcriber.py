from io import StringIO

from pysubs.interfaces.asr import ASR
import whisper
from whisper.utils import write_srt

from pysubs.utils.models import Media


class WhisperTranscriber(ASR):
    def __init__(self):
        self.model = whisper.load_model("base")

    def process_audio(self, audio: Media) -> dict[str, list | dict]:
        return self.model.transcribe(audio.local_storage_path)

    def generate_subtitles(self, processed_data: dict) -> str:
        content = StringIO()
        write_srt(processed_data["segments"], file=content)
        return content.getvalue()
