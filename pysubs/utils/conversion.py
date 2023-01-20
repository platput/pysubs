import os
import tempfile
import uuid

import ffmpeg

from pysubs.exceptions.media import UnsupportedMediaConversionError
from pysubs.utils.models import ConvertedFile, Media, MediaType


def convert_to_mp3(media: Media) -> ConvertedFile:
    if media.file_type != MediaType.MP4:
        raise UnsupportedMediaConversionError(f"Unsupported file type conversion tried. {media.file_type}")
    mp3_filename = f"{str(uuid.uuid4())}.mp3"
    temp_audio_filepath = os.path.join(tempfile.gettempdir(), mp3_filename)
    ffmpeg_convert(source=media.local_storage_path, dest=temp_audio_filepath, codec="mp3")
    return ConvertedFile(local_storage_path=temp_audio_filepath)


def ffmpeg_convert(source: str, dest: str, codec: str):
    ffmpeg.input(source).output(dest, acodec=codec).run()
