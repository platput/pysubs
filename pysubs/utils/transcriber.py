import tempfile

from pysubs.utils.interfaces.asr import ASR
import whisper

from pysubs.utils.models import Media


class WhisperTranscriber(ASR):
    def __init__(self):
        self.model = whisper.load_model("base")

    def process_audio(self, audio: Media) -> dict[str, list | dict]:
        with open(tempfile.TemporaryFile(), "w") as audio_file:
            audio_file.write(audio.content.decode("utf-8"))
            audio_file.seek(0)
        return self.model.transcribe(audio_file)

    def generate_subtitles(self, processed_data: dict) -> str:
        return processed_data["text"]

