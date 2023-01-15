from abc import ABCMeta, abstractmethod

from pysubs.utils.models import Media


class ASR(metaclass=ABCMeta):
    @abstractmethod
    def process_audio(self, audio: Media) -> dict[str, list | dict]:
        pass

    @abstractmethod
    def generate_subtitles(self, processed_data: dict) -> str:
        pass

    @abstractmethod
    def get_detected_language(self, processed_data: dict) -> str:
        pass
