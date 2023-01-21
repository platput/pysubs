from abc import ABCMeta, abstractmethod

from pysubs.utils.models import Media


class ASR(metaclass=ABCMeta):
    """
    This class is an abstract class which has to be implemented by all audio speech recognition services
    """
    @abstractmethod
    def process_audio(self, audio: Media) -> dict[str, list | dict]:
        """
        Process the audio by the speech transcriptor and returns a dict with all the required details
        :param audio:
        :return:
        """
        pass

    @abstractmethod
    def generate_subtitles(self, processed_data: dict) -> str:
        """
        get the subtitles from the processed audio file's data
        :param processed_data:
        :return:
        """
        pass

    @abstractmethod
    def get_detected_language(self, processed_data: dict) -> str:
        """
        get the detected language from teh processed audio.
        :param processed_data:
        :return:
        """
        pass
